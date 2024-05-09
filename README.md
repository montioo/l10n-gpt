
# L10n-GPT

Context-Aware Localization (l10n) of iOS Apps with ChatGPT.

**TL;DR:** Enhance your iOS app's user interface with high-quality translations by providing context and usage details for each string, not just translating them. This approach ensures a more accurate and user-centric localization in any app developed with Xcode.

This file only describes the usage. Find information on what this repo does [here](https://montebaur.tech/projects/context-aware_localization.html).


## Requirements

- Using String Catalogs for localization (as discussed in step 2), not the legacy Strings File or Stringsdict File. Requires Xcode 15+
- Have an OpenAI API token. See next section for more info


## Setup

First, you need to install the OpenAI API:

```bash
pip3 install openai
```


Next, you need to give this repo access to the OpanAI API token. This is possible in one of two ways:

### 1. With a `translate_info.py` file (preferred)

In the root of this repository, create a file called `translate_info.py` which contains your constraints:

```python
CHATGPT_TOKEN = "put the token from OpenAI here"

APP_CONTEXT = "This is my App, here is a summary what it does."  # optional
```

Using the `translate_info.py` file is preferred because it allows adding context info on what your app does. Just add some sentences describing what your app is used for. This will enable ChatGPT to tailor the translations for your specific use-case.

### 2. Or via Environment Arg

Start the python script as follows

```bash
OPENAI_API_KEY="put the token from OpenAI here" python3 script.py
```


## Usage


### 1. Generate Context Information (optional)

Run the script `add_localization.py` to generate context information in the `.swift` files. This will replace normal strings that appear in the UI with ones that are initialized as follows:

```swift
String(
    localized: "<string in main language>",
    comment: "<comment describing in which context the string appears in the UI>"
)
```

Example usage to localize one file:
```bash
python3 add_localization.py --output localized/my_view.swift my/project/my_view.swift"
```

You can also pass multiple files or a single directory. The generated comment will be used in step three to provide better translations. For more info, run
```bash
python3 add_localization.py --help
```


### 2. Generate a `Localizable.xcstrings` with Xcode

Follow this tutorial to do so: [Apple Docs](https://developer.apple.com/documentation/Xcode/localizing-and-varying-text-with-a-string-catalog#Add-a-string-catalog-to-your-project)


### 3. Use Context Information to generate Translations

Run the script `translate_localization.py` which will modify a `Localizable.xcstrings` file to add the terms and sentences for the new language. 

Example translating to Latin American Spanish in project folder:

```bash
python3 translate_localization.py --output my/project/Localizable_w_de.xcstrings de my/project/Localizable.xcstrings
```

You can also pass multiple files or a single directory. The generated comment will be used in step three to provide better translations.
By default, no existing translations in your `Localizable.xcstrings` will be overwritten. You can passe the flag `--update-existing` to redo all translations for the selected language. For more info, run
```bash
python3 add_localization.py --help
```

You can find more info on the language codes that Xcode supports in the [Apple Docs](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPInternational/LanguageandLocaleIDs/LanguageandLocaleIDs.html#//apple_ref/doc/uid/10000171i-CH15).


## Contributing

If you would like to contribute to the development of the app, you're welcome to create pull requests or propose features by opening a GitHub issue.
 
To run the project's tests, you need to have `pytest` and the `rerunfailures` plugin installed:

```bash
pip3 install pytest pytest-rerunfailures
```
 