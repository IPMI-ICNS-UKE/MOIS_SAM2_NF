import csv
from collections import defaultdict
from pathlib import Path

import numpy as np

try:
    from .calculate_dice_scores import calculate_dice_scores_by_pat_files
    from .display_names import get_display_rater_name
    from .paths import MEAN_DICE_SCORES_CSV, SEGMENTATION_BASE_DIR
except ImportError:
    from calculate_dice_scores import calculate_dice_scores_by_pat_files
    from display_names import get_display_rater_name
    from paths import MEAN_DICE_SCORES_CSV, SEGMENTATION_BASE_DIR


def calculate_mean_dice_scores_by_pairs(
    dice_scores_by_file: dict[str, list[dict[str, object]]] | None = None,
    binary_mask_arrays_by_file: dict[str, dict[str, np.ndarray]] | None = None,
    base_dir: str | Path = SEGMENTATION_BASE_DIR,
) -> list[dict[str, object]]:
    """
    This is my function for calculating mean dice scores for each rater pair.
    """
    if dice_scores_by_file is None:
        dice_scores_by_file = calculate_dice_scores_by_pat_files(
            binary_mask_arrays_by_file=binary_mask_arrays_by_file,
            base_dir=base_dir,
        )

    scores_by_rater_pair: defaultdict[tuple[str, str], list[float]] = defaultdict(list)

    # rater_pair: tuple[str, str]
    # dice_score: list[float]
    #
    # scores_by_rater_pair: dict[
    #     tuple[str, str],
    #     list[float]
    # ]

    for file_results in dice_scores_by_file.values():
        for result in file_results:
            rater_pair = (result["rater_a"], result["rater_b"])

            # if not rater_pair in scores_by_rater_pair:
            #     scores_by_rater_pair[rater_pair] = []

            scores_by_rater_pair[rater_pair].append(result["dice_score"])

    mean_dice_scores: list[dict[str, object]] = []

    for rater_pair, dice_scores in sorted(scores_by_rater_pair.items()):
        mean_dice_scores.append(
            {
                "rater_a": rater_pair[0],
                "rater_b": rater_pair[1],
                "mean_dice_score": float(np.mean(dice_scores)),
                "num_files": len(dice_scores),
            }
        )
        # per_rater_pair: dict[str, object] = {
        #    "rater_a":         str,
        #    "rater_b":         str,
        #    "mean_dice_score": float,
        #    "num_files":       int,
        # }
        # mean_dice_scores: list[per_rater_pair] = []

    return mean_dice_scores


def print_mean_dice_score_report(
    base_dir: str | Path = SEGMENTATION_BASE_DIR,
) -> None:
    mean_dice_scores = calculate_mean_dice_scores_by_pairs(base_dir=base_dir)

    for result in mean_dice_scores:
        print(
            f"{result['rater_a']} vs {result['rater_b']}: "
            f"mean DSC={result['mean_dice_score']:.4f} "
            f"from {result['num_files']} files"
        )


def save_mean_dice_scores_to_csv(
    mean_dice_scores: list[dict[str, object]],
    output_path: str | Path = MEAN_DICE_SCORES_CSV,
) -> Path:
    mean_dice_csv_path = Path(output_path)
    mean_dice_csv_path.parent.mkdir(parents=True, exist_ok=True)

    with mean_dice_csv_path.open("w", newline="", encoding="utf-8") as csv_file:
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

    return mean_dice_csv_path


if __name__ == "__main__":
    # print_mean_dice_score_report()
    save_mean_dice_scores_to_csv(calculate_mean_dice_scores_by_pairs())
