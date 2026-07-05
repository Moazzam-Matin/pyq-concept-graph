import pandas as pd
import re

df = pd.read_csv("data/raw/master_raw_questions_clean.csv")

def clean(text):
    text = str(text)

    # NEW: strip anything that isn't plain ASCII (removes Ω, √, °, and other
    # math/Greek symbols that PDFs often leave behind). \x00-\x7F is the
    # standard ASCII range.
    text = re.sub(r"[^\x00-\x7F]+", " ", text)

    
    # Pattern 1: remove MCQ option markers like (A) (B) (C) (D)
    # Also catches Greek lookalike letters some PDFs extract instead of A/B/C/D
    text = re.sub(r"\([A-DΑ-Ω]\)", " ", text)

    # Pattern 2: remove all punctuation and math symbols
    # \w means "word character" (letters, digits, underscore)
    # \s means "whitespace"
    # [^\w\s] means "anything that is NOT a word character or whitespace"
    text = re.sub(r"[^\w\s]", " ", text)


    # Pattern 3: remove standalone numbers (but keep words)
    # \b means "word boundary" -- this ensures we only match whole numbers,
    # not numbers that are part of a word
    text = re.sub(r"\b\d+\b", " ", text)

    # Clean up: collapse multiple spaces into one, and trim edges
    text = re.sub(r"\s+", " ", text).strip()

    return text


# Apply our clean() function to every row in Question_Text,
# storing the result in a brand new column called Clean_Text
df["Clean_Text"] = df["Question_Text"].apply(clean)

# Let's look at a before/after comparison for the first 2 rows
print(df[["Question_Text", "Clean_Text"]].head(2).to_string())

# Save this as our new working file -- we don't touch the original raw CSV again
df.to_csv("output/01_cleaned.csv", index=False)
print("\nSaved to output/01_cleaned.csv")