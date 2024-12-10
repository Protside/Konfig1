import os
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
import shutil
import time
import unittest
import tempfile


def read_config(path):
    tree = ET.parse(path)
    root = tree.getroot()
    vfs_path = root.find('vfs').text
    log_path = root.find('log').text
    return vfs_path, log_path

class VirtualFileSystem:
    def __init__(self, zip_path):
        self.root = "Console"
        self.current_path = self.root
        self.extract_zip(zip_path)

    def extract_zip(self, zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.root)

    def list_directory(self):
        items = []
        for item in os.listdir(self.current_path):
            item_path = os.path.join(self.current_path, item)
            stats = os.stat(item_path)
            size = stats.st_size
            modified_time = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            item_type = 'Directory' if os.path.isdir(item_path) else 'File'
            items.append(f"{item_type: <10} {size: <10} {modified_time} {item}")
        return "\n".join(items)

    def change_directory(self, path):
        if path == '..':
            if self.current_path != self.root:
                self.current_path = os.path.dirname(self.current_path)
            else:
                raise FileNotFoundError("You are already at the root directory")
        else:
            new_path = os.path.join(self.current_path, path)
            if os.path.isdir(new_path):
                self.current_path = new_path
            else:
                raise FileNotFoundError("Directory not found")

    def get_relative_path(self):
        return os.path.relpath(self.current_path, self.root).replace('\\', '/')

    def read_file(self, file_name):
        file_path = os.path.join(self.current_path, file_name)
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.readlines()
            except UnicodeDecodeError:
                return "Error reading file: unsupported characters"
        else:
            raise FileNotFoundError("File not found")
    def move(self, path_A, path_B):
        try:
            shutil.move(os.path.join(self.current_path, path_A), os.path.join(self.current_path, path_B))
        except FileNotFoundError:
            raise FileNotFoundError("File not found")


def ls(vfs):
    try:
        return vfs.list_directory()
    except Exception as e:
        return str(e)

def cd(vfs, path):
    if path.startswith('...') or '...' in path:
        raise ValueError("Error: More than two consecutive dots are not allowed in the directory path.") #Raise Value Error instead of returning string

    try:
        vfs.change_directory(path)
        return f"Changed directory to {vfs.current_path}"
    except FileNotFoundError as e:
        raise e  # Re-raise the FileNotFoundError
    except Exception as e:
        raise e #Re-raise other exceptions

def pwd(vfs):
    return vfs.get_relative_path()

def uptime():
    return f"Uptime: {int(time.time() - time.monotonic())} seconds"

def run_shell(vfs_path, log_path):
    vfs = VirtualFileSystem(vfs_path)
    log = ET.Element('log')

    def log_action(command, result):
        action = ET.SubElement(log, 'action')
        ET.SubElement(action, 'timestamp').text = datetime.now().isoformat()
        ET.SubElement(action, 'command').text = command
        ET.SubElement(action, 'result').text = str(result)


    def get_prompt():
        relative_path = vfs.get_relative_path()
        return f"./{relative_path}> " if relative_path else "./> "

    while True:
        command = input(get_prompt())
        if command.lower() == 'exit':
            tree = ET.ElementTree(log)
            tree.write(log_path)
            break

        output = ""
        try:
            parts = command.split()
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd == 'ls':
                output = ls(vfs)
            elif cmd == 'cd':
                if not args:
                    output = "Please specify a directory."
                else:
                    output = cd(vfs, args[0])
            elif cmd == 'pwd':
                output = pwd(vfs)
            elif cmd == 'uptime':
                output = uptime()
            else:
                output = "Unknown command"

        except Exception as e:
            output = str(e)

        log_action(command, output)
        print(output)



class TestVirtualFileSystem(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(self.temp_dir, 'test_vfs.zip')
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr('test_file.txt', 'Test content')
            dir1_path = os.path.join(self.temp_dir, 'dir1')
            os.makedirs(dir1_path, exist_ok=True)
            zf.writestr('dir1/test_file2.txt', 'More test content')
            dir2_path = os.path.join(self.temp_dir, 'dir2')
            os.makedirs(dir2_path, exist_ok=True)
            zf.write(dir2_path, "dir2")

        self.vfs = VirtualFileSystem(zip_path)


    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_ls_root(self):
        self.assertIn('dir1', ls(self.vfs))
        self.assertIn('test_file.txt', ls(self.vfs))

    def test_ls_subdir(self):
        cd(self.vfs, 'dir1')
        self.assertIn('test_file2.txt', ls(self.vfs))
        self.assertNotIn('test_file.txt', ls(self.vfs))


    def test_cd_root(self):
        self.assertEqual(cd(self.vfs, 'dir1'), f"Changed directory to {os.path.join(self.vfs.root, 'dir1')}")
        self.assertEqual(cd(self.vfs, '..'), f"Changed directory to {self.vfs.root}")

    def test_cd_subdir(self):
        self.assertEqual(cd(self.vfs, 'dir1'), f"Changed directory to {os.path.join(self.vfs.root, 'dir1')}")
        self.assertEqual(cd(self.vfs,'..'), f"Changed directory to {self.vfs.root}")

    def test_cd_invalid(self):
        with self.assertRaises(FileNotFoundError):
            result = cd(self.vfs, 'invalid_dir')
            if isinstance(result,FileNotFoundError):
                raise result
            else:
                self.fail("FileNotFoundError not raised")

    def test_ls_empty_dir(self):
        empty_dir_path = os.path.join(self.vfs.root, "empty_dir")
        if os.path.exists(empty_dir_path):
            shutil.rmtree(empty_dir_path) #Remove if exists
        os.makedirs(empty_dir_path)
        cd(self.vfs, "empty_dir")
        self.assertEqual(ls(self.vfs).strip(), "")
        cd(self.vfs, "..")

    def test_pwd_root(self):
        self.assertEqual(pwd(self.vfs), '.')

    def test_pwd_subdir(self):
        cd(self.vfs, 'dir1')
        self.assertEqual(pwd(self.vfs), 'dir1')

    def test_pwd_after_cd_up(self):
        cd(self.vfs, 'dir1')
        cd(self.vfs, '..')
        self.assertEqual(pwd(self.vfs), '.')


    def test_uptime(self):
        # Проверка, что uptime возвращает строку с числом секунд
        self.assertTrue(isinstance(uptime(), str))
        self.assertTrue("Uptime:" in uptime())


if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)