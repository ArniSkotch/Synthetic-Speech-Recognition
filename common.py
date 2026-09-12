"""
src/common.py

Общие утилиты, переиспользуемые во всех ноутбуках-пайплайнах проекта
(01_project_setup, 02_eda, 03_baseline_lfcc_cqcc_gmm и последующие).

Вынесено сюда, чтобы не дублировать одинаковый boilerplate-код
(загрузка конфига, индексация аудио на диске, расчёт EER, сохранение
результатов для итогового сравнения пайплайнов) в каждом новом ноутбуке.

Использование в ноутбуке (запускается из корня проекта):

    import sys
    sys.path.append("..")  # если ноутбук лежит в notebooks/, иначе не нужно
    from src.common import load_config, load_protocol_with_paths, compute_eer, save_pipeline_results
"""

import os
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from dotenv import load_dotenv
from sklearn.metrics import roc_curve


AUDIO_EXTENSIONS = {".flac", ".wav", ".ogg", ".mp3"}


def load_config(config_path: str = "config.yaml", env_path: str = ".env") -> dict:
    """Загружает .env (секреты) и config.yaml (константы проекта), возвращает dict конфига."""
    load_dotenv(dotenv_path=env_path)
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


def ensure_project_dirs(config: dict) -> None:
    """Создаёт все папки, перечисленные в config['paths'], если их ещё нет."""
    for value in config["paths"].values():
        Path(value).mkdir(parents=True, exist_ok=True)


def build_audio_index(root: Path) -> dict:
    """Индексирует все аудиофайлы под root: {имя_без_расширения: полный_путь}.

    Один проход по дереву каталогов (os.walk) — устойчиво к любой структуре
    подпапок, которую использует конкретное зеркало датасета.
    """
    root = Path(root)
    index = {}
    if not root.exists():
        return index
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            stem, ext = os.path.splitext(name)
            if ext.lower() in AUDIO_EXTENSIONS:
                index[stem] = Path(dirpath) / name
    return index


def load_protocol_with_paths(config: dict) -> pd.DataFrame:
    """Загружает сводную таблицу протокола (созданную в 02_eda.ipynb) и
    восстанавливает столбец full_path через индексацию data/raw.

    Бросает FileNotFoundError с понятным сообщением, если 02_eda.ipynb ещё
    не запускался — таблица протокола является общим "контрактом" между
    ноутбуками: все пайплайны читают разметку из одного места.
    """
    protocol_path = Path(config["eda"]["protocol_table_path"])
    if not protocol_path.exists():
        raise FileNotFoundError(
            f"Не найден {protocol_path}. Сначала запустите 02_eda.ipynb — "
            "он строит сводную таблицу протокола, которую переиспользуют "
            "все последующие пайплайны."
        )

    df = pd.read_csv(protocol_path)
    audio_index = build_audio_index(config["paths"]["raw_dir"])
    df["full_path"] = df["filename"].map(audio_index)

    missing = df["full_path"].isna().sum()
    if missing:
        print(f"[load_protocol_with_paths] Внимание: {missing} из {len(df)} файлов не найдено на диске.")

    return df


def compute_eer(bonafide_scores: np.ndarray, spoof_scores: np.ndarray):
    """Equal Error Rate: точка на ROC-кривой, где FAR (False Acceptance Rate)
    приблизительно равен FRR/FNR (False Rejection Rate).

    Больший score должен означать «более похоже на bonafide».
    Возвращает (eer, порог_на_котором_достигается_eer).
    """
    y_true = np.concatenate([np.ones(len(bonafide_scores)), np.zeros(len(spoof_scores))])
    y_score = np.concatenate([bonafide_scores, spoof_scores])

    far, tpr, thresholds = roc_curve(y_true, y_score)
    frr = 1 - tpr  # False Rejection Rate = False Negative Rate

    idx = np.nanargmin(np.abs(frr - far))
    eer = float((frr[idx] + far[idx]) / 2)
    threshold = float(thresholds[idx])
    return eer, threshold


def save_pipeline_results(name: str, metrics: dict, config: dict) -> Path:
    """Сохраняет метрики пайплайна в единый results_dir/<name>.json.

    Единый формат и общая папка позволяют финальному ноутбуку сравнения
    (04_compare_pipelines.ipynb и далее) просто собрать все *.json из
    results_dir и построить сводную таблицу/график, не трогая код
    отдельных пайплайнов.
    """
    results_dir = Path(config["paths"]["results_dir"])
    results_dir.mkdir(parents=True, exist_ok=True)

    payload = {"pipeline": name, **metrics}
    out_path = results_dir / f"{name}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)

    print(f"Результаты пайплайна '{name}' сохранены: {out_path}")
    return out_path


def load_all_pipeline_results(config: dict) -> pd.DataFrame:
    """Собирает все results_dir/*.json в единый DataFrame — используется в
    итоговом ноутбуке сравнения пайплайнов.
    """
    results_dir = Path(config["paths"]["results_dir"])
    rows = []
    if results_dir.exists():
        for path in sorted(results_dir.glob("*.json")):
            with open(path, "r", encoding="utf-8") as f:
                rows.append(json.load(f))
    return pd.DataFrame(rows)
