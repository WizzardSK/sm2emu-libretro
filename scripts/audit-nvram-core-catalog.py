#!/usr/bin/env python3
"""Audit the NVRAM Core Options against the screenshot-derived catalog.

The screenshot catalog owns menu presence, order, native defaults and observed
values. The reviewed workbook owns the parent-game selection. Clone selections
inherit that review, except for the two explicitly reviewed clone-only fields
below and Motor Raid Deluxe's read-only Engine Volume row.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import re
import json
import hashlib
import tomllib
import sys
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "GAME_SETTINGS_CATALOG.md"
WORKBOOK = ROOT / "Docs/revisione_core_options_model2.xlsx"
GAMES_XML = ROOT / "data/games.xml"
CORE_DATA = ROOT / "src/libretro/nvram_settings_data.inc"

# These are the only reviewed clone-only Core Options. All other clone choices
# are inherited from the parent's reviewed workbook selection.
CLONE_ADDITIONS = {
    "daytonas": {"PROMOTE SATURN"},
    "motoraiddx": {"CABINET TYPE"},
}
CLONE_EXCLUSIONS = {
    # The Deluxe menu displays this row as OUT OF USE and cannot select it.
    "motoraiddx": {"ENGINE VOLUME"},
}


def normalized(value: str) -> str:
    value = value.upper().replace("’", "'")
    value = re.sub(r"U\.?S\.?A?\.?\b", "USA", value)
    value = re.sub(r"\bJPN\b", "JAPAN", value)
    value = re.sub(r"\bEXP\b", "EXPORT", value)
    value = re.sub(r"\bEUR\b", "EUROPE", value)
    value = re.sub(r"C\.?R\.?T\.?", "CRT", value)
    return re.sub(r"[^A-Z0-9#+-]+", " ", value).strip()


def parse_catalog() -> dict[str, list[dict[str, str]]]:
    result: dict[str, list[dict[str, str]]] = {}
    current = None
    for line in CATALOG.read_text().splitlines():
        heading = re.match(r"^### .* \(`([^`]+)`\)$", line)
        if heading:
            current = heading.group(1)
            result[current] = []
        elif current and re.match(r"^\| \d+ \|", line):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            result[current].append(
                {"label": cells[1], "default": cells[2], "values": cells[3]}
            )
    return result


def parse_parent_selections() -> dict[str, list[str]]:
    namespace = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    selected: dict[str, list[str]] = defaultdict(list)
    with zipfile.ZipFile(WORKBOOK) as archive:
        sheet = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
    rows = sheet.findall(".//m:sheetData/m:row", namespace)[1:]
    for row in rows:
        values: dict[str, str] = {}
        for cell in row.findall("m:c", namespace):
            column = re.match(r"[A-Z]+", cell.attrib["r"]).group(0)
            if cell.attrib.get("t") == "inlineStr":
                value = "".join(
                    text.text or "" for text in cell.findall(".//m:t", namespace)
                )
            else:
                raw = cell.find("m:v", namespace)
                value = "" if raw is None else raw.text or ""
            values[column] = value
        if values.get("F") == "Yes":
            selected[values["B"]].append(values["C"])
    return selected


def parse_core_options() -> dict[str, list[dict[str, object]]]:
    source = CORE_DATA.read_text()
    value_arrays: dict[str, list[tuple[str, str]]] = {}
    value_pattern = re.compile(
        r"static constexpr Value (k\w*Values\d*)\[\] = \{(.*?)\n\};", re.S
    )
    for match in value_pattern.finditer(source):
        value_arrays[match.group(1)] = re.findall(
            r'\{"([^"]+)", "([^"]*)",', match.group(2)
        )

    block = source.split("static constexpr Option kOptions[] = {", 1)[1].split(
        "\n};", 1
    )[0]
    option_pattern = re.compile(
        r'^\s*\{"([^"]+)", "([^"]+)", "([^"]+)", '
        r'"((?:[^"\\]|\\.)*)", "([^"]+)", (k\w*Values\d*),',
        re.M,
    )
    options: dict[str, list[dict[str, object]]] = defaultdict(list)
    for match in option_pattern.finditer(block):
        values = value_arrays[match.group(6)]
        options[match.group(1)].append(
            {
                "suffix": match.group(2),
                "label": match.group(3),
                "description": match.group(4),
                "default_key": match.group(5),
                "values": values,
            }
        )
    return options


def documented_values(cell: str) -> list[str]:
    if cell in {"—", "nessun ciclo dedicato", "non acquisiti"}:
        return []
    return [value.strip() for value in cell.split(",")]


def expected_default(game: str, option: dict[str, object], native: str) -> str:
    suffix = str(option["suffix"])
    labels = [label for _, label in option["values"]]
    overrides = {
        ("daytona", "cabinet"): "DELUXE",
        ("daytona93", "cabinet"): "DELUXE",
        ("daytonas", "cabinet"): "DELUXE",
        ("manxtt", "cabinet_type"): "TWIN",
        ("motoraiddx", "cabinet_type"): "TWIN",
        ("overrev", "hardware_type"): "SEGA STCC",
        ("sgt24h", "io_type"): "C",
        # LINK MAX is unavailable while LINK TYPE is NOT LINK. Its first real
        # selectable value is therefore the only meaningful option default.
        ("sgt24h", "link_max"): "2",
    }
    if (game, suffix) in overrides:
        return overrides[(game, suffix)]
    if game in {"powsled", "powsledm", "powsledr"} and suffix == "ride_id":
        return "Silver"  # Native ROM fallback; no menu Use Default command.
    if suffix in {"country", "nation"}:
        return (
            next((label for label in labels if normalized(label) == "EXPORT"), None)
            or next((label for label in labels if normalized(label) == "EUROPE"), None)
            or next((label for label in labels if normalized(label) == "USA"), native)
        )
    if "link" in suffix or "network" in suffix:
        offline = {"SINGLE", "NOT LINK", "NOTLINK", "STAND ALONE"}
        return next((label for label in labels if normalized(label) in offline), native)
    return native


def audit_power_sled_campaign(options, errors):
    games = {"powsled", "powsledm", "powsledr"}
    with zipfile.ZipFile(WORKBOOK) as archive:
        namespace = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        book = ET.fromstring(archive.read("xl/workbook.xml"))
        sheets = book.findall("m:sheets/m:sheet", namespace)
        coverage = next((sheet for sheet in sheets if sheet.get("name") == "Power Sled Campaign"), None)
        if coverage is None:
            errors.append("Missing Power Sled campaign review sheet")
            return
        relation = coverage.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        target = next(r.get("Target") for r in rels if r.get("Id") == relation)
        part = target.lstrip("/") if target.startswith("/") else "xl/" + target
        xml = ET.fromstring(archive.read(part))
        # The campaign sheet uses inline strings, independent of the option table.
        cells = {c.get("r"): "".join(c.itertext()) for c in xml.findall(".//m:c", namespace)}
        recorded = {cells.get(f"B{row}") for row in range(2, 5)}
        if recorded != games:
            errors.append(f"Power Sled workbook roster mismatch: {recorded}")
        acquired_mapping = (ROOT / "build-libretro-gpu/validation/power-sled-phase2-20261009/coverage.json").exists()
        integrity_path = ROOT / "build-libretro-gpu/validation/power-sled-integrity-20261009/coverage.json"
        integrity_acquired = integrity_path.exists()
        for row in range(2, 5):
            expected_mapping = ("Numeric And Color Fields Verified" if row<4 else
                                "Numeric Fields Verified; Relay Pending") if acquired_mapping else "Pending"
            expected_setup = "Initial Setup Implemented" if options.get("powsled") else ("Initial Image Verified; Implementation Pending" if integrity_acquired else "Pending")
            if cells.get(f"F{row}") != expected_mapping or cells.get(f"G{row}") != expected_setup:
                errors.append("Power Sled workbook mapping/setup status differs from acquired evidence")
        tables = [ET.fromstring(archive.read(name)) for name in archive.namelist()
                  if name.startswith("xl/tables/") and name.endswith(".xml")]
        if options.get("powsled"):
            table = next((t for t in tables if t.get("name") == "PowerSledCoreOptions"), None)
            if (table is None or table.get("ref") != "A326:G347"
                    or table.find("m:autoFilter", namespace) is None
                    or table.find("m:tableStyleInfo", namespace).get("name") != "TableStyleMedium8"):
                errors.append("Missing approved Power Sled Core Options review table")
            row = 327
            for game in ["powsledm", "powsledr", "powsled"]:
                for option in options.get(game, []):
                    label = str(option["label"]).title().replace("Id", "ID")
                    if (cells.get(f"A{row}") != game or cells.get(f"B{row}") != label
                            or cells.get(f"E{row}") != "Approved"
                            or cells.get(f"F{row}") != "Implemented"):
                        errors.append(f"Power Sled review differs from implementation at row {row}")
                    c = xml.find(f".//m:c[@r='C{row}']", namespace)
                    bold = c.findall("m:is/m:r", namespace) if c is not None else []
                    actual_default = ["".join(r.itertext()) for r in bold
                                      if r.find("m:rPr/m:b", namespace) is not None]
                    wanted = next(label for key, label in option["values"] if key == option["default_key"])
                    if actual_default != [wanted]: errors.append(f"Default emphasis differs at C{row}")
                    row += 1
            if row != 348: errors.append("Expected 21 approved Power Sled option rows")
            color_table = next((t for t in tables if t.get("name") == "PowerSledFourColors"), None)
            if (color_table is None or color_table.get("ref") != "A349:G352"
                    or color_table.find("m:autoFilter", namespace) is None
                    or color_table.find("m:tableStyleInfo", namespace).get("name") != "TableStyleMedium8"):
                errors.append("Missing current four-color Power Sled review table")
            for row, game in enumerate(["powsledm", "powsledr", "powsled"], 350):
                if (cells.get(f"A{row}") != game
                        or cells.get(f"C{row}") != "Silver, Red, Black, Yellow"
                        or cells.get(f"E{row}") != "Approved"
                        or cells.get(f"F{row}") != "Implemented"):
                    errors.append(f"Four-color review differs at row {row}")
                text = (ROOT / f"data/diagnostic-menus/{game}.yaml").read_text()
                for key in ["ride_color_extension", "ride_color_acquisition"]:
                    if key+":" not in text:
                        errors.append(f"Missing {game} four-color evidence: {key}")
                if "ride_color_acquisition:" in text:
                    acquisition = json.JSONDecoder().raw_decode(text.split("ride_color_acquisition:",1)[1].lstrip())[0]
                    if (acquisition.get("mapping") != {"Silver":0,"Red":1,"Black":2,"Yellow":3}
                            or acquisition.get("offsets") != [8,264,520]
                            or acquisition.get("status") != "commits_and_fresh_reloads_validated"):
                        errors.append(f"Invalid acquired {game} four-color mapping")
                    evidence = ROOT / acquisition["evidence"]
                    if evidence.exists():
                        journal = json.loads(evidence.read_text())
                        if hashlib.sha256(evidence.read_bytes()).hexdigest() != acquisition["evidence_sha256"]:
                            errors.append(f"Changed four-color acquisition journal: {game}")
                        for raw, color in enumerate(["silver","red","black","yellow"]):
                            for action in ["commit", "reload"]:
                                sample = journal["samples"][f"{action}-{color}"]
                                record = next(r for r in sample["records"] if r["set"] == game)
                                if sample["status"] != "validated" or record["copies"] != [raw]*3:
                                    errors.append(f"Missing native {game} {action}-{color} proof")
            implementation_path = ROOT / "build-libretro-gpu/validation/power-sled-options-20261009/coverage.json"
            if implementation_path.exists():
                implementation = json.loads(implementation_path.read_text())
                wanted_records = {(stage, game) for stage in
                    ["initial", "overrides", "existing-srm", "native-saves", "srm-over-native"]
                    for game in games}
                records = implementation.get("records", [])
                if (implementation.get("status") != "options_and_initial_save_precedence_verified_in_retroarch"
                        or len(records) != 15
                        or {(r["stage"], r["set"]) for r in records} != wanted_records):
                    errors.append("Power Sled option/save-precedence coverage incomplete")
                for record in records:
                    for file in [{"path": record["srm"], "sha256": record["srm_sha256"]}, *record["screenshots"]]:
                        path = Path(file["path"])
                        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != file["sha256"]:
                            errors.append(f"Changed implementation evidence: {path}")
                for game in games:
                    text = (ROOT/f"data/diagnostic-menus/{game}.yaml").read_text()
                    if "core_option_implementation:" not in text:
                        errors.append(f"Missing implementation YAML: {game}")
                        continue
                    metadata = json.JSONDecoder().raw_decode(text.split("core_option_implementation:",1)[1].lstrip())[0]
                    # This pinned historical package preceded Relay Ride ID;
                    # the independently acquired extension above owns that row.
                    if (metadata["evidence_sha256"] != hashlib.sha256(implementation_path.read_bytes()).hexdigest()
                            or metadata["core_sha256"] != implementation["core_sha256"]
                            or metadata["approved_fields"] != [o["suffix"] for o in options[game]
                                if game != "powsledr" or o["suffix"] != "ride_id"]):
                        errors.append(f"Power Sled implementation YAML differs: {game}")
        if integrity_acquired:
            evidence = json.loads(integrity_path.read_text())
            if (evidence.get("status") != "native_integrity_and_per_set_initial_images_validated"
                    or evidence.get("planned_stages") != 11 or len(evidence.get("initial_images", [])) != 3):
                errors.append("Power Sled native integrity/initial-image evidence incomplete")
            for name, address in [("PowerSledNativeIntegrity", "A281:G314"),
                                  ("PowerSledInitialImages", "A319:G322")]:
                table = next((t for t in tables if t.get("name") == name), None)
                if (table is None or table.get("ref") != address
                        or table.find("m:autoFilter", namespace) is None
                        or table.find("m:tableStyleInfo", namespace).get("name") != "TableStyleMedium8"):
                    errors.append(f"Missing native green filtered table: {name}")
            title = lambda value: " ".join(word.title() for word in re.split(r"[-_]", value))
            row = 282
            for stage, entry in evidence["stages"].items():
                if entry.get("status") != "validated" or len(entry.get("records", [])) != 3:
                    errors.append(f"Incomplete integrity trial: {stage}")
                for record in entry["records"]:
                    expected = [record["set"], title(stage), title(record["settings_choice"]),
                        title(record["bookkeeping_choice"]), str(record["time_values"][0]),
                        "Verified In RetroArch", stage]
                    if [cells.get(f"{column}{row}") for column in "ABCDEFG"] != expected:
                        errors.append(f"Native integrity workbook mismatch at row {row}")
                    for field in ["backup", "srm", "screenshot"]:
                        path = Path(record[field])
                        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != record[field+"_sha256"]:
                            errors.append(f"Changed native integrity evidence: {path}")
                    row += 1
            if row != 315:
                errors.append("Expected 33 native integrity program records")
            for row, record in enumerate(evidence["initial_images"], 320):
                expected = [record["set"], "28", "52", "Native Defaults", "Verified In RetroArch",
                            "Implemented" if options.get("powsled") else "Implementation Pending", record["set"]+".bin"]
                if [cells.get(f"{column}{row}") for column in "ABCDEFG"] != expected:
                    errors.append(f"Initial image workbook mismatch at row {row}")
                path = Path(record["initial_payload"])
                if not path.exists() or len(path.read_bytes()) != 16384+128 or hashlib.sha256(path.read_bytes()).hexdigest() != record["initial_payload_sha256"]:
                    errors.append(f"Changed initial image evidence: {path}")
            for game in games:
                text = (ROOT/f"data/diagnostic-menus/{game}.yaml").read_text()
                if "target_core_integrity:" not in text:
                    errors.append(f"Missing native integrity YAML: {game}")
                    continue
                metadata = json.JSONDecoder().raw_decode(text.split("target_core_integrity:", 1)[1].lstrip())[0]
                if (metadata.get("status") != evidence["status"]
                        or metadata.get("evidence_sha256") != hashlib.sha256(integrity_path.read_bytes()).hexdigest()):
                    errors.append(f"Native integrity YAML evidence mismatch: {game}")
        inventory_table = next((t for t in tables if t.get("name") == "PowerSledMainInventory"), None)
        if (inventory_table is None or inventory_table.get("ref") != "A17:G32"
                or inventory_table.find("m:autoFilter", namespace) is None
                or inventory_table.find("m:tableStyleInfo", namespace).get("name") != "TableStyleMedium8"):
            errors.append("Missing native filtered green Main operator inventory table")
        inventory_root = ROOT / "build-libretro-gpu/validation/power-sled-main-operator-20261008"
        inventory_path = inventory_root / "observations.json"
        for row in range(18, 33):
            if (cells.get(f"A{row}") != "powsledm" or cells.get(f"F{row}") != ("Pending Review" if row < 25 else "Excluded Calibration")
                    or cells.get(f"G{row}") != ("Pending" if row < 25 else "Not Applicable")):
                errors.append("Main inventory must retain per-set pending review/automation")
        if inventory_path.exists():
            inventory = json.loads(inventory_path.read_text())
            for row, values in enumerate(inventory["workbook_rows"], 17):
                if row == 18:
                    values = values[:4] + ["Export Observed; Encoding Pending"] + values[5:]
                elif 19 <= row <= 23:
                    values = values[:4] + [f"5–99 Seconds; Step 1; Default {[49,35,35,30,30][row-19]}"] + values[5:]
                elif row == 24:
                    values = values[:4] + ["10.0–45.0 Degrees; Step 0.5; Default 38.0"] + values[5:]
                elif row >= 25:
                    values = values[:4] + ["Listed Only — Calibration", "Excluded Calibration", "Not Applicable"]
                if [cells.get(f"{column}{row}") for column in "ABCDEFG"] != [str(v) for v in values]:
                    errors.append(f"Main operator inventory workbook mismatch at row {row}")
            manifest = json.loads((inventory_root / "manifest.json").read_text())
            summaries = list(inventory_root.rglob("summary.json"))
            if (sum(len(json.loads(p.read_text())) for p in summaries) != 6
                    or any(record["status"] != "ok" for p in summaries
                           for record in json.loads(p.read_text()))):
                errors.append("Main inventory must retain six clean isolated acquisition runs")
            screenshots = list((inventory_root / "inventory/screenshots").glob("*.png"))
            screenshots += list((inventory_root / "editor/screenshots").glob("*.png"))
            screenshots += list((inventory_root / "volume-probe/screenshots").glob("*.png"))
            if len(screenshots) != 7:
                errors.append("Main inventory must retain seven documentary screenshots")
            for name, digest in manifest["files"].items():
                path = inventory_root / name
                if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                    errors.append(f"Main operator inventory evidence missing/changed: {name}")
        operator_table = next((t for t in tables if t.get("name") == "PowerSledOperatorSettings"), None)
        if (operator_table is None or operator_table.get("ref") != "A37:G58"
                or operator_table.find("m:autoFilter", namespace) is None
                or operator_table.find("m:tableStyleInfo", namespace).get("name") != "TableStyleMedium8"):
            errors.append("Missing native filtered operator settings table")
        row = 38
        for game in ["powsledm", "powsledr", "powsled"]:
            expected = [[game, "Country", "Country", "Export Observed; Encoding Pending", "Export Retained", "Pending Review", "Pending"]]
            expected += [[game, "Time Extension Setting", f"Checkpoint {k}",
                          f"5–99 Seconds; Step 1; Default {default}",
                          "Native Commit And Fresh Reload Verified", "Pending Review", "Pending"]
                         for k, default in enumerate([49,35,35,30,30])]
            expected += [[game, "Maximum Rotation Setting", "Motion Angle", "10.0–45.0 Degrees; Step 0.5; Default 38.0",
                          "Native Commit And Fresh Reload Verified", "Pending Review", "Pending"]]
            for values in expected:
                if [cells.get(f"{column}{row}") for column in "ABCDEFG"] != values:
                    errors.append(f"Operator settings workbook mismatch at row {row}")
                if values[2].startswith("Checkpoint") or values[2] == "Motion Angle":
                    c=xml.find(f".//m:c[@r='D{row}']",namespace)
                    bold = c.findall("m:is/m:r/m:rPr/m:b",namespace)
                    if not bold: errors.append(f"Native default lacks rich-text bold at D{row}")
                row += 1
        campaign_root = ROOT / "build-libretro-gpu/validation/power-sled-settings-20261008"
        observation_path = campaign_root / "operator-settings-observations.json"
        if observation_path.exists():
            observed = json.loads(observation_path.read_text())
            if observed["status"] != "numeric_fields_verified" or len(observed["sets"]) != 3:
                errors.append("Reduced numeric campaign status mismatch")
            records = list(observed["sets"].values())
            if "core_import" in observed: records.append(observed["core_import"])
            records += [record for trial in observed["integrity_probe"].values() for record in trial.values()]
            for record in records:
                for name,digest in record["files"].items():
                    path=campaign_root/name
                    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
                        errors.append(f"Reduced campaign evidence missing/changed: {name}")
            for name in ["decoded-time-values.json","committed-time-values.json","decoded-motion-values.json"]:
                decoded=json.loads((campaign_root/name).read_text())
                groups=decoded.get("fields",decoded)
                for group in groups.values():
                    records=[group] if "screenshots" in group else group.values()
                    for record in records:
                        for field in ["screenshots","samples"]:
                            for name,digest in record.get(field,{}).items():
                                path=campaign_root/name
                                if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
                                    errors.append(f"Numeric range evidence missing/changed: {name}")
        phase1_path = ROOT / "build-libretro-gpu/validation/power-sled-phase1-20261008/service-menu-observations.json"
        for name, ref in [("PowerSledPhase1Settings", "A61:G85"), ("PowerSledPhase1Root", "A89:G99"), ("PowerSledPhase1Commands", "A103:G110")]:
            table=next((t for t in tables if t.get("name")==name),None)
            if (table is None or table.get("ref")!=ref or table.find("m:autoFilter",namespace) is None
                    or table.find("m:tableStyleInfo",namespace).get("name")!="TableStyleMedium8"):
                errors.append(f"Missing filtered Phase 1 table: {name}")
        if phase1_path.exists():
            documentation=json.loads(phase1_path.read_text())
            row=62
            for game in ["powsledm","powsledr","powsled"]:
                settings=documentation["sets"][game]["settings"]
                if len(settings)!=8:errors.append(f"{game}: incomplete Phase 1 inventory")
                for item in settings:
                    expected=[game,item["menu_path"][1],item["label"],item["display_values"],
                              "No Use Default Command" if item["native_default"] is None else "Native Use Default Action",
                              item["behavior"],"Documented In Tested Topology"]
                    if [cells.get(f"{col}{row}") for col in "ABCDEFG"]!=expected:
                        errors.append(f"Phase 1 workbook inventory mismatch at row {row}")
                    if item["native_default"] is not None:
                        c=xml.find(f".//m:c[@r='D{row}']",namespace)
                        if not c.findall("m:is/m:r/m:rPr/m:b",namespace):errors.append(f"Phase 1 native default lacks bold at D{row}")
                    row+=1
            for row in range(2,5):
                if cells.get(f"E{row}") not in {"Phase 2 Partial; Motion Default And Step Persisted", "Phase 2 Field Mapping And Fresh Reload Verified"}:
                    errors.append("Power Sled workbook phase gate mismatch")
        motion_table = next((t for t in tables if t.get("name") == "PowerSledCoreMotion"), None)
        if (motion_table is None or motion_table.get("ref") != "A114:G123"
                or motion_table.find("m:autoFilter", namespace) is None
                or motion_table.find("m:tableStyleInfo", namespace).get("name") != "TableStyleMedium8"):
            errors.append("Missing filtered green target-core Motion Angle table")
        for offset, game in enumerate(["powsledm", "powsledr", "powsled"]):
            for index, (stage, value, evidence) in enumerate([
                    ("Native Default", "38", "Motion Native Default"),
                    ("Increment", "38.5", "Motion Plus Step"),
                    ("Fresh Reload", "38.5", "Motion Reload")]):
                row = 115 + offset * 3 + index
                expected = [game, "Motion Angle", stage, value, "Degrees", "Verified In RetroArch", evidence]
                if [cells.get(f"{col}{row}") for col in "ABCDEFG"] != expected:
                    errors.append(f"Target-core Motion Angle workbook mismatch at row {row}")
            yaml = (ROOT / f"data/diagnostic-menus/{game}.yaml").read_text()
            if ("target_core_motion_acquisition:" not in yaml
                    or "native_default_increment_and_fresh_reload_verified" not in yaml):
                errors.append(f"Missing target-core Motion Angle YAML evidence for {game}")
        linked_recipe = ROOT / "scripts/libretro_nvram_samples.power-sled-linked.toml"
        with linked_recipe.open("rb") as stream:
            recipe = tomllib.load(stream)
        suffixes = {s.get("suffix") for s in recipe.get("samples", [])}
        expected = {"motion-native-default", "motion-plus-step", "motion-reload",
            "motion-minimum", "motion-byte-before", "motion-byte-after", "motion-maximum",
            "motion-limits-reload", "country-initial", "country-alternate", "country-cycle-close",
            "country-reload", "ride-main-initialize", "ride-initialize",
            "ride-silver-cycle", "ride-silver-reload", "ride-red-initialize", "ride-red-cycle",
            "ride-red-reload", "ride-red-relay-repeat", "ride-red-relay-reload", "ride-black-slave-initialize", "ride-black-initialize", "ride-black-reload"}
        expected.update(f"checkpoint-{i}-{stage}" for i in range(5)
                        for stage in ["default", "step", "minimum", "maximum", "reload"])
        if suffixes != expected:
            errors.append("Complete linked Power Sled recipe coverage mismatch")
        complete_evidence = ROOT / "build-libretro-gpu/validation/power-sled-phase2-20261009/coverage.json"
        if complete_evidence.exists():
            acquired = json.loads(complete_evidence.read_text())
            if acquired.get("status") != "acquisition_and_native_reload_validated" or len(acquired.get("records", [])) != 147:
                errors.append("Complete target-core Power Sled evidence incomplete")
            complete_table = next((t for t in tables if t.get("name") == "PowerSledCoreAcquisition"), None)
            if (complete_table is None or complete_table.get("ref") != "A129:G276"
                    or complete_table.find("m:autoFilter", namespace) is None
                    or complete_table.find("m:tableStyleInfo", namespace).get("name") != "TableStyleMedium8"):
                errors.append("Missing native filtered green complete acquisition table")
            for row in range(2,5):
                if cells.get(f"E{row}") != "Phase 2 Field Mapping And Fresh Reload Verified":
                    errors.append("Workbook complete acquisition gate mismatch")
            for row, record in enumerate(acquired.get("records", []), 130):
                key = record["setting"]
                name = {"motion":"Motion Angle", "country":"Country", "ride_id":"Ride ID (Color)"}.get(key, key.replace("_", " ").title())
                raw = record["raw"]
                value = (format(raw/10,"g") if key=="motion" else
                    (f"Relay (Stored {raw})" if record["set"]=="powsledr" else ("Uninitialized (255)" if raw==255 else ["Silver Ride","Red Ride","Black Ride"][raw])) if key=="ride_id" else str(raw))
                unit = {"motion":"Degrees", "ride_id":"Stored Byte; Relay Label" if record["set"]=="powsledr" else "Ride", "country":"Stored Byte; Export Label"}.get(key,"Seconds")
                stage = re.sub(r"^(checkpoint-[0-4]-|motion-|country-|ride-)","",record["stage"]).replace("-"," ").title()
                expected_row = [record["set"],name,stage,value,unit,"Captured For Initialization" if record.get("setup_only") else "Verified In RetroArch",record["stage"]]
                if [cells.get(f"{col}{row}") for col in "ABCDEFG"] != expected_row:
                    errors.append(f"Complete acquisition workbook mismatch at row {row}")
                for path_key,hash_key in [("backup","backup_sha256"),("screenshot","screenshot_sha256")]:
                    path = Path(record[path_key])
                    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=record[hash_key]:
                        errors.append(f"Complete acquisition evidence missing/changed: {path}")
            for game in ["powsledm","powsledr","powsled"]:
                text = (ROOT/f"data/diagnostic-menus/{game}.yaml").read_text()
                metadata = json.JSONDecoder().raw_decode(text.split("target_core_campaign:",1)[1].lstrip())[0]
                if (metadata.get("status") != "acquisition_and_native_reload_validated"
                        or metadata.get("program_records") != len(acquired["records"])
                        or metadata.get("evidence_sha256") != hashlib.sha256(complete_evidence.read_bytes()).hexdigest()):
                    errors.append(f"Complete acquisition YAML gate mismatch for {game}")
        motion_evidence = ROOT / "build-libretro-gpu/validation/power-sled-phase2-20261008/motion-summary.json"
        if motion_evidence.exists():
            report = json.loads(motion_evidence.read_text())
            if report.get("status") != "passed" or len(report.get("records", [])) != 9:
                errors.append("Target-core Motion Angle evidence incomplete")
            for record in report.get("records", []):
                for path_key, hash_key in [("backup", "backup_sha256"), ("screenshot", "screenshot_sha256")]:
                    path = Path(record[path_key])
                    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != record[hash_key]:
                        errors.append(f"Target-core Motion Angle evidence missing/changed: {path}")

        ride_table = next((t for t in tables if t.get("name") == "PowerSledRideId"), None)
        if ride_table is None or ride_table.get("ref") != "A9:G12" or ride_table.find("m:autoFilter", namespace) is None:
            errors.append("Missing native filtered Ride ID review table")
        elif ride_table.find("m:tableStyleInfo", namespace).get("name") != "TableStyleMedium8":
            errors.append("Ride ID table must retain the green reference style")
        observations = ROOT / "build-libretro-gpu/validation/mame-power-sled-20261008/ride-id-observations.json"
        if observations.exists():
            observed = json.loads(observations.read_text())["sets"]
            for row in range(10, 13):
                game = cells.get(f"A{row}")
                if game not in observed:
                    errors.append("Ride ID table roster mismatch")
                    continue
                value = observed[game]["commit"]["fresh_reload_value"]
                identifier = "0x100" if value["id"] == 256 else str(value["id"])
                if cells.get(f"D{row}") != f"{identifier} — {value['label']}":
                    errors.append(f"{game}: workbook Ride ID reload differs from evidence")
                if cells.get(f"F{row}") != "Pending Review" or cells.get(f"G{row}") != "Pending":
                    errors.append(f"{game}: Ride ID review/automation must remain pending")
    for game in sorted(games):
        recipe = ROOT / f"scripts/libretro_nvram_samples.{game}.toml"
        with recipe.open("rb") as stream:
            data = tomllib.load(stream)
        if data["campaign"]["game"] != game:
            errors.append(f"{game}: recipe identity mismatch")
        for key in ("sm2_initial_nvram_setup", "sm2_nvram_settings"):
            if data.get("core_options", {}).get(key) != "disabled":
                errors.append(f"{game}: acquisition must disable {key}")
        if options.get(game):
            wanted = ["ride_id"] + [f"checkpoint_{i}" for i in range(5)] + ["motion_angle"]
            if [o["suffix"] for o in options[game]] != wanted:
                errors.append(f"{game}: Power Sled exposes fields outside the approved review")
            for option in options[game]:
                if option["suffix"].startswith("checkpoint_"):
                    expected = [(str(v),str(v)) for v in range(5,100)]
                elif option["suffix"] == "motion_angle":
                    expected = [(f"{v/10:.1f}",f"{v/10:.1f}") for v in range(100,451,5)]
                else: expected = [("silver","Silver"),("red","Red"),("black","Black"),("yellow","Yellow")]
                if option["values"] != expected: errors.append(f"{game}: approved values differ")
    evidence = ROOT / "build-libretro-gpu/validation/power-sled-service-menu-20261008"
    manifest_path = evidence / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        if set(manifest["sets"]) != games:
            errors.append("Power Sled manifest roster mismatch")
        for game, record in manifest["sets"].items():
            for name, digest in record["files"].items():
                path = evidence / game / name
                if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                    errors.append(f"{game}: missing/changed evidence {name}")
            for sample in record["samples"]:
                if sample["loaded_set"] != game or not sample["screenshots"]:
                    errors.append(f"{game}: sample identity/screenshots incomplete")
                if sample["native_integrity_validated"]:
                    errors.append(f"{game}: navigation evidence cannot validate native integrity")
    else:
        print("Power Sled raw evidence is unavailable in this checkout; acquisition remains pending")

    reference = ROOT / "build-libretro-gpu/validation/mame-power-sled-20261008"
    acquisition_manifest = reference / "ride-id-acquisition-manifest.json"
    if acquisition_manifest.exists():
        acquisition = json.loads(acquisition_manifest.read_text())
        for name, digest in acquisition["files"].items():
            path = reference / name
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                errors.append(f"Power Sled Ride ID evidence missing/changed: {name}")
        for name, run in acquisition["runs"].items():
            for unit in run["units"]:
                if unit["returncode"] != run["expected_returncode"] or (run["expected_returncode"] == 0 and not unit["probe_ok"]):
                    errors.append(f"Power Sled reference run outcome mismatch: {name}/{unit['set']}")


def main() -> int:
    catalog = parse_catalog()
    parent_selections = parse_parent_selections()
    options = parse_core_options()
    games = ET.parse(GAMES_XML).getroot().findall("game")
    parents = {game.get("name"): game.get("parent") for game in games}
    errors: list[str] = []
    routed = 0

    if set(catalog) != set(parents):
        errors.append(
            "catalog/games.xml set mismatch: "
            f"missing={sorted(set(parents) - set(catalog))}, "
            f"extra={sorted(set(catalog) - set(parents))}"
        )

    for game, rows in catalog.items():
        parent = parents[game]
        option_game = game if options.get(game) else parent
        actual = options.get(option_game, [])
        if actual:
            routed += 1

        row_by_label = {normalized(row["label"]): row for row in rows}
        if game in {"powsled", "powsledm", "powsledr"}:
            row_by_label = {("RIDE ID" if label == "RIDE ID COLOR" else label): row
                            for label, row in row_by_label.items()}
        parent_selected = parent_selections.get(parent or game, [])
        expected_labels = {
            normalized(label)
            for label in parent_selected
            if normalized(label) in row_by_label
        }
        expected_labels |= {
            normalized(label) for label in CLONE_ADDITIONS.get(game, set())
        }
        expected_labels -= {
            normalized(label) for label in CLONE_EXCLUSIONS.get(game, set())
        }
        if game in {"powsled", "powsledm", "powsledr"}:
            expected_labels = {f"CHECKPOINT {i}" for i in range(5)} | {"MOTION ANGLE"}
            expected_labels.add("RIDE ID")

        actual_labels = [normalized(str(option["label"])) for option in actual]
        actual_set = set(actual_labels)
        missing = expected_labels - actual_set
        extra = actual_set - expected_labels
        if missing:
            errors.append(f"{game}: missing selected options {sorted(missing)}")
        if extra:
            errors.append(f"{game}: exposes unselected/absent options {sorted(extra)}")

        positions = [
            list(row_by_label).index(label)
            for label in actual_labels
            if label in row_by_label
        ]
        if len(positions) != len(actual_labels):
            absent = [label for label in actual_labels if label not in row_by_label]
            errors.append(f"{game}: routed catalog {option_game!r} exposes absent rows {absent}")
        elif positions != sorted(positions):
            errors.append(f"{game}: Core Option order differs from the Service Menu")

        for option in actual:
            label = normalized(str(option["label"]))
            row = row_by_label.get(label)
            if not row:
                continue
            value_pairs = list(option["values"])
            documented = documented_values(row["values"])
            if documented and game not in {"powsled", "powsledm", "powsledr"}:
                expected_values = {normalized(value) for value in documented}
                actual_values = {normalized(label) for _, label in value_pairs}
                if expected_values != actual_values:
                    errors.append(
                        f"{game}:{option['suffix']}: value mismatch "
                        f"missing={sorted(expected_values - actual_values)}, "
                        f"extra={sorted(actual_values - expected_values)}"
                    )

            default_label = next(
                (label for key, label in value_pairs if key == option["default_key"]), None
            )
            wanted_default = expected_default(str(option_game), option, row["default"])
            if default_label is None or normalized(default_label) != normalized(wanted_default):
                errors.append(
                    f"{game}:{option['suffix']}: default {default_label!r}, "
                    f"expected {wanted_default!r}"
                )
            description = str(option["description"])
            if str(option["label"]) not in description or "operator NVRAM" not in description:
                errors.append(f"{game}:{option['suffix']}: incomplete description")

    audit_power_sled_campaign(options, errors)

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(
        "NVRAM Core Option audit passed: "
        f"{len(catalog)} sets, {routed} with NVRAM Settings, "
        f"{len(catalog) - routed} intentionally without them, "
        f"{sum(len(group) for group in options.values())} options"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
