import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure with your API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ GOOGLE_API_KEY not found in .env file")
    exit(1)

genai.configure(api_key=api_key)

print("🔍 Fetching available Gemini models...\n")

try:
    # List all available models
    models = genai.list_models()
    
    print("✅ Available Models:")
    print("=" * 80)
    
    for model in models:
        print(f"📝 Name: {model.name}")
        print(f"   📋 Supported Generation Methods: {model.supported_generation_methods}")
        print(f"   📊 Input Token Limit: {getattr(model, 'input_token_limit', 'N/A')}")
        print(f"   📈 Output Token Limit: {getattr(model, 'output_token_limit', 'N/A')}")
        print("-" * 80)
        
except Exception as e:
    print(f"❌ Error fetching models: {e}")