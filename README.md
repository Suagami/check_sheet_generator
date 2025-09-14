# Check Sheet Generator

Генератор чек-листов на Python.  
Проект использует **Python 3.12+**, [pydantic](https://docs.pydantic.dev/) и [xlsxwriter](https://xlsxwriter.readthedocs.io/).

---

## 🚀 Установка на Windows

### 1. Установка Python
Скачайте и установите [Python 3.12](https://www.python.org/downloads/windows/).  
⚠️ При установке обязательно отметьте галочку **"Add Python to PATH"**.

Проверьте установку:
```powershell
python --version
```

### 2. Клонирование проекта

Склонируйте репозиторий:

```powershell
git clone https://github.com/Suagami/check-sheet-generator.git
cd check-sheet-generator
```

### 3. Создание виртуального окружения

```powershell
pip install uv
```

### 4. Установка зависимостей

```powershell
uv sync
```

### 5. Запуск

Пример запуска:

```powershell
uv run python main.py
```

## 🧪 Тестирование

Запуск тестов:

```powershell
uv run pytest
```

---

## 🧹 Линтинг и форматирование

Проверка кода:

```powershell
uv run ruff check .
```

Автоисправление:

```powershell
uv run ruff check . --fix
```

Форматирование:

```powershell
uv run ruff format .
```


