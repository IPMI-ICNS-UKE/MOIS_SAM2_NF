import csv
from itertools import combinations
from pathlib import Path

import numpy as np
import SimpleITK as sitk

from src.display_names import get_display_pat_file_name, get_display_rater_name


SEGMENTATION_BASE_DIR = "/home/sophieschouten/Internship/MOIS_SAM2_NF/segmentation_analysis/data/segmentations_from_radiologists"
MRI_BASE_DIR = "/home/sophieschouten/Internship/MOIS_SAM2_NF/segmentation_analysis/data/patients_for_annotation"
OVERLAY_OUTPUT_DIR = "/home/sophieschouten/Internship/MOIS_SAM2_NF/segmentation_analysis/results/overlay_masks"
OVERLAY_INDEX_CSV = "/home/sophieschouten/Internship/MOIS_SAM2_NF/segmentation_analysis/results/overlay_masks.csv"


def _load_binary_mask_images(
    base_dir: str = SEGMENTATION_BASE_DIR,
) -> dict[str, dict[str, sitk.Image]]:
    base_path = Path(base_dir)

    if not base_path.exists():
        raise FileNotFoundError(f"Directory not found: {base_path}")

    binary_masks_by_file: dict[str, dict[str, sitk.Image]] = {}

    for rater_dir in sorted(path for path in base_path.iterdir() if path.is_dir()):

        # rater_dirs = []
        # for path in base_path.iterdir():
        #     if path.is_dir():
        #         rater_dirs.append(path)

        # rater_dirs = sorted(rater_dirs)

        # for rater_dir in rater_dirs:

        for pat_file in sorted(rater_dir.glob("*.nii.gz")):
            mask = sitk.ReadImage(str(pat_file))
            mask_array = (sitk.GetArrayFromImage(mask) > 0).astype(np.uint8)
            binary_image = sitk.GetImageFromArray(mask_array)
            binary_image.CopyInformation(mask)
            binary_masks_by_file.setdefault(pat_file.name, {})[
                rater_dir.name
            ] = binary_image

    if not binary_masks_by_file:
        raise FileNotFoundError(f"No .nii.gz files found in: {base_path}")

    return binary_masks_by_file


def find_reference_mri_images(
    mri_base_dir: str = MRI_BASE_DIR,
) -> dict[str, Path]:
    mri_base_path = Path(mri_base_dir)

    if not mri_base_path.exists():
        raise FileNotFoundError(f"Directory not found: {mri_base_path}")

    reference_mri_paths_by_file: dict[str, Path] = {}

    for pat_file in sorted(mri_base_path.rglob("*.nii.gz")):
        if pat_file.name.startswith("segmentation_"):
            continue
        reference_mri_paths_by_file[pat_file.name] = pat_file

    if not reference_mri_paths_by_file:
        raise FileNotFoundError(f"No reference MRI files found in: {mri_base_path}")

    return reference_mri_paths_by_file


def create_overlay_mask(mask_a: np.ndarray, mask_b: np.ndarray) -> np.ndarray:
    if mask_a.shape != mask_b.shape:
        raise ValueError(
            f"Overlay can only be computed for masks with the same shape: {mask_a.shape} != {mask_b.shape}"
        )

    overlay = np.zeros(mask_a.shape, dtype=np.uint8)
    overlay[(mask_a == 1) & (mask_b == 1)] = 1
    overlay[(mask_a == 1) & (mask_b == 0)] = 2
    overlay[(mask_a == 0) & (mask_b == 1)] = 3
    return overlay


def save_overlay_masks(
    segmentation_base_dir: str = SEGMENTATION_BASE_DIR,
    mri_base_dir: str = MRI_BASE_DIR,
    output_dir: str = OVERLAY_OUTPUT_DIR,
    index_csv_path: str = OVERLAY_INDEX_CSV,
) -> list[dict[str, str]]:
    binary_masks_by_file = _load_binary_mask_images(segmentation_base_dir)
    reference_mri_paths_by_file = find_reference_mri_images(mri_base_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    saved_overlays: list[dict[str, str]] = []

    for pat_file, masks_by_rater in sorted(binary_masks_by_file.items()):
        if pat_file not in reference_mri_paths_by_file:
            raise FileNotFoundError(f"No matching MRI file found for: {pat_file}")

        file_output_dir = output_path / get_display_pat_file_name(pat_file).replace(
            " ", "_"
        )
        file_output_dir.mkdir(parents=True, exist_ok=True)
        reference_mri_path = reference_mri_paths_by_file[pat_file]

        for rater_a, rater_b in combinations(sorted(masks_by_rater), 2):
            mask_image_a = masks_by_rater[rater_a]
            mask_image_b = masks_by_rater[rater_b]
            mask_a = sitk.GetArrayFromImage(mask_image_a)
            mask_b = sitk.GetArrayFromImage(mask_image_b)
            overlay_array = create_overlay_mask(mask_a, mask_b)
            overlay_image = sitk.GetImageFromArray(overlay_array)
            overlay_image.CopyInformation(mask_image_a)

            rater_label_a = get_display_rater_name(rater_a)
            rater_label_b = get_display_rater_name(rater_b)
            overlay_path = (
                file_output_dir / f"{rater_label_a}_vs_{rater_label_b}_overlay.nii.gz"
            )
            sitk.WriteImage(overlay_image, str(overlay_path))

            saved_overlays.append(
                {
                    "pat_file": pat_file,
                    "pat_label": get_display_pat_file_name(pat_file),
                    "rater_a": rater_a,
                    "rater_a_label": rater_label_a,
                    "rater_b": rater_b,
                    "rater_b_label": rater_label_b,
                    "reference_mri_path": str(reference_mri_path),
                    "overlay_mask_path": str(overlay_path),
                }
            )

    index_csv = Path(index_csv_path)
    index_csv.parent.mkdir(parents=True, exist_ok=True)

    with index_csv.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "pat_file",
                "pat_label",
                "rater_a",
                "rater_a_label",
                "rater_b",
                "rater_b_label",
                "reference_mri_path",
                "overlay_mask_path",
            ],
        )
        writer.writeheader()
        writer.writerows(saved_overlays)

    return saved_overlays


def print_overlay_mask_summary() -> None:
    saved_overlays = save_overlay_masks()

    for result in saved_overlays:
        print(
            f"{result['pat_label']}: {result['rater_a_label']} vs {result['rater_b_label']} "
            f"-> {result['overlay_mask_path']}"
        )


if __name__ == "__main__":
    print_overlay_mask_summary()
