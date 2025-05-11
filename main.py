import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
from crew.sales_analysis_crew import SalesAnalysisCrew
import logging.config
logging.config.fileConfig('logging_config.ini')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app_debug.log'),
        logging.StreamHandler()
    ]
)

def validate_csv_format():
    """Show required CSV format"""
    print("\nRequired CSV format:")
    print("Year,Make,Model,Quantity,Region,Price")
    print("\nExample:")
    print("2023,Toyota,Camry,15000,North,25000")

def display_menu():
    """Display user menu"""
    print("\n" + "="*40)
    print("🚗 Car Sales Data Analyzer".center(40))
    print("="*40)
    print("1. 📋 Get sales summary")
    print("2. 📈 Analyze yearly trends")
    print("3. ❓ Answer custom query")
    print("4. 🚪 Exit")
    print("="*40)

def display_result(title, data, is_trends=False, is_breakdown=False):
    """Format output display"""
    print(f"\n{'⭐'*3} {title} {'⭐'*3}")
    if isinstance(data, str):
        print(data)
        return
        
    if is_trends:
        print("  Year   │   Units Sold")
        print("  ───────┼────────────")
        for year, qty in sorted(data.get('total_by_year', {}).items()):
            print(f"  {year} │ {qty:,}")
        
        if is_breakdown:
            print("\n  Breakdown by Make:")
            for make, years in data.get('by_make', {}).items():
                print(f"  - {make}:")
                for year, qty in sorted(years.items()):
                    print(f"    {year}: {qty:,}")
    else:
        for key, value in data.items():
            if isinstance(value, dict):
                print(f"\n  {key.replace('_', ' ').title()}:")
                for k, v in value.items():
                    print(f"    - {k}: {v}")
            else:
                print(f"  - {key.replace('_', ' ').title()}: {value}")

def test_llm_connection(crew):
    """Verify LLM is working"""
    print("\n=== LLM CONNECTION TEST ===")
    try:
        if not hasattr(crew, 'query_handler'):
            print("❌ QueryHandler not found in crew")
            return
            
        if not hasattr(crew.query_handler, 'llm') or crew.query_handler.llm is None:
            print("❌ LLM not initialized in QueryHandler")
            return
            
        # Test direct LLM access
        test_response = crew.query_handler.execute_task("What is 2+2?")
        print(f"LLM Response: {test_response}")
        
        # Verify response contains expected content
        if "4" not in test_response:
            print("❌ Unexpected LLM response format")
            print(f"Raw response: {test_response}")
        else:
            print("✅ LLM is functioning properly")
            
    except Exception as e:
        print(f"❌ LLM FAILURE: {str(e)}")
        if "API key" in str(e):
            print("Check GROQ_API_KEY in .env file")
        elif "model" in str(e):
            print("Verify model name in QueryHandlerAgent")
    print("==========================")

def main():
    try:
        load_dotenv()
        
        # Enable debug logging if flag passed
        if "--debug" in sys.argv:
            os.environ["LITELLM_LOG"] = "DEBUG"
            logging.getLogger().setLevel(logging.DEBUG)
            logging.info("Debug mode enabled")
        
        print("\n🔍 Initializing analysis crew...")
        crew = SalesAnalysisCrew("data/car_sales.csv")
        
        # Run LLM connectivity test if requested
        if "--test-llm" in sys.argv or "--debug" in sys.argv:
            test_llm_connection(crew)
            if "--test-llm" in sys.argv:  # Exit after test if only testing
                sys.exit(0)
        
        print("✅ System ready\n")
        
        while True:
            display_menu()
            choice = input("⌨️  Enter your choice (1-4): ").strip()
            
            try:
                if choice == "1":
                    result = crew.run()
                    if 'summary' in result:
                        display_result("Sales Summary", result['summary'])
                        display_result("Metadata", result.get('metadata', {}))
                    else:
                        print(f"❌ Error: {result.get('error', 'Unknown error')}")
                        
                elif choice == "2":
                    result = crew.run()
                    if 'trends' in result:
                        display_result("Yearly Trends", result['trends'], 
                                     is_trends=True, is_breakdown=True)
                    else:
                        print(f"❌ Error: {result.get('error', 'Unknown error')}")
                        
                elif choice == "3":
                    query = input("\n📝 Enter your question: ").strip()
                    if not query:
                        print("⚠️ Please enter a valid question")
                        continue
                        
                    # Enable FULL debugging
                    debug_state = os.getenv("LITELLM_LOG")
                    os.environ["LITELLM_LOG"] = "DEBUG"  # Force debug ON
                    logging.getLogger().setLevel(logging.DEBUG)  # Enable all logs
                    
                    start_time = datetime.now()
                    result = crew.run(query=query)
                    
                    # Restore original logging
                    os.environ["LITELLM_LOG"] = debug_state or "ERROR"
                    logging.getLogger().setLevel(logging.INFO)
                    
                    elapsed = datetime.now() - start_time
                    print(f"\n🤖 Answer ({elapsed.total_seconds():.2f}s):")
                    print("-"*60)
                    print(result.get('query_response', 'No response'))
                    print("-"*60)
                    
                elif choice == "4":
                    print("\n👋 Thank you for using Car Sales Data Analyzer!")
                    sys.exit(0)
                    
                else:
                    print("⚠️ Invalid choice. Please enter 1-4")
                    
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                if "columns" in str(e):
                    validate_csv_format()
                continue

    except Exception as e:
        print(f"\n💥 Critical Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Car Sales Data Analyzer")
        print("Usage: python main.py [--debug] [--test-llm]")
        print("\nOptions:")
        print("  --debug     Enable verbose logging")
        print("  --test-llm  Verify LLM connectivity")
        validate_csv_format()
        sys.exit(0)
    
    main()