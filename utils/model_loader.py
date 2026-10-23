import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from utils.config_loader import ConfigLoader


class ModelLoader:
    def __init__(self, config_loader: ConfigLoader | None = None) -> None:
        self.config_loader = config_loader or ConfigLoader()

    def load_llm(self) -> ChatGroq:
        config = self.config_loader.load_config()
        llm_config = config.get("llm")
        if not isinstance(llm_config, dict):
            raise ValueError("Configuration must contain an 'llm' mapping")

        groq_config = llm_config.get("groq")
        if not isinstance(groq_config, dict):
            raise ValueError("Configuration must contain an 'llm.groq' mapping")

        provider = groq_config.get("provider", "groq")
        if provider != "groq":
            raise ValueError(f"Unsupported model provider: {provider}")

        model_name = groq_config.get("model_name")
        if not isinstance(model_name, str) or not model_name.strip():
            raise ValueError("'llm.groq.model_name' must be a non-empty string")

        temperature = groq_config.get("temperature", 0.7)
        if isinstance(temperature, bool) or not isinstance(temperature, (int, float)):
            raise ValueError("'llm.groq.temperature' must be a number")

        project_root = self.config_loader.config_path.parent.parent
        load_dotenv(project_root / ".env")
        working_directory_env = Path.cwd() / ".env"
        if working_directory_env != project_root / ".env":
            load_dotenv(working_directory_env)
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not set. Add it to the environment or project .env file."
            )

        return ChatGroq(
            model=model_name,
            temperature=float(temperature),
            api_key=api_key,
        )
