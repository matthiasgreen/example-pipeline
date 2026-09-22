# Mock Impect API

A FastAPI wrapper that serves the [Impect open data](https://github.com/ImpectAPI/open-data) JSON files as a REST API.
Used to mock a realistic data source for the pipeline.

## Run

```sh
# one-time: fetch the data
./scripts/fetch_open_data.sh

# from the project root
uv sync
uv run uvicorn api.main:app --reload --port 8000
```

Open <http://localhost:8000/docs> for the Swagger UI.

