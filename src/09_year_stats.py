import pandas as pd
import json

df = pd.read_pickle("output/04_merged.pkl")

# Question_ID looks like "2007_1_Q01" -- the year is everything before the first underscore
df["Year"] = df["Question_ID"].str.split("_").str[0].astype(int)

#print(df[["Question_ID", "Year"]].head(3).to_string())

all_years = sorted(df["Year"].unique())
#print("\nYears in dataset:", all_years)
print("Total distinct years:", len(all_years))

TOTAL_YEARS = len(all_years)

# For each question, get its unique terms paired with its year
term_years = {}  # term -> set of years it appeared in

for _, row in df.iterrows():
    year = row["Year"]
    for term in set(row["Terms"]):
        if term not in term_years:
            term_years[term] = set()
        term_years[term].add(year)

# Build the final stats dictionary
term_stats = {}
for term, years in term_years.items():
    term_stats[term] = {
        "years": sorted(years),
        "years_count": len(years),
        "recurrence_pct": round(len(years) / TOTAL_YEARS * 100, 1),
        "last_year": max(years),
    }

# Quick sanity check on a term we know well
print(term_stats.get("reaction"))
print(term_stats.get("equilibrium"))

with open("output/06_term_year_stats.json", "w") as f:
    json.dump(term_stats, f)

print("\nSaved output/06_term_year_stats.json")