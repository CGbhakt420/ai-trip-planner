import os
from typing import Any

import httpx
import streamlit as st


DEFAULT_API_URL = "http://localhost:8000"
REQUEST_TIMEOUT_SECONDS = 120.0


def build_query_with_context(
    conversation: list[dict[str, str]], current_query: str
) -> str:
    if not conversation:
        return current_query

    earlier_turns = "\n\n".join(
        f"{'Traveler' if message['role'] == 'user' else 'Trip planner'}: "
        f"{message['content']}"
        for message in conversation
    )
    return (
        "Use the following conversation as context for the current request. "
        "Answer the current request and retain relevant trip details from earlier turns.\n\n"
        f"{earlier_turns}\n\nTraveler (current request): {current_query}"
    )


def request_trip_plan(api_url: str, query: str) -> str:
    response = httpx.post(
        api_url,
        json={"query": query},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    payload: Any = response.json()
    if not isinstance(payload, dict) or not isinstance(payload.get("response"), str):
        raise ValueError("The API returned an unexpected response format.")
    return payload["response"]


st.set_page_config(
    page_title="AI Trip Planner",
    page_icon="✈️",
    layout="centered",
)

st.title("AI Trip Planner")
st.caption(
    "Plan a trip with a day-by-day itinerary, places to stay and eat, "
    "transport options, weather, and a budget breakdown."
)

with st.sidebar:
    st.header("Connection")
    api_url = st.text_input(
        "Trip planner API URL",
        value=os.getenv("TRIP_PLANNER_API_URL", DEFAULT_API_URL),
        help="The URL of the FastAPI /query endpoint.",
    ).strip()
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.caption("Each request is sent to the FastAPI backend.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if query := st.chat_input("Where would you like to travel?"):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    context_query = build_query_with_context(
        st.session_state.messages[:-1],
        query,
    )
    if not api_url:
        st.error("Enter the FastAPI /query endpoint URL in the sidebar.")
    else:
        try:
            with st.chat_message("assistant"):
                with st.spinner("Planning your trip..."):
                    answer = request_trip_plan(api_url, context_query)
                st.markdown(answer)
            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )
        except httpx.TimeoutException:
            st.error(
                "The trip planner took too long to respond. Please try again."
            )
        except httpx.HTTPStatusError as error:
            try:
                detail = error.response.json().get("detail", error.response.text)
            except ValueError:
                detail = error.response.text
            st.error(f"The trip planner API returned an error: {detail}")
        except httpx.RequestError as error:
            st.error(
                "Could not connect to the trip planner API. Make sure the "
                "FastAPI server is running and the endpoint URL is correct."
            )
        except ValueError as error:
            st.error(str(error))
