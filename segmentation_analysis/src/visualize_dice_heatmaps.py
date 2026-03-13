import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap


HEATMAP_CMAP = LinearSegmentedColormap.from_list(
    "dice_custom",
    ["#0B1675", "#680083", "#BD4F75", "#FEA151", "#FCE833"],
)
HEATMAP_CMAP.set_bad(color="white")


def _build_symmetric_matrix(
    rows: list[dict[str, str]], column: str
) -> tuple[list[str], np.ndarray]:
    rater_label_by_name: dict[str, str] = {}

    for row in rows:
        rater_label_by_name[row["rater_a"]] = row.get("rater_a_label", row["rater_a"])
        rater_label_by_name[row["rater_b"]] = row.get("rater_b_label", row["rater_b"])

    rater_names = sorted(rater_label_by_name)
    rater_labels = [rater_label_by_name[rater_name] for rater_name in rater_names]
    # for rater_name in rater_names:
    #     rater_label = rater_label_by_name[rater_name]
    #     rater_labels.append(label)

    rater_index = {rater_name: index for index, rater_name in enumerate(rater_names)}
    # rater_index = {}
    # for index, rater_name in enumerate(rater_names):
    #     rater_index[rater_index] = index

    matrix = np.full((len(rater_names), len(rater_names)), np.nan, dtype=float)

    for row in rows:
        dice_score_value = float(row[column])
        index_a = rater_index[row["rater_a"]]
        index_b = rater_index[row["rater_b"]]
        matrix[index_a, index_b] = dice_score_value
        matrix[index_b, index_a] = dice_score_value

    return rater_labels, matrix


def _plot_heatmap(
    matrix: np.ndarray,
    rater_labels: list[str],
    title: str,
    output_path: Path,
) -> Path:
    figure, axis = plt.subplots(figsize=(8, 6))
    masked_matrix = np.ma.masked_invalid(matrix)
    image = axis.imshow(masked_matrix, cmap=HEATMAP_CMAP, vmin=0.0, vmax=1.0)
    colorbar = figure.colorbar(image, ax=axis)
    colorbar.set_label("DSC")

    axis.set_xticks(range(len(rater_labels)))
    axis.set_yticks(range(len(rater_labels)))
    axis.set_xticklabels(rater_labels, rotation=45, ha="right")
    axis.set_yticklabels(rater_labels)
    axis.set_title(title)

    for row_index in range(matrix.shape[0]):
        for column_index in range(matrix.shape[1]):
            dice_score_value = matrix[row_index, column_index]
            if np.isnan(dice_score_value):
                continue
            axis.text(
                column_index,
                row_index,
                f"{dice_score_value:.2f}",
                ha="center",
                va="center",
                color="white" if dice_score_value < 0.65 else "black",
                fontsize=8,
            )

    figure.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(figure)

    return output_path


def create_mean_dice_heatmap(
    csv_path: str = "/home/sophieschouten/Internship/MOIS_SAM2_NF/segmentation_analysis/results/mean_dice_scores.csv",
    output_path: str = "/home/sophieschouten/Internship/MOIS_SAM2_NF/segmentation_analysis/results/dice_heatmaps/mean_dice_heatmap.png",
) -> Path:
    source_path = Path(csv_path)

    with source_path.open("r", encoding="utf-8", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))

    rater_labels, matrix = _build_symmetric_matrix(rows, "mean_dice_score")
    mean_dice_heatmap_path = _plot_heatmap(
        matrix, rater_labels, "Mean Dice Scores", Path(output_path)
    )

    return mean_dice_heatmap_path


def create_dice_heatmaps_by_pat(
    csv_path: str = "/home/sophieschouten/Internship/MOIS_SAM2_NF/segmentation_analysis/results/dice_scores.csv",
    output_dir: str = "/home/sophieschouten/Internship/MOIS_SAM2_NF/segmentation_analysis/results/dice_heatmaps",
) -> list[Path]:
    source_path = Path(csv_path)

    with source_path.open("r", encoding="utf-8", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))

    rows_by_file: dict[str, list[dict[str, str]]] = {}
    # ext_dict: "pat_file"
    # int_dict: list[pat_file_rows]
    #
    # rows_by_file:{
    #     "pat_file_1"[
    #         {
    #             "pat_file_1_1":   str,
    #             "rater_a_1_1":    str,
    #             "rater_b_1_1":    str,
    #             "dice_score_1_1": str,
    #         }
    #         {
    #             "pat_file_1_2":   str,
    #             "rater_a_1_2":    str,
    #             ...
    #         }
    #     ]
    # }

    # for row in rows:
    #     rows_by_file.setdefault(row["pat_file"], []).append(row)
    for row in rows:
        pat_file = row["pat_file"]

        if not pat_file in rows_by_file:
            rows_by_file[pat_file] = []

        rows_by_file[pat_file].append(row)

    output_paths: list[Path] = []

    for pat_file, file_rows in sorted(rows_by_file.items()):
        rater_labels, matrix = _build_symmetric_matrix(file_rows, "dice_score")
        pat_label = file_rows[0].get("pat_label", pat_file)
        output_path = Path(output_dir) / f"{pat_label}_heatmap.png"
        heatmap_path = _plot_heatmap(
            matrix, rater_labels, f"Dice Scores: {pat_label}", output_path
        )
        output_paths.append(heatmap_path)

    return output_paths


def print_heatmap_summary() -> None:
    mean_heatmap_path = create_mean_dice_heatmap()
    per_file_paths = create_dice_heatmaps_by_pat()

    print(f"Mean heatmap saved: {mean_heatmap_path}")

    for path in per_file_paths:
        print(f"File heatmap saved: {path}")


if __name__ == "__main__":
    print_heatmap_summary()
