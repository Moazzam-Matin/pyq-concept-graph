from fastapi import FastAPI
import importlib.util
import json

from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

class SearchRequest(BaseModel):
    query: str

class TermResult(BaseModel):
    term: str
    years_count: int
    recurrence_pct: float
    last_year: int

class SearchResponse(BaseModel):
    terms: list[str]
    results: list[TermResult]

def _load_extract_terms():
    spec = importlib.util.spec_from_file_location(
        "extract_keywords", "src/03_extract_keywords.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.extract_terms

extract_terms = _load_extract_terms()


def _load_graph_node_ids():
    with open("output/graph_colored.json") as f:
        graph = json.load(f)
    return {node["id"] for node in graph["nodes"]}

GRAPH_NODE_IDS = _load_graph_node_ids()

def _load_term_year_stats():
    with open("output/06_term_year_stats.json") as f:
        return json.load(f)

TERM_YEAR_STATS = _load_term_year_stats()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://moazzam-matin.github.io",
        "http://localhost:8000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def read_root():
    return {"message": "Backend is running"}

@app.post("/search", response_model=SearchResponse)
def search(request: SearchRequest):
    extracted = extract_terms(request.query)
    matched = sorted({term for term in extracted if term in GRAPH_NODE_IDS})

    results = []
    for term in matched:
        stats = TERM_YEAR_STATS.get(term)
        if stats:
            results.append(TermResult(
                term=term,
                years_count=stats["years_count"],
                recurrence_pct=stats["recurrence_pct"],
                last_year=stats["last_year"],
            ))

    return SearchResponse(terms=matched, results=results)