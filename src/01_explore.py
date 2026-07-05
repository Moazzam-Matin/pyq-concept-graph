import pandas as pd

#Load the csv in DataFrame
df = pd.read_csv("data/raw/master_raw_questions_clean.csv")

print("Shape (rows,columns):", df.shape)

print("\nColumns:", df.columns.tolist())

print("\nFirst 3 rows:")
print(df.head(3))

missing = df["Question_Text"].isnull().sum()
print(f"Missing Question_text values: {missing}")