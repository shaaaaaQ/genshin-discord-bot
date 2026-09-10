import unittest

from cogs.codes import Codes
from cogs.gacha import Gacha
from cogs.profile import Profile
from cogs.stage import Stage


class HelpDescriptionTests(unittest.TestCase):
    def test_top_level_commands_have_help_descriptions(self) -> None:
        commands = (
            Codes.codes,
            Codes.codesnotify,
            Gacha.gacha,
            Profile.profile,
            Stage.stage,
        )

        for command in commands:
            with self.subTest(command=command.name):
                self.assertTrue(command.short_doc)

    def test_codesnotify_subcommands_have_help_descriptions(self) -> None:
        for name in ('set', 'remove'):
            command = Codes.codesnotify.get_command(name)
            with self.subTest(command=name):
                self.assertIsNotNone(command)
                self.assertTrue(command.short_doc)


if __name__ == '__main__':
    unittest.main()
