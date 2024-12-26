
from scrapy.http import HtmlResponse
from scrapy import signals
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import time


class YellowpagesSpiderMiddleware:

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        return None

    def process_spider_output(self, response, result, spider):
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        pass

    def process_start_requests(self, start_requests, spider):
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class YellowpagesDownloaderMiddleware:
    def __init__(self):
        # Configure Selenium WebDriver
        self.ua = UserAgent(os='windows', browsers=['edge', 'chrome'], min_percentage=1.3)
        self.options = Options()
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-notifications')
        self.options.add_argument('--incognito')
        self.options.add_argument('--no-sandbox')  # Helps with some environments (e.g., Docker)
        self.options.add_argument(f'user-agent={self.ua.random}')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)


    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        if not request.meta.get('use_selenium', False):
            return None

        spider.logger.info(f"Processing URL with Selenium: {request.url}")
        self.driver.get(request.url)

        time.sleep(3)

        return HtmlResponse(
            url=request.url,
            body=self.driver.page_source,
            encoding='utf-8',
            request=request
        )

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

    def __del__(self):
        # Ensure WebDriver is properly closed
        self.driver.quit()
