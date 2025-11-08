import scrapy

class NtaSpider(scrapy.Spider):
    name = "nta"
    allowed_domains = ["nta.ac.in"]
    start_urls = ["https://nta.ac.in/PublicNotice"]

    def parse(self, response):
        # Scrape public notices table or links
        notices = response.css('table tbody tr')
        for notice in notices:
            title = notice.css('td:nth-child(2) a::text').get()
            link = notice.css('td:nth-child(2) a::attr(href)').get()
            date = notice.css('td:nth-child(3)::text').get()
            if title and link:
                yield {
                    'title': title.strip(),
                    'link': response.urljoin(link),
                    'date': date.strip() if date else None,
                    'source': 'NTA'
                }
