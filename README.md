
# L10n-GPT

Context-Aware Localization (l10n) of iOS Apps with ChatGPT.

This file only describes the usage. Find information on what this repo does [here](https://montebaur.tech/projects/context-aware_localization.html).


## Requirements

- Using String Catalogs for localization (as discussed in step 2), not the legacy Strings File or Stringsdict File. Requires Xcode 15+
- Have an OpenAI API token. See next section for more info


## Setup

First, you need to install the OpenAI API:

```bash
pip3 install openai
```


Next, you need to give these scripts access to the OpanAI API token. This is possible in one of two ways:

### 1. With a `translate_info.py` file

In the root of this repository, create a file called `translate_info.py` which contains this line of code:

```python
CHATGPT_TOKEN = "put the token from OpenAI here"

APP_CONTEXT = "This is my App, here is a summary what it does."
```

### 2. Via Environment Arg

Start the python script as follows

```bash
OPENAI_API_KEY="put the token from OpenAI here" python3 translate_info.py
```


## Usage


### 1. Generate Context Information (optional)

Run the script `localize_files.py` to generate context information in the `.swift` files. This will replace normal strings that appear in the UI with ones that are initialized as follows:

```swift
String(
    localized: "<string in main language>",
    comment: "comment describing in which context the string appears in the UI"
)
```


### 2. Generate a `Localizable.xcstrings` with Xcode

Follow this tutorial to do so: [Apple Docs](https://developer.apple.com/documentation/Xcode/localizing-and-varying-text-with-a-string-catalog#Add-a-string-catalog-to-your-project)


### 3. Use Context Information to generate Translations

You have can either put `chat_gpt_interface.py` & `translate_localization.py` to your project folder or clone the scripts whereever you want and use your `Localizable.xcstrings`'s path as second parameter.

Run the script `translate_localizations.py` which will change the `Localizable.xcstrings` to add the terms and sentences for the new language. 
**Make sure to your have a restoreable backup of this file.**

Example translating to Latin American Spanish in project folder:

```bash
python3 translate_localization.py es-419
```
