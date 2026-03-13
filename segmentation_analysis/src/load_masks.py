from collections import defaultdict
from pathlib import Path

import SimpleITK as sitk


def load_mask_shapes(
    base_dir: str = "/home/sophieschouten/Internship/MOIS_SAM2_NF/segmentation_analysis/data/segmentations_from_radiologists",
) -> dict[str, dict[str, tuple[int, ...]]]:
    """
    This is my function for getting shapes of segmentation masks.
    """
    base_path = Path(base_dir)

    if not base_path.exists():
        raise FileNotFoundError(f"Directory not found: {base_path}")

    rater_dirs = sorted(path for path in base_path.iterdir() if path.is_dir())
    # rater_dirs = []
    # for path in base_path.iterdir():
    #     if path.is_dir():
    #         rater_dirs.append(path)
    #     else:
    #         # The path is not a directory
    #         pass
    # rater_dirs = sorted(rater_dirs)

    if not rater_dirs:
        raise FileNotFoundError(f"No subdirectories found in: {base_path}")

    shapes_by_file: dict[str, dict[str, tuple[int, ...]]] = {}

    for rater_dir in rater_dirs:
        pat_files = sorted(rater_dir.glob("*.nii.gz"))

        if not pat_files:
            continue

        for pat_file in pat_files:
            mask = sitk.ReadImage(str(pat_file))
            shape = sitk.GetArrayFromImage(mask).shape

            if pat_file.name not in shapes_by_file:
                shapes_by_file[pat_file.name] = {}

            shapes_by_file[pat_file.name][rater_dir.name] = shape
            # ext_key:      [pat_file.name]
            # int_key:      [rater_dir.name]
            # int_value:    shape

            # shapes_by_file = {
            #       patient_1: {
            #           rater_1: shape_1_1,
            #           rater_2: shape_1_2,
            #       }
            # }
            #        patient_2: {
            #           rater_1: shape_2_1,
            #           rater_2: shape_2_2,
            #       }
            # }

    if not shapes_by_file:
        raise FileNotFoundError(f"No .nii.gz files found in: {base_path}")

    return shapes_by_file


def print_mask_shapes(
    base_dir: str = "/home/sophieschouten/Internship/MOIS_SAM2_NF/segmentation_analysis/data/segmentations_from_radiologists",
) -> None:
    shapes_by_file = load_mask_shapes(base_dir)

    for pat_file in sorted(shapes_by_file):
        print(f"\n{pat_file}")
        for rater_name, shape in sorted(shapes_by_file[pat_file].items()):
            print(f"  {rater_name}: {shape}")


def load_mask_shapes_v0(arg_1, arg_2, base_dir="my_path"):
    print("Hello world")
    print(f"arg 1: {arg_1}, arg 2: {arg_2}, base_dir: {base_dir}")


if __name__ == "__main__":
    print_mask_shapes()
