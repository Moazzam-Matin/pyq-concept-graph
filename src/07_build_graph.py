import pandas as pd
from collections import Counter, defaultdict
from itertools import combinations
import json

df = pd.read_pickle("output/04_merged.pkl")

print("Rows:", len(df))
#print(df[["Question_ID", "Terms"]].head(3).to_string())

node_freq = Counter()
edge_weight = defaultdict(int)

for terms in df["Terms"]:
    unique_terms = sorted(set(terms))  # remove duplicates within one question, then sort

    for term in unique_terms:
        node_freq[term] += 1

    for term_a, term_b in combinations(unique_terms, 2):
        edge_weight[(term_a, term_b)] += 1

print("Unique nodes found:", len(node_freq))
print("Unique edges found:", len(edge_weight))
#print("\nMost common nodes:", node_freq.most_common(5))

MIN_NODE_FREQ = 3
MIN_EDGE_WEIGHT = 2

kept_nodes = {term for term, count in node_freq.items() if count >= MIN_NODE_FREQ}

edges = [
    {"source": a, "target": b, "weight": w}
    for (a, b), w in edge_weight.items()
    if a in kept_nodes and b in kept_nodes and w >= MIN_EDGE_WEIGHT
]

nodes = [{"id": term, "freq": node_freq[term]} for term in kept_nodes]

print("Nodes after filtering:", len(nodes))
print("Edges after filtering:", len(edges))

graph = {"nodes": nodes, "edges": edges}

with open("output/graph_full.json", "w") as f:
    json.dump(graph, f)

print(f"\nSaved full graph to output/graph_full.json")

# Also save a smaller prototype: top 150 nodes by frequency, for a quick/fast preview
top_nodes = sorted(nodes, key=lambda n: -n["freq"])[:150]
top_ids = {n["id"] for n in top_nodes}
top_edges = [e for e in edges if e["source"] in top_ids and e["target"] in top_ids]

prototype = {"nodes": top_nodes, "edges": top_edges}
with open("output/graph_prototype.json", "w") as f:
    json.dump(prototype, f)

print(f"Saved prototype graph ({len(top_nodes)} nodes, {len(top_edges)} edges) to output/graph_prototype.json")