# Admission Scraper

A Python-based tool for scraping and processing university admission announcements.

## Project Overview

This project is designed to automate the collection, processing, and storage of university admission announcements. It uses web scraping techniques to gather information from university websites, processes the data using LLMs (specifically Google's Gemini), and stores structured information in a database.

## Architecture

The project is organized into several components:

- **Web Scraping**: Collects HTML content from university websites
- **LLM Processing**: Uses Google's Gemini to extract structured data from raw HTML
- **Database**: Stores processed announcements, programs, and institution information

## Data Processing Pipeline

1. **Data Collection**: Web pages are scraped and stored in a JSONL file (`pages.jsonl`)
2. **Data Extraction**: The HTML content is processed using Gemini to extract structured announcement data
3. **Data Storage**: Extracted announcements are stored in a database with proper relationships

## Data Scraping Process

The data scraping process follows these steps:

1. **Initial Scraping**: Web pages from university websites are scraped and their page content is stored in `pages.jsonl` with the following structure:
   - `context`: The text content having dates in it.
   - `url`: The source URL
   - `site`: The base website domain

2. **Information Extraction**:
   - The `process.py` script reads the JSONL file
   - It sends each page's content to Gemini via the `extract_with_gemini` function
   - Gemini analyzes the content and returns structured data about admission announcements

3. **Data Processing**:
   - For each extracted announcement, the system:
     - Identifies the associated institution based on the website URL
     - Processes the announcement details
     - Links the announcement with relevant academic programs
     - Stores everything in the database with proper relationships

4. **Database Structure**:
   - `Announcement`: Stores announcement details with links to institutions
   - `AnnouncementProgram`: Maps announcements to relevant academic programs
   - Additional tables for institutions, programs, and states

## Setup and Usage

### Prerequisites
- Python 3.8+
- PostgreSQL or compatible database

### Installation
1. Clone the repository
```bash
git clone <repository-url>
cd admission_scraper
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure database connection in the appropriate configuration file and seed the initial data

### Running the Scraper
```bash
scrapy crawl -o uni.json:json uni
scrapy crawl -o pages.jsonl:jsonl pages
python -m llm.process
```

## Project Structure
```
admission_scraper/
├── admission_scraper/  # Scrapy package dir
│   ├── uni.py          # Crawl's the site to match required pages
│   └── pages.py        # Extract context around regex matches with intelligent clustering and deduplication
├── db/
│   ├── models.py       # Database ORM models
│   ├── session.py      # Database connection management
│   └── data.py         # Data access functions
├── llm/
│   ├── gemini.py       # Google Gemini API integration
│   └── process.py      # Main processing script
├── pages.jsonl         # Raw scraped data
└── README.md           # This documentation
```

## Further Development

Potential areas for enhancement:
- Implementing incremental scraping
- Adding more LLM processors for comparison
- Creating a web interface for viewing and managing scraped data
- Extending to additional educational institutions
