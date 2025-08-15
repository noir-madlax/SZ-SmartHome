import argparse
import os
import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def main():
	parser = argparse.ArgumentParser(description="Run Discourse crawler")
	parser.add_argument("--url", type=str, help="Single Discourse topic URL to crawl", required=False)
	parser.add_argument("--pages", type=int, default=1, help="Max list pages (unused in single-url mode)")
	parser.add_argument("--replies", type=int, default=100, help="Max replies per topic")
	parser.add_argument("--delay", type=float, default=1.5, help="Download delay seconds")
	parser.add_argument("--debug", action="store_true", help="Enable debug logging")
	parser.add_argument("--list", choices=["latest"], help="Crawl a listing instead of a single topic", required=False)
	parser.add_argument("--limit", type=int, default=200, help="Max items for listing crawls")
	args = parser.parse_args()

	os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "discourse_spider.settings")
	settings = get_project_settings()

	# Override some runtime settings
	settings.set("DOWNLOAD_DELAY", args.delay, priority='cmdline')
	settings.set("CUSTOM_SETTINGS", {
		"MAX_REPLIES_PER_POST": args.replies,
		"OUTPUT_DIR": "output",
		"FORUM_NAME": "Home Assistant Community",
	}, priority='cmdline')
	if args.debug:
		settings.set("LOG_LEVEL", "DEBUG", priority='cmdline')

	process = CrawlerProcess(settings)

	if args.list == "latest":
		from discourse_spider.spiders.latest_topics import LatestTopicsSpider
		process.crawl(LatestTopicsSpider, limit=args.limit)
		process.start()
		return 0

	from discourse_spider.spiders.discourse_topic import DiscourseTopicSpider

	if args.url:
		process.crawl(DiscourseTopicSpider, url=args.url)
	else:
		print("Please provide --url for Discourse topic crawling or use --list latest", file=sys.stderr)
		return 1

	process.start()
	return 0


if __name__ == "__main__":
	sys.exit(main())
