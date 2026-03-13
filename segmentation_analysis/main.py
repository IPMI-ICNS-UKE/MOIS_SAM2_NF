from src.calculate_dice_scores import save_dice_scores_to_csv
from src.calculate_mean_dice_scores import save_mean_dice_scores_to_csv
from src.compare_mask_shapes import compare_mask_shapes
from src.create_overlay_masks import save_overlay_masks
from src.load_masks import load_mask_shapes
from src.unify_masks import unify_masks_to_binary
from src.visualize_dice_heatmaps import (
    create_mean_dice_heatmap,
    create_dice_heatmaps_by_pat,
)


if __name__ == "__main__":
    print("1/7 Load mask shapes")
    load_mask_shapes()

    print("2/7 Compare matching file shapes")
    shape_comparison_results = compare_mask_shapes()
    all_shapes_equal = all(
        result["all_shapes_equal"] for result in shape_comparison_results.values()
    )
    print(f"   All shapes equal: {all_shapes_equal}")

    print("3/7 Normalize masks to binary")
    masks = unify_masks_to_binary()

    print("4/7 Save Dice scores to CSV")
    dice_csv_path = save_dice_scores_to_csv()
    print(f"   CSV saved: {dice_csv_path}")

    print("5/7 Save mean Dice scores to CSV")
    mean_dice_csv_path = save_mean_dice_scores_to_csv()
    print(f"   CSV saved: {mean_dice_csv_path}")

    print("6/7 Create heatmaps")
    create_mean_dice_heatmap()
    create_dice_heatmaps_by_pat()

    print("7/7 Create overlay masks")
    save_overlay_masks()

    print("Workflow completed")
