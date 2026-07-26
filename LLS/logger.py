"""
Модуль для настройки и использования многоуровневого логирования.
Логи разделяются по категориям (critical, errors, warnings, info, debug)
и сохраняются в отдельные файлы, а также в общий лог-файл.
Автоматически удаляются старые файлы, остаются последние `keep` штук.
"""

from os import (
    path,
    remove,
    listdir,
    getcwd,
    makedirs
)

from logging import (
    Filter,
    LogRecord,
    Formatter,
    getLogger,
    DEBUG,
    INFO,
    WARNING,
    ERROR,
    CRITICAL

)

from logging.handlers import RotatingFileHandler

from datetime import datetime


class LevelFilter(Filter):
    """
    Фильтр, пропускающий записи только с указанными уровнями логирования.
    """

    def __init__(self, levels):
        self.levels = levels
        super().__init__()

    def filter(self, record):
        return record.levelno in self.levels


class LoggerSystem():
    """
    Синглтон-класс для управления логгером в заданной папке.
    Для каждой папки (folder) создаётся отдельный экземпляр.
    """

    _inst = {}
    _global_st = datetime.now()

    def __new__(cls, folder, max_folders=5):
        if folder not in cls._inst:
            instance = super().__new__(cls)
            instance._initialized = False
            cls._inst[folder] = instance
        return cls._inst[folder]

    def __init__(self, folder="default", max_folders=5):
        """
        Инициализация экземпляра. Выполняется только один раз для каждой папки.
        :param folder: имя папки для хранения логов (подпапка в logs/)
        :param max_folders: количество последних файлов, которые сохраняются в каждой категории
        """
        if self._initialized:
            return

        self.folder = folder
        self.max_folders = max_folders

        self.logger = None
        self._all_file = None
        self.start_time = LoggerSystem._global_st

    def _clear(self, dir):
        """
        Удаляет старые .log-файлы в директории, оставляя только последние self.keep штук.
        Сортировка по имени файла (предполагается, что имена содержат временную метку).
        """

        if not path.exists(dir):
            return

        files = [f for f in listdir(dir) if f.endswith('.log')]

        if len(files) <= self.max_folders:
            return

        files.sort()
        for old in files[:-self.max_folders]:
            try:
                remove(path.join(dir, old))
            except OSError:
                pass

    @staticmethod
    def _format(level, msg):
        """
        Форматирует запись для ручной записи в лог-файл (используется при инициализации).
        """

        formatter = Formatter(
            '[%(asctime)s] [%(levelname)s] [%(filename)s] '
            '[%(funcName)s] [%(lineno)d] -> %(message)s',
            datefmt='%d.%m.%Y %H:%M:%S'
        )

        record = LogRecord(
            name='logger.py',
            level=level,
            pathname='logger.py',
            lineno=0,
            msg=msg,
            args=(),
            exc_info=None,
            func='<module>'
        )

        record.asctime = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        return formatter.format(record)

    def _write(self, log_file):
        """
        Записывает в новый лог-файл сообщение об инициализации для данной папки.
        """

        msg = (f"Логирование инициализировано для [{self.folder}]: {self.start_time.strftime('%H:%M:%S %d.%m.%Y')}.")

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(self._format(INFO, msg) + '\n')

    def _path(self, category):
        """
        Создаёт директорию для категории и возвращает путь к файлу лога.
        Если файл не существует, записывает начальное сообщение.
        После создания выполняет очистку старых файлов.
        """

        logs_dir = path.join(getcwd(), "logs", self.folder)

        category_dir = path.join(logs_dir, category)

        makedirs(category_dir, exist_ok=True)

        time_str = self.start_time.strftime("%H.%M.%S_%d.%m.%Y")

        log_file = path.join(category_dir, f"{time_str}.log")

        if not path.exists(log_file):
            self._write(log_file)

        self._clear(category_dir)
        return log_file

    def _all(self):
        """
        Создаёт директорию 'all' и возвращает путь к глобальному лог-файлу.
        При первом создании записывает сообщение о глобальной инициализации.
        """

        all_dir = path.join(getcwd(), "logs", "all")

        makedirs(all_dir, exist_ok=True)

        time_str = self.start_time.strftime("%H.%M.%S_%d.%m.%Y")

        log_file = path.join(all_dir, f"{time_str}.log")

        self._all_file = log_file

        if not path.exists(log_file):
            msg = (f"Глобальное логирование инициализировано: {self.start_time.strftime('%H:%M:%S %d.%m.%Y')}.")

            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(self._format(INFO, msg) + '\n')

        self._clear(all_dir)
        return log_file

    def setup(self):
        """
        Настраивает логгер: создаёт обработчики для каждой категории и глобальный обработчик.
        Вызывается автоматически при первом обращении к логгеру.
        """

        if self._initialized:
            return self.logger

        self.logger = getLogger(self.folder)
        self.logger.setLevel(DEBUG)
        self.logger.propagate = False

        categories = {
            "critical": LevelFilter([CRITICAL]),
            "errors": LevelFilter([ERROR]),
            "warnings": LevelFilter([WARNING]),
            "info": LevelFilter([INFO]),
            "debug": LevelFilter([DEBUG]),
        }

        formatter = Formatter(
            '[%(asctime)s] [%(levelname)s] [%(filename)s] '
            '[%(funcName)s] [%(lineno)d] -> %(message)s',
            datefmt='%d.%m.%Y %H:%M:%S'
        )

        for category_name, level_filter in categories.items():
            log_path = self._path(category_name)
            handler = RotatingFileHandler(
                log_path,
                maxBytes=10 * 1024 * 1024,
                backupCount=0,
                encoding='utf-8'
            )
            handler.setLevel(DEBUG)
            handler.addFilter(level_filter)
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        all_log_path = self._all()
        all_handler = RotatingFileHandler(
            all_log_path,
            maxBytes=10 * 1024 * 1024,
            backupCount=0,
            encoding='utf-8'
        )
        all_handler.setLevel(DEBUG)
        all_handler.setFormatter(formatter)
        self.logger.addHandler(all_handler)

        self._initialized = True
        return self.logger

    def __getattr__(self, name):
        """
        Позволяет обращаться к методам логирования через сокращения:
        d -> debug, i -> info, w -> warning, e -> error, c -> critical.
        Также поддерживаются полные имена.
        """
        if not self._initialized:
            self.setup()

        short_names = {
            'd': 'debug',
            'i': 'info',
            'w': 'warning',
            'e': 'error',
            'c': 'critical'
        }
        if name in short_names:
            return getattr(self.logger, short_names[name])
        if name in ['debug', 'info', 'warning', 'error', 'critical']:
            return getattr(self.logger, name)
        raise AttributeError(f"'LoggerSystem' object has no attribute '{name}'")


_log = {}


def log_init(folder="default", max_folders=5):
    """
    Фабричная функция для получения экземпляра LoggerSystem для заданной папки.
    При первом вызове для папки автоматически выполняется настройка.
    :param folder: имя папки для хранения логов
    :param max_folders: количество последних файлов, которые сохраняются в каждой категории
    """

    if folder not in _log:
        _log[folder] = LoggerSystem(folder, max_folders)
        _log[folder].setup()
    return _log[folder]
