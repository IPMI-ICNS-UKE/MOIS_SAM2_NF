from src.load_masks import load_mask_shapes


def compare_mask_shapes(
    base_dir: str = "/home/sophieschouten/Internship/MOIS_SAM2_NF/segmentation_analysis/data/segmentations_from_radiologists",
) -> dict[str, dict[str, object]]:
    """
    This is my function for comparing shapes of masks for each patient.
    """
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

        # mask_comparison_results = {
        #     patient_1: {
        #         "shapes_by_rater": {rater_1: shape_1_1, rater_2: shape_1_2, ...},
        #         "all_shapes_equal": True,
        #         "reference_shape": shape_1,
        #     }
        # }

    return shape_comparison_results


def print_shape_comparison_report(
    base_dir: str = "/home/sophieschouten/Internship/MOIS_SAM2_NF/segmentation_analysis/data/segmentations_from_radiologists",
) -> None:
    mask_comparison_results = compare_mask_shapes(base_dir)

    for file_name, result in mask_comparison_results.items():
        print(f"\n{file_name}")

        if result["all_shapes_equal"]:
            print(f"  Shape matches: {result['reference_shape']}")
        else:
            print("  Shape does not match across all subdirectories.")

        # for rater_name, shape in result["shapes_by_rater"].items():
        #     print(f"  {rater_name}: {shape}")


if __name__ == "__main__":
    print_shape_comparison_report()
