from functools import lru_cache

from fastapi import FastAPI, HTTPException
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel, Field, field_validator

from agent.agentic_workflow import GraphBuilder

app = FastAPI()


class QueryRequest(BaseModel):
    query: str = Field(min_length=1)

    @field_validator("query")
    @classmethod
    def strip_query(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Query cannot be empty")
        return value


class QueryResponse(BaseModel):
    response: str


@lru_cache(maxsize=1)
def get_graph() -> CompiledStateGraph:
    return GraphBuilder().build_graph()


@app.post("/query", response_model=QueryResponse)
async def query_travel_agent(request: QueryRequest) -> QueryResponse:
    try:
        graph = get_graph()
    except (OSError, ValueError) as error:
        raise HTTPException(
            status_code=503,
            detail="The AI model is not configured correctly.",
        ) from error

    result = await graph.ainvoke({"messages": [HumanMessage(content=request.query)]})
    messages = result.get("messages", [])
    final_message = next(
        (message for message in reversed(messages) if isinstance(message, AIMessage)),
        None,
    )
    if final_message is None or not isinstance(final_message.content, str):
        raise HTTPException(
            status_code=502,
            detail="The AI model did not return a text response.",
        )

    return QueryResponse(response=final_message.content)
