# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from webdriver_manager.chrome import ChromeDriverManager



class ScrapesuperpagesSpiderMiddleware:

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


class ScrapesuperpagesDownloaderMiddleware:
    def __init__(self):
        self.ua = UserAgent(os='windows', browsers=['edge', 'chrome'], min_percentage=1.3)
        self._initialize_driver()

    def _initialize_driver(self):
        """Initialize Selenium WebDriver with default options."""
        self.options = Options()
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-notifications')
        self.options.add_argument('--incognito')
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option("useAutomationExtension", False)

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=self.options
        )

    def _update_user_agent(self):
        """Dynamically set a new User-Agent without restarting the driver."""
        user_agent = self.ua.random
        self.driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": user_agent})
        return user_agent

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    def process_request(self, request, spider):
        spider.logger.info(f"Using Selenium to fetch: {request.url}")

        try:
            user_agent = self._update_user_agent()
            spider.logger.info(f"User-Agent set to: {user_agent}")
            self.driver.get(request.url)

            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".srp-listing"))
            )

            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            body = self.driver.page_source

            return HtmlResponse(
                url=self.driver.current_url,
                body=body,
                encoding="utf-8",
                request=request,
            )
        except WebDriverException as e:
            spider.logger.error(f"WebDriver error for {request.url}: {e}")

            return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

    def spider_closed(self, spider):
        spider.logger.info("Closing Selenium WebDriver")
        self.driver.quit()