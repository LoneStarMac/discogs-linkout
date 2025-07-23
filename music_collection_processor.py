#!/usr/bin/env python3
"""
Music Collection Processor
Enhanced tool for processing music collection exports with keyword generation,
link creation, and HTML report generation.

Supports multiple export formats (Discogs, Last.fm, etc.) and search engines.
"""

import pandas as pd
import re
import argparse
import os
import sys
import json
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

# ========================
# Configuration
# ========================

DEFAULT_CONFIG = {
    "input_file": "collection_export.csv",
    "output_formats": ["csv", "html"],
    "artist_columns": ["Artist", "artist", "Artist Name", "artist_name"],
    "title_columns": ["Title", "title", "Album", "album", "Release Title", "release_title"],
    "max_keywords": 5,
    "search_engines": {
        "wikipedia": "https://en.wikipedia.org/wiki/Special:Search?search={query}",
        "spotify": "https://open.spotify.com/search/{query}",
        "youtube": "https://www.youtube.com/results?search_query={query}",
        "discogs": "https://www.discogs.com/search/?q={query}",
        "allmusic": "https://www.allmusic.com/search/all/{query}",
        "musicbrainz": "https://musicbrainz.org/search?query={query}&type=release"
    },
    "default_search_engine": "wikipedia",
    "html_items_per_page": 100,
    "stopwords": [
        "the", "a", "an", "of", "and", "is", "are", "was", "were", "at", "on", "in",
        "to", "for", "with", "without", "how", "do", "does", "did", "i", "am", "be",
        "by", "from", "that", "it's", "its", "you", "we", "this", "those", "these",
        "as", "up", "out", "off", "will", "my", "your", "our", "not", "yes", "no",
        "vol", "volume", "part", "feat", "featuring", "original", "soundtrack", "ost",
        "single", "ep", "lp", "cd", "vinyl", "remaster", "remastered", "deluxe", "edition"
    ]
}

# ========================
# Logging Setup
# ========================

def setup_logging(silent: bool = False, log_file: str = "collection_processor.log") -> logging.Logger:
    """Setup logging configuration."""
    logger = logging.getLogger("collection_processor")
    logger.setLevel(logging.DEBUG)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # File handler
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    if not silent:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    return logger

# ========================
# Core Processing Functions
# ========================

class CollectionProcessor:
    def __init__(self, config: Dict = None, logger: logging.Logger = None):
        self.config = config or DEFAULT_CONFIG
        self.logger = logger or logging.getLogger("collection_processor")
        self.stopwords = set(word.lower() for word in self.config["stopwords"])
    
    def detect_columns(self, df: pd.DataFrame) -> Tuple[Optional[str], Optional[str]]:
        """Auto-detect artist and title columns."""
        artist_col = None
        title_col = None
        
        # Find artist column
        for col_name in self.config["artist_columns"]:
            if col_name in df.columns:
                artist_col = col_name
                break
        
        # Find title column
        for col_name in self.config["title_columns"]:
            if col_name in df.columns:
                title_col = col_name
                break
        
        return artist_col, title_col
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text for keyword generation."""
        if pd.isna(text) or not text:
            return ""
        
        # Convert to string and lowercase
        text = str(text).lower()
        
        # Remove parentheses and brackets content
        text = re.sub(r'[\(\[\{].*?[\)\]\}]', '', text)
        
        # Remove special characters except spaces and hyphens
        text = re.sub(r'[^\w\s\-]', ' ', text)
        
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def generate_keywords(self, artist: str, title: str, max_words: int = None) -> str:
        """Generate search-friendly keywords from artist and title."""
        max_words = max_words or self.config["max_keywords"]
        
        artist_clean = self.clean_text(artist)
        title_clean = self.clean_text(title)
        
        # Split into words and remove stopwords/duplicates while preserving order
        artist_words = []
        for word in artist_clean.split():
            if word not in self.stopwords and word not in artist_words and len(word) > 1:
                artist_words.append(word)
        
        title_words = []
        for word in title_clean.split():
            if word not in self.stopwords and word not in title_words and len(word) > 1:
                title_words.append(word)
        
        # Handle "Various Artists" case
        if any(word in ["various", "va", "compilation"] for word in artist_words):
            artist_words = []
        
        # Combine artist and title words, prioritizing artist
        combined_words = []
        
        # Add up to 2 artist words first
        for word in artist_words[:2]:
            if len(combined_words) < max_words:
                combined_words.append(word)
        
        # Fill remaining slots with title words
        for word in title_words:
            if len(combined_words) >= max_words:
                break
            if word not in combined_words:
                combined_words.append(word)
        
        return ' '.join(combined_words)
    
    def generate_search_links(self, keywords: str, search_engines: List[str] = None) -> Dict[str, str]:
        """Generate search links for specified search engines."""
        if not search_engines:
            search_engines = [self.config["default_search_engine"]]
        
        links = {}
        query = urllib.parse.quote_plus(keywords)
        
        for engine in search_engines:
            if engine in self.config["search_engines"]:
                url_template = self.config["search_engines"][engine]
                links[engine] = url_template.format(query=query)
            else:
                self.logger.warning(f"Unknown search engine: {engine}")
        
        return links
    
    def process_dataframe(self, df: pd.DataFrame, artist_col: str = None, 
                         title_col: str = None, search_engines: List[str] = None) -> pd.DataFrame:
        """Process the dataframe to add keywords and search links."""
        # Auto-detect columns if not specified
        if not artist_col or not title_col:
            detected_artist, detected_title = self.detect_columns(df)
            artist_col = artist_col or detected_artist
            title_col = title_col or detected_title
        
        if not artist_col or not title_col:
            raise ValueError(f"Could not find artist/title columns. Available columns: {list(df.columns)}")
        
        if artist_col not in df.columns:
            raise ValueError(f"Artist column '{artist_col}' not found in data")
        if title_col not in df.columns:
            raise ValueError(f"Title column '{title_col}' not found in data")
        
        self.logger.info(f"Processing {len(df)} records...")
        self.logger.info(f"Using columns: Artist='{artist_col}', Title='{title_col}'")
        
        # Generate keywords
        self.logger.info("Generating keywords...")
        df['Keywords'] = df.apply(
            lambda row: self.generate_keywords(row[artist_col], row[title_col]), 
            axis=1
        )
        
        # Generate search links
        if not search_engines:
            search_engines = [self.config["default_search_engine"]]
        
        self.logger.info(f"Generating search links for: {', '.join(search_engines)}")
        
        for engine in search_engines:
            df[f'{engine.title()}_Link'] = df['Keywords'].apply(
                lambda kw: self.generate_search_links(kw, [engine]).get(engine, '')
            )
        
        # Add a combined search link column for the primary engine
        primary_engine = search_engines[0]
        df['Search_Link'] = df[f'{primary_engine.title()}_Link']
        
        return df

# ========================
# HTML Generation
# ========================

def generate_html_report(df: pd.DataFrame, output_path: str, items_per_page: int = 100, 
                        config: Dict = None, logger: logging.Logger = None):
    """Generate a paginated HTML report."""
    config = config or DEFAULT_CONFIG
    logger = logger or logging.getLogger("collection_processor")
    
    total_items = len(df)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    # Create output directory
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    base_name = Path(output_path).stem
    
    for page in range(total_pages):
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        page_df = df.iloc[start_idx:end_idx]
        
        # Generate filename
        if total_pages == 1:
            filename = f"{base_name}.html"
        else:
            filename = f"{base_name}_page_{page + 1}.html"
        
        filepath = output_dir / filename
        
        # Generate HTML content
        html_content = generate_page_html(page_df, page + 1, total_pages, config)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Generated HTML page: {filepath}")

def generate_page_html(df: pd.DataFrame, page_num: int, total_pages: int, config: Dict) -> str:
    """Generate HTML content for a single page."""
    
    # Detect key columns
    artist_col, title_col = None, None
    for col in config["artist_columns"]:
        if col in df.columns:
            artist_col = col
            break
    for col in config["title_columns"]:
        if col in df.columns:
            title_col = col
            break
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Music Collection - Page {page_num}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }}
        .pagination {{
            text-align: center;
            margin: 20px 0;
            font-size: 16px;
            color: #666;
        }}
        .album-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .album-card {{
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            background: #fff;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .album-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .artist {{
            font-weight: bold;
            font-size: 16px;
            color: #007bff;
            margin-bottom: 5px;
        }}
        .title {{
            font-size: 14px;
            color: #333;
            margin-bottom: 10px;
        }}
        .keywords {{
            font-size: 12px;
            color: #666;
            font-style: italic;
            margin-bottom: 15px;
        }}
        .links {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .link-btn {{
            padding: 6px 12px;
            background: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 12px;
            transition: background 0.2s;
        }}
        .link-btn:hover {{
            background: #0056b3;
        }}
        .stats {{
            text-align: center;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        @media (max-width: 768px) {{
            .album-grid {{
                grid-template-columns: 1fr;
            }}
            .container {{
                padding: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 Music Collection</h1>
        
        <div class="stats">
            <strong>Page {page_num} of {total_pages}</strong> • 
            Showing {len(df)} items • 
            Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
"""

    if total_pages > 1:
        html += f"""
        <div class="pagination">
            Navigation: 
"""
        for p in range(1, total_pages + 1):
            if p == page_num:
                html += f"<strong>{p}</strong> "
            else:
                page_file = f"_page_{p}.html" if total_pages > 1 else ".html"
                html += f'<a href="{Path(output_path).stem}{page_file}">{p}</a> '
        html += "</div>"

    html += '<div class="album-grid">'
    
    for _, row in df.iterrows():
        artist = row.get(artist_col, 'Unknown Artist') if artist_col else 'Unknown Artist'
        title = row.get(title_col, 'Unknown Title') if title_col else 'Unknown Title'
        keywords = row.get('Keywords', '')
        
        html += f"""
        <div class="album-card">
            <div class="artist">{artist}</div>
            <div class="title">{title}</div>
            <div class="keywords">Keywords: {keywords}</div>
            <div class="links">
"""
        
        # Add search links
        link_columns = [col for col in df.columns if col.endswith('_Link')]
        for link_col in link_columns:
            if pd.notna(row[link_col]) and row[link_col]:
                engine_name = link_col.replace('_Link', '')
                html += f'<a href="{row[link_col]}" target="_blank" class="link-btn">{engine_name}</a>'
        
        html += """
            </div>
        </div>
"""
    
    html += """
        </div>
    </div>
</body>
</html>
"""
    
    return html

# ========================
# Main Functions
# ========================

def load_config(config_path: str = "config.json") -> Dict:
    """Load configuration from file if it exists."""
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                config = DEFAULT_CONFIG.copy()
                config.update(user_config)
                return config
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
    
    return DEFAULT_CONFIG

def save_config(config: Dict, config_path: str = "config.json"):
    """Save current configuration to file."""
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save config file: {e}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Enhanced Music Collection Processor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i my_collection.csv
  %(prog)s -i discogs_export.csv -o processed --html --search wikipedia spotify
  %(prog)s -i collection.csv --artist "Artist Name" --title "Album Title"
  %(prog)s --list-engines
        """
    )
    
    parser.add_argument("-i", "--input", help="Input CSV file", 
                       default=DEFAULT_CONFIG["input_file"])
    parser.add_argument("-o", "--output", help="Output file prefix (without extension)")
    parser.add_argument("--artist", help="Artist column name")
    parser.add_argument("--title", help="Title column name") 
    parser.add_argument("--search", nargs='+', help="Search engines to generate links for",
                       choices=list(DEFAULT_CONFIG["search_engines"].keys()),
                       default=[DEFAULT_CONFIG["default_search_engine"]])
    parser.add_argument("--max-keywords", type=int, default=DEFAULT_CONFIG["max_keywords"],
                       help="Maximum number of keywords")
    parser.add_argument("--csv", action="store_true", help="Generate CSV output", default=True)
    parser.add_argument("--html", action="store_true", help="Generate HTML output")
    parser.add_argument("--items-per-page", type=int, default=DEFAULT_CONFIG["html_items_per_page"],
                       help="Items per HTML page")
    parser.add_argument("--config", help="Configuration file path", default="config.json")
    parser.add_argument("--save-config", action="store_true", help="Save current settings as default")
    parser.add_argument("--list-engines", action="store_true", help="List available search engines")
    parser.add_argument("-s", "--silent", action="store_true", help="Suppress console output")
    parser.add_argument("--log-file", default="collection_processor.log", help="Log file path")
    parser.add_argument("--version", action="version", version="Music Collection Processor 2.0")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Update config with command line arguments
    if args.max_keywords != DEFAULT_CONFIG["max_keywords"]:
        config["max_keywords"] = args.max_keywords
    if args.items_per_page != DEFAULT_CONFIG["html_items_per_page"]:
        config["html_items_per_page"] = args.items_per_page
    
    # List engines and exit
    if args.list_engines:
        print("Available search engines:")
        for engine, url in config["search_engines"].items():
            print(f"  {engine}: {url}")
        return
    
    # Save configuration if requested
    if args.save_config:
        save_config(config, args.config)
        print(f"Configuration saved to {args.config}")
        return
    
    # Setup logging
    logger = setup_logging(args.silent, args.log_file)
    
    try:
        # Check input file
        if not os.path.exists(args.input):
            logger.error(f"Input file not found: {args.input}")
            sys.exit(1)
        
        logger.info(f"Loading data from: {args.input}")
        
        # Load CSV with error handling
        try:
            df = pd.read_csv(args.input, encoding='utf-8')
        except UnicodeDecodeError:
            logger.info("UTF-8 failed, trying with latin-1 encoding...")
            df = pd.read_csv(args.input, encoding='latin-1')
        
        logger.info(f"Loaded {len(df)} records with columns: {list(df.columns)}")
        
        # Initialize processor
        processor = CollectionProcessor(config, logger)
        
        # Process the data
        processed_df = processor.process_dataframe(
            df, 
            artist_col=args.artist,
            title_col=args.title,
            search_engines=args.search
        )
        
        # Determine output path
        output_base = args.output or Path(args.input).stem + "_processed"
        
        # Generate outputs
        if args.csv or not args.html:
            csv_path = f"{output_base}.csv"
            processed_df.to_csv(csv_path, index=False, encoding='utf-8')
            logger.info(f"CSV saved to: {csv_path}")
        
        if args.html:
            html_path = f"{output_base}.html"
            generate_html_report(
                processed_df, 
                html_path, 
                args.items_per_page,
                config,
                logger
            )
        
        logger.info("Processing complete!")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        if not args.silent:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
