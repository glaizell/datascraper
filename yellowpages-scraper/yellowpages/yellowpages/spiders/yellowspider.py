
import scrapy
from scrapy_selenium import SeleniumRequest


class YellowspiderSpider(scrapy.Spider):
    name = "yellowspider"

    allowed_domains = ["www.yellowpages.com"]
    start_urls = [
        "https://www.yellowpages.com/search?search_terms=industrial%20equipment%20training&geo_location_terms=FL&page=1"
    ]


    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(
                url=url,
                callback=self.parse,
                meta={'use_selenium': True}
            )

    def parse(self, response):
        listings_data = response.css('div.srp-listing')
        for listing in listings_data:
            listing_url = listing.css('a.business-name::attr(href)').get()

            if listing_url:
                full_url = response.urljoin(listing_url)
                yield response.follow(
                    full_url,
                    callback=self.parse_listing,

                )

        next_page = response.css('li > a.next.ajax-page::attr(href)').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield response.follow(
                next_page_url,
                callback=self.parse,

            )

    def parse_listing(self, response):

        section_headers = response.css('#listing-card')
        business_name = section_headers.css('h1.business-name::text').get(default='Not found').strip()


        details_card = response.css('#details-card')
        website_url = details_card.css('p.website a::attr(href)').get(default='Not found')
        phone_number = details_card.css('p.phone::text').get(default='Not found').strip()
        address = details_card.css('p:contains("Address")::text').get(default='Serving the Miami Area').strip()


        if not address:
            address = 'Serving Miami Area'


        if website_url == 'Not found' or website_url is None:
            yield {
                'Business Name': business_name,
                'Website url': website_url,
                'Phone number': phone_number,
                'Address': address,
            }
