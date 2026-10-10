#!/usr/bin/env python3
"""ROM-free checks for the linked launcher's game-list and ANS contract."""
import importlib.util
from pathlib import Path
import sys
import json
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("linked_launcher", Path(__file__).with_name("launch-linked-cabinets.py"))
launcher = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = launcher
spec.loader.exec_module(launcher)


class GameSelectionChecks(unittest.TestCase):
    def test_one_name_repeats_without_substituting_roms(self):
        entries, _, _, _ = launcher.game_plan("daytona", 4, False)
        self.assertEqual(entries, [("daytona", None)] * 4)
        self.assertEqual(launcher.game_plan("von", 3, False)[0], [("von", None)] * 3)
        self.assertEqual(launcher.game_plan("powsled", None, True)[0], [("powsled", None)] * 3)

    def test_list_selects_the_corresponding_rom(self):
        entries, order, _, _ = launcher.game_plan("vonj,vonu,vonr", None, False)
        self.assertEqual(entries, [("vonj", None), ("vonu", None), ("vonr", None)])
        self.assertEqual(order, [0, 1, 2])
        self.assertEqual(launcher.game_plan("daytona,stcc,vf2", None, False)[0],
                         [("daytona", None), ("stcc", None), ("vf2", None)])

    def test_colon_sets_ans_without_changing_the_rom_name(self):
        entries, order, power, relay = launcher.game_plan(
            "powsledm:1,powsled:2,powsledr:relay", None, True)
        self.assertEqual(entries, [("powsledm", "1"), ("powsled", "2"), ("powsledr", "relay")])
        self.assertEqual(order, [0, 1, 2])  # Relay follows the playable cabinet.
        self.assertTrue(power)
        self.assertFalse(relay)  # Power Sled ignores the optional flag.
        self.assertTrue(launcher.game_plan("stcc:1,stcc:2,stcc:relay", None, False)[3])
        self.assertEqual(launcher.game_plan("daytona:0,daytona:0", None, False)[0],
                         [("daytona", "0")] * 2)

    def test_invalid_syntax_is_rejected(self):
        for selection in ("daytona:master,daytona:2", "daytona:100,daytona:2",
                          "daytona:,daytona:2", "daytona,,daytona", "../game,daytona",
                          "daytona:1:2,daytona:2"):
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


if __name__ == "__main__":
    unittest.main()
