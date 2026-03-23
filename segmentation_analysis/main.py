from src.calculate_dice_scores import (
    calculate_dice_scores_by_pat_files,
    save_dice_scores_by_pat_to_csv,
)
from src.calculate_mean_dice_scores import (
    calculate_mean_dice_scores_by_pairs,
    save_mean_dice_scores_to_csv,
)
from src.compare_mask_shapes import compare_mask_shapes
from src.create_overlay_masks import save_overlay_masks
from src.load_masks import load_and_unify_masks
from src.paths import (
    DICE_HEATMAPS_BY_PAT_DIR,
    PATIENTS_FOR_ANNOTATION_DIR,
    SEGMENTATION_BASE_DIR,
    OVERLAY_MASKS_DIR,
)
from src.visualize_dice_heatmaps import (
    create_mean_dice_heatmap,
    create_dice_heatmaps_by_pat,
)


if __name__ == "__main__":
    print("1/8 Load and unify masks")
    shapes_by_file, binary_mask_arrays_by_file = load_and_unify_masks(
        SEGMENTATION_BASE_DIR
    )

    print("2/8 Compare matching file shapes")
    all_shapes_equal = compare_mask_shapes(shapes_by_file)
    if not all_shapes_equal:
        raise ValueError("Masks come in different shapes – Pipeline aborted.")
    print(f"   All shapes equal: {all_shapes_equal}")

    print("3/8 Calculate dice scores by patient")
    dice_scores_by_file = calculate_dice_scores_by_pat_files(
        binary_mask_arrays_by_file=binary_mask_arrays_by_file
    )

    print("4/8 Save dice scores by patient to CSV")
    dice_csv_path = save_dice_scores_by_pat_to_csv(
        dice_scores_by_file=dice_scores_by_file
    )
    print(f"   Dice Scores by patient CSV saved: {dice_csv_path}")

    print("5/8 Calculate mean dice scores by rater pairs")
    mean_dice_scores = calculate_mean_dice_scores_by_pairs(
        dice_scores_by_file=dice_scores_by_file
    )

    print("6/8 Save mean dice scores by rater pairs to CSV")
    mean_dice_csv_path = save_mean_dice_scores_to_csv(mean_dice_scores=mean_dice_scores)
    print(f"   Mean Dice Scores CSV saved: {mean_dice_csv_path}")

    print("7/8  Create heatmaps")
    # mean_dice_heatmap_path = create_mean_dice_heatmap(
    #     mean_dice_scores=mean_dice_scores
    # )
    dice_heatmap_paths_by_pat = create_dice_heatmaps_by_pat(
        dice_scores_by_file=dice_scores_by_file
    )
    # print(f"   Mean heatmap saved: {mean_dice_heatmap_path}")
    print(
        f"   Heatmaps by patient saved: {len(dice_heatmap_paths_by_pat)} in {DICE_HEATMAPS_BY_PAT_DIR}"
    )

    print("8/8 Create overlay masks")
    saved_overlays = save_overlay_masks(
        binary_mask_arrays_by_file=binary_mask_arrays_by_file,
        mri_base_dir=PATIENTS_FOR_ANNOTATION_DIR,
    )
    print(f"   Overlays saved: {len(saved_overlays)} in {OVERLAY_MASKS_DIR}")

    print("Workflow completed")
