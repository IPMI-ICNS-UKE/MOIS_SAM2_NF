from pathlib import Path


SEGMENTATION_ANALYSIS_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = SEGMENTATION_ANALYSIS_DIR / "data"
RESULTS_DIR = SEGMENTATION_ANALYSIS_DIR / "results"

SEGMENTATION_BASE_DIR = DATA_DIR / "segmentations_from_radiologists"
PATIENTS_FOR_ANNOTATION_DIR = DATA_DIR / "patients_for_annotation"

DICE_SCORES_CSV = RESULTS_DIR / "dice_scores.csv"
MEAN_DICE_SCORES_CSV = RESULTS_DIR / "mean_dice_scores.csv"
DICE_HEATMAPS_DIR = RESULTS_DIR / "dice_heatmaps"
DICE_MEAN_HEATMAP_PATH = DICE_HEATMAPS_DIR / "mean_dice_heatmap.png"
DICE_HEATMAPS_BY_PAT_DIR = DICE_HEATMAPS_DIR / "heatmaps_by_pat"
OVERLAY_MASKS_DIR = RESULTS_DIR / "overlay_masks"
OVERLAY_INDEX_CSV = RESULTS_DIR / "overlay_masks.csv"
