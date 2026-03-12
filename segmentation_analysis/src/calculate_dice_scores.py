import csv
from itertools import combinations
from pathlib import Path

import numpy as np

from src.display_names import get_display_pat_file_name, get_display_rater_name
from src.unify_masks import normalize_masks_to_binary


def calculate_dice_score(mask_a: np.ndarray, mask_b: np.ndarray) -> float:
    """
    This is my function for dice score calculation definition.
    """
    if mask_a.shape != mask_b.shape:
        raise ValueError(
            f"Dice can only be computed for masks with the same shape: {mask_a.shape} != {mask_b.shape}"
        )

    foreground_a = int(mask_a.sum())
    foreground_b = int(mask_b.sum())

    if foreground_a == 0 and foreground_b == 0:
        return 1.0

    intersection = int(np.logical_and(mask_a, mask_b).sum())
    return (2.0 * intersection) / (foreground_a + foreground_b)


def calculate_dice_scores_by_pat_files(
    base_dir: str = "/home/sophieschouten/Internship/MOIS_SAM2_NF/segmentation_analysis/data/segmentations_from_radiologists",
) -> dict[str, list[dict[str, object]]]:
    """
    This is my function for calculating dice scores for each patient and rater pair.
    """
    binary_masks_by_file = normalize_masks_to_binary(base_dir)

    dice_scores_by_file: dict[str, list[dict[str, object]]] = {}

    # ext_dict:
    # dice_scores_by_file: dict[str, list[by_rater_pair]] = {}
    #     key:    pat_file: str
    #     value:  list[by_rater_pair]
    #
    # int_dict:
    # list[by_rater_pair]: dict[str, object] = {
    #     "rater_a":    str,
    #     "rater_b":    str,
    #     "dice_score": float,
    # }

    for pat_file, masks_by_rater in sorted(binary_masks_by_file.items()):
        dice_scores_by_file[pat_file] = []

        for rater_a, rater_b in combinations(sorted(masks_by_rater), 2):
            mask_a = masks_by_rater[rater_a]
            mask_b = masks_by_rater[rater_b]
            dice_score = calculate_dice_score(mask_a, mask_b)

            dice_scores_by_file[pat_file].append(
                {
                    "rater_a": rater_a,
                    "rater_b": rater_b,
                    "dice_score": dice_score,
                }
            )

    return dice_scores_by_file


def print_dice_score_report(
    base_dir: str = "/home/sophieschouten/Internship/MOIS_SAM2_NF/segmentation_analysis/data/segmentations_from_radiologists",
) -> None:
    dice_scores_by_pat_file = calculate_dice_scores_by_pat_files(base_dir)

    for pat_file, file_results in dice_scores_by_pat_file.items():
        print(f"\n{pat_file}")

        for result in file_results:
            print(
                f"  {result['rater_a']} vs {result['rater_b']}: DSC={result['dice_score']:.4f}"
            )


def save_dice_scores_to_csv(
    base_dir: str = "/home/sophieschouten/Internship/MOIS_SAM2_NF/segmentation_analysis/data/segmentations_from_radiologists",
    output_path: str = "/home/sophieschouten/Internship/MOIS_SAM2_NF/segmentation_analysis/results/dice_scores.csv",
) -> Path:
    """
    This is my function for saving dice scores to csv file.
    """
    dice_scores_by_pat_file = calculate_dice_scores_by_pat_files(base_dir)
    csv_path = Path(output_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                "pat_file",
                "pat_label",
                "rater_a",
                "rater_a_label",
                "rater_b",
                "rater_b_label",
                "dice_score",
            ]
        )

        for pat_file, calculation_results in dice_scores_by_pat_file.items():
            for result in calculation_results:
                writer.writerow(
                    [
                        pat_file,
                        get_display_pat_file_name(pat_file),
                        result["rater_a"],
                        get_display_rater_name(result["rater_a"]),
                        result["rater_b"],
                        get_display_rater_name(result["rater_b"]),
                        f"{result['dice_score']:.6f}",
                    ]
                )

    return csv_path


if __name__ == "__main__":
    # print_dice_score_report()
    save_dice_scores_to_csv()
