import json
from collections import Counter
from pathlib import Path

def analyze_training_data():
    with open('data/training_data.jsonl', 'r') as f:
        examples = [json.loads(line) for line in f]
        
    print(f"\n✨ Training Data Analysis")
    print(f"Total examples: {len(examples)}")
    
    # Count unique formats
    formats = Counter()
    geos = Counter()
    sources = Counter()
    partners = Counter()
    
    for ex in examples:
        # Get the parsed output from assistant's response
        deal = json.loads(ex['messages'][2]['content'])['parsed_data']
        formats[deal['pricing_model']] += 1
        geos[deal['geo']] += 1
        sources[deal['source']] += 1
        partners[deal['partner']] += 1
        
    print("\n📊 Pricing Models:")
    for model, count in formats.most_common():
        print(f"  {model}: {count}")
        
    print("\n🌍 Top 10 GEOs:")
    for geo, count in geos.most_common(10):
        print(f"  {geo}: {count}")
        
    print("\n📱 Sources:")
    for source, count in sources.most_common():
        print(f"  {source}: {count}")
        
    print("\n🤝 Top 10 Partners:")
    for partner, count in partners.most_common(10):
        print(f"  {partner}: {count}")

if __name__ == "__main__":
    analyze_training_data() 