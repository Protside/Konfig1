import unittest
from emulator import ShellEmulator

class TestShellEmulator(unittest.TestCase):
    def setUp(self):
        self.emulator = ShellEmulator('config.toml')

    def test_ls(self):
        self.emulator.ls()

    def test_cd(self):
        self.emulator.cd('some_directory')

    def test_exit(self):
        with self.assertRaises(SystemExit):
            self.emulator.exit()

    def test_pwd(self):
        self.emulator.pwd()

    def test_uptime(self):
        self.emulator.uptime()

if __name__ == '__main__':
    unittest.main()