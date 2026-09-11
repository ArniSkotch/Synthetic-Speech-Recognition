# Synthetic Speech Detection

Тема: `Исследование методов обнаружения синтезированной речи в задачах голосовой аутентификации`

## Состав

| Файл | Назначение |
|---|---|
| `.#NUM$~_project_setup.ipynb` | Ноутбук инициализации: импорты, проверка версий, конфиг, зеркало HF, загрузка датасета с Kaggle с его текущей версией |
| `config.yaml` | Все константы проекта (пути, гиперпараметры, slug датасета и т.д.) |
| `.env.example` | Шаблон секретов для файла .env |
| `requirements.txt` | Список зависимостей для `pip install` |
| `.gitignore` | Исключает `.env`, большие данные и кэши из git |

## Быстрый старт (Anaconda / Jupyter)

```bash
conda create -n spoof-detect python=3.10 -y
conda activate spoof-detect
pip install -r requirements.txt
cp .env.example .env
jupyter notebook .#NUM$~_project_setup.ipynb
```

## Про slug датасета на Kaggle

В `config.yaml` в `dataset.kaggle_slug` сейчас стоит один из популярных
зеркал ASVspoof 2019 LA на Kaggle (`awsaf49/asvpoof-2019-dataset`).

## Про зеркало HuggingFace

Если официальный `huggingface.co` недоступен, зеркало включается через
`huggingface.mirror_endpoint` в `config.yaml`.
