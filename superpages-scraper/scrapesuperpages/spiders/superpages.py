import scrapy
from scrapy import signals


class SuperpagesSpider(scrapy.Spider):
    name = "superpages"
    allowed_domains = ["superpages.com"]
    start_urls = [
        "https://www.superpages.com/search?search_terms=industrial%20equipment%20training&geo_location_terms=FL&refinements=headingtext%3AIndustrial%2C%20Technical%20%26%20Trade%20Schools&refinements=headingtext%3ATraining%20Consultants&page=1"]
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(SuperpagesSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.item_scraped_signal, signal=signals.item_scraped)
        spider.raw_item_count = 0
        return spider
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
            )
    def parse(self, response):


        listings = response.css('.srp-listing')

        for listing in listings:
            self.raw_item_count += 1

            business_name = listing.css('a.business-name > span::text').get(default="Not Found")
            website = listing.css('a.weblink-button::attr(href)').get(default="Not Found")
            contact_number = listing.css("a.phones.primary span.call-number::text").get(default="Not Found")
            address = listing.css("p.adr span.street-address::text").get(default="Not Found")

            if website == "Not Found" or website is None:
                yield {
                    "Business name": business_name,
                    "Website": website,
                    "Contact Number": contact_number,
                    "Address": address
                }

        next_page = response.css('li > a.next.ajax-page::attr(href)').get()
        if next_page:
            yield response.follow(
                next_page,
                callback=self.parse, )

    def item_scraped_signal(self, item, response, spider):
        """Signal handler for each scraped item."""
        self.logger.info(f"Raw item count (before filtering): {self.raw_item_count}")

    def close(self, reason):
        """Log final count when the spider closes."""
        self.logger.info(f"Total raw items processed (before filtering): {self.raw_item_count}")
