# Synthetic Speech Detection

Тема: `Исследование методов обнаружения синтезированной речи в задачах голосовой аутентификации`

## Состав

| Файл | Назначение |
|---|---|
| `01_project_setup.ipynb` | Ноутбук инициализации: импорты, проверка версий, конфиг, зеркало HF, загрузка датасета с Kaggle |
| `02_eda.ipynb` | Разведочный анализ: объём данных по train/dev/eval, баланс классов, типы атак, длительности, waveform/MFCC/мел-спектрограммы на примерах. Работает даже без скачанного датасета — автоматически переключается в демо-режим на синтетических данных |
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
