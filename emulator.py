import os
import zipfile
import xml.etree.ElementTree as ET
import sys
import time
from datetime import datetime


class ShellEmulator:
    def __init__(self, config_path):
        self.load_config(config_path)
        self.current_directory = '/'
        self.log_entries = []
        self.start_time = time.time()

    def load_config(self, config_path):
        tree = ET.parse(config_path)
        root = tree.getroot()
        self.vfs_path = root.find('vfs_path').text
        self.log_file = root.find('log_file').text
        self.extract_vfs()

    def extract_vfs(self):
        with zipfile.ZipFile(self.vfs_path, 'r') as zip_ref:
            zip_ref.extractall('/tmp/vfs')

    def log_action(self, action):
        self.log_entries.append(f"{action} | {datetime.now()}")

    def write_log(self):
        root = ET.Element("log")
        for entry in self.log_entries:
            ET.SubElement(root, "action").text = entry
        tree = ET.ElementTree(root)
        tree.write(self.log_file)

    def ls(self):
        entries = os.listdir('/tmp/vfs' + self.current_directory)
        print("\n".join(entries))
        self.log_action(f"ls in {self.current_directory}")

    def cd(self, directory):
        new_path = os.path.join('/tmp/vfs' + self.current_directory, directory)
        if os.path.isdir(new_path):
            self.current_directory = os.path.join(self.current_directory, directory)
            self.log_action(f"cd to {self.current_directory}")
        else:
            print(f"cd: no such file or directory: {directory}")

    def exit(self):
        self.write_log()
        print("Exiting shell emulator.")
        sys.exit(0)

    def pwd(self):
        print(self.current_directory)
        self.log_action("pwd")

    def uptime(self):
        elapsed_time = time.time() - self.start_time
        print(f"Uptime: {elapsed_time:.2f} seconds")
        self.log_action("uptime")

    def run(self):
        while True:
            command = input(f"{self.current_directory} $ ").strip().split()
            if not command:
                continue
            cmd = command[0]
            if cmd == "ls":
                self.ls()
            elif cmd == "cd":
                if len(command) > 1:
                    self.cd(command[1])
                else:
                    print("cd: missing argument")
            elif cmd == "exit":
                self.exit()
            elif cmd == "pwd":
                self.pwd()
            elif cmd == "uptime":
                self.uptime()
            else:
                print(f"{cmd}: command not found")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)
    config_path = sys.argv[1]
    emulator = ShellEmulator(config_path)
    emulator.run()
