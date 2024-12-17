# Shell Emulator

# Вариант №19 
Задание №1 
Разработать эмулятор для языка оболочки ОС. Необходимо сделать работу 
эмулятора как можно более похожей на сеанс shell в UNIX-подобной ОС. 
Эмулятор должен запускаться из реальной командной строки, а файл с 
виртуальной файловой системой не нужно распаковывать у пользователя. 
Эмулятор принимает образ виртуальной файловой системы в виде файла формата 
zip. Эмулятор должен работать в режиме CLI. 
Конфигурационный файл имеет формат xml и содержит: 
- **Путь к архиву виртуальной файловой системы.** 
- **Путь к лог-файлу.** 

Лог-файл имеет формат xml и содержит все действия во время последнего 
сеанса работы с эмулятором. Для каждого действия указаны дата и время. 
Необходимо поддержать в эмуляторе команды ls, cd и exit, а также 
следующие команды: 
- **pwd.**
- **uptime.** 

Все функции эмулятора должны быть покрыты тестами, а для каждой из 
поддерживаемых команд необходимо написать 3 теста.

## Описание программы

Программа позволяет:
- **Просматривать содержимое каталогов** с помощью команды `ls`.
- **Перемещаться между каталогами** с помощью команды `cd`.
- **Отображать текущий путь** с помощью команды `pwd`.
- **Показывать время работы программы** с помощью команды `uptime`.
- **Выходить из эмулятора**, сохраняя лог действий в XML-файл, с помощью команды `exit`.

Эмулятор загружает конфигурацию из XML-файла, в котором указывается путь к архиву VFS и файл для сохранения лога.

## Требования

- Python 3.x
- Наличие библиотеки `unittest` для запуска тестов

## Установка и запуск

1. **Создайте конфигурационный файл (config.xml):**
   Пример файла `config.xml`:
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <config>
       <vfs_path>test_zip_1.zip</vfs_path>
       <log_file>log.xml</log_file>
   </config>
   ```

2. **Запустите эмулятор:**
   ```bash
   python shell_emulator.py config.xml
   ```
   
   Эмулятор откроет виртуальную оболочку с приглашением `$` для ввода команд.

## Команды оболочки

| Команда           | Описание                               |
|-------------------|----------------------------------------|
| `ls`             | Вывести список файлов в текущем каталоге. |
| `cd <путь>`      | Перейти в указанный каталог.           |
| `pwd`            | Показать текущий путь.                 |
| `uptime`         | Показать время работы программы.       |
| `exit`           | Завершить работу и сохранить лог.      |

## Пример работы

```bash
$ ls
file1.txt
file2.txt
subdir

$ cd subdir
$ pwd
/subdir

$ uptime
Uptime: 12.34 seconds

$ exit
Exiting shell emulator.
```

После завершения работы программы будет создан лог-файл `log.xml` с историей всех выполненных действий.

## Разбор кода на Python

Ниже приведён разбор ключевых компонентов программы:

### Класс `ShellEmulator`

#### Инициализация
```python
class ShellEmulator:
    def __init__(self, config_path):
        self.load_config(config_path)  # Загружаем конфигурацию из XML-файла
        self.current_directory = '/'  # Начальный путь
        self.log_entries = []         # Логируем действия пользователя
        self.start_time = time.time() # Засекаем время запуска программы
```

- **`load_config`** — загружает настройки VFS и лога из файла `config.xml`.
- **`extract_vfs`** — распаковывает ZIP-архив виртуальной файловой системы во временный каталог `/tmp/vfs`.

#### Основные методы

- **`ls`**
   Выводит содержимое текущего каталога:
   ```python
   def ls(self):
       entries = os.listdir('/tmp/vfs' + self.current_directory)
       print("\n".join(entries))
       self.log_action(f"ls in {self.current_directory}")
   ```

- **`cd`**
   Позволяет перемещаться между директориями:
   ```python
   def cd(self, directory):
       new_path = os.path.join('/tmp/vfs' + self.current_directory, directory)
       if os.path.isdir(new_path):
           self.current_directory = os.path.join(self.current_directory, directory)
           self.log_action(f"cd to {self.current_directory}")
       else:
           print(f"cd: no such file or directory: {directory}")
   ```

- **`pwd`**
   Выводит текущий путь:
   ```python
   def pwd(self):
       print(self.current_directory)
       self.log_action("pwd")
   ```

- **`uptime`**
   Показывает время работы программы:
   ```python
   def uptime(self):
       elapsed_time = time.time() - self.start_time
       print(f"Uptime: {elapsed_time:.2f} seconds")
       self.log_action("uptime")
   ```

- **`exit`**
   Завершает работу программы и сохраняет лог в XML-файл:
   ```python
   def exit(self):
       self.write_log()
       print("Exiting shell emulator.")
       sys.exit(0)
   ```

#### Метод `run`
   Основной цикл программы, обрабатывающий команды пользователя:
   ```python
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
   ```
   
### Тестирование с `unittest`
В файле `test_emulator.py` реализованы тесты для методов:
- `ls`
- `cd`
- `pwd`
- `uptime`
- `exit`

Пример теста:
```python
import unittest
from emulator import ShellEmulator

class TestShellEmulator(unittest.TestCase):
    def setUp(self):
        self.emulator = ShellEmulator('config.xml')

    def test_ls(self):
        self.emulator.ls()

    def test_cd(self):
        self.emulator.cd('some_directory')

if __name__ == '__main__':
    unittest.main()
```

## Тестирование

Для тестирования программы используется модуль `unittest`.

1. Запустите тесты с помощью команды:
   ```bash
   python -m unittest test_emulator.py
   ```

2. Пример тестов включен в файле `test_emulator.py`.

## Структура проекта

```
.
├── shell_emulator.py     # Основной файл программы
├── test_emulator.py      # Тесты
├── config.xml            # Конфигурационный файл
├── test_zip_1.zip        # ZIP-архив с VFS
└── README.md             # Этот файл
```

## Логи и конфигурация

- **config.xml** — файл конфигурации, содержит пути к VFS и лог-файлу.
- **log.xml** — файл лога, сохраняет историю команд, выполненных в сессии.
