import pandas as pd
import joblib

model = joblib.load("models/subject_recognition_model.pkl")

df = pd.read_csv("output/01_cleaned.csv")

df["Predicted_Subject"] = model.predict(df["Question_Text"])

print(df[["Question_Text", "Predicted_Subject"]].head(5).to_string())

print("\nSubject distribution:")
print(df["Predicted_Subject"].value_counts())

df.to_csv("output/03_classified.csv", index=False)
print("\nSaved to output/03_classified.csv")