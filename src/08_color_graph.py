import json
import pandas as pd

with open("output/graph_full.json") as f:
    graph = json.load(f)

subjects_df = pd.read_csv("output/05_term_subjects.csv")

# Build a fast lookup: term -> dominant subject
# .set_index() makes "Term" the row label, .to_dict() then converts that
# into a plain Python dictionary: {"reaction": "chemistry", "point": "mathematics", ...}
term_to_subject = subjects_df.set_index("Term")["Dominant_Subject"].to_dict()

color_map = {
    "physics": "#3B82F6",     # blue
    "chemistry": "#10B981",   # green
    "mathematics": "#F59E0B", # amber/orange
}

for node in graph["nodes"]:
    subject = term_to_subject.get(node["id"], "unknown")
    node["subject"] = subject
    node["color"] = color_map.get(subject, "#9CA3AF")  # gray fallback

# quick sanity check
print(graph["nodes"][:10])

with open("output/graph_colored.json", "w") as f:
    json.dump(graph, f)

unknown_count = sum(1 for node in graph["nodes"] if node["subject"] == "unknown")
print(f"\nNodes with unknown subject: {unknown_count} out of {len(graph['nodes'])}")

print("\nSaved output/graph_colored.json")