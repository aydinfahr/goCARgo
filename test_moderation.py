from db.utils import moderate_text  # ✅ Import the function

# ✅ Define test sentences
test_sentences = [
    "This is a clean comment.",  # ✅ Should NOT be blocked
    "Fuck this shit!",  # 🚨 Should be blocked (contains banned words)
    "You are so dumb!",  # 🚨 Should be blocked (contains banned words)
    "I hate you!",  # ❓ Might be blocked (depends on DeepAI)
    "boobs and ass",  # 🚨 Should be blocked (contains banned words)
    "Kill yourself!"  # ❓ Might be blocked (depends on DeepAI)
]

# ✅ Run the test
for text in test_sentences:
    result = moderate_text(text)
    print(f"Text: {text} -> Blocked: {result}")





  #  ----------------------------------------------------------------------------------------------------------------------
  #  ----------------------------------------------------------------------------------------------------------------------
        #  Step 2: Run the Script
        # Open your terminal (or Command Prompt) and run the script inside your project:

        # python test_moderation.py

  #  ----------------------------------------------------------------------------------------------------------------------
  #  ----------------------------------------------------------------------------------------------------------------------
