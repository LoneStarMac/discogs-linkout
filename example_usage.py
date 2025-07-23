#!/usr/bin/env python3
"""
Example usage script for Music Collection Processor
Creates sample data and demonstrates various processing options
"""

import pandas as pd
import os
import subprocess
import sys

def create_sample_data():
    """Create sample music collection data for testing."""
    sample_data = [
        {"Artist": "The Beatles", "Title": "Abbey Road", "Year": "1969"},
        {"Artist": "Pink Floyd", "Title": "The Dark Side of the Moon", "Year": "1973"},
        {"Artist": "Led Zeppelin", "Title": "Led Zeppelin IV", "Year": "1971"},
        {"Artist": "Queen", "Title": "A Night at the Opera", "Year": "1975"},
        {"Artist": "The Rolling Stones", "Title": "Sticky Fingers", "Year": "1971"},
        {"Artist": "David Bowie", "Title": "The Rise and Fall of Ziggy Stardust", "Year": "1972"},
        {"Artist": "Fleetwood Mac", "Title": "Rumours", "Year": "1977"},
        {"Artist": "Various Artists", "Title": "Pulp Fiction Soundtrack", "Year": "1994"},
        {"Artist": "Radiohead", "Title": "OK Computer", "Year": "1997"},
        {"Artist": "Nirvana", "Title": "Nevermind", "Year": "1991"},
        {"Artist": "Michael Jackson", "Title": "Thriller", "Year": "1982"},
        {"Artist": "Prince", "Title": "Purple Rain", "Year": "1984"},
        {"Artist": "Stevie Wonder", "Title": "Songs in the Key of Life", "Year": "1976"},
        {"Artist": "Bob Dylan", "Title": "Highway 61 Revisited", "Year": "1965"},
        {"Artist": "The Velvet Underground", "Title": "The Velvet Underground & Nico", "Year": "1967"}
    ]
    
    df = pd.DataFrame(sample_data)
    df.to_csv("sample_collection.csv", index=False)
    print("✅ Created sample_collection.csv with 15 albums")
    return "sample_collection.csv"

def run_examples():
    """Run various example commands."""
    
    # Create sample data
    sample_file = create_sample_data()
    
    print("\n" + "="*60)
    print("🎵 MUSIC COLLECTION PROCESSOR EXAMPLES")
    print("="*60)
    
    examples = [
        {
            "name": "Basic Processing (CSV only)",
            "cmd": f"python3 collection_processor.py -i {sample_file} -o example1",
            "description": "Generates keywords and Wikipedia search links"
        },
        {
            "name": "HTML Report Generation",
            "cmd": f"python3 collection_processor.py -i {sample_file} -o example2 --html",
            "description": "Creates a beautiful HTML page with clickable links"
        },
        {
            "name": "Multiple Search Engines",
            "cmd": f"python3 collection_processor.py -i {sample_file} -o example3 --search wikipedia spotify youtube --html",
            "description": "Generates links for Wikipedia, Spotify, and YouTube"
        },
        {
            "name": "Custom Configuration",
            "cmd": f"python3 collection_processor.py -i {sample_file} -o example4 --max-keywords 3 --items-per-page 5 --html",
            "description": "Uses fewer keywords and smaller HTML pages"
        },
        {
            "name": "List Available Search Engines",
            "cmd": "python3 collection_processor.py --list-engines",
            "description": "Shows all available search engines"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n📋 Example {i}: {example['name']}")
        print(f"Description: {example['description']}")
        print(f"Command: {example['cmd']}")
        
        response = input("\nRun this example? [y/n/q]: ").strip().lower()
        
        if response == 'q':
            break
        elif response == 'y':
            print(f"\n🚀 Running: {example['cmd']}")
            try:
                result = subprocess.run(example['cmd'], shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ Success!")
                    if result.stdout:
                        print("Output:", result.stdout[-500:])  # Last 500 chars
                else:
                    print("❌ Error:", result.stderr)
            except Exception as e:
                print(f"❌ Error running command: {e}")
        else:
            print("⏭️  Skipped")
    
    print(f"\n🎉 Examples complete! Check the generated files:")
    
    # List generated files
    generated_files = []
    for file in os.listdir('.'):
        if file.startswith('example') and (file.endswith('.csv') or file.endswith('.html')):
            generated_files.append(file)
    
    if generated_files:
        for file in sorted(generated_files):
            size = os.path.getsize(file)
            print(f"  📄 {file} ({size:,} bytes)")
    
    print(f"\n📝 Also check the log file: collection_processor.log")

def demonstrate_formats():
    """Show examples of different input formats."""
    
    print("\n" + "="*50)
    print("📊 SUPPORTED INPUT FORMATS")
    print("="*50)
    
    # Discogs format
    discogs_data = [
        {"Artist": "The Beatles", "Title": "Abbey Road", "Label": "Apple Records", "Format": "Vinyl"},
        {"Artist": "Pink Floyd", "Title": "Dark Side of the Moon", "Label": "Harvest", "Format": "CD"}
    ]
    pd.DataFrame(discogs_data).to_csv("sample_discogs.csv", index=False)
    print("✅ Created sample_discogs.csv (Discogs format)")
    
    # Last.fm format  
    lastfm_data = [
        {"artist": "radiohead", "album": "ok computer", "playcount": "156"},
        {"artist": "the beatles", "album": "revolver", "playcount": "89"}
    ]
    pd.DataFrame(lastfm_data).to_csv("sample_lastfm.csv", index=False)
    print("✅ Created sample_lastfm.csv (Last.fm format)")
    
    # Custom format
    custom_data = [
        {"Band Name": "Led Zeppelin", "Album Title": "Physical Graffiti", "Rating": "5/5"},
        {"Band Name": "Queen", "Album Title": "Bohemian Rhapsody", "Rating": "4/5"}
    ]
    pd.DataFrame(custom_data).to_csv("sample_custom.csv", index=False)
    print("✅ Created sample_custom.csv (Custom format)")
    
    print("\nTo process these different formats:")
    print("  Discogs: python3 collection_processor.py -i sample_discogs.csv --html")
    print("  Last.fm: python3 collection_processor.py -i sample_lastfm.csv --artist artist --title album --html")
    print("  Custom:  python3 collection_processor.py -i sample_custom.csv --artist 'Band Name' --title 'Album Title' --html")

if __name__ == "__main__":
    print("🎵 Music Collection Processor - Example Usage")
    print("="*50)
    
    # Check if the main script exists
    if not os.path.exists("collection_processor.py"):
        print("❌ Error: collection_processor.py not found!")
        print("Make sure you're in the correct directory.")
        sys.exit(1)
    
    choice = input("\nWhat would you like to do?\n1. Run interactive examples\n2. Create sample format files\n3. Both\n\nChoice [1/2/3]: ").strip()
    
    if choice in ["2", "3"]:
        demonstrate_formats()
    
    if choice in ["1", "3"]:
        run_examples()
    
    print("\n🎉 All done! Enjoy processing your music collection!")
