import httpx
import json
import os
import sys
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def check_server():
    """Check if local server is running"""
    try:
        async with httpx.AsyncClient() as client:
            await client.get("http://localhost:8000")
        return True
    except:
        return False

async def test_webhook():
    """Send test updates to your webhook"""
    
    # Check if server is running
    if not await check_server():
        print("❌ Error: Local server is not running!")
        print("\nPlease start the local server first:")
        print("1. Open a new terminal window")
        print("2. Run: python scripts/test_local.py")
        print("3. Then run this script again")
        sys.exit(1)
    
    # Check for required environment variables
    telegram_id = os.getenv("YOUR_TELEGRAM_ID")
    webhook_secret = os.getenv("WEBHOOK_SECRET")
    
    if not telegram_id:
        print("❌ Error: YOUR_TELEGRAM_ID not found in .env file")
        sys.exit(1)

    # Sample Telegram update
    test_update = {
        "update_id": 123456789,
        "message": {
            "message_id": 123,
            "from": {
                "id": int(telegram_id),
                "first_name": "Test",
                "is_bot": False
            },
            "chat": {
                "id": int(telegram_id),
                "type": "private"
            },
            "date": 1234567890,
            "text": "Test message"
        }
    }

    print("🚀 Sending test webhook request...")
    
    # Send test update to local server
    async with httpx.AsyncClient(timeout=10.0) as client:
        headers = {
            "Content-Type": "application/json",
            "X-Telegram-Bot-Api-Secret-Token": webhook_secret or ""
        }
        
        try:
            response = await client.post(
                "http://localhost:8000/api/telegram",
                json=test_update,
                headers=headers
            )
            
            print(f"\n✨ Results:")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
        except httpx.ConnectError:
            print("\n❌ Error: Could not connect to local server")
            print("Make sure you've started the local server:")
            print("python scripts/test_local.py")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🔍 Testing Telegram webhook...")
    print("\n1. Checking local server...")
    asyncio.run(test_webhook()) 