#!/usr/bin/env python3

#
# Marius Montebaur
# 
# Oktober 2023
# 


import os
import openai
import datetime
import json
from typing import Callable


class ChatGPT:

    def __init__(self, openai_token: str = None, model: str = "gpt-4"):
        """
        openai_token: token that can be obtained from the OpenAI website. Either provded here or set as an environment variable OPENAI_API_KEY before starting the script.
        model: string describing the gpt model to use. Possible values are available here https://platform.openai.com/docs/models
        """

        if openai_token:
            openai.api_key = openai_token
        elif "OPENAI_API_KEY" in os.environ:
            openai.api_key = os.getenv("OPENAI_API_KEY")
        else:
            raise RuntimeError("Need openai key. Either as class constructor argument or in environment variable OPENAI_API_KEY")

        # e.g. "gpt-4-0613", "gpt-4", "gpt-3.5-turbo",
        self.model = model
    
    def complete_query(self, system_command: str, user_input: str, is_valid_callback: Callable[[str], bool] = None, max_attempts: int = 2) -> str:
        """
        Method takes a system_command and user_input and prompts ChatGPT for a
        response. Response is checked in several ways to make sure it's valid.
        Optionally, the user can provide a callback that is used to check the
        response as well. The content of the response is returned as a string.

        system_command: Command provided to the model that explains the task.
        user_input: Data or anyting else provided by the user.
        is_valid_callback: a function that takes the response_text and checks whether it is valid before returning.
        max_attempts: Maximum number of attempts for getting a valid response.
        """

        # https://platform.openai.com/docs/guides/chat/chat-vs-completions
        messages = [
          {"role": "system", "content": system_command},
          {"role": "user", "content": user_input}
        ]

        for _ in range(max_attempts):

            date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            with open(f"queries/{date_str}_1_system-input.txt", "w") as f:
                f.write(system_command)
            with open(f"queries/{date_str}_2_user-input.txt", "w") as f:
                f.write(user_input)

            # https://platform.openai.com/docs/guides/gpt/chat-completions-response-format

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages
            )

            finish_reason = response["choices"][0]["finish_reason"]
            if finish_reason == "length":
                # max tokens exceeded
                error_text = "Maximum tokens exceeded.\n"
                error_text += "Maybe try using a model with more tokens like gpt-3.5-turbo-16k or gpt-4-0613\n"
                error_text += "List of possible models is available here: https://platform.openai.com/docs/models"
                raise RuntimeError(error_text)

            if finish_reason != "stop":
                # model didn't finish for whatever reason. Trying again
                print("model terminated with finish_reason", finish_reason)
                continue

            with open(f"queries/{date_str}_3_api-response.txt", "w") as f:
                f.write(json.dumps(response, indent=4))

            try:
                response_text = response["choices"][0]["message"]["content"]
            except:
                print("Error, got unexpected response format:", response)
                continue

            with open(f"queries/{date_str}_4_gpt-output.txt", "w") as f:
                f.write(response_text)

            if is_valid_callback:
                if not is_valid_callback(response_text):
                    continue

            return response_text
        
        raise RuntimeError(f"Error, could not get a valid response after {max_attempts} tries.")
