

import os
import re
import sys
import pytest
from utils import ArgProvider, is_executed_in_script_dir, remove_newlines_in_parentheses

SCRIPT_FOLDER_PATH = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.dirname(SCRIPT_FOLDER_PATH))
from add_localization import _parse_args


GPT_RETRY_COUNT = 2
COMMON_TEST_ARGS = ["--log-path", os.path.join(SCRIPT_FOLDER_PATH, "..", "queries")]


def test_arg_parse_file_list_relative_paths():
    if not is_executed_in_script_dir():
        print("This test needs to be run from test/ directory. Aborting.")
        return

    # TODO: Add test with relative file paths
    # ...
    # rel_sfp = abs_source_file_path[len(SCRIPT_FOLDER_PATH)+1:]
    # rel_tfp = abs_target_file_path[len(SCRIPT_FOLDER_PATH)+1:]
    pass


def test_arg_parse_file_list():
    """
    Test to make sure that the files that are passed to the cli are correctly used.
    """

    files = ["dummy_proj/a.swift", "dummy_proj/folder_1/b.swift"]
    files = list(map(lambda f: os.path.join(SCRIPT_FOLDER_PATH, f), files))

    with ArgProvider(["--no-confirmation"] + COMMON_TEST_ARGS + files):
        localization_pairs = _parse_args().localization_pairs

        for i, (abs_source_file_path, abs_target_file_path) in enumerate(localization_pairs):

            assert abs_source_file_path == files[i], f"Source paths do not match.\nExpected: {files[i]}\nGot: {abs_source_file_path}"
            assert abs_target_file_path == files[i], f"Target paths do not match.\nExpected: {files[i]}\nGot: {abs_target_file_path}"


def test_arg_parse_project_folder():
    """
    Test that getting .swift files from a project folder works as expected
    """

    source_folder = os.path.join(SCRIPT_FOLDER_PATH, "dummy_proj")
    target_folder = os.path.join(SCRIPT_FOLDER_PATH, "target_folder")

    all_files = [
        "a.swift",
        "folder_1/b.swift",
        "folder_1/folder_1_1/d.swift",
        "folder_1/folder_1_1/c.swift",
    ]

    with ArgProvider(COMMON_TEST_ARGS + ["--no-confirmation", "--output", target_folder, source_folder]):
        localization_pairs = _parse_args().localization_pairs

        for i, (abs_source_file_path, abs_target_file_path) in enumerate(localization_pairs):
            
            ref_sfp = os.path.join(SCRIPT_FOLDER_PATH, source_folder, all_files[i])
            assert abs_source_file_path == ref_sfp, \
                f"Source paths do not match.\nExpected: {ref_sfp}\nGot: {abs_source_file_path}"

            ref_tsp = os.path.join(SCRIPT_FOLDER_PATH, target_folder, all_files[i])
            assert abs_target_file_path == ref_tsp, \
                f"Target paths do not match.\nExpected: {ref_tsp}\nGot: {abs_target_file_path}"
                


@pytest.mark.flaky(reruns=GPT_RETRY_COUNT, reruns_delay=3)
def test_add_l10n_to_files():
    """
    Check that only lines with strings are modified by ChatGPT.
    """

    # 1. Read SettingsView and localize it
    #  - tell chatgpt to do the construction in-place. No new String variables should be introduced
    # 2. Compare line by line and check that each string was changed

    source_swift_filename = "SettingsView_non-localized.swift"
    source_swift_file_path = os.path.join(SCRIPT_FOLDER_PATH, "simple_example", source_swift_filename)
    output_folder = os.path.join(SCRIPT_FOLDER_PATH, "test_output_data")
    script_path = os.path.join(SCRIPT_FOLDER_PATH, "../add_localization.py")
    cmd = f"python3 {script_path} --single-line-modifications --output {output_folder} {source_swift_file_path}"

    _debug_regenerate = True
    if _debug_regenerate:
        status = os.system(cmd)
        exit_code = os.WEXITSTATUS(status)
        assert exit_code == 0, f"Exit code of add_localization.py is not 0 but: {exit_code}"

    # Three files are used:
    # - input: File with just strings in quotes ".."
    with open(source_swift_file_path) as f:
        input_content = f.read().strip()

    # - localized: File with localized strings using String(localized:comment:)
    with open(os.path.join(output_folder, source_swift_filename)) as f:
        # remove newlines that ChatGPT added to view method calls
        localized_content = remove_newlines_in_parentheses(f.read())

    # - single_line: Removing all new lines that might have been introduced in swift view method calls
    # just keeping this file for debugging purposes
    single_line_swift_file_path = os.path.join(output_folder, "SettingsView_localized_single-line.swift")
    with open(single_line_swift_file_path, "w") as f:
        f.write(localized_content)

    input_lines = input_content.split("\n")
    localized_lines = localized_content.split("\n")
    
    assert len(input_lines) == len(localized_lines), \
        f"Input file and localized files do not have the same number of lines.\n" + \
        f"Input file: {source_swift_file_path}\nLocalized file: {single_line_swift_file_path}"

    for line_idx in range(len(input_lines)):
        if '"' not in input_lines[line_idx]:
            continue

        # split each input line into:  < pre >"content of string"< post >
        pattern = r'(.*?)\"([^\"]*)\"(.*)'

        match = re.search(pattern, input_lines[line_idx])
        assert match, f"Did not find string in line: {input_lines[line_idx]}"
        input_pre, input_content, input_post = match.groups()

        # split each localized line into: < pre >String(localized:comment:)< post >
        # 1. (.*?) - Captures any characters before the `String(localized:...` non-greedily (as 'pre')
        # 2. String\(localized:\s*"([^"]*)"\s*,\s*comment:\s*"([^"]*)"\) - Matches the structured localized string
        #    with the following captures:
        #    a. ([^"]*) - Captures the localized text (as 'loc')
        #    b. ([^"]*) - Captures the comment text (as 'comment')
        # 3. (.*) - Captures any characters after the closing parenthesis (as 'post')
        pattern = r'(.*?)String\(localized:\s*"([^"]*)"\s*,\s*comment:\s*"([^"]*)"\)(.*)'

        match = re.search(pattern, localized_lines[line_idx])
        assert match, f"Did not find String constructor in line: {localized_lines[line_idx]}"
        loc_pre, loc_content, loc_comment, loc_post = match.groups()

        assert input_pre == loc_pre, f"Content before String constructor was changed in line {line_idx}"
        assert input_post == loc_post, f"Content after String constructor was changed in line {line_idx}"
        assert input_content == loc_content, f"Content in String constructor was changed in line {line_idx}"


