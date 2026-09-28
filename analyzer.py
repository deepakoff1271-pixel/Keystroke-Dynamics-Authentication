"""Analysis routines for the keystroke dynamics project."""

from __future__ import annotations

import numpy as np
from sklearn.manifold import TSNE
from sklearn.neighbors import KNeighborsClassifier

from data_processor import PASSWORDS, load_data


def _corrcoef(x: np.ndarray, y: np.ndarray) -> float:
    x_centered = x - np.mean(x)
    y_centered = y - np.mean(y)
    denominator = np.sqrt(np.sum(x_centered**2) * np.sum(y_centered**2))
    if denominator <= 0:
        return 0.0
    return float(np.sum(x_centered * y_centered) / denominator)


def compute_variance_analysis(password_name: str) -> dict[str, float]:
    defence_data, attack_data, _ = load_data(password_name)
    results: dict[str, float] = {}

    for participant_id, rows in defence_data.items():
        results[f"Participant {participant_id}"] = round(float(np.mean(np.std(rows, axis=0))), 4)

    results["Attack"] = round(float(np.mean(np.std(attack_data, axis=0))), 4)
    participant_values = [value for key, value in results.items() if key != "Attack"]
    results["Average"] = round(float(np.mean(participant_values)), 4)
    return results


def compute_correlation_analysis(password_name: str) -> dict[str, dict[str, float]]:
    defence_data, attack_data, _ = load_data(password_name)
    rng = np.random.default_rng(sum(ord(char) for char in password_name))

    datasets = {f"Participant {participant_id}": rows for participant_id, rows in defence_data.items()}
    datasets["Attack"] = attack_data
    labels = list(datasets.keys())

    matrix: dict[str, dict[str, float]] = {}
    for left_label in labels:
        matrix[left_label] = {}
        left_rows = datasets[left_label]
        left_indices = rng.choice(len(left_rows), min(30, len(left_rows)), replace=False)

        for right_label in labels:
            right_rows = datasets[right_label]
            right_indices = rng.choice(len(right_rows), min(30, len(right_rows)), replace=False)
            correlations: list[float] = []
            for left_index in left_indices:
                for right_index in right_indices:
                    if left_label == right_label and left_index == right_index:
                        continue
                    correlations.append(_corrcoef(left_rows[left_index], right_rows[right_index]))
            matrix[left_label][right_label] = round(float(np.mean(correlations)) if correlations else 0.0, 3)

    return matrix


def run_knn_fast(password_name: str, k: int = 3) -> dict[str, dict[str, float]]:
    defence_data, attack_data, _ = load_data(password_name)
    ordered_participants = sorted(defence_data.items())

    train_rows = []
    train_labels = []
    participant_offsets: dict[int, tuple[int, int]] = {}
    cursor = 0
    for participant_id, rows in ordered_participants:
        participant_offsets[participant_id] = (cursor, len(rows))
        for row in rows:
            train_rows.append(row)
            train_labels.append(participant_id)
        cursor += len(rows)
    for row in attack_data:
        train_rows.append(row)
        train_labels.append(0)

    train_rows = np.asarray(train_rows)
    train_labels = np.asarray(train_labels)
    results: dict[str, dict[str, float]] = {}

    for participant_id, rows in ordered_participants:
        start_index, participant_size = participant_offsets[participant_id]
        sample_size = min(40, participant_size)
        sample_indices = np.random.default_rng(participant_id).choice(participant_size, sample_size, replace=False)

        correct = 0
        for sample_index in sample_indices:
            holdout_index = start_index + sample_index
            mask = np.ones(len(train_rows), dtype=bool)
            mask[holdout_index] = False
            model = KNeighborsClassifier(n_neighbors=k, metric="manhattan")
            model.fit(train_rows[mask], train_labels[mask])
            prediction = model.predict(rows[sample_index : sample_index + 1])[0]
            if prediction == participant_id:
                correct += 1

        tar = correct / sample_size
        frr = 1 - tar

        model = KNeighborsClassifier(n_neighbors=k, metric="manhattan")
        model.fit(train_rows, train_labels)
        attack_predictions = model.predict(attack_data)
        false_accepts = int(np.sum(attack_predictions == participant_id))
        trr = (len(attack_data) - false_accepts) / len(attack_data)
        far = false_accepts / len(attack_data)

        results[f"Participant {participant_id}"] = {
            "TAR": round(float(tar), 3),
            "FRR": round(float(frr), 3),
            "TRR": round(float(trr), 3),
            "FAR": round(float(far), 3),
        }

    return results


def compute_correlation_kda(password_name: str) -> dict[str, dict[str, float]]:
    defence_data, attack_data, _ = load_data(password_name)
    rng = np.random.default_rng(sum(ord(char) for char in password_name) + 11)
    results: dict[str, dict[str, float]] = {}

    for participant_id, rows in sorted(defence_data.items()):
        sample_size = min(40, len(rows))
        sample_indices = rng.choice(len(rows), sample_size, replace=False)

        self_scores: list[float] = []
        for sample_index in sample_indices:
            comparisons = [
                _corrcoef(rows[sample_index], other_row)
                for other_index, other_row in enumerate(rows)
                if other_index != sample_index
            ]
            self_scores.append(float(np.mean(comparisons)) if comparisons else 0.0)

        attack_scores: list[float] = []
        attack_sample = attack_data[rng.choice(len(attack_data), min(80, len(attack_data)), replace=False)]
        defense_sample = rows[rng.choice(len(rows), min(40, len(rows)), replace=False)]
        for attack_row in attack_sample:
            attack_scores.append(float(np.mean([_corrcoef(attack_row, defense_row) for defense_row in defense_sample])))

        self_scores_array = np.asarray(self_scores)
        attack_scores_array = np.asarray(attack_scores)
        combined_scores = np.concatenate([self_scores_array, attack_scores_array])
        thresholds = np.linspace(float(np.min(combined_scores)), float(np.max(combined_scores)), 250)

        best_error = 1.0
        best_threshold = float(np.mean(combined_scores))
        eer_frr = 1.0
        eer_far = 1.0
        fr0 = 1.0
        best_gap = float("inf")
        for threshold in thresholds:
            frr = float(np.mean(self_scores_array < threshold))
            far = float(np.mean(attack_scores_array >= threshold))
            gap = abs(frr - far)
            if gap < best_gap:
                best_gap = gap
                best_error = (frr + far) / 2
                best_threshold = float(threshold)
                eer_frr = frr
                eer_far = far
            if far <= 0.005:
                fr0 = frr
                break

        results[f"Participant {participant_id}"] = {
            "self_correlation": round(float(np.mean(self_scores_array)), 3),
            "attack_correlation": round(float(np.mean(attack_scores_array)), 3),
            "EER": round(float(best_error) * 100, 1),
            "EER_threshold": round(best_threshold, 3),
            "EER_FRR": round(float(eer_frr) * 100, 1),
            "EER_FAR": round(float(eer_far) * 100, 1),
            "FRR_at_FAR0": round(float(fr0) * 100, 1),
        }

    return results


def compute_tsne(password_name: str, perplexity: int = 30) -> list[dict[str, float | str]]:
    defence_data, attack_data, _ = load_data(password_name)
    points: list[np.ndarray] = []
    labels: list[str] = []
    colors: list[str] = []

    palette = {
        1: "#ffb86b",
        2: "#2dd4bf",
        3: "#7dd3fc",
        4: "#f9a8d4",
        5: "#fca5a5",
    }

    rng = np.random.default_rng(sum(ord(char) for char in password_name) + 23)
    for participant_id, rows in sorted(defence_data.items()):
        sample_size = min(40, len(rows))
        for index in rng.choice(len(rows), sample_size, replace=False):
            points.append(rows[index])
            labels.append(f"Participant {participant_id}")
            colors.append(palette.get(participant_id, "#cbd5e1"))

    attack_sample = attack_data[rng.choice(len(attack_data), min(100, len(attack_data)), replace=False)]
    for row in attack_sample:
        points.append(row)
        labels.append("Attack")
        colors.append("#cbd5e1")

    points_array = np.asarray(points)
    if len(points_array) < 3:
        return []

    safe_perplexity = max(2, min(perplexity, len(points_array) - 1))
    reducer = TSNE(
        n_components=2,
        perplexity=safe_perplexity,
        random_state=42,
        init="pca",
        learning_rate="auto",
        max_iter=1000,
    )
    coordinates = reducer.fit_transform(points_array)

    return [
        {"x": float(x_coord), "y": float(y_coord), "label": label, "color": color}
        for (x_coord, y_coord), label, color in zip(coordinates, labels, colors, strict=False)
    ]


def get_all_analysis(password_name: str) -> dict[str, object]:
    return {
        "password": password_name,
        "password_info": PASSWORDS.get(password_name, {}),
        "variance": compute_variance_analysis(password_name),
        "correlation": compute_correlation_analysis(password_name),
        "knn": run_knn_fast(password_name),
        "correlation_kda": compute_correlation_kda(password_name),
    }
