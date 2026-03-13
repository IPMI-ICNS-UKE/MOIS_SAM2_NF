from pathlib import Path

import numpy as np
import SimpleITK as sitk


def unify_masks_to_binary(
    base_dir: str = "/home/sophieschouten/Internship/MOIS_SAM2_NF/segmentation_analysis/data/segmentations_from_radiologists",
) -> dict[str, dict[str, np.ndarray]]:
    """
    This is my function for normalizing each mask to a binary segmentation mask.
    """
    base_path = Path(base_dir)

    # if not base_path.exists():
    #     raise FileNotFoundError(f"Directory not found: {base_path}")

    rater_dirs = sorted(path for path in base_path.iterdir() if path.is_dir())
    # rater_dirs = []
    # for path in base_path.iterdir():
    #     if path.is_dir:
    #         rater_dirs.append(path)

    # if not rater_dirs:
    #     raise FileNotFoundError(f"No subdirectories found in: {base_path}")

    binary_masks_by_file: dict[str, dict[str, np.ndarray]] = {}

    for rater_dir in rater_dirs:
        pat_files = sorted(rater_dir.glob("*.nii.gz"))

        for pat_file in pat_files:
            mask = sitk.ReadImage(str(pat_file))
            mask_array = sitk.GetArrayFromImage(mask)
            binary_mask = (mask_array >= 1).astype(np.uint8)

            if pat_file.name not in binary_masks_by_file:
                binary_masks_by_file[pat_file.name] = {}

            binary_masks_by_file[pat_file.name][rater_dir.name] = binary_mask
            # ext_key:    [pat_file.name]
            # int_key:    [rater_dir.name]
            # int_value:  binary_mask

            # binary_masks_by_file: {
            #     patient_1:{
            #         rater_1: array_1_1(...),
            #         rater_2: array_1_2(...),
            #     }
            #     patient_2:{
            #         rater_1: array_2_1(...),
            #     }
            # }

    if not binary_masks_by_file:
        raise FileNotFoundError(f"No .nii.gz files found in: {base_path}")

    return binary_masks_by_file


def print_binary_mask_summary(
    base_dir: str = "/home/sophieschouten/Internship/MOIS_SAM2_NF/segmentation_analysis/data/segmentations_from_radiologists",
) -> None:
    binary_masks_by_file = unify_masks_to_binary(base_dir)

    for file_name in sorted(binary_masks_by_file):
        print(f"\n{file_name}")
        for rater_name, binary_mask in sorted(binary_masks_by_file[file_name].items()):
            unique_values = np.unique(binary_mask)
            print(
                f"  {rater_name}: shape={binary_mask.shape}, binary_values={unique_values.tolist()}"
            )


if __name__ == "__main__":
    print_binary_mask_summary()
