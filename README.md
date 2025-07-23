# 🎵 Discogs-linkout: a music collection processor

An enhanced Python tool for processing music collection exports with keyword generation, search link creation, and beautiful HTML report generation.

## ✨ Features

- **Smart column detection**: Automatically detects artist and title columns from various export formats.
- **Keyword generation**: Creates clean, search-friendly keywords from artist and album names.
- **Multiple search engines**: Generates clickable search links for Wikipedia, Spotify, YouTube, Discogs, AllMusic, and more.
- **Beautiful HTML reports**: Creates paginated, responsive HTML pages with clickable search links.
- **Robust error handling**: Handles various CSV formats, encodings, and missing data gracefully.
- **Configurable**: Customizable via JSON configuration file.
- **Collection agnostic**: Works with exports from Discogs, Last.fm, MusicBrainz, and custom formats.

## 🚀 Quickstart

### Installation

1. Clone the repo:
```bash
git clone https://github.com/lonestarmac/discogs-linkout.git
cd discogs linkout
```

2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

### Basic Usage

Process a Discogs export with default settings:
```bash
python3 collection_processor.py -i my_discogs_export.csv --html
```

Generate search links for multiple engines:
```bash
python3 collection_processor.py -i collection.csv --search wikipedia spotify youtube --html
```

## 📊 Supported Formats

The tool automatically detects columns from various music service exports:

| Service | Artist Column | Title Column |
|---------|---------------|--------------|
| Discogs | Artist | Title |
| Last.fm | artist | album |
| MusicBrainz | artist_name | release_title |
| Custom | (configurable) | (configurable) |

## 🔧 Command Line Options
We can't write a python script without a big ol' fatty CLI, right?
TODO: Make it 1980's termainal-fantastic...

```
usage: collection_processor.py [-h] [-i INPUT] [-o OUTPUT] [--artist ARTIST] 
                               [--title TITLE] [--search SEARCH [SEARCH ...]]
                               [--max-keywords MAX_KEYWORDS] [--csv] [--html]
                               [--items-per-page ITEMS_PER_PAGE] [--config CONFIG]
                               [--save-config] [--list-engines] [-s] 
                               [--log-file LOG_FILE] [--version]

Enhanced Music Collection Processor

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input CSV file
  -o OUTPUT, --output OUTPUT
                        Output file prefix (without extension)
  --artist ARTIST       Artist column name
  --title TITLE         Title column name
  --search SEARCH [SEARCH ...]
                        Search engines to generate links for
  --max-keywords MAX_KEYWORDS
                        Maximum number of keywords
  --csv                 Generate CSV output
  --html                Generate HTML output
  --items-per-page ITEMS_PER_PAGE
                        Items per HTML page
  --config CONFIG       Configuration file path
  --save-config         Save current settings as default
  --list-engines        List available search engines
  -s, --silent          Suppress console output
  --log-file LOG_FILE   Log file path
  --version             show program's version number and exit
```

## 🔍 Available Search Engines

List all available search engines:
```bash
python3 collection_processor.py --list-engines
```

Current options:
- **wikipedia**: Wikipedia search
- **spotify**: Spotify search
- **youtube**: YouTube search
- **discogs**: Discogs database search
- **allmusic**: AllMusic search
- **musicbrainz**: MusicBrainz search
- **genius**: Genius lyrics search
- **rateyourmusic**: Rate Your Music search
- **google**: Google search with "album" modifier

  TODO: Ask the user what they're trying to do, and then use API calls to pull the data into the CSV instead of making them do it all manually.

## ⚙️ Configuration

Create a `config.json` file to customize default settings:

```json
{
  "max_keywords": 5,
  "default_search_engine": "wikipedia",
  "html_items_per_page": 50,
  "artist_columns": ["Artist", "artist", "Artist Name", "Performer"],
  "title_columns": ["Title", "Album", "Release Title", "Track"],
  "stopwords": ["the", "a", "an", "remaster", "deluxe", "edition"]
}
```

Save your current command-line settings as defaults:
```bash
python3 collection_processor.py --save-config
```

## 📋 Examples

### Process Discogs Export
```bash
# Basic processing with HTML output
python3 collection_processor.py -i discogs_20250723.csv --html

# Multiple search engines
python3 collection_processor.py -i discogs_export.csv --search wikipedia spotify discogs --html
```

### Process Last.fm Export
```bash
# Specify column names for Last.fm format
python3 collection_processor.py -i lastfm_library.csv --artist "artist" --title "album" --html
```

### Custom Processing
```bash
# Custom columns and output location
python3 collection_processor.py -i my_music.csv --artist "Band Name" --title "Album Title" -o processed_collection --html

# Large collection with smaller page sizes
python3 collection_processor.py -i huge_collection.csv --html --items-per-page 50
```

## 📁 Output Files

The tool generates several output files:

### CSV Output (`collection_processed.csv`)
Enhanced CSV with additional columns:
- `Keywords`: Clean search terms
- `Wikipedia_Link`: Wikipedia search URL
- `Spotify_Link`: Spotify search URL (if requested)
- `Search_Link`: Primary search engine link

### HTML Output (`collection_processed.html`)
Beautiful, responsive web pages featuring:
- **Grid Layout**: Clean card-based display
- **Clickable Links**: Direct access to search engines
- **Pagination**: Manageable page sizes for large collections
- **Mobile Responsive**: Works on all device sizes
- **Search Integration**: Multiple search engine buttons per album

TODO: Build yet another "Pretty Discogs Collection" HTML page people can share because [there's only 3,451 of them already](https://xkcd.com/927/)...

### Log File (`collection_processor.log`)
Detailed processing log with:
- Column detection results
- Processing statistics
- Error messages and warnings
- Performance metrics

## 🎶 Use Cases

### Music Discovery
- Generate Wikipedia links to learn about albums in your collection
- Quick access to Spotify for listening
- YouTube links for music videos and reviews
- 🏴‍☠️☠️?

### Collection Management
- Clean keyword generation for cataloging
- Multiple search engines for research
- HTML reports for sharing your collection

### Data Analysis
- Export enhanced CSV data for further analysis
- Standardized keywords for search and filtering
- Link generation for automated workflows

## 🛠️ Advanced Features

### "Automatic" Column Detection
The tool intelligently detects artist and title columns from common export formats:

```python
# Looks for these artist column variations:
["Artist", "artist", "Artist Name", "artist_name", "Performer"]

# Looks for these title column variations:
["Title", "title", "Album", "album", "Release Title", "release_title"]
```

### Smart Keyword Generation
- Removes parenthetical information: `"The Beatles (Remastered)"` → `"beatles"`
- Filters common stopwords: `"The Dark Side of the Moon"` → `"dark side moon"`
- Handles "Various Artists" collections appropriately
- Prioritizes artist name in keyword selection
- Removes duplicate words while preserving order

### Error Recovery
- Multiple encoding attempts (UTF-8, Latin-1)
- Graceful handling of missing columns
- Robust text cleaning and normalization
- Detailed error logging

## 🔮 Future Enhancements

### Planned Features
- **Discogs API Integration**: Direct collection import from Discogs
- **GitHub Pages Hosting**: Web-based collection processor
- **Additional Export Formats**: JSON, XML output options
- **Album Art Integration**: Fetch and display cover images
- **Advanced Filtering**: Genre, year, rating-based filtering
- **Batch Processing**: Multiple file processing
- **Custom Search Engines**: User-defined search URL templates

### Contributing
We welcome contributions! Areas where help is needed:
- Additional music service export format support
- New search engine integrations
- UI/UX improvements for HTML output
- Performance optimizations
- Documentation improvements

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Python and Pandas
- Inspired by the need for better music collection management
- Thanks to the music community for feedback and suggestions

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/music-collection-processor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/music-collection-processor/discussions)
- **Documentation**: This README and inline help (`--help`)

---

**Happy music exploring!** 🎵
