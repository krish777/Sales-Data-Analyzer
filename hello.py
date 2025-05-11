import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import sys

def test_groq():
    """Test Groq API connection with current models"""
    print("🔍 Starting Groq API Test...\n")
    
    # 1. Load environment variables
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("❌ Error: GROQ_API_KEY not found in environment variables")
        print("Please create a .env file with:")
        print("GROQ_API_KEY=your_api_key_here")
        return False

    # 2. Current working models (June 2024)
    available_models = {
        "llama3-70b": "llama3-70b-8192",  # Current primary model
        "llama3-8b": "llama3-8b-8192",    # Faster alternative
        "mixtral": "mixtral-8x7b-32768"   # Alternative (may work for some accounts)
    }
    
    print("⚙️ Available Models:")
    for name, model_id in available_models.items():
        print(f"- {name} ({model_id})")

    # 3. Test configuration - trying models in order
    test_models = [
        "llama3-70b-8192",  # First try the 70b model
        "llama3-8b-8192",   # Fallback to 8b if needed
        "mixtral-8x7b-32768" # Final fallback
    ]

    for model in test_models:
        print(f"\n🔧 Testing with model: {model}")
        
        try:
            # 4. Initialize client
            print("🔄 Initializing Groq client...")
            chat = ChatGroq(
                model_name=model,
                api_key=api_key,
                temperature=0.7,
                max_tokens=100
            )
            
            # 5. Test query
            print("💭 Sending test query...")
            response = chat.invoke("Explain quantum computing in one sentence")
            
            print("\n✅ Test Successful!")
            print(f"📥 Response: {response.content}")
            return True
            
        except Exception as e:
            print(f"❌ Failed with {model}: {str(e)}")
            continue

    print("\n🔧 All model attempts failed. Possible solutions:")
    print("1. Check latest models at: https://console.groq.com/docs/models")
    print("2. Verify your API key has proper permissions")
    print("3. Try updating your langchain-groq package")
    return False

if __name__ == "__main__":
    success = test_groq()
    sys.exit(0 if success else 1)