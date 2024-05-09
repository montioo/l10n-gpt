#!/usr/bin/env python3

#
# Marius Montebaur
# 
# October 2023
# 


import os
import time
import openai
import datetime
import json
from typing import Callable


SCRIPT_FOLDER_PATH = os.path.dirname(os.path.realpath(__file__))


class ChatGPT:

    def __init__(self, openai_token: str = None, model: str = "gpt-4", log_path: str = "queries", cooldown_duration_sec: int = 2):
        if not openai_token:
            openai_token = os.getenv("OPENAI_API_KEY")
        
        if not openai_token:
            raise RuntimeError("An OpenAI API key is required, either as a constructor argument or in the 'OPENAI_API_KEY' environment variable.")
        
        self.model = model
        self.client = openai.OpenAI(api_key=openai_token)

        self._queries_folder_path = log_path if os.path.isabs(log_path) else os.path.abspath(log_path)
        os.makedirs(self._queries_folder_path, exist_ok=True)

        self._cooldown_duration_sec = cooldown_duration_sec
        self._last_query_timestamp = 0


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

            ts = time.time()
            if ts - self._last_query_timestamp < self._cooldown_duration_sec:
                time.sleep(self._cooldown_duration_sec - (ts - self._last_query_timestamp))
                print(f"  -- going to sleep for {self._cooldown_duration_sec} secs to not exceed openai rate limit --")
            self._last_query_timestamp = ts

            date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            with open(os.path.join(self._queries_folder_path, f"{date_str}_1_system-input.txt"), "w") as f:
                f.write(system_command)
            with open(os.path.join(self._queries_folder_path, f"{date_str}_2_user-input.txt"), "w") as f:
                f.write(user_input)

            # https://platform.openai.com/docs/guides/gpt/chat-completions-response-format

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            
            finish_reason = response.choices[0].finish_reason
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
                
            message = response.choices[0].message.content
            # print("response" + message)
            with open(os.path.join(self._queries_folder_path, f"{date_str}_3_api-response.txt"), "w") as f:
                f.write(json.dumps(message, indent=4))

            try:
                response_text = response.choices[0].message.content.strip()
            except:
                print("Error, got unexpected response format:", response)
                continue

            with open(os.path.join(self._queries_folder_path, f"{date_str}_4_gpt-output.txt"), "w") as f:
                f.write(response_text)

            if is_valid_callback:
                if not is_valid_callback(response_text):
                    print(f"Response was invalid for request {date_str}. Will try again.")
                    continue

            return response_text
        
        raise RuntimeError(f"Error, could not get a valid response after {max_attempts} tries.")
