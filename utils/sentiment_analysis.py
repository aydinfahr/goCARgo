from textblob import TextBlob

def analyze_sentiment(text: str) -> float:
    """
    Analyzes the sentiment of a given text and returns a score.
    - Positive values indicate positive sentiment.
    - Negative values indicate negative sentiment.
    - Values close to 0 are neutral.
    """
    blob = TextBlob(text)
    return blob.sentiment.polarity  # Returns a value between -1 and 1

def moderate_text(text: str) -> bool:
    """
    Uses sentiment analysis to check if a review contains offensive or extremely negative content.
    
    Returns:
        - True: If the text is inappropriate (negative sentiment below threshold).
        - False: If the text is acceptable.
    """
    sentiment_score = analyze_sentiment(text)
    print(f"Sentiment Score: {sentiment_score} for comment: {text}")  # Debugging log

    return sentiment_score < -0.5  # Eğer skor çok negatifse (örneğin -0.5'ten düşükse) engelle
