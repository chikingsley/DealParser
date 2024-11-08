"""
Test script to verify package imports are working correctly.
"""
try:
    from bot import callback, message
    print("✓ Bot package imports successful")
except ImportError as e:
    print("✗ Bot package import failed:", e)

try:
    from core import client, deal, prompts
    print("✓ Core package imports successful")
except ImportError as e:
    print("✗ Core package import failed:", e)

try:
    from tools import check_stats, finetune, generate_training_data, training_client, validate_data
    print("✓ Tools package imports successful")
except ImportError as e:
    print("✗ Tools package import failed:", e)
