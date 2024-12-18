# Shell Emulator

Этот проект представляет собой эмулятор командной строки, который работает как сеанс shell в UNIX-подобной ОС. Эмулятор использует виртуальную файловую систему в формате `.tar` и включает графический интерфейс (GUI), разработанный с использованием библиотеки Tkinter.

## Возможности

- Эмуляция командной строки с поддержкой пользовательских приглашений.
- Работа с виртуальной файловой системой без её распаковки пользователем.
- Поддержка следующих команд:
  - `ls`: вывод списка файлов и папок в текущей директории.
  - `cd`: смена текущей директории.
  - `exit`: выход из эмулятора.
  - `uniq`: вывод уникальных строк из указанного файла.
  - `history`: отображение истории выполненных команд.
  - `head`: вывод первых 10 строк указанного файла.
- Логирование всех действий пользователя в формате XML.
- Выполнение стартового скрипта при запуске.

## Структура проекта

```bash
├── config.toml         # Конфигурационный файл
├── emulator.py         # Исходный код эмулятора
├── log.xml             # Лог-файл с действиями пользователя
├── start.sh            # Стартовый скрипт с командами
├── virtual_fs.tar      # Виртуальная файловая система
```
Описание файлов

    config.toml: Конфигурационный файл, содержащий параметры для запуска эмулятора:
        Имя пользователя и имя хоста для приглашения.
        Пути к архиву виртуальной файловой системы, лог-файлу и стартовому скрипту.

    emulator.py: Основной файл программы, реализующий:
        Чтение конфигурации.
        Загрузка виртуальной файловой системы.
        Выполнение команд и управление интерфейсом GUI.

    log.xml: Лог-файл с записью всех действий пользователя за текущий сеанс.

    start.sh: Стартовый скрипт для выполнения команд при запуске.

    virtual_fs.tar: Архив с виртуальной файловой системой.

Как запустить проект

    Убедитесь, что у вас установлен Python 3.8+ и библиотека Tkinter.
    Установите зависимости (если требуются).
    Разместите все файлы проекта в одной директории.
    Запустите эмулятор с помощью команды:

    python emulator.py

    Эмулятор откроется в режиме GUI.

Пример конфигурационного файла

- [user]
  - name = "user"

- [system]
  - hostname = "emulator"

- [paths]
  - fs_archive = "virtual_fs.tar"
  - log_file = "log.xml"
  - startup_script = "start.sh"

## Поддерживаемые команды

| Команда   | Описание                                                                 |
|-----------|--------------------------------------------------------------------------|
| `ls`      | Вывод списка файлов и директорий в текущей директории.                   |
| `cd`      | Смена текущей директории.                                               |
| `exit`    | Завершение работы эмулятора.                                            |
| `uniq`    | Вывод уникальных строк из указанного файла.                             |
| `history` | Показ истории выполненных команд.                                       |
| `head`    | Вывод первых 10 строк указанного файла.                                 |

## Логирование

Все команды, выполненные пользователем, записываются в файл log.xml. Каждая запись включает:

    Метку времени.
    Имя пользователя.
    Имя хоста.
    Текст выполненной команды.
