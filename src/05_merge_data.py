import pandas as pd

terms_df = pd.read_pickle("output/02_terms.pkl")
subject_df = pd.read_csv("output/03_classified.csv")

# From subject_df, keep only the columns we actually need for the merge:
# the join key (Question_ID) and the new information we don't already have (Predicted_Subject)
subject_df = subject_df[["Question_ID", "Predicted_Subject"]]

# Merge terms_df (which already has Question_ID, Question_Text, Clean_Text, Terms)
# with subject_df (which now only adds Predicted_Subject)
merged = terms_df.merge(subject_df, on="Question_ID", how="left")

print(merged.columns.tolist())
print(merged[["Question_ID", "Terms", "Predicted_Subject"]].head(5).to_string())

merged.to_pickle("output/04_merged.pkl")
print("\nSaved to output/04_merged.pkl")