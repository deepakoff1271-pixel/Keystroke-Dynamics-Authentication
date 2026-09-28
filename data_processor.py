"""Data generation, loading, and feature extraction for the KDA project."""

from __future__ import annotations

import os
from typing import Iterable

import numpy as np
import pandas as pd

PASSWORDS = {
    "observer": {"keystrokes": 8, "dimensions": 25, "entropy": 37},
    "Ob$erv3r": {"keystrokes": 11, "dimensions": 34, "entropy": 49},
    "gigabit receiver": {"keystrokes": 16, "dimensions": 49, "entropy": 75},
    "Gigab!t R3ceiver": {"keystrokes": 19, "dimensions": 58, "entropy": 98},
    "flying automatic monster": {"keystrokes": 24, "dimensions": 73, "entropy": 112},
    "repetition learn machine thinker": {"keystrokes": 32, "dimensions": 97, "entropy": 150},
}

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def _safe_name(password: str) -> str:
    return (
        password.replace(" ", "_")
        .replace("$", "S")
        .replace("!", "I")
        .replace("/", "_")
    )


def _feature_columns(num_keys: int) -> list[str]:
    columns = ["participant", "entry"]
    for key_index in range(num_keys):
        columns.extend([f"PP_{key_index + 1}", f"RP_{key_index + 1}", f"HT_{key_index + 1}"])
    columns.append("HT_enter")
    return columns


def extract_metrics(raw_events: list[dict]) -> list[float] | None:
    """Convert raw key events into the fixed-text feature vector used by the app."""
    key_events = [event for event in raw_events if event.get("key") and event.get("type") in {"keydown", "keyup"}]
    presses = [event for event in key_events if event["type"] == "keydown"]
    releases = [event for event in key_events if event["type"] == "keyup"]

    if len(presses) != len(releases) or not presses:
        return None

    metrics: list[float] = []
    for index in range(len(presses)):
        press_time = float(presses[index]["timestamp"])
        release_time = float(releases[index]["timestamp"])
        hold_time = max(release_time - press_time, 0.0)
        press_to_press = 0.0 if index == 0 else max(press_time - float(presses[index - 1]["timestamp"]), 0.0)
        release_to_press = 0.0 if index == 0 else press_time - float(releases[index - 1]["timestamp"])
        metrics.extend([press_to_press, release_to_press, hold_time])

    metrics.append(float(metrics[-1]))
    return metrics


def generate_typing_profile(num_keys: int, typing_speed_keys_per_sec: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    avg_interval = 1000.0 / typing_speed_keys_per_sec
    base_pp = np.random.normal(avg_interval, avg_interval * 0.15, num_keys)
    base_pp = np.maximum(base_pp, 30)
    base_pp[0] = 0

    base_ht = np.random.normal(90, 25, num_keys)
    base_ht = np.clip(base_ht, 40, 200)

    base_rp = np.zeros(num_keys)
    for index in range(1, num_keys):
        base_rp[index] = base_pp[index] - base_ht[index - 1]

    return base_pp, base_rp, base_ht


def generate_entry(base_pp: np.ndarray, base_rp: np.ndarray, base_ht: np.ndarray, noise_level: float = 0.05) -> list[float]:
    num_keys = len(base_pp)
    pp = base_pp + np.random.normal(0, np.maximum(np.abs(base_pp) * noise_level, 3), num_keys)
    rp = base_rp + np.random.normal(0, np.maximum(np.abs(base_rp) * noise_level + 2, 3), num_keys)
    ht = base_ht + np.random.normal(0, np.maximum(base_ht * noise_level, 2), num_keys)

    pp[0] = 0
    rp[0] = 0
    ht = np.maximum(ht, 20)

    features: list[float] = []
    for index in range(num_keys):
        features.extend([float(pp[index]), float(rp[index]), float(ht[index])])
    features.append(float(np.random.normal(100, 20)))
    return features


def generate_synthetic_data() -> bool:
    os.makedirs(DATA_DIR, exist_ok=True)

    defence_speeds = [10.0, 5.0, 8.0, 3.5, 3.7]
    defence_noise = [0.03, 0.06, 0.05, 0.09, 0.10]

    for password_name, password_info in PASSWORDS.items():
        num_keys = password_info["keystrokes"]
        dimensions = password_info["dimensions"]
        columns = _feature_columns(num_keys)
        safe = _safe_name(password_name)

        defence_rows: list[list[float]] = []
        for participant_index in range(5):
            base_pp, base_rp, base_ht = generate_typing_profile(num_keys, defence_speeds[participant_index])
            for entry_index in range(200):
                features = generate_entry(base_pp, base_rp, base_ht, noise_level=defence_noise[participant_index])
                defence_rows.append([participant_index + 1, entry_index + 1] + features[:dimensions])
        pd.DataFrame(defence_rows, columns=columns).to_csv(
            os.path.join(DATA_DIR, f"defence_{safe}.csv"), index=False
        )

        attack_rows: list[list[float]] = []
        for attacker_index in range(33):
            typing_speed = np.random.uniform(2.0, 7.0)
            noise_level = np.random.uniform(0.08, 0.18)
            base_pp, base_rp, base_ht = generate_typing_profile(num_keys, typing_speed)
            for entry_index in range(10):
                features = generate_entry(base_pp, base_rp, base_ht, noise_level=noise_level)
                attack_rows.append([attacker_index + 1, entry_index + 1] + features[:dimensions])
        pd.DataFrame(attack_rows, columns=columns).to_csv(
            os.path.join(DATA_DIR, f"attack_{safe}.csv"), index=False
        )

    return True


def _candidate_paths(prefix: str, safe: str) -> list[str]:
    return [
        os.path.join(DATA_DIR, f"collected_{prefix}_{safe}.csv"),
        os.path.join(DATA_DIR, f"{prefix}_{safe}.csv"),
    ]


def _load_first_existing(paths: Iterable[str]) -> pd.DataFrame | None:
    for path in paths:
        if os.path.exists(path):
            return pd.read_csv(path)
    return None


def load_data(password_name: str) -> tuple[dict[int, np.ndarray], np.ndarray, list[str]]:
    safe = _safe_name(password_name)
    defence_df = _load_first_existing(_candidate_paths("defence", safe))
    attack_df = _load_first_existing(_candidate_paths("attack", safe))

    if defence_df is None or attack_df is None:
        generate_synthetic_data()
        defence_df = _load_first_existing(_candidate_paths("defence", safe))
        attack_df = _load_first_existing(_candidate_paths("attack", safe))

    if defence_df is None or attack_df is None:
        raise FileNotFoundError(f"No dataset found for password '{password_name}'")

    feature_cols = [column for column in defence_df.columns if column not in {"participant", "entry"}]

    defence_data: dict[int, np.ndarray] = {}
    for participant_id in sorted(defence_df["participant"].unique()):
        participant_rows = defence_df[defence_df["participant"] == participant_id]
        numeric_id = pd.to_numeric(pd.Series([participant_id]), errors="coerce").fillna(0).astype(int).iloc[0]
        defence_data[int(numeric_id)] = participant_rows[feature_cols].values

    attack_data = attack_df[feature_cols].values
    return defence_data, attack_data, feature_cols


def _normalize_metrics(metrics: list[float], expected_length: int) -> list[float]:
    cleaned = [float(value) for value in metrics]
    if len(cleaned) < expected_length:
        cleaned.extend([0.0] * (expected_length - len(cleaned)))
    return cleaned[:expected_length]


def save_collected_keystrokes(password: str, participant_id: str | int, session_type: str, metrics_list: list) -> bool:
    os.makedirs(DATA_DIR, exist_ok=True)

    password_info = PASSWORDS.get(password)
    if not password_info:
        return False

    safe = _safe_name(password)
    filename = f"collected_{session_type}_{safe}.csv"
    filepath = os.path.join(DATA_DIR, filename)

    columns = _feature_columns(password_info["keystrokes"])
    rows: list[list[float | str]] = []
    for entry_index, metrics in enumerate(metrics_list):
        metrics_vector = metrics
        if isinstance(metrics_vector, dict):
            metrics_vector = list(metrics_vector.values())
        row = [participant_id, entry_index + 1] + _normalize_metrics(list(metrics_vector), len(columns) - 2)
        rows.append(row)

    new_frame = pd.DataFrame(rows, columns=columns)
    if os.path.exists(filepath):
        existing_frame = pd.read_csv(filepath)
        new_frame = pd.concat([existing_frame, new_frame], ignore_index=True)
    new_frame.to_csv(filepath, index=False)
    return True


if __name__ == "__main__":
    generate_synthetic_data()
