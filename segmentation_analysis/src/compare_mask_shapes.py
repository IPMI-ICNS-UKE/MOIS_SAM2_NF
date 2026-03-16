from pathlib import Path

try:
    from .load_masks import load_mask_shapes
    from .paths import SEGMENTATION_BASE_DIR
except ImportError:
    from load_masks import load_mask_shapes
    from paths import SEGMENTATION_BASE_DIR


def _build_shape_comparison_results(
    shapes_by_file: dict[str, dict[str, tuple[int, ...]]] | None = None,
    base_dir: str | Path = SEGMENTATION_BASE_DIR,
) -> dict[str, dict[str, object]]:
    if shapes_by_file is None:
        shapes_by_file = load_mask_shapes(base_dir)
    shape_comparison_results: dict[str, dict[str, object]] = {}

    for pat_file, unsorted_shapes_by_rater in sorted(shapes_by_file.items()):
        shapes_by_rater = dict(sorted(unsorted_shapes_by_rater.items()))
        unique_shapes = sorted(set(shapes_by_rater.values()))

        shape_comparison_results[pat_file] = {
            "shapes_by_rater": shapes_by_rater,
            "all_shapes_equal": len(unique_shapes) == 1,
            "reference_shape": unique_shapes[0] if len(unique_shapes) == 1 else None,
        }
        # ext_key:      [pat_file]
        # ext_value:    int_dict
        # int_dict:     {"shapes_by_rater": dict, "all_shapes_equal": bool, "reference_shape": tuple/None}

        # shape_comparison_results = {
        #     patient_1: {
        #         "shapes_by_rater": {rater_1: shape_1_1, rater_2: shape_1_2, ...},
        #         "all_shapes_equal": True,
        #         "reference_shape": shape_1,
        #     }
        # }

    return shape_comparison_results


def compare_mask_shapes(
    shapes_by_file: dict[str, dict[str, tuple[int, ...]]] | None = None,
    base_dir: str | Path = SEGMENTATION_BASE_DIR,
) -> bool:
    """
    This is my function for checking whether mask shapes match for all patients.
    """
    shape_comparison_results = _build_shape_comparison_results(
        shapes_by_file=shapes_by_file,
        base_dir=base_dir,
    )
    return all(
        result["all_shapes_equal"] for result in shape_comparison_results.values()
    )


def print_shape_comparison_report(
    base_dir: str | Path = SEGMENTATION_BASE_DIR,
) -> None:
    shape_comparison_results = _build_shape_comparison_results(base_dir=base_dir)

    for file_name, result in shape_comparison_results.items():
        print(f"\n{file_name}")

        if result["all_shapes_equal"]:
            print(f"  Shape matches: {result['reference_shape']}")
        else:
            print("  Shape does not match across all subdirectories.")

        # for rater_name, shape in result["shapes_by_rater"].items():
        #     print(f"  {rater_name}: {shape}")


if __name__ == "__main__":
    print_shape_comparison_report()
