#!/usr/bin/env python3
"""ROM-free checks for the linked launcher's game-list and ANS contract."""
import importlib.util
from pathlib import Path
import sys
import json
import tempfile
import unittest
import plistlib
from unittest.mock import patch, Mock

spec = importlib.util.spec_from_file_location("linked_launcher", Path(__file__).with_name("launch-linked-cabinets.py"))
launcher = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = launcher
spec.loader.exec_module(launcher)


class GameSelectionChecks(unittest.TestCase):
    def test_mac_controllers_use_one_named_order_for_all_instances(self):
        devices = [{"Product": name, "PrimaryUsagePage": 1, "PrimaryUsage": 5, "Transport": "Bluetooth"}
                   for name in ("Xbox White", "Xbox Black", "DualSense")]
        devices.append({"Product": "GamePad-1", "PrimaryUsagePage": 1, "PrimaryUsage": 5})
        for order in (devices, list(reversed(devices))):
            with patch.object(launcher.runner.subprocess, "check_output",
                              return_value=plistlib.dumps(order)):
                self.assertEqual(launcher.runner.mac_controller_names([0, 1, 2]),
                                 ["DualSense", "Xbox Black", "Xbox White"])
        with patch.object(launcher.runner.subprocess, "check_output",
                          return_value=plistlib.dumps([devices[0], devices[0]])):
            with self.assertRaisesRegex(RuntimeError, "ambiguous"):
                launcher.runner.mac_controller_names([0])

    def test_controller_reservation_does_not_alias_disabled_ports(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "overrides.cfg"
            config.touch()
            launcher.runner.write_controller_config(config, 2, "Xbox White")
            pairs = launcher.re.findall(r'^([^\s=]+) = "([^"\n]*)"$', config.read_text(), launcher.re.M)
            self.assertEqual(len(pairs), len({key for key, _ in pairs}))
            entries = dict(pairs)
            self.assertEqual(entries['input_player1_reserved_device'], 'Xbox White')
            self.assertEqual(entries['input_player1_device_reservation_type'], '2')
            self.assertEqual(entries['input_joypad_driver'], 'hid')
            self.assertEqual(len({entries[f'input_player{p}_joypad_index'] for p in range(1, 17)}), 16)
            self.assertTrue(all(entries[f'input_libretro_device_p{p}'] == '0' for p in range(2, 9)))

    def test_one_name_repeats_without_substituting_roms(self):
        entries, _, _, _ = launcher.game_plan("daytona", 4, False)
        self.assertEqual(entries, [("daytona", str(i), i) for i in range(1, 5)])
        self.assertEqual(launcher.game_plan("von", 3, False)[0], [("von", str(i), i) for i in range(1, 4)])
        self.assertEqual(launcher.game_plan("powsled", None, True)[0], [("powsled", "1", 1)])

    def test_list_selects_the_corresponding_rom(self):
        entries, order, _, _ = launcher.game_plan("vonj,vonu,vonr", None, False)
        self.assertEqual(entries, [("vonj", "1", 1), ("vonu", "2", 2), ("vonr", "3", 3)])
        self.assertEqual(order, [0, 1, 2])
        self.assertEqual(launcher.game_plan("daytona,stcc,vf2", None, False)[0],
                         [("daytona", "1", 1), ("stcc", "2", 2), ("vf2", "3", 3)])

    def test_colon_sets_ans_without_changing_the_rom_name(self):
        entries, order, power, relay = launcher.game_plan(
            "powsledm:1,powsled:2,powsledr:relay", None, True)
        self.assertEqual(entries, [("powsledm", "1", 1), ("powsled", "2", 2), ("powsledr", "relay", 3)])
        self.assertEqual(order, [0, 1, 2])  # Relay follows the playable cabinet.
        self.assertTrue(power)
        self.assertFalse(relay)  # Power Sled ignores the optional flag.
        self.assertTrue(launcher.game_plan("stcc:1,stcc:2,stcc:relay", None, False)[3])
        self.assertEqual(launcher.game_plan("daytona:0,daytona:0", None, False)[0],
                         [("daytona", "0", 1), ("daytona", "0", 2)])

    def test_power_sled_pair_keeps_colors_and_omits_relay(self):
        entries, order, power, relay = launcher.game_plan("powsledm:1,powsled:2", None, False)
        self.assertEqual(entries, [("powsledm", "1", 1), ("powsled", "2", 2)])
        self.assertEqual(order, [0, 1])
        self.assertFalse(power)  # A pair uses the generic side-by-side layout.
        self.assertFalse(relay)

    def test_single_instance_accepts_disabled_ans_and_explicit_color(self):
        for game in ("powsledm", "daytona", "vf2"):
            for preset in (None, "0", "1"):
                for cabinets in (None, 1):
                    selection = game if preset is None else f"{game}:{preset}"
                    entries, order, power, relay = launcher.game_plan(selection, cabinets, False)
                    self.assertEqual(entries, [(game, preset or "1", 1)])
                    self.assertEqual(order, [0])
                    self.assertFalse(power)
                    self.assertFalse(relay)

    def test_single_instance_defaults_preserve_manual_nvram(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "config").mkdir()
            for game in ("powsledm", "daytona", "vf2"):
                launcher.runner.write_options(root, game, 1, 0, False, True)
                text = (root / "config/core-options.cfg").read_text()
                self.assertIn(f'sm2_linked_cabinets_{game} = "disabled"', text)
                self.assertIn(f'sm2_automatic_network_{game} = "0"', text)
                self.assertNotIn(f"sm2_nvram_{game}_", text)

    def test_optional_fields_and_reservations(self):
        for selection, expected in (
            ("daytona", ("daytona", "1", 1)),
            ("daytona:1", ("daytona", "1", 1)),
            ("daytona:1:", ("daytona", "1", None)),
            ("daytona::2", ("daytona", "1", 2)),
            ("daytona::", ("daytona", "1", None)),
            ("daytona:", ("daytona", "1", 1)),
        ):
            self.assertEqual(launcher.game_plan(selection, None, False)[0], [expected])
        self.assertEqual(launcher.game_plan("daytona,stcc:1:1,vf2::", None, False)[0],
                         [("daytona", "2", 2), ("stcc", "1", 1), ("vf2", "3", None)])
        self.assertEqual(launcher.game_plan("daytona::", 2, False)[0],
                         [("daytona", "1", None), ("daytona", "2", None)])
        self.assertEqual(launcher.game_plan("stcc", 3, True)[0][-1], ("stcc", "relay", 3))

    def test_four_riders_then_relay_preserve_each_assignment(self):
        entries, order, power, relay = launcher.game_plan(
            "powsledr:relay:,powsled:2,powsledm:1,powsled:3,powsled:4", None, False)
        self.assertTrue(power)
        self.assertFalse(relay)
        self.assertEqual(order, [2, 1, 3, 4, 0])
        self.assertEqual([entries[i][1] for i in order], ["1", "2", "3", "4", "relay"])
        positions = [launcher.runner.window_position(i, "side-by-side", 4) for i in range(5)]
        self.assertEqual(len({y for _, y in positions[:4]}), 1)
        self.assertEqual(positions[4][0], positions[0][0])
        self.assertGreater(positions[4][1], positions[0][1])

    def test_actual_window_size_must_match_and_stay_stable(self):
        process = Mock(pid=123)
        process.poll.return_value = None
        with patch.object(launcher.runner.subprocess, "check_output", return_value="24, 57, 343, 281") as call:
            frame = launcher.runner.fit_process_window(process, 24, 57, 343, 281, apply=False)
            self.assertEqual(frame["frame_width"], 343)
            self.assertNotIn("set size", call.call_args[0][0][-1])
        with patch.object(launcher.runner.subprocess, "check_output", return_value="24, 57, 512, 412"):
            with self.assertRaisesRegex(RuntimeError, "differs"):
                launcher.runner.fit_process_window(process, 24, 57, 343, 281)

    def test_missing_window_values_do_not_fail_passive_measurement(self):
        process = Mock(pid=123)
        process.poll.return_value = None
        with patch.object(launcher.runner.subprocess, "check_output", return_value="missing value"), patch.object(launcher.runner.time, "sleep"):
            self.assertIsNone(launcher.runner.fit_process_window(process, 24, 57, 343, 281, apply=False))
            with self.assertRaisesRegex(RuntimeError, "could not read"):
                launcher.runner.fit_process_window(process, 24, 57, 343, 281)
        process.poll.return_value = 0
        self.assertIsNone(launcher.runner.fit_process_window(process, 24, 57, 343, 281, apply=False))

    def test_window_quit_recovers_only_unsaved_observed_options(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root / "config").mkdir()
            path = root / "config/core-options.cfg"; log = root / "instance.log"
            key = "sm2_power_sled_relay_audio"
            original = f'{key} = "enabled"\nsm2_renderer = "auto"\n'
            path.write_text(original)
            log.write_text(f'[INFO] Saved core options file to "{path}".\n'
                           f'[DEBUG] [Environ] GET_VARIABLE: {key} = "disabled"\n'
                           '[DEBUG] [Environ] GET_VARIABLE: sm2_unknown = "enabled"\n')
            self.assertEqual(launcher.runner.recover_unsaved_core_options(root, log), {key: "disabled"})
            self.assertIn(f'{key} = "disabled"', path.read_text())
            self.assertIn('sm2_renderer = "auto"', path.read_text())
            self.assertEqual(path.with_name("core-options-before-exit-recovery.cfg").read_text(), original)
            path.write_text(original)
            log.write_text(log.read_text() + f'[INFO] Saved core options file to "{path}".\n')
            self.assertEqual(launcher.runner.recover_unsaved_core_options(root, log), {})
            self.assertEqual(path.read_text(), original)

    def test_relay_short_alias_is_normalized(self):
        self.assertEqual(launcher.game_plan("stcc:1,stcc:r:", None, False),
                         launcher.game_plan("stcc:1,stcc:relay:", None, False))
        self.assertEqual(launcher.game_plan("powsledr:r:1", None, False)[0],
                         [("powsledr", "relay", 1)])

    def test_game_selection_is_required(self):
        result = launcher.subprocess.run(
            [sys.executable, str(Path(launcher.__file__)), "--dry-run"],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("required: --game", result.stderr)

    def test_fitted_windows_stay_inside_desktop(self):
        for count, columns in ((1, 1), (3, 2), (5, 4), (9, 8)):
            for width, height in ((1470, 861), (1280, 720), (1920, 1080), (800, 600)):
                w, h = launcher.runner.fitted_window_size(count, columns, width, height)
                rows = (count + columns - 1) // columns
                self.assertLessEqual(48 + columns * (w + 16) + (columns - 1) * 16, width)
                self.assertLessEqual(48 + rows * (h + 28) + (rows - 1) * 16, height)
                self.assertAlmostEqual(w / h, 496 / 384, delta=0.03)
        self.assertEqual(launcher.runner.usable_desktop("1920x1080"), (0, 0, 1920, 1080))
        with self.assertRaises(RuntimeError):
            launcher.runner.usable_desktop("0x100")

    def test_no_pad_does_not_resolve_or_reserve_hardware(self):
        with patch.object(launcher.runner.subprocess, "check_output") as query:
            self.assertEqual(launcher.runner.mac_controller_names([None, None]), [None, None])
            query.assert_not_called()
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "overrides.cfg"
            config.touch()
            launcher.runner.write_controller_config(config, None, None)
            text = config.read_text()
            self.assertIn('input_libretro_device_p1 = "0"', text)
            self.assertIn('input_autodetect_enable = "false"', text)
            self.assertNotIn('joypad_index = "-1"', text)
            self.assertNotIn('device_reservation_type = "2"', text)

    def test_invalid_syntax_is_rejected(self):
        for selection in ("daytona:master,daytona:2", "daytona:100,daytona:2",
                          "daytona,,daytona", "../game,daytona",
                          "daytona:1:0", "daytona:1:17", "daytona:1:2:3", "daytona:1:1,daytona:2:1"):
            with self.subTest(selection=selection), self.assertRaises(ValueError):
                launcher.game_plan(selection, None, False)
        with self.assertRaises(ValueError):
            launcher.game_plan("daytona,daytona", 3, False)

    def test_old_session_follows_the_rom_when_roles_change(self):
        with tempfile.TemporaryDirectory() as directory:
            baseline = Path(directory)
            (baseline / "manifest.json").write_text(json.dumps({
                "roles": ["host", "client1", "client2"],
                "instance_sets": ["powsledm", "powsledr", "powsled"],
            }))
            self.assertEqual(launcher.runner.baseline_directory(baseline, "client1", "powsled", 1),
                             baseline / "client2")
            self.assertEqual(launcher.runner.baseline_directory(baseline, "_relay", "powsledr", 2),
                             baseline / "client1")
            self.assertEqual(launcher.runner.baseline_directory(baseline, "host", "powsledm", 0),
                             baseline / "host")

    def test_same_game_relay_resume_retains_participant_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            baseline = Path(directory)
            (baseline / "manifest.json").write_text(json.dumps({
                "roles": ["host", "client1", "client2"],
                "instance_sets": ["stcc"] * 3,
            }))
            self.assertEqual(launcher.runner.baseline_directory(baseline, "_relay", "stcc", 2),
                             baseline / "client2")

    def test_missing_master_entry_is_owned_and_donors_stay_in_place(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            roms, assets, staging = root / "roms", root / "assets", root / "run/content"
            roms.mkdir(); assets.mkdir()
            (assets / "games.xml").write_text('<games><game name="powsledm" rom_fallback="powsledr" /></games>')
            donor = roms / "powsledr.zip"
            donor.write_bytes(b"donor")
            content = launcher.runner.resolve_content(roms / "powsledm.zip", assets, staging)
            self.assertEqual(content, staging / "powsledm.zip")
            self.assertEqual(content.stat().st_size, 22)
            self.assertTrue((staging / donor.name).is_symlink())
            self.assertEqual((staging / donor.name).resolve(), donor.resolve())
            self.assertFalse((roms / "powsledm.zip").exists())
            with self.assertRaises(FileNotFoundError):
                launcher.runner.resolve_content(roms / "daytona.zip", assets, staging)


if __name__ == "__main__":
    unittest.main()
