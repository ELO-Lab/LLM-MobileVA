import re
import copy
import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, SimpleJsonOutputParser
from langchain_openai import ChatOpenAI

################################
#Langchain executor
################################
class LangChainExecutor:
    def __init__(self, model_name):
        self.model_name = model_name
        self.platform = 'gpt' if 'gpt' in model_name else 'gemini'
        self.api_key = os.getenv("OPEN_AI_API_KEY") if self.platform == "gpt" else os.getenv("GEMINI_API_KEY")
        if self.platform == "gpt":
            self.default_config = {
                "temperature": 1,
                "max_tokens": None,
            }
        elif self.platform == "gemini":
            self.default_config = {
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
            }

    def create_model(self, model_name, cp_config):
        # redefine by model_name
        self.platform = 'gpt' if 'gpt' in model_name else 'gemini'
        self.api_key = os.getenv("OPEN_AI_API_KEY") if self.platform == "gpt" else os.getenv("GEMINI_API_KEY")
        if self.platform == "gpt":
            self.default_config = {
                "temperature": 1,
                "max_tokens": None,
            }
        elif self.platform == "gemini":
            self.default_config = {
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": None,
            }

        if self.platform == "gpt":
            return ChatOpenAI(
                model=model_name,
                api_key=self.api_key,
                temperature=cp_config["temperature"],
                max_tokens=cp_config.get("max_tokens")
            )
        elif self.platform == "gemini":
            return ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=self.api_key,
                temperature=cp_config["temperature"],
                top_p=cp_config.get("top_p"),
                top_k=cp_config.get("top_k"),
                max_output_tokens=cp_config.get("max_output_tokens")
            )

    def clean_response(self, response):
        pattern = r'^(?:```json|```csv|```)\s*(.*?)\s*```$'
        return re.sub(pattern, r'\1', response, flags=re.DOTALL).strip()

    def execute(self, model_input, user_input, model_name="", temperature=0):
        cp_config = copy.deepcopy(self.default_config)
        cp_config["temperature"] = temperature
        if model_name == "":
            model_name = self.model_name

        model = self.create_model(model_name, cp_config)

        chat_template = ChatPromptTemplate.from_messages(
            [
                ("system", "{model_input}"),
                ("human", "{user_input}"),
            ]
        )

        parser = StrOutputParser()

        run_chain = chat_template | model | parser

        map_args = {
            "model_input": model_input,
            "user_input": user_input,
        }
        response = run_chain.invoke(map_args)

        response = self.clean_response(response)

        return response

    def execute_with_image(self, model_input, user_input, base64_image, model_name="", temperature=0):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "{model_input}\n{user_input}"),
                (
                    "user",
                    [
                        {
                            "type": "image_url",
                            "image_url": {"url": "data:image/jpeg;base64,{image_data}"},
                        }
                    ],
                ),
            ]
        )

        cp_config = copy.deepcopy(self.default_config)
        cp_config["temperature"] = temperature
        if model_name == "":
            model_name = self.model_name

        model = self.create_model(model_name, cp_config)

        parser = StrOutputParser()

        run_chain = prompt | model | parser

        response = run_chain.invoke({
            "image_data": base64_image,
            "model_input": model_input,
            "user_input": user_input
        })

        response = self.clean_response(response)

        return response       
