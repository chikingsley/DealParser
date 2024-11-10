import asyncio
import json
from ft_client import FineTunedDealParser
from dotenv import load_dotenv

async def test_model():
    print("\n🔍 Testing Fine-Tuned Model")
    
    # Test deal
    test_deal = """Partner: Sutra
AU - 1,300+13% - mainly Beatskai iq (fb)"""

    # Initialize parser
    parser = FineTunedDealParser()
    
    try:
        # Parse deal
        print("\n📝 Parsing test deal...")
        result = await parser.parse_deals(test_deal)
        
        print("\n✨ Result:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    load_dotenv()
    asyncio.run(test_model()) 