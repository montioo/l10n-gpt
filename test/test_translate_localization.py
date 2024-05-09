

import os
import json
import pytest

SCRIPT_FOLDER_PATH = os.path.dirname(os.path.realpath(__file__))

GPT_RETRY_COUNT = 2
    

@pytest.mark.flaky(reruns=GPT_RETRY_COUNT, reruns_delay=3)
def test_translating_localizable():
    """
    Test that translates a file and checks whether the output has the same
    amount of line breaks, quotes and numbers.
    """

    # TODO: Add test for format strings with variables

    target_lang = "de"
    localizable_filepath = os.path.join(SCRIPT_FOLDER_PATH, "localizable_strings/Localizable.xcstrings")
    script_path = os.path.join(SCRIPT_FOLDER_PATH, "../translate_localization.py")
    output_filepath = os.path.join(SCRIPT_FOLDER_PATH, "test_output_data", "Localizable.xcstrings")
    cmd = f"python3 {script_path} --openai_api_cooldown 10 --output {output_filepath} {target_lang} {localizable_filepath}"

    _debug_regenerate = True
    if _debug_regenerate:
        status = os.system(cmd)
        exit_code = os.WEXITSTATUS(status)
        assert exit_code == 0, f"Exit code of translate_localization.py is not 0 but: {exit_code}"

    with open(output_filepath, "r") as f:
        loc = json.loads(f.read())

    for en_string, info_dict in loc["strings"].items():

        loc_string = info_dict["localizations"][target_lang]["stringUnit"]["value"]

        expected_substrings = ["\\n", "\""]

        # TODO: Add test for numbers in string

        for es in expected_substrings:
            en_count = en_string.count(es)
            loc_count = loc_string.count(es)

            print(en_count, loc_count)

            assert en_count == loc_count, f"Expected to find {en_count} {es}, but found {loc_count}\n" + \
                f"English: {en_string}\nTranslated: {loc_string}"
        

