# LibraryLogSystem (LLS)

**LLS** - это универсальная система логирования для Python приложений.
Позволяет разделять логи по категориям (debug, info, warning, error, critical) и создавать отдельные директории для разных модулей.

[Проект на PyPi.org!](https://pypi.org/project/EOF-413-LLS/)

## Особенности

- Разделение логов по уровням: debug, info, warning, error, critical
- Автоматическое создание папок для каждого модуля
- Общая папка all/ со всеми логами без сортировки
- Автоматическая очистка старых логов (хранится 5 последних файлов)
- Singleton паттерн для каждого логгера
- Поддержка коротких имен методов: d(), i(), w(), e(), c()

## Установка

```python
from LLS import log_init
```

## Использование

### Базовое использование

```python
from LLS import log_init

# Создание логгера для конкретного модуля
log = log_init('main')

# Запись логов
log.debug("Отладочное сообщение")
log.info("Информационное сообщение")
log.warning("Предупреждение")
log.error("Ошибка")
log.critical("Критическая ошибка")
```

### Короткие имена методов

```python
from LLS import log_init

log = log_init('main')

log.d("debug")   # debug
log.i("info")    # info
log.w("warning") # warning
log.e("error")   # error
log.c("critical") # critical
```

### Использование в разных модулях

```python
# http/client.py
from LLS import log_init

log = log_init('http')

log.info("HTTP запрос отправлен")

# github/repository.py
from LLS import log_init

log = log_init('GitHub')

log.info("Поиск репозиториев")
```

## Структура логов

```text
logs/
├── all/
│   └── 21.59.18_25.07.2026.log
├── main/
│   ├── debug/
│   ├── info/
│   ├── warnings/
│   ├── errors/
│   └── critical/
├── http/
│   ├── debug/
│   ├── info/
│   ├── warnings/
│   ├── errors/
│   └── critical/
└── GitHub/
    ├── debug/
    ├── info/
    ├── warnings/
    ├── errors/
    └── critical/
```

## Формат логов

```log
[25.07.2026 21:59:18] [INFO] [main.py] [<module>] [5] -> Сообщение
[25.07.2026 21:59:18] [ERROR] [client.py] [get] [25] -> Ошибка запроса
```

## API

### log_init(folder: str) -> LoggerSystem

Создает или возвращает экземпляр логгера для указанной папки.

Параметры:
- folder (str): Имя папки для хранения логов (например, "main", "http", "GitHub")

Возвращает:
- LoggerSystem: Экземпляр логгера

### Методы логгера

| Метод | Короткий | Описание |
|-------|----------|----------|
| debug(msg) | d(msg) | Запись отладочного сообщения |
| info(msg) | i(msg) | Запись информационного сообщения |
| warning(msg) | w(msg) | Запись предупреждения |
| error(msg) | e(msg) | Запись ошибки |
| critical(msg) | c(msg) | Запись критической ошибки |

## Очистка логов

Система автоматически хранит только 5 последних лог-файлов для каждой категории. Старые файлы удаляются автоматически.
