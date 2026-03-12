import csv
from collections import defaultdict
from pathlib import Path

import numpy as np

from src.calculate_dice_scores import calculate_dice_scores_by_pat_files
from src.display_names import get_display_rater_name


def calculate_mean_dice_scores_by_pairs(
    base_dir: str = "/home/sophieschouten/Internship/MOIS_SAM2_NF/segmentation_analysis/data/segmentations_from_radiologists",
) -> list[dict[str, object]]:
    """
    This is my function for calculating mean dice scores for each rater pair.
    """
    dice_scores_by_file = calculate_dice_scores_by_pat_files(base_dir)

    scores_by_rater_pair: dict[tuple[str, str], list[float]] = defaultdict(list)

    # rater_pair: tuple[str, str]
    # dice_score: list[float]
    #
    # scores_by_rater_pair: dict[
    #     tuple[str, str],
    #     list[float]
    # ] = defaultdict(list)

    for file_results in dice_scores_by_file.values():
        for result in file_results:
            rater_pair = (result["rater_a"], result["rater_b"])
            scores_by_rater_pair[rater_pair].append(result["dice_score"])

    mean_dice_scores: list[dict[str, object]] = []

    # per_rater_pair: dict[str, object] = {
    #    "rater_a":         str,
    #    "rater_b":         str,
    #    "mean_dice_score": float,
    #    "num_files":       int,
    # }
    # mean_dice_scores: list[
    #     per_rater_pair
    # ] = []

    for rater_pair, dice_scores in sorted(scores_by_rater_pair.items()):
        mean_dice_scores.append(
            {
                "rater_a": rater_pair[0],
                "rater_b": rater_pair[1],
                "mean_dice_score": float(np.mean(dice_scores)),
                "num_files": len(dice_scores),
            }
        )

    return mean_dice_scores


def print_mean_dice_score_report(
    base_dir: str = "/home/sophieschouten/Internship/MOIS_SAM2_NF/segmentation_analysis/data/segmentations_from_radiologists",
) -> None:
    mean_dice_scores = calculate_mean_dice_scores_by_pairs(base_dir)

    for result in mean_dice_scores:
        print(
            f"{result['rater_a']} vs {result['rater_b']}: "
            f"mean DSC={result['mean_dice_score']:.4f} "
            f"from {result['num_files']} files"
        )


def save_mean_dice_scores_to_csv(
    base_dir: str = "/home/sophieschouten/Internship/MOIS_SAM2_NF/segmentation_analysis/data/segmentations_from_radiologists",
    output_path: str = "/home/sophieschouten/Internship/MOIS_SAM2_NF/segmentation_analysis/results/mean_dice_scores.csv",
) -> Path:
    mean_dice_scores = calculate_mean_dice_scores_by_pairs(base_dir)
    csv_path = Path(output_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                "rater_a",
                "rater_a_label",
                "rater_b",
                "rater_b_label",
                "mean_dice_score",
                "num_files",
            ]
        )

        for result in mean_dice_scores:
            writer.writerow(
                [
                    result["rater_a"],
                    get_display_rater_name(result["rater_a"]),
                    result["rater_b"],
                    get_display_rater_name(result["rater_b"]),
                    f"{result['mean_dice_score']:.6f}",
                    result["num_files"],
                ]
            )

    return csv_path


if __name__ == "__main__":
    print_mean_dice_score_report()
    save_mean_dice_scores_to_csv()
