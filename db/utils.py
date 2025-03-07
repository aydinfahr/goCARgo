import requests

# ✅ API key for DeepAI
DEEPAI_API_KEY = "513f052c-282c-435d-8b17-1ae7cb5cb6ec"

# ✅ List of manually banned words (for additional filtering)
BANNED_WORDS = {
    "fuck", "shit", "bitch", "asshole", "bastard", "cunt", 
    "dumb", "stupid", "boobs", "penis", "gerizekali"
}

def moderate_text(text: str) -> bool:
    """
    Uses DeepAI's text moderation API and manual filtering to detect offensive content.
    
    Returns:
        - True: If the text is inappropriate (contains offensive language).
        - False: If the text is clean.
    """

    try:
        # ✅ Step 1: Send text to DeepAI API for moderation
        response = requests.post(
            "https://api.deepai.org/api/text-moderation",
            data={"text": text},
            headers={"api-key": DEEPAI_API_KEY}
        )

        if response.status_code == 200:
            moderation_result = response.json()
            print(f"DeepAI Response: {moderation_result}")  # ✅ Debugging log

            # ✅ Check if the API flagged the text as inappropriate
            if moderation_result.get("output", {}).get("moderated", False):
                return True  # 🚨 API detected offensive content

        else:
            print(f"DeepAI API error: {response.status_code} - {response.text}")  # 🚨 Log API error

    except Exception as e:
        print(f"DeepAI API request failed: {e}")  # 🚨 Log connection failure

    # ✅ Step 2: Manual check using banned words
    words = set(text.lower().split())  # Convert text to lowercase and split into words
    if words.intersection(BANNED_WORDS):  
        return True  # 🚨 Block if any banned words are found

    return False  # ✅ The text is clean
