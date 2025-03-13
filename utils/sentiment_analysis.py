# import os
# import re
# from transformers import pipeline
# from dotenv import load_dotenv
# from textblob import TextBlob

# # ✅ Load Hugging Face AI Models (Free & No API Key Needed)
# sentiment_analysis_model = pipeline("sentiment-analysis")  # AI Model for Sentiment Analysis
# hate_speech_model = pipeline("text-classification", model="facebook/roberta-hate-speech-dynabench-r4-target")

# # ✅ Manual Banned Words List (Extra Filtering)
# BANNED_WORDS = {"fuck", "shit", "asshole", "bitch", "bastard", "nazi", "racist", "offensive", "slur", "hate"}

# # ✅ Load sentiment analysis model (Transformers)
# sentiment_pipeline = pipeline("sentiment-analysis")

# def analyze_sentiment(text: str) -> float:
#     """
#     ✅ Analyzes sentiment using TextBlob (Backup Method).
#     - Returns a polarity score:
#       - Positive (> 0) = Positive sentiment
#       - 0 = Neutral
#       - Negative (< 0) = Negative sentiment
#     """
#     blob = TextBlob(text)
#     return blob.sentiment.polarity  # ✅ Returns polarity score

# def ai_moderation(text: str) -> bool:
#     """
#     ✅ Uses Free AI Models (Hugging Face) to Detect:
#     - Hate speech
#     - Offensive language
#     - Extremely negative sentiment
#     - Returns True if the text is inappropriate.
#     """

#     # ✅ Step 1: Check for manual banned words (case insensitive)
#     words = set(re.sub(r'[^a-zA-Z0-9]', ' ', text.lower()).split())  # Normalize text
#     if words & BANNED_WORDS:  # ✅ Check for intersection
#         return True

#     # ✅ Step 2: AI Hate Speech Detection
#     hate_result = hate_speech_model(text)
#     if hate_result[0]["label"] == "HATE_SPEECH":
#         return True

#     # ✅ Step 3: AI Sentiment Analysis (Detect Extremely Negative Sentiment)
#     sentiment_result = sentiment_analysis_model(text)
#     if sentiment_result[0]["label"] == "NEGATIVE":
#         return True

#     return False  # ✅ If no issues found, return False (text is safe)

import os
import re
from transformers import pipeline
from dotenv import load_dotenv
from textblob import TextBlob

# ✅ Load Hugging Face AI Models (Free & No API Key Needed)
sentiment_analysis_model = pipeline("sentiment-analysis")  # AI Model for Sentiment Analysis
hate_speech_model = pipeline("text-classification", model="facebook/roberta-hate-speech-dynabench-r4-target")

# ✅ Manual Banned Words List (Extra Filtering)
BANNED_WORDS = {"fuck", "shit", "asshole", "bitch", "bastard", "nazi", "racist", "offensive", "slur", "hate"}

def analyze_sentiment(text: str) -> float:
    """
    ✅ Analyzes sentiment using TextBlob (Backup Method).
    - Returns a polarity score:
      - Positive (> 0) = Positive sentiment
      - 0 = Neutral
      - Negative (< 0) = Negative sentiment
    """
    blob = TextBlob(text)
    return blob.sentiment.polarity  # ✅ Returns polarity score

def ai_moderation(text: str) -> bool:
    """
    ✅ Uses Free AI Models (Hugging Face) to Detect:
    - Hate speech
    - Offensive language
    - Extremely negative sentiment
    - Returns True if the text is inappropriate.
    """

    # ✅ Step 1: Check for manual banned words (case insensitive)
    words = set(re.sub(r'[^a-zA-Z0-9]', ' ', text.lower()).split())  # Normalize text
    if words & BANNED_WORDS:  # ✅ Check for intersection
        return True

    # ✅ Step 2: AI Hate Speech Detection (Ignore "mild" cases)
    hate_result = hate_speech_model(text)
    if hate_result[0]["label"] in ["HATE_SPEECH", "INSULT"]:  # Ignore mild offensive text
        return True

    # ✅ Step 3: AI Sentiment Analysis (Only Block Extremely Negative Sentiment)
    sentiment_result = sentiment_analysis_model(text)
    if sentiment_result[0]["label"] == "NEGATIVE":
        sentiment_score = analyze_sentiment(text)  # Check exact negativity score
        if sentiment_score < -0.6:  # Allow mild negativity but block extreme cases
            return True

    return False  # ✅ If no issues found, return False (text is safe)


