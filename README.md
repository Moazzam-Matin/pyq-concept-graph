# PYQ Concept Graph

An NLP + graph pipeline for competitive exam analysis — starting with JEE Advanced (2007–2025), extracting technical keywords and building subject-colored co-occurrence networks. JEE Mains and NEET coming next.

![Graph overview](assets/graph_overview.png)

## What this does

Every JEE Advanced question (2007–2025) is broken down into its core technical
concepts (e.g. _resistance_, _equilibrium_, _matrix_), then mapped into an
interactive network graph where:

- **Node size** = how many questions that concept appeared in
- **Edge strength** = how often two concepts appear together in the same question
- **Color** = the concept's dominant subject (Physics / Chemistry / Mathematics),
  determined by a trained classifier

The result is a visual map of how JEE Advanced topics actually relate to each
other — clusters of tightly-connected concepts emerge naturally from the data.

![Graph zoomed in](assets/graph_zoomed.png)

## Pipeline

Raw PDF-extracted questions go through the following stages:

1. **`src/02_clean_text.py`** — strip MCQ markers, symbols, and numbers from raw question text
2. **`src/03_extract_keywords.py`** — NLTK tokenization, POS tagging (nouns only),
   lemmatization, and blacklist filtering to isolate real technical vocabulary
   from exam-format boilerplate
3. **`src/04_classify_subjects.py`** — a trained TF-IDF + Logistic Regression
   model labels each question's subject
4. **`src/05_merge_data.py`** — join extracted terms with predicted subjects
5. **`src/06_subject_color.py`** — determine each keyword's dominant subject by
   counting its occurrences across question subjects
6. **`src/07_build_graph.py`** — build the co-occurrence graph: nodes (keywords
   - frequency) and edges (co-occurrence weight)
7. **`src/08_color_graph.py`** — attach each node's subject color

(`src/01_explore.py` and `src/09_viewer.html` are early exploration/prototyping
scripts, kept for reference.)

The frontend (`web/`) renders the final graph using D3.js force-directed layout,
with zoom/pan, curved colored edges, and progressive label reveal on zoom.

## Tech stack

- **Python**: pandas, NLTK, scikit-learn
- **Frontend**: D3.js (force simulation, zoom behavior), vanilla HTML/CSS/JS

## Running it locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

python src/02_clean_text.py
python src/03_extract_keywords.py
python src/04_classify_subjects.py
python src/05_merge_data.py
python src/06_subject_color.py
python src/07_build_graph.py
python src/08_color_graph.py

python -m http.server 8000
# then open http://localhost:8000/web/index.html
```

## Roadmap

- [ ] Search bar: type a question, highlight matching concepts on the graph
- [ ] JEE Mains data
- [ ] NEET data
- [ ] Historical recurrence stats per topic (e.g. "appeared in 8 of last 10 years")

## Data source

Question text sourced from publicly released JEE Advanced previous-year papers.
