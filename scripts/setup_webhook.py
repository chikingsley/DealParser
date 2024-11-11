# scripts/setup_webhook.py
import os
import sys
import httpx
from dotenv import load_dotenv

load_dotenv()

def setup_webhook():
    """Set up Telegram webhook during build process"""
    
    # Get environment variables
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    webhook_secret = os.getenv("WEBHOOK_SECRET")
    
    # Get Vercel URL from environment
    vercel_url = os.getenv("VERCEL_URL")  # Vercel provides this during build
    vercel_env = os.getenv("VERCEL_ENV")  # 'production', 'preview', or 'development'
    
    if not all([bot_token, webhook_secret, vercel_url]):
        print("Missing required environment variables")
        print(f"VERCEL_URL: {'✓' if vercel_url else '✗'}")
        print(f"BOT_TOKEN: {'✓' if bot_token else '✗'}")
        print(f"WEBHOOK_SECRET: {'✓' if webhook_secret else '✗'}")
        sys.exit(1)
    
    # Only set webhook in production
    if vercel_env != "production":
        print(f"Skipping webhook setup for environment: {vercel_env}")
        sys.exit(0)
    
    webhook_url = f"https://{vercel_url}/api/telegram"
    
    try:
        # First, delete any existing webhook
        delete_url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
        response = httpx.post(delete_url)
        response.raise_for_status()
        
        # Set the new webhook
        set_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        params = {
            "url": webhook_url,
            "secret_token": webhook_secret,
        }
        
        response = httpx.post(set_url, params=params)
        response.raise_for_status()
        
        # Verify webhook is set correctly
        info_url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        response = httpx.get(info_url)
        response.raise_for_status()
        
        webhook_info = response.json()
        if webhook_info["ok"]:
            print("✅ Webhook setup successful!")
            print(f"URL: {webhook_url}")
            sys.exit(0)
        else:
            print("❌ Webhook setup failed!")
            print(webhook_info)
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error setting up webhook: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    setup_webhook()