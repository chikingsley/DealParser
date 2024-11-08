import json
import sys
from pathlib import Path

def validate_jsonl(file_path: str) -> bool:
    """Validate JSONL training data format"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            line_number = 0
            for line in f:
                line_number += 1
                try:
                    data = json.loads(line)
                    
                    # Check required fields
                    if 'messages' not in data:
                        print(f"Line {line_number}: Missing 'messages' field")
                        return False
                        
                    messages = data['messages']
                    if not isinstance(messages, list):
                        print(f"Line {line_number}: 'messages' must be a list")
                        return False
                        
                    # Validate each message
                    for msg in messages:
                        if not isinstance(msg, dict):
                            print(f"Line {line_number}: Each message must be a dictionary")
                            return False
                            
                        if 'role' not in msg or 'content' not in msg:
                            print(f"Line {line_number}: Messages must have 'role' and 'content'")
                            return False
                            
                        if msg['role'] not in ['system', 'user', 'assistant']:
                            print(f"Line {line_number}: Invalid role: {msg['role']}")
                            return False
                            
                except json.JSONDecodeError:
                    print(f"Line {line_number}: Invalid JSON")
                    return False
                    
            print(f"Successfully validated {line_number} examples")
            return True
            
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_data.py path/to/training_data.jsonl")
        sys.exit(1)
        
    file_path = sys.argv[1]
    if not Path(file_path).exists():
        print(f"File not found: {file_path}")
        sys.exit(1)
        
    if validate_jsonl(file_path):
        print("Validation successful!")
        sys.exit(0)
    else:
        print("Validation failed!")
        sys.exit(1)