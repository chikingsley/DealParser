# DealParser

## Project Overview
DealParser is a sophisticated Telegram bot project designed to parse and process deal-related information using advanced AI and machine learning techniques.

## Project Structure
- `api/`: API-related functionality
- `bot/`: Core bot implementation
  - `handlers/`: Different handler classes for bot interactions
- `archive/`: Historical data and model training resources
  - `data/`: Training and validation datasets
  - `model_training/`: Scripts for model creation and validation
- `scripts/`: Utility scripts for deployment and testing

## Setup and Installation
1. Clone the repository
2. Create a virtual environment:
   ```
   python3.12 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration
- Create a `.env` file with the following variables:
  - `TELEGRAM_BOT_TOKEN`
  - `NOTION_TOKEN`
  - Other necessary API keys

## Running the Bot
- For local testing:
  ```
  python scripts/test_local.py
  ```
- For webhook deployment:
  ```
  python scripts/setup_webhook.py
  ```

## Model Training
Scripts in `archive/model_training/` can be used to:
- Generate training data
- Validate datasets
- Fine-tune models

## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
[Add license information if applicable]

## Contact
[Add contact information or project maintainer details]
