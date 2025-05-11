import os
import time
import hashlib
import logging
import requests
from dotenv import load_dotenv

class LLMVerifier:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
        
    def test_connection(self):
        """Direct API test bypassing LangChain"""
        print("\n=== DIRECT API TEST ===")
        
        # Test 1: Simple completion
        test_payload = {
            "model": "llama3-70b-8192",
            "messages": [{"role": "user", "content": "Say only this: PING"}],
            "max_tokens": 10,
            "temperature": 0.0
        }
        
        try:
            start = time.time()
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=test_payload,
                timeout=10
            )
            latency = time.time() - start
            
            if response.status_code != 200:
                print(f"❌ API Error: {response.status_code} - {response.text}")
                return False
                
            content = response.json()["choices"][0]["message"]["content"]
            print(f"⏱️ Response ({latency:.2f}s): {content}")
            
            if content.strip() != "PING":
                print(f"❌ Unexpected response: {content}")
                return False
                
            print("✅ Direct API test passed")
            return True
            
        except Exception as e:
            print(f"💥 API Test Failed: {str(e)}")
            return False

if __name__ == "__main__":
    verifier = LLMVerifier()
    if not verifier.test_connection():
        print("\nTROUBLESHOOTING:")
        print("1. Verify GROQ_API_KEY in .env")
        print("2. Check network connectivity to api.groq.com")
        print("3. Test with: curl -v https://api.groq.com")
        print("4. Visit https://console.groq.com to check API status")