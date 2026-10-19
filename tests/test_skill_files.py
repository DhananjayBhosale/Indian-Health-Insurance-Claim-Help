from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
RELEASE_WORKFLOW = SKILL_ROOT / ".github" / "workflows" / "release.yml"


class SkillFileTests(unittest.TestCase):
    def test_frontmatter_fits_claude_ai_upload_limits(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)[1]
        fields = dict(
            line.split(": ", 1) for line in frontmatter.strip().splitlines()
        )
        self.assertEqual(fields["name"], SKILL_ROOT.name.lower())
        self.assertLessEqual(len(fields["name"]), 64)
        self.assertLessEqual(len(fields["description"]), 200)
        # A second ": " would turn the plain YAML scalar into an invalid mapping.
        self.assertNotIn(": ", fields["description"])

    def test_chat_guide_fits_a_pasted_prompt_or_instruction_field(self) -> None:
        guide = (SKILL_ROOT / "GUIDE.md").read_text(encoding="utf-8")
        self.assertLessEqual(len(guide), 7000)

    def test_chat_scenarios_are_complete(self) -> None:
        text = (SKILL_ROOT / "tests" / "chat-scenarios.md").read_text(encoding="utf-8")
        scenarios = re.split(r"^## Scenario \d+ ", text, flags=re.MULTILINE)[1:]
        self.assertEqual(len(scenarios), 6)
        for scenario in scenarios:
            for heading in ("### User turns", "### Planted gaps", "### Expected"):
                with self.subTest(scenario=scenario.splitlines()[0], heading=heading):
                    self.assertIn(heading, scenario)

    def test_release_zip_includes_every_linked_skill_file(self) -> None:
        workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        for name in ("SKILL.md", "GUIDE.md"):
            text = (SKILL_ROOT / name).read_text(encoding="utf-8")
            for target in re.findall(r"\]\(([^)#]+)\)", text):
                if "://" in target:
                    continue
                with self.subTest(source=name, target=target):
                    self.assertTrue((SKILL_ROOT / target).is_file())
                    self.assertRegex(workflow, rf"\s{re.escape(Path(target).parts[0])}(\s|$)")


if __name__ == "__main__":
    unittest.main()
