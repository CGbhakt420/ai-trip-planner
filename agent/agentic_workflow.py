from langgraph.graph.state import CompiledStateGraph
from langchain.agents import create_agent

from prompt_library.prompt import SYSTEM_PROMPT
from tools.calculator_tool import calculate
from tools.currency_conversion_tools import convert_currency
from tools.place_search_tool import search_places
from tools.weather_info_tool import get_current_weather, get_weather_forecast
from tools.web_search_tool import search_web
from utils.model_loader import ModelLoader


class GraphBuilder:
    def __init__(self) -> None:
        self.tools = [
            get_current_weather,
            get_weather_forecast,
            search_places,
            search_web,
            calculate,
            convert_currency,
        ]
        self.system_prompt = SYSTEM_PROMPT

    def build_graph(self) -> CompiledStateGraph:
        return create_agent(
            model=ModelLoader().load_llm(),
            tools=self.tools,
            system_prompt=self.system_prompt,
        )

    def __call__(self) -> CompiledStateGraph:
        return self.build_graph()
