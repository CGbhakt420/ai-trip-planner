# AI Trip Planner

## Run locally

Set `GROQ_API_KEY` in the project `.env` file, then start the API and UI in
separate terminals:

```powershell
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

```powershell
uv run streamlit run streamlit_app.py
```

The Streamlit UI sends requests to `http://127.0.0.1:8000/query` by default.
Set `TRIP_PLANNER_API_URL` to use a different API endpoint.

## Agent tools

The agent uses these configured services:

- `OPENWEATHERMAP_API_KEY` for current conditions and the available five-day
  forecast.
- `GPLACES_API_KEY` (or `GOOGLE_API_KEY`) for Google Places searches, with
  `FOURSQUARE_API_KEY` as the fallback when Google is unavailable or has no
  matching places.
- `TAVILY_API_KEY` for current web research and source links.
- `EXCHANGE_RATE_API_KEY` for currency conversion.
- Budget calculations run locally and do not require an API key.

Set the corresponding key in the project `.env` file. Provider errors are
reported to the agent rather than replaced with invented results.