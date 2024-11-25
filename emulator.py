import os
import tarfile
import toml
from tkinter import Tk, Text, END
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime

class ShellEmulator:
    def __init__(self, config_path):
        """Инициализация эмулятора оболочки."""
        self.load_config(config_path)
        self.load_virtual_fs()
        self.history = []
        self.init_gui()
        self.run_startup_script()

    def load_config(self, config_path):
        """Загрузка конфигурационного файла TOML."""
        try:
            with open(config_path, 'r') as file:
                config = toml.load(file)
            self.username = config['user']['name']
            self.hostname = config['system']['hostname']
            self.fs_archive = config['paths']['fs_archive']
            self.log_file = config['paths']['log_file']
            self.startup_script = config['paths']['startup_script']
        except Exception as e:
            raise ValueError(f"Ошибка загрузки конфигурации: {e}")

    def load_virtual_fs(self):
        """Извлечение виртуальной файловой системы из архива tar."""
        self.virtual_fs_path = './virtual_fs'  # Папка для виртуальной файловой системы

        # Удаляем старую папку, если она существует
        if os.path.exists(self.virtual_fs_path):
            shutil.rmtree(self.virtual_fs_path)
        os.mkdir(self.virtual_fs_path)  # Создаём новую папку

        try:
            # Открываем tar-архив и извлекаем его содержимое
            with tarfile.open(self.fs_archive, 'r') as tar:
                tar.extractall(self.virtual_fs_path)
            # Устанавливаем текущий путь на корень виртуальной файловой системы
            self.current_path = self.virtual_fs_path
        except Exception as e:
            raise ValueError(f"Ошибка загрузки виртуальной файловой системы: {e}")

    def init_gui(self):
        """Создание графического интерфейса."""
        self.root = Tk()  # Создаём главное окно
        self.root.title("Shell Emulator")  # Устанавливаем заголовок окна

        # Создаём текстовое поле для отображения терминала
        self.text_area = Text(self.root, wrap="word", height=40, width=100,font=("Calibri",14))
        self.text_area.pack(padx=10, pady=10)
        # Привязываем обработчик нажатия клавиши Enter
        self.text_area.bind("<Return>", self.handle_enter_key)
        # Добавляем начальное приглашение
        self.update_prompt()

    def run_startup_script(self):
        """Выполнение стартового скрипта, если указан."""
        if os.path.exists(self.startup_script):  # Проверяем наличие скрипта
            with open(self.startup_script, 'r') as file:
                commands = file.readlines()
            if len(commands)!=0:
                for command in commands:
                    self.execute_command(command.strip())
                    self.update_prompt()
            else:
                return
    def handle_enter_key(self, event):
        """Обработка нажатия клавиши Enter."""
        # Получаем весь текст из текстового поля
        content = self.text_area.get("1.0", END).strip()
        last_line = content.splitlines()[-1]
        # Извлекаем команду из строки
        command = last_line.split(f"{self.username}@{self.hostname}: {self.current_path}$ ", 1)[-1]
        self.execute_command(command)
        self.update_prompt()
        return "break"  # Предотвращаем автоматический перенос строки

    def execute_command(self, command):
        """Обработка команды."""
        if not command.strip():
            return
        self.append_output("\n")
        self.history.append(command)
        parts = command.split()  # Разделяем команду на части
        cmd = parts[0]  # Имя команды
        args = parts[1:]  # Аргументы команды
        self.log_command(command)
        # Обработка команд
        if cmd == "ls":
            self.command_ls()
        elif cmd == "cd":
            self.command_cd(args)
        elif cmd == "exit":
            self.root.quit()
        elif cmd == "uniq":
            self.command_uniq(args)
        elif cmd == "history":
            self.command_history()
        elif cmd == "head":
            self.command_head(args)
        else:
            self.append_output("\n")
            self.append_output(f"Команда не найдена: {cmd}\n", error=True)

    def log_command(self, command):
        """Запись команды в лог-файл XML."""
        try:
            if os.path.exists(self.log_file):
                tree = ET.parse(self.log_file)
                root = tree.getroot()
            else:
                root = ET.Element("log")  # Если файл не существует, создаём новый

            action = ET.SubElement(root, "action")
            action.set("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            action.set("user", self.username)
            action.set("hostname", self.hostname)
            action.set("command", command)

            # Запись изменений в файл
            tree = ET.ElementTree(root)
            tree.write(self.log_file)
        except Exception as e:
            self.append_output(f"Ошибка записи в лог: {e}\n", error=True)

    def command_ls(self):
        """Команда ls."""
        try:
            items = os.listdir(self.current_path)  # Получаем список файлов и папок
            self.append_output("\n".join(items) + "\n")
        except Exception as e:
            self.append_output(f"Ошибка выполнения ls: {e}\n", error=True)

    def command_cd(self, args):
        """Команда cd."""

        if not args:  # Если путь не указан
            self.append_output("cd: путь не указан\n", error=True)
            return

        target = os.path.join(self.current_path, args[0])  # Формируем полный путь
        if args[0] == "..":
            if self.current_path == self.virtual_fs_path:
                return
            else:
                # Переход к родительской директории
                self.current_path = os.path.dirname(self.current_path)
        else:
            # Проверяем, что директория существует
            if os.path.isdir(target):
                self.current_path = target
            else:
                self.append_output(f"cd: путь не найден: {args[0]}\n", error=True)

    def command_uniq(self, args):
        """Команда uniq."""
        if not args:
            self.append_output("uniq: файл не указан\n", error=True)
            return
        file_path = os.path.join(self.current_path, args[0])  # Формируем путь к файлу
        try:
            with open(file_path, 'r',encoding='utf-8') as file:
                lines = file.readlines()
            unique_lines = list(dict.fromkeys(lines))
            self.append_output("".join(unique_lines))
        except Exception as e:
            self.append_output(f"Ошибка выполнения uniq: {e}\n", error=True)

    def command_history(self):
        """Команда history."""
        self.append_output("\n".join(self.history) + "\n")

    def command_head(self, args):
        """Команда head."""
        if not args:
            self.append_output("head: файл не указан\n", error=True)
            return
        file_path = os.path.join(self.current_path, args[0])
        try:
            with open(file_path, 'r',encoding='utf-8') as file:
                lines = file.readlines()[:10]
            self.append_output("".join(lines))
        except Exception as e:
            self.append_output(f"Ошибка выполнения head: {e}\n", error=True)

    def append_output(self, text, error=False):
        """Вывод текста в область вывода."""
        self.text_area.insert(END, text)  # Добавляем текст в конец
        self.text_area.see(END)  # Скроллим вниз, чтобы показать текст

    def update_prompt(self):
        """Обновление приглашения."""
        prompt = f"{self.username}@{self.hostname}: {self.current_path}$ "
        self.text_area.insert(END, prompt)  # Добавляем приглашение
        self.text_area.see(END)

    def run(self):
        """Запуск GUI."""
        self.root.mainloop()


if __name__ == "__main__":
    emulator = ShellEmulator("config.toml")
    emulator.run()
