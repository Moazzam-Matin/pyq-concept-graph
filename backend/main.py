from fastapi import FastAPI
import importlib.util
import json

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

class SearchRequest(BaseModel):
    query: str

class SearchResponse(BaseModel):
    terms: list[str]

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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Backend is running"}

@app.post("/search", response_model=SearchResponse)
def search(request: SearchRequest):
    extracted = extract_terms(request.query)
    matched = {term for term in extracted if term in GRAPH_NODE_IDS}
    return SearchResponse(terms=sorted(matched))