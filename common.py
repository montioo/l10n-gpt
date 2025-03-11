
import os
import argparse
import subprocess


def get_openapi_token() -> str:
    """
    Fetch token from environment if not found in translate_info.py
    """

    try:
        from translate_info import CHATGPT_TOKEN as token_from_file
    except ImportError:
        token_from_file = None

    token = token_from_file or os.getenv("CHATGPT_TOKEN")
    if token is None:
        print("No OpenAI API token found.")
        print("  Token can be passed as environment variable or in translate_info.py")
        print("  See README.md for more info.")
        print("Aborting.")
        exit(1)

    return token


def get_app_context():
    """
    Fetch the user's description of his own app.
    """
    try:
        from translate_info import APP_CONTEXT as context
        return context
    except ImportError:
        return None


def add_common_args(parser: argparse.ArgumentParser):
    parser.add_argument("--openai_api_cooldown", type=int, default=60, help="Adjusts the time in seconds between two calls to the OpenAI API.")
    parser.add_argument("--log-path", type=str, default="queries", help="Optional log folder. The ChatGPT queries and responses will be placed here.")
    parser.add_argument("--no-confirmation", action="store_true", help="Overwrite without confirmation. Ignored if --output is specified.")


def user_approved_overwrite_warning() -> bool:
    """
    Returns false if the user wants to abort the execution.
    """

    print("Warning: This script will apply localization to the swift files in-place, i.e. overwrite them!")
    print("If you don't have a version control system, this is not recommended!\n")
    answer = input("Please type 'yes' to continue or any other key to abort. ")
    if answer == "yes":
        return True

    print("\nAborting.")
    return False


def file_has_uncommitted_changes(file_path: str) -> bool:
    """
    Check if a file is in a Git repository and has uncommitted changes.
    
    :param file_path: Absolute path to the file.
    :return: True if the file is in a Git repo and has uncommitted changes, False otherwise.
    """
    if not os.path.isfile(file_path):
        return False
    
    file_dir = os.path.dirname(file_path)
    
    try:
        # Get the top-level Git directory
        repo_root = subprocess.run(
            ['git', '-C', file_dir, 'rev-parse', '--show-toplevel'],
            capture_output=True, text=True, check=True
        ).stdout.strip()
        
        # Ensure the file is inside the Git repo
        if not file_path.startswith(repo_root):
            return False
        
        # Check if the file has uncommitted changes
        status_result = subprocess.run(
            ['git', '-C', repo_root, 'status', '--porcelain', '--', file_path],
            capture_output=True, text=True, check=True
        ).stdout.strip()
        
        return bool(status_result)  # If there is output, the file has changes
    
    except subprocess.CalledProcessError:
        return False  # Not a Git repo or other error
