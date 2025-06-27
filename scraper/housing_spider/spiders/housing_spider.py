import scrapy
from ..items import HousingSpiderItem
from datetime import datetime
import os

class HousingSpider(scrapy.Spider):
    name = "housing_spider"
    allowed_domains = []
    start_urls = []

    def start_requests(self):
        # 读取本地 mock_data.html 文件
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        html_path = os.path.join(base_dir, 'scraper', 'mock_data.html')
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        yield scrapy.http.TextResponse(url='file://' + html_path, body=html_content, encoding='utf-8')

    def parse(self, response):
        today_str = datetime.now().strftime('%Y-%m-%d')
        for city_sel in response.css('div.city-data'):
            city_name = city_sel.css('h2::text').get()
            for row in city_sel.css('table tbody tr'):
                area = row.css('td:nth-child(1)::text').get().strip()
                price = int(row.css('td:nth-child(2)::text').get().strip())
                item = HousingSpiderItem(
                    city=city_name,
                    area=area,
                    price=price,
                    date=today_str
                )
                yield item
