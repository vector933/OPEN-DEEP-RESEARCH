import os
from google import genai
from google.genai.errors import APIError
import time

# --- 1. Initialization and API Key Setup ---
# The client will look for the key in the GEMINI_API_KEY environment variable.
try:
    # Initialize the client (it will look for the key you set in the terminal)
    client = genai.Client()
    # Using the fast, capable, and free-tier-friendly model
    MODEL_NAME = 'gemini-2.5-flash'
except Exception as e:
    print("Error initializing Gemini client.")
    print("Please ensure your GEMINI_API_KEY is set as an environment variable in the terminal.")
    exit()

# --- 2. Get User Input ---
print("--- AI Research Assistant Start (Using Gemini) ---")
topic = input("Enter your research topic (e.g., Impact of AI on education): ")

# --- 3. Step 1: Generate Sub-questions (The Planner Agent) ---
print("\n[AGENT] Step 1: Generating sub-questions...")

# Define the prompt for the model.
sub_qs_prompt = (
    f"Based on the main research topic '{topic}', "
    f"generate exactly three detailed, distinct, and high-level "
    f"research sub-questions. List them clearly, one per line."
)

try:
    # Send the request to the Gemini model using the generate_content method
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=sub_qs_prompt
    )
    
    # Extract the generated text content
    sub_questions_text = response.text
    
    # Display the result
    print("\n✅ Generated Sub-questions:")
    print(sub_questions_text)

    time.sleep(1) 

except APIError as e:
    print(f"\n❌ A Gemini API Error occurred: {e}. Check your connection or API key.")
    exit()
except Exception as e:
    print(f"\n❌ An unexpected error occurred: {e}")
    exit()


# --- 4. Step 2: Summarize the Findings (The Writer Agent) ---
print("\n[AGENT] Step 2: Summarizing sub-questions...")

# Define the summary prompt. This step uses the *result* from Step 1.
summary_prompt = (
    f"Summarize the following list of research sub-questions "
    f"into one cohesive, concise, introductory paragraph. "
    f"The sub-questions are:\n\n---\n{sub_questions_text}"
)

try:
    # Send the second request to the Gemini model
    summary_response = client.models.generate_content(
        model=MODEL_NAME,
        contents=summary_prompt
    )
    
    # Extract the summary text
    summary_text = summary_response.text
    
    # Display the final summary
    print("\n✅ Final Summary:")
    print(summary_text)

except APIError as e:
    print(f"\n❌ A Gemini API Error occurred during summary generation: {e}.")
except Exception as e:
    print(f"\n❌ An unexpected error occurred: {e}")

print("\n--- AI Research Assistant End ---")








#     $env:GEMINI_API_KEY="AIzaSyDLhwQiy5pzxUXj_-7xhD3w7jwXZxyrW9I"

#     python AIResearchAgent.py