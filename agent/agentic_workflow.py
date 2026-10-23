from utils.model_loader import ModelLoader
from prompt_library.prompt import SYSTEM_PROMPT
from langgraph.graph import StateGraph, MessagesState, END, START
from langgraph.prebuilt import ToolNode, tools_condition

from tools.weather_info_tool import WeatherInfoTool
from tools.place_search_tool import PlaceSearchTool
from tools.calculator_tool import CalculatorTool
from tools.currency_conversion_tools import CurrencyConverterTool

class GraphBuilder():
    def __init__(self):
        self.tools = []
        self.system_prompt = SYSTEM_PROMPT
    
    def agent_function(self, state:MessagesState):
        user_question =
        input_question = 
    
    def build_graph(self):
        graph_builder = StateGraph(MessagesState)
        
        graph_builder.add_node("agent", self.agent_function)
        graph_builder.add_node("tools", ToolNode(tools=self.tools))
        graph_builder.add_edge(START, "agent")
        graph_builder.add_conditional_edges("agent", tools_condition)
        graph_builder.add_edge("tools", "agent")
        graph_builder.add_edge("agent", END)
        
        self.graph = graph_builder.compile()
        return self.graph
    def __call__(self):
        return self.build_graph()