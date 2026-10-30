#!/usr/bin/env python3
"""Tests du parsing robots.txt pour IndexNow (sans réseau)."""

from __future__ import annotations

import unittest
from pathlib import Path

from indexnow import (
    CANONICAL_KEY_FILE,
    disallow_rules_for_indexnow,
    parse_robots_groups,
    path_is_disallowed,
)

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "robots_sopjanitech_live.txt"
LOCAL_ROBOTS = Path(__file__).resolve().parent.parent / "robots.txt"


class RobotsParsingTests(unittest.TestCase):
    def test_fixture_loads(self) -> None:
        self.assertTrue(FIXTURE.is_file(), f"fixture manquante : {FIXTURE}")

    def test_live_fixture_many_agent_groups(self) -> None:
        text = FIXTURE.read_text(encoding="utf-8")
        groups = parse_robots_groups(text)
        agents_flat = [a for agents, _ in groups for a in agents]
        self.assertIn("*", agents_flat)
        self.assertIn("GPTBot", agents_flat)
        self.assertGreater(len(groups), 5)

    def test_live_fixture_key_and_home_allowed(self) -> None:
        rules = disallow_rules_for_indexnow(FIXTURE.read_text(encoding="utf-8"))
        self.assertNotIn("/", set(rules), "Disallow: / des robots IA ne doit pas s'appliquer")
        key_path = f"/{CANONICAL_KEY_FILE}"
        self.assertFalse(path_is_disallowed(key_path, rules), key_path)
        self.assertFalse(path_is_disallowed("/", rules))
        self.assertFalse(path_is_disallowed("/contact.html", rules))

    def test_live_fixture_site_paths_still_blocked(self) -> None:
        rules = disallow_rules_for_indexnow(FIXTURE.read_text(encoding="utf-8"))
        for path in (
            "/AGENTS.md",
            "/README.md",
            "/.gitignore",
            "/sopdibran-collab.github.io-gzimmo/",
            "/sopdibran-collab.github.io-gzimmo/page.html",
        ):
            self.assertTrue(path_is_disallowed(path, rules), path)

    def test_local_robots_allows_key(self) -> None:
        rules = disallow_rules_for_indexnow(LOCAL_ROBOTS.read_text(encoding="utf-8"))
        key_path = f"/{CANONICAL_KEY_FILE}"
        self.assertFalse(path_is_disallowed(key_path, rules))

    def test_comments_and_multi_agent_group(self) -> None:
        sample = """
        # commentaire
        User-agent: *
        User-agent: Bingbot
        Disallow: /secret/  # inline
        Disallow: /other
        User-agent: GPTBot
        Disallow: /
        """
        rules = disallow_rules_for_indexnow(sample)
        self.assertEqual(rules, ["/secret/", "/other"])
        self.assertFalse(path_is_disallowed("/", rules))
        self.assertTrue(path_is_disallowed("/secret/page", rules))

    def test_multiple_star_groups_merge(self) -> None:
        sample = """
        User-agent: *
        Allow: /

        User-agent: GPTBot
        Disallow: /

        User-agent: *
        Disallow: /only-from-second-star
        """
        rules = disallow_rules_for_indexnow(sample)
        self.assertEqual(rules, ["/only-from-second-star"])
        self.assertFalse(path_is_disallowed("/index.html", rules))


if __name__ == "__main__":
    unittest.main()
