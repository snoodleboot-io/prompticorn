"""The marketing site must not outlive the truth (PRO-149).

`website/index.html` sat three months stale claiming five supported tools while
the registry held seventeen, and six CLI commands while there were eleven. The
counts were hand-written in twelve places, so every new tool silently made the
page wronger.

These tests do not check prose. They check the handful of claims that are
*facts about the code* — how many tools, which tools, which commands — so the
page fails the build rather than quietly misleading a reader.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from prompticorn.cli import cli
from prompticorn.tools import TOOLS

_SITE = Path(__file__).resolve().parents[2] / "website" / "index.html"


@pytest.fixture(scope="module")
def page() -> str:
    return _SITE.read_text(encoding="utf-8")


def test_the_site_exists_where_the_test_thinks_it_does():
    """Guards every assertion below: a moved file must fail loudly, not vacuously."""
    assert _SITE.is_file(), f"no page at {_SITE}"


class TestToolClaims:
    def test_every_supported_tool_is_named(self, page: str):
        """The whole point of the grid. A tool shipped but unlisted is a feature
        nobody can discover."""
        missing = sorted(
            spec.display_label for spec in TOOLS.values() if spec.display_label not in page
        )

        assert not missing, f"supported tools missing from the site: {missing}"

    def test_the_claimed_tool_count_matches_the_registry(self, page: str):
        """The claim that actually went stale. Written out in several places, so
        every occurrence is checked rather than the first."""
        claimed = set(re.findall(r"(\d+) (?:AI )?[Tt]ools", page))
        expected = str(len(TOOLS))

        assert claimed, "the page no longer states a tool count — update this test"
        assert claimed == {expected}, (
            f"the site claims {sorted(claimed)} tools; the registry has {expected}"
        )

    def test_no_spelled_out_stale_count_survives(self, page: str):
        """"Five tools" is invisible to the numeric check above, and that is the
        exact form the page was stale in."""
        stale = re.findall(r"\b(?:five|Five|FIVE|six|Six)\b[^.<]{0,20}\b(?:tools|Tools)\b", page)

        assert not stale, f"spelled-out tool counts still on the page: {stale}"


class TestCommandClaims:
    def test_every_cli_command_is_listed(self, page: str):
        """`build`, `lock`, `verify` and `regenerate` all shipped without ever
        reaching the site."""
        missing = sorted(
            name for name in cli.commands if f"prompticorn {name}" not in page
        )

        assert not missing, f"CLI commands missing from the site: {missing}"

    def test_the_claimed_command_count_matches_the_cli(self, page: str):
        """Spelled out on the page, so matched as a word rather than a digit."""
        words = {
            6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten",
            11: "Eleven", 12: "Twelve", 13: "Thirteen", 14: "Fourteen",
        }
        expected = words.get(len(cli.commands))

        assert expected, f"no spelled-out word for {len(cli.commands)} commands — extend this map"
        assert f"{expected} commands" in page, (
            f"the site should say '{expected} commands'; the CLI has {len(cli.commands)}"
        )
