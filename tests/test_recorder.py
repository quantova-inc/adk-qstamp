# Copyright 2026 Quantova Inc
# SPDX-License-Identifier: Apache-2.0 OR MIT

import asyncio
import hashlib
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from adk_qstamp import QstampToolRecorder  # noqa: E402


def run(coro):
    return asyncio.run(coro)


class RecorderTests(unittest.TestCase):
    def test_anchors_one_digest_per_call(self):
        calls = []

        def anchor(digests, kind):
            calls.append((digests, kind))
            return [{"anchor": {"tx": "tx0"}}]

        got = []
        rec = QstampToolRecorder(anchor, kind="7757", on_receipt=lambda r, n: got.append(n))
        run(rec.record("search", {"q": "x"}, {"content": []}))
        self.assertEqual(len(calls), 1)
        self.assertEqual(len(calls[0][0]), 1)
        self.assertEqual(len(calls[0][0][0]), 32)
        self.assertEqual(calls[0][1], "7757")
        self.assertEqual(got, ["search"])

    def test_only_digest_leaves(self):
        seen = {}

        def anchor(digests, kind):
            seen["payload"] = json.dumps([d.hex() for d in digests])
            return [{"ok": True}]

        rec = QstampToolRecorder(anchor, project=lambda n, a, r: {"n": n, "a": a, "r": r})
        run(rec.record("t", {"k": "TOP-SECRET-IN"}, {"text": "TOP-SECRET-OUT"}))
        self.assertNotIn("TOP-SECRET-IN", seen["payload"])
        self.assertNotIn("TOP-SECRET-OUT", seen["payload"])

    def test_digest_is_deterministic_and_key_order_independent(self):
        rec = QstampToolRecorder(lambda d, k: [None])
        a = rec.digest("t", {}, {"a": 1, "b": 2})
        b = rec.digest("t", {}, {"b": 2, "a": 1})
        self.assertEqual(a, b)
        self.assertEqual(len(a), 32)

    def test_digest_matches_plain_sha3(self):
        rec = QstampToolRecorder(lambda d, k: [None])
        canonical = json.dumps({"tool": "t", "result": {"x": 1}}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        self.assertEqual(rec.digest("t", {}, {"x": 1}), hashlib.sha3_256(canonical.encode()).digest())

    def test_async_anchor_supported(self):
        async def anchor(digests, kind):
            return [{"async": True}]

        got = []
        rec = QstampToolRecorder(anchor, on_receipt=lambda r, n: got.append(r))
        run(rec.record("t", {}, {}))
        self.assertEqual(got, [{"async": True}])

    def test_anchor_failure_routed_to_on_error(self):
        def anchor(digests, kind):
            raise RuntimeError("chain unreachable")

        errs = []
        rec = QstampToolRecorder(anchor, on_error=lambda e, n: errs.append((n, str(e))))
        out = run(rec.record("t", {}, {}))
        self.assertIsNone(out)
        self.assertEqual(len(errs), 1)

    def test_anchor_failure_raises_without_handler(self):
        def anchor(digests, kind):
            raise RuntimeError("boom")

        rec = QstampToolRecorder(anchor)
        with self.assertRaises(RuntimeError):
            run(rec.record("t", {}, {}))

    def test_rejects_bad_construction(self):
        with self.assertRaises(ValueError):
            QstampToolRecorder(None)
        with self.assertRaises(ValueError):
            QstampToolRecorder(lambda d, k: [], alg="md5")


if __name__ == "__main__":
    unittest.main()
