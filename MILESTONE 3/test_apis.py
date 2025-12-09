"""Quick test to verify API keys are working"""
import os
from dotenv import load_dotenv

load_dotenv()

print("Checking API keys...")
print(f"GOOGLE_API_KEY: {'✓ Set' if os.getenv('GOOGLE_API_KEY') else '✗ Missing'}")
print(f"TAVILY_API_KEY: {'✓ Set' if os.getenv('TAVILY_API_KEY') else '✗ Missing'}")

# Test Tavily
try:
    from tavily import TavilyClient
    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    result = tavily.search("test query", max_results=1)
    print("\n✓ Tavily API: Working")
except Exception as e:
    print(f"\n✗ Tavily API Error: {e}")

# Test Google Gemini with google-generativeai directly
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say hello")
    print(f"✓ Google Gemini API: Working")
    print(f"  Response: {response.text[:50]}...")
except Exception as e:
    print(f"\n✗ Google Gemini API Error: {e}")
