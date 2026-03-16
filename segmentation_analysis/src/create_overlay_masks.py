import csv
from itertools import combinations
from pathlib import Path

import numpy as np
import SimpleITK as sitk

try:
    from .display_names import get_display_pat_file_name, get_display_rater_name
    from .load_masks import unify_masks_to_binary
    from .paths import (
        OVERLAY_INDEX_CSV,
        OVERLAY_MASKS_DIR,
        PATIENTS_FOR_ANNOTATION_DIR,
        SEGMENTATION_BASE_DIR,
    )
except ImportError:
    from display_names import get_display_pat_file_name, get_display_rater_name
    from load_masks import unify_masks_to_binary
    from paths import (
        OVERLAY_INDEX_CSV,
        OVERLAY_MASKS_DIR,
        PATIENTS_FOR_ANNOTATION_DIR,
        SEGMENTATION_BASE_DIR,
    )

def find_reference_mri_images(
    mri_base_dir: str | Path = PATIENTS_FOR_ANNOTATION_DIR,
) -> dict[str, Path]:
    mri_base_path = Path(mri_base_dir)

    if not mri_base_path.exists():
        raise FileNotFoundError(f"Directory not found: {mri_base_path}")

    reference_mri_paths_by_file: dict[str, Path] = {}
    # key:      mri_file.name (str)
    # value:    mri_path (Path)

    for mri_path in sorted(mri_base_path.rglob("*.nii.gz")):
        if mri_path.name.startswith("segmentation_"):
            continue
        reference_mri_paths_by_file[mri_path.name] = mri_path

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
    binary_mask_arrays_by_file: dict[str, dict[str, np.ndarray]] | None = None,
    mri_base_dir: str | Path = PATIENTS_FOR_ANNOTATION_DIR,
    output_dir: str | Path = OVERLAY_MASKS_DIR,
    index_csv_path: str | Path = OVERLAY_INDEX_CSV,
) -> list[dict[str, str]]:
    if binary_mask_arrays_by_file is None:
        binary_mask_arrays_by_file = unify_masks_to_binary(SEGMENTATION_BASE_DIR)
    reference_mri_paths_by_file = find_reference_mri_images(mri_base_dir)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    saved_overlays: list[dict[str, str]] = []

    for pat_file, binary_mask_arrays_by_rater in sorted(
        binary_mask_arrays_by_file.items()
    ):
        if pat_file not in reference_mri_paths_by_file:
            raise FileNotFoundError(f"No matching MRI file found for: {pat_file}")

        file_output_dir = output_path / get_display_pat_file_name(pat_file)
        file_output_dir.mkdir(parents=True, exist_ok=True)

        reference_mri_path = reference_mri_paths_by_file[pat_file]
        reference_mri_image = sitk.ReadImage(str(reference_mri_path))

        for rater_a, rater_b in combinations(sorted(binary_mask_arrays_by_rater), 2):
            binary_mask_array_a = binary_mask_arrays_by_rater[rater_a]
            binary_mask_array_b = binary_mask_arrays_by_rater[rater_b]
            overlay_array = create_overlay_mask(
                binary_mask_array_a, binary_mask_array_b
            )
            overlay_image = sitk.GetImageFromArray(overlay_array)
            overlay_image.CopyInformation(reference_mri_image)

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
