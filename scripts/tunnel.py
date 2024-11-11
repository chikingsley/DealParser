from pyngrok import ngrok
import os
import sys
import requests
from dotenv import load_dotenv
import time

load_dotenv()

def setup_tunnel():
    """Create tunnel and set webhook for testing"""
    try:
        print("🚀 Starting ngrok tunnel...")
        # Start ngrok tunnel
        http_tunnel = ngrok.connect(8000)
        tunnel_url = http_tunnel.public_url
        
        # Get environment variables
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        webhook_secret = os.getenv("WEBHOOK_SECRET")
        
        webhook_url = f"{tunnel_url}/api/telegram"
        
        print("\n🔄 Setting up Telegram webhook...")
        # Set webhook to ngrok URL
        response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/setWebhook",
            json={
                "url": webhook_url,
                "secret_token": webhook_secret
            }
        )
        
        if response.status_code == 200:
            print(f"\n✅ Webhook set successfully!")
            print(f"URL: {webhook_url}")
            print("\n📱 You can now send messages to your bot on Telegram")
            print("Press Ctrl+C to stop the tunnel")
            
            # Keep the script running
            while True:
                time.sleep(1)
        else:
            print(f"\n❌ Failed to set webhook: {response.text}")
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping tunnel...")
        # Clean up webhook
        requests.post(f"https://api.telegram.org/bot{bot_token}/deleteWebhook")
        print("✅ Webhook cleaned up")
        ngrok.kill()
        print("✅ Tunnel closed")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    setup_tunnel() 