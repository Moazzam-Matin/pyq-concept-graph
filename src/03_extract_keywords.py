import pandas as pd

import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from collections import Counter

stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()
noun_tags = ("NN", "NNS", "NNP", "NNPS")


BLACKLIST = {
    # roman numerals (from "Statement I/II", "Column I/II/III/IV" style questions)
    "ii", "iii", "iv", "vi", "vii", "viii", "ix", "xi", "xii",
    # broken chemical-formula fragments left after numbers were stripped
    "ch", "co", "oh", "cl", "cm", "mol", "nh",
    "h2o", "h3c", "no2", "no3", "ph3", "hno3", "kcn", "kcl", "nacl",
    "socl", "ccl", "caco", "alcl", "hooc", "ch2oh", "pbo", "sno", "mno",
    "phch", "phmgbr", "xef", "chcl", "fecl", "pcl", "agno", "kmno",
    "hclo", "nabh", "mgbr", "cro", "conc", "dil",
    # LaTeX math-command leftovers (\frac, \sqrt, \theta, \circ, \det, \arg)
    "frac", "sqrt", "theta", "circ", "det", "arg",
    # exam-format boilerplate, not science content
    "statement", "value", "number", "list", "column", "option",
    "let", "structure", "figure", "image", "end", "comprehension",
    "paragraph", "match", "entry", "choice", "correct", "following",
    "given", "assume", "suppose", "respect", "consider", "situation",
    "define", "indicate", "denote", "satisfies", "exists", "ignore",
    "note", "text", "word", "letter", "choose", "contains", "matching",
    "fig",
}


def extract_terms(text):
    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)
    terms = []
    for word, tag in tagged:
        low = word.lower()
        if (
            tag in noun_tags
            and low not in stop_words
            and len(low) > 2
            and "_" not in low
        ):
            lemma = lemmatizer.lemmatize(low)
            if lemma not in BLACKLIST:
                terms.append(lemma)
    return terms


df = pd.read_csv("output/01_cleaned.csv")

df["Terms"] = df["Clean_Text"].apply(extract_terms)

#print(df[["Clean_Text", "Terms"]].head(3).to_string())

df.to_pickle("output/02_terms.pkl")
print("\nSaved to output/02_terms.pkl")



all_terms = [term for term_list in df["Terms"] for term in term_list]
freq = Counter(all_terms)

print("\nTotal unique terms:", len(freq))
print("\nTop 50 most frequent terms:")
for term, count in freq.most_common(100):
    print(f"  {term}: {count}")


sorted_terms = freq.most_common()  # no number = ALL terms, sorted by frequency, highest first

with open("output/all_terms.txt", "w") as f:
    for term, count in sorted_terms:
        f.write(f"{term}: {count}\n")

print(f"\nWrote {len(sorted_terms)} unique terms to output/all_terms.txt")