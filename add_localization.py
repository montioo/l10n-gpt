#!/usr/bin/env python3

# 
# Marius Montebaur
# 
# 02.10.2023
# 
# Python script which hands a bunch of files to ChatGPT to intelligently add localization info to strings.
# 


import os
import argparse
from typing import List, Tuple
from dataclasses import dataclass
from pathlib import Path
import time
from chat_gpt_interface import ChatGPT
from common import get_openapi_token, add_common_args, user_approved_overwrite_warning


task_desc_intro = """
I want you to look for strings in a Swift file and replace them with calls to the `String` initializer with the arguments `localized` and `comment` so that the file can be easier used for localization of an app.
In the string you will provide to the `comment` field in the initializer, include information about where the text will be visible, e.g. in a footer in the user interface, as part of a row in a table, as a heading for the whole page, etc.
Do this for all text that appears in the UI, even if a translation might not be necessary.
Do not remove any other text from the input file.
Just output the content of the modified file. Do not add introductory text like "Here is the updated file" or similar.
Just change the string. Do not add any wrapping Text views or similar.
"""

task_desc_multiline = """
If the lines get very long, do not put `String(localized: "...", comment: "...")` in one line, but do it like this:
```
String(
    localized: "...",
    comment: "..."
)
```
"""

task_desc_singleline = """
Even if the lines get very long, do not add any newlines to `String(localized: "...", comment: "...")`.
Do not add any line breaks. Do not add any new variables like `let string = ...`.
"""

task_desc_end = """
You will be given three files.
First, an example of a file that has not been adapted with the string constructors.
Second, the same file, but with the required changes already applied.
Third, a file without the calls to the `String` initializer where it's your task to make those modifications and to return the whole file modified.
"""

# Reference files
SCRIPT_FOLDER_PATH = os.path.dirname(os.path.realpath(__file__))
non_localized_file = os.path.join(SCRIPT_FOLDER_PATH, "reference/PinEntryView_not-localized.swift")
localized_file = os.path.join(SCRIPT_FOLDER_PATH, "reference/PinEntryView_localized.swift")


def generate_swift_localization_command(input_swift_file, force_single_line = False) -> str:
    """
    force_single_line: Will ensure the content keeps the same number of lines.
    """

    # models: https://platform.openai.com/docs/models/gpt-3-5
    # token count = number of words + number of dots, commas and so on

    line_handling = task_desc_singleline if force_single_line else task_desc_multiline
    system_command = task_desc_intro + line_handling + task_desc_end + "\n"

    system_command += "First, a file without the modifications:\n\n"

    with open(non_localized_file, "r") as f:
        system_command += f.read()

    system_command += "\n\n\n" + "Now the same file, but with the required changes already applied:\n\n"

    with open(localized_file, "r") as f:
        system_command += f.read()

    system_command += "\n\n\n" + "Now the last file, for which you should make those changes and respond with the while file in updated form."
    
    with open(input_swift_file, "r") as f:
        user_input = f.read()
    
    return system_command, user_input


@dataclass
class AddL10nConfig:
    localization_pairs: List[Tuple[str, str]]
    openai_api_cooldown: int
    single_line_modifications: bool
    log_path: str


def _parse_args() -> AddL10nConfig:
    """
    Reads the command line arguments and builds list that contains tuples. Each
    tuple has the absolute path of a file that is used as an input (i.e. will be
    read and used to generate a localized version) and an absolute path
    determining the location of the localized version. Both may be the same.
    """

    parser = argparse.ArgumentParser(description="Processes .swift files and replaces strings constructed with quotes by String(localized:comment:) constructors. The comment will describe how the string is used in the app's UI.")
    parser.add_argument("paths", nargs="+", help="Either provide multiple paths of .swift files. Or provide a single path to a folder to process all .swift files found in that folder.")
    parser.add_argument("--output", type=str, help="Optional output folder. The localized files will be written to this location. If not specified, will overwrite input.")
    parser.add_argument("--single-line-modifications", action="store_true", help="If this optional flag is set, the resulting String(..) constructors will be done in place for the existing strings, not adding any new variables or line breaks.")
    add_common_args(parser)

    args = parser.parse_args()

    output_path = None
    if args.output:
        output_path = os.path.abspath(args.output)
        if os.path.exists(output_path) and not os.path.isdir(output_path):
            print(f"--output needs to be a folder but {output_path} was given.\n Aborting.")
            return
        
    # A path to a folder in which all the supplied files are located.
    # <common path>/<individual path>.swift
    # The relative path (the individual path) will be recreated in the output folder
    common_path_prefix = None

    if os.path.isdir(args.paths[0]):
        # found a single folder

        if len(args.paths) > 1:
            print(f"Warning: Only a single input folder is supported but {len(args.paths)} were given.")
            print(f"  Using the first given folder path: {args.paths[0]}")

        common_path_prefix = os.path.abspath(args.paths[0])
        input_file_paths = Path(args.paths[0]).rglob("*.swift")
    
    else:
        # files were given
        for path in args.paths:
            if os.path.isdir(path):
                print(f"Path must be a file, not a folder like {path}. Aborting.")
                exit(1)
            if not os.path.exists(path):
                print(f"File not found: {path}\nAborting.")
                exit(1)
        input_file_paths = args.paths
        common_path_prefix = os.path.commonpath(map(lambda p: os.path.dirname(p), input_file_paths))

    if not args.no_confirmation and output_path is None:
        if not user_approved_overwrite_warning():
            # User aborted the execution
            exit(1)

    # A list of [(input_file_path, output_file_path), ...]
    localization_pairs = []

    for input_file_path in input_file_paths:
        abs_input_file_path = os.path.abspath(input_file_path)

        if output_path is None:
            localization_pairs.append((abs_input_file_path, abs_input_file_path))
            continue

        # use the common prefix from all the supplied paths and recreate the
        # remaining structure in output_path
        input_file_path_wo_common_path = abs_input_file_path[len(common_path_prefix)+1:]
        localization_pairs.append((
            abs_input_file_path,
            os.path.join(output_path, input_file_path_wo_common_path)
        ))

    user_conf = AddL10nConfig(
        localization_pairs = localization_pairs,
        openai_api_cooldown = args.openai_api_cooldown,
        single_line_modifications = args.single_line_modifications,
        log_path = args.log_path
    )

    return user_conf

    
def main():

    user_config = _parse_args()
    localization_pairs = user_config.localization_pairs

    openai_api_token = get_openapi_token()
    
    # Need to use new model with large token count
    cpt = ChatGPT(openai_api_token, model="gpt-4-0613", log_path=user_config.log_path)

    for i, (input_file_path, output_file_path) in enumerate(localization_pairs):

        print(f"Generating localized version for:\n  {input_file_path}")
        if input_file_path == output_file_path:
            print(f"  Result will overwrite input")
        else:
            print(f"  Result will be written to:\n  {output_file_path}")

        system_command, user_input = generate_swift_localization_command(input_file_path, user_config.single_line_modifications)
        rewrite = cpt.complete_query(system_command, user_input)

        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        with open(output_file_path, "w") as f:
            f.write(rewrite)
        

if __name__ == "__main__":
    main()

