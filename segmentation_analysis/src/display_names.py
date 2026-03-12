import re


RATER_PREFIX_PATTERN = re.compile(r"^Segmentation_\d+")
FILE_PATIENT_PATTERN = re.compile(r"P_(\d+)")


def get_display_rater_name(rater_name: str) -> str:
    rater_label = RATER_PREFIX_PATTERN.sub("", rater_name, count=1)
    return rater_label or rater_name


def get_display_pat_file_name(pat_file_name: str) -> str:
    match = FILE_PATIENT_PATTERN.search(pat_file_name)

    if match is None:
        return pat_file_name

    return f"P_{match.group(1)}"


def get_display_rater_names(rater_names: list[str]) -> list[str]:
    return [get_display_rater_name(rater_name) for rater_name in rater_names]


def get_display_pat_file_names(file_names: list[str]) -> list[str]:
    return [get_display_pat_file_name(file_name) for file_name in file_names]
