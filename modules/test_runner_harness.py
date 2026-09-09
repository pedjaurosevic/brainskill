"""Offline checks for Domain-2 sims and HTTP retry-once."""

from __future__ import annotations

import io
import json
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "benchmark"))
from run_battery import SIMULATED_OUTPUTS, call_chat_completion, simulate_tool_execution  # noqa: E402


class SimulatedOutputsTests(unittest.TestCase):
    def test_all_domain2_items_present(self) -> None:
        self.assertEqual(set(SIMULATED_OUTPUTS), {f"d2.{i:02d}" for i in range(1, 13)})

    def test_probes_are_item_specific(self) -> None:
        probes = {
            "d2.01": "btrfs filesystem df /",
            "d2.02": "systemctl status",
            "d2.03": "ss -tulpn",
            "d2.04": "nvidia-smi",
            "d2.05": "waybar",
            "d2.06": "df -i",
            "d2.07": "ss -tulpn",
            "d2.08": "systemctl show foo",
            "d2.09": "cat /etc/resolv.conf",
            "d2.10": "getfacl secret.txt",
            "d2.11": "dmesg | tail",
            "d2.12": "locale",
        }
        for item_id, command in probes.items():
            out = simulate_tool_execution(item_id, "bash_inspect", {"command": command})
            self.assertNotIn("no anomalies found", out, msg=item_id)


class RetryTests(unittest.TestCase):
    def test_retries_once_then_succeeds(self) -> None:
        calls = {"n": 0}

        def fake_urlopen(req, timeout=120):  # noqa: ARG001
            calls["n"] += 1
            if calls["n"] == 1:
                raise urllib.error.URLError("temporary")

            class Resp(io.BytesIO):
                def __enter__(self):
                    return self

                def __exit__(self, *args):
                    return False

                def read(self):
                    return json.dumps(
                        {"choices": [{"message": {"content": "{}"}, "finish_reason": "stop"}]}
                    ).encode()

            return Resp()

        with mock.patch("urllib.request.urlopen", fake_urlopen):
            call_chat_completion(
                "http://127.0.0.1:9/v1",
                None,
                "m",
                [{"role": "user", "content": "hi"}],
                max_attempts=2,
            )
        self.assertEqual(calls["n"], 2)

    def test_second_failure_raises(self) -> None:
        calls = {"n": 0}

        def always_fail(req, timeout=120):  # noqa: ARG001
            calls["n"] += 1
            raise urllib.error.URLError("down")

        with mock.patch("urllib.request.urlopen", always_fail):
            with self.assertRaises(urllib.error.URLError):
                call_chat_completion(
                    "http://127.0.0.1:9/v1",
                    None,
                    "m",
                    [{"role": "user", "content": "hi"}],
                    max_attempts=2,
                )
        self.assertEqual(calls["n"], 2)


if __name__ == "__main__":
    unittest.main()
