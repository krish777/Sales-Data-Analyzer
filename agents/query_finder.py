import os
import time
import random
import logging
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('llm_audit.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('LLM_Verifier')

class QueryHandlerAgent:
    def __init__(self, use_llm=True):
        """Initialize with connection verification"""
        load_dotenv()
        self.llm = None
        self.last_call_metadata = {}
        
        if use_llm:
            self._initialize_llm()
            self._verify_connection()

    def _initialize_llm(self):
        """Initialize LLM with strict settings"""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY missing in .env")
        
        self.llm = ChatGroq(
            model_name="llama3-70b-8192",
            api_key=api_key,
            temperature=0.0,  # Maximize determinism
            max_tokens=1024,
            timeout=10.0
        )

    def _verify_connection(self):
        """Make test call to verify working connection"""
        test_id = random.randint(100000, 999999)
        test_prompt = f"""
        [VERIFICATION]
        This is a connection test. 
        Respond ONLY with: TEST_OK_{test_id}
        """
        
        response = self._call_llm(test_prompt, is_verification=True)
        
        if f"TEST_OK_{test_id}" not in response:
            raise ConnectionError(f"Verification failed. Got: {response}")

    def _call_llm(self, prompt: str, is_verification=False) -> str:
        """Core LLM call with full observability"""
        call_id = random.randint(100000, 999999)
        start_time = time.time()
        
        # Store call metadata
        self.last_call_metadata = {
            'call_id': call_id,
            'timestamp': time.time(),
            'prompt': prompt,
            'is_verification': is_verification
        }
        
        print(f"\n🔍 [LLM CALL #{call_id}]")
        print(f"Prompt: {prompt[:100]}...")
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content
            latency = time.time() - start_time
            
            print(f"⏱️ [LLM RESPONSE #{call_id}] {latency:.2f}s")
            print(f"Content: {content[:100]}...")
            
            logger.info(
                f"LLM call #{call_id} completed in {latency:.2f}s\n"
                f"Prompt: {prompt[:200]}...\n"
                f"Response: {content[:200]}..."
            )
            
            return content
            
        except Exception as e:
            error_msg = f"LLM call #{call_id} failed: {str(e)}"
            logger.error(error_msg)
            print(f"💥 ERROR: {error_msg}")
            raise

    def execute_task(self, task: str) -> str:
        """Public method with verification"""
        if not self.llm:
            return "LLM_NOT_INITIALIZED"
        
        # Create verification prompt
        call_id = random.randint(100000, 999999)
        verified_prompt = f"""
        [CALL_ID:{call_id}]
        [INSTRUCTION]
        {task}
        
        [REQUIREMENTS]
        1. Include CALL_ID in response
        2. Be accurate and concise
        """
        
        try:
            response = self._call_llm(verified_prompt)
            
            # Verify response contains call ID
            if str(call_id) not in response:
                raise ValueError(f"Call ID missing in response: {response}")
                
            return response
            
        except Exception as e:
            return f"LLM_ERROR: {str(e)}"

    def get_last_call_info(self) -> dict:
        """Retrieve metadata about last LLM call"""
        return self.last_call_metadata

    def __repr__(self):
        return f"<QueryHandlerAgent: {'ready' if self.llm else 'disabled'}>"