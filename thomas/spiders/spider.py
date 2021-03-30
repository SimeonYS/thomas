import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import ThomasItem
from itemloaders.processors import TakeFirst
import requests
import json

pattern = r'(\xa0)?'
url = "https://www.thomastonsavingsbank.com/json/news-articles"

payload = "parent=183&page={}&category="
headers = {
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    'Accept': '*/*',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://www.thomastonsavingsbank.com',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://www.thomastonsavingsbank.com/news',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cookie': 'COCC_WebHosting=u0021FAi2+GbHmh+tIe6yJVTMCrvFtENQ99Pxku3uWDgUGuKS4lfFAOxsXxsOcGYNgPR3YJN9OSbB2BIdykewl0vzulZpAQSeztma+aVjrr4=; _ga=GA1.2.2072095109.1617094831; _gid=GA1.2.1323668355.1617094831; _hjTLDTest=1; _hjid=42428cce-ef7f-4afc-abe9-87b5c37e19bb; _hjFirstSeen=1; _hjIncludedInPageviewSample=1; _hjAbsoluteSessionInProgress=0; _hjIncludedInSessionSample=1; _uetsid=61c43110913611ebb46677ac5df96a9a; _uetvid=61c47d10913611eba10fad48765cf5ea; COCC_WebHosting=!V0WMeqP9WyKBH5GyJVTMCrvFtENQ9zA9waaBqSq8JNcFloIU9XkjrmNmHdAud1n6HMUgzcBsq7ICkfg4/SmorEXjedO7ZP+mGikmNZc='
}


class ThomasSpider(scrapy.Spider):
    name = 'thomas'
    page = 1
    start_urls = ['https://www.thomastonsavingsbank.com/news']

    def parse(self, response):
        data = requests.request("POST", url, headers=headers, data=payload.format(self.page))
        data = json.loads(data.text)
        for index in range(len(data['results'])):
            link = data['results'][index]['url']
            yield response.follow(link, self.parse_post)
        if not self.page == data['pages']:
            self.page += 1
            yield response.follow(response.url, self.parse, dont_filter=True)

    def parse_post(self, response):
        date = response.xpath('//h2/text()').get()
        title = response.xpath('//h1/text()').get()
        content = response.xpath('//div[@class="col-sm-6 col-md-7 col-sm-push-6 col-md-push-5"]//text() |//div[@class="col-sm-12"]//text()').getall()
        content = [p.strip() for p in content if p.strip()]
        content = re.sub(pattern, "",' '.join(content))

        item = ItemLoader(item=ThomasItem(), response=response)
        item.default_output_processor = TakeFirst()

        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('date', date)

        yield item.load_item()
