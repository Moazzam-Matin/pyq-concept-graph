import pandas as pd

df = pd.read_pickle("output/04_merged.pkl")

# For each question, get the UNIQUE terms only (a term appearing 3 times in
# one question should count as ONE question containing that term, not three
# -- we care about "how many questions", not "how many word occurrences")
df["Unique_Terms"] = df["Terms"].apply(lambda t: list(set(t)))

# Explode: turn each list of terms into multiple separate rows,
# one per term, duplicating the other column values (like Predicted_Subject)
exploded = df.explode("Unique_Terms")

#print(df[["Question_ID", "Terms", "Unique_Terms"]].head(2).to_string())
#print("\n--- After exploding ---")
#print(exploded[["Question_ID", "Unique_Terms", "Predicted_Subject"]].head(10).to_string())

#print("\nTotal exploded rows:", len(exploded))

subject_counts = exploded.pivot_table(
    index="Unique_Terms",
    columns="Predicted_Subject",
    aggfunc="size",
    fill_value=0
)

# Add a Total column so we can sort by overall importance, not alphabetically
subject_counts["Total"] = subject_counts.sum(axis=1)

# Sort by Total, highest first, then look at the top 15 
#print(subject_counts.sort_values("Total", ascending=False).head(15))

subject_columns = ["chemistry", "mathematics", "physics"]

subject_counts["Dominant_Subject"] = subject_counts[subject_columns].idxmax(axis=1)

#print(subject_counts[subject_columns + ["Total", "Dominant_Subject"]].sort_values("Total", ascending=False).head(15))

# Reset the index so "Unique_Terms" becomes a normal column again,
# instead of being the DataFrame's row-label
term_subject_map = subject_counts[["Dominant_Subject"]].reset_index()

term_subject_map.columns = ["Term", "Dominant_Subject"]

print(term_subject_map.head())

term_subject_map.to_csv("output/05_term_subjects.csv", index=False)
print(f"\nSaved {len(term_subject_map)} term-subject mappings to output/05_term_subjects.csv")