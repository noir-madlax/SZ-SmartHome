# Discourse Forum Crawler (Home Assistant Community)

A Scrapy-based crawler tailored for Discourse forums like `community.home-assistant.io`.

## Features
- Crawl a single topic URL (e.g., `https://community.home-assistant.io/t/emhass-an-energy-management-for-home-assistant/338126/6`)
- Extract topic (post) and replies with pagination
- Output JSON and merged TXT per topic
- Anti-ban basics: rotating User-Agent, polite delays, caching

## Install
```bash
pip install -r requirements.txt
```

## Usage
```bash
# Crawl a single Discourse topic (all pages)
python run.py --url "https://community.home-assistant.io/t/emhass-an-energy-management-for-home-assistant/338126/6" --replies 100

# Show help
python run.py --help
```

Outputs are saved under `output/Home Assistant Community/<topicId>_<title>/完整内容.txt` and `output/{posts,replies}.json`.

## Notes
- This crawler focuses on Discourse HTML structure and may need selector tweaks if the forum theme changes.
- Respect the website's ToS and crawl responsibly.
