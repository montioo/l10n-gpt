#!/usr/bin/env python3

# 
# Marius Montebaur
# 
# 02.10.2023
# 
# Python script which hands a bunch of files to ChatGPT to intelligently add localization info to strings.
# 


import os
import sys
from pathlib import Path
import time
from chat_gpt_interface import ChatGPT
from translate_info import CHATGPT_TOKEN


task_description_intro = """
I want you to look for strings in a Swift file and replace them with calls to the `String` initializer with the arguments `localized` and `comment` so that the file can be easier used for localization of an app.
In the string you will provide to the `comment` field in the initializer. Include information about where the text will be visible, e.g. in a footer in the user interface, as part of a row in a table, as a heading for the whole page, etc.
Do not remove any other text from the input file.
Just output the content of the modified file. Do not add introductory text like "Here is the updated file" or similar.
If the lines get very long, do not put `String(localized: "...", comment: "...")` in one line, but do it like this:
```
String(
    localized: "...",
    comment: "..."
)
```

You will be given three files.
First, an example of a file that has not been adapted with the string constructors.
Second, the same file, but with the required changes already applied.
Third, a file without the calls to the `String` initializer where it's your task to make those modifications and to return the whole file modified.
"""

non_localized_file = "reference/PinEntryView_not-localized.swift"
localized_file = "reference/PinEntryView_localized.swift"


    
def generate_swift_localization_command(input_swift_file) -> str:

    # models: https://platform.openai.com/docs/models/gpt-3-5
    # token count = number of words + number of dots, commas and so on

    system_command = task_description_intro + "\n\n"
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


def main():

    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <path to folder containing swift files>")
        return

    # Path to the Xcode projects. Searches for swift files and will localize them in place
    xcode_project_folder_path = sys.argv[1]

    print("Warning: This script will apply localization to the swift files in-place, i.e. overwrite them!")
    print("If you don't have a version control system, this is not recommended!\n")
    answer = input("Please type 'yes' to continue or any other key to abort. ")
    if answer != "yes":
        print("\nAborting.")
        return

    files = Path(xcode_project_folder_path).rglob("*.swift")
    
    # NOTE: If you don't want to apply localization to all files, just put the
    # absolute paths to the files you want to change in a list called `files`:
    # files = ["main.swift", "View2.swift"]
    # files = map(lambda p: os.path.join(xcode_project_folder_path, p), files)
    
    # Need to use new model with large token count
    cpt = ChatGPT(CHATGPT_TOKEN, model="gpt-4-0613")

    for swift_file in files:

        swift_file_str = str(swift_file)

        print("Generating localized version for:", swift_file_str.removeprefix(xcode_project_folder_path))

        system_command, user_input = generate_swift_localization_command(swift_file_str)
        rewrite = cpt.complete_query(system_command, user_input)

        with open(swift_file_str, "w") as f:
            f.write(rewrite)
        
        print("  -- going to sleep for 60 secs to not exceed openai rate limit --")
        time.sleep(60)


if __name__ == "__main__":
    main()

