import pandas as pd
import spacy
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download stopwords (only runs once)
nltk.download("stopwords")

# Load stopwords
stop_words = set(stopwords.words("english"))

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Load skills dataset (optional but fine to keep)
skills_df = pd.read_csv("skills_dataset.csv")
SKILLS = skills_df["skill"].str.lower().tolist()


def clean_text(text):
    """
    Clean resume text:
    - lowercase
    - remove stopwords
    - keep only alphabetic words
    """
    doc = nlp(text.lower())
    tokens = [
        token.text
        for token in doc
        if token.text not in stop_words and token.is_alpha
    ]
    return " ".join(tokens)


def match_skills(resume_text, selected_skills):
    """
    Match selected skills against resume text using:
    1. Direct keyword check (for HTML, CSS, etc.)
    2. TF-IDF + cosine similarity (ML-based)
    """

    # Clean resume text
    resume_clean = clean_text(resume_text)

    # Normalize selected skills
    skills_clean = [s.strip().lower() for s in selected_skills]

    # TF-IDF vectorization
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([resume_clean] + skills_clean)

    # Similarity scores
    similarities = cosine_similarity(vectors[0:1], vectors[1:])[0]

    matched = []
    missing = []

    # Hybrid matching logic
    for i, skill in enumerate(skills_clean):
        if skill in resume_clean:
            matched.append(selected_skills[i])
        elif similarities[i] > 0.15:
            matched.append(selected_skills[i])
        else:
            missing.append(selected_skills[i])

    # Calculate score
    score_percent = (
        (len(matched) / len(selected_skills)) * 100
        if selected_skills else 0
    )

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "score": round(score_percent, 2)
    }
