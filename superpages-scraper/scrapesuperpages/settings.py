

BOT_NAME = "scrapesuperpages"

SPIDER_MODULES = ["scrapesuperpages.spiders"]
NEWSPIDER_MODULE = "scrapesuperpages.spiders"



ROBOTSTXT_OBEY = False


DOWNLOAD_DELAY = 3
RANDOMIZE_DOWNLOAD_DELAY = True

SPIDER_MIDDLEWARES = {
   "scrapesuperpages.middlewares.ScrapesuperpagesSpiderMiddleware": 543,
}


DOWNLOADER_MIDDLEWARES = {
   "scrapesuperpages.middlewares.ScrapesuperpagesDownloaderMiddleware": 542,
}



TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
