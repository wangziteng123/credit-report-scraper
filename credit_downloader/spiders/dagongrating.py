# -*- coding: utf-8 -*-
import datetime
import scrapy
from credit_downloader import items


class DagongratingSpider(scrapy.Spider):
    ''' 爬取大公资信 '''
    name = 'dagongrating'
    allowed_domains = ['dagongcredit.com']
    start_urls = [
        'http://www.dagongcredit.com/index.php?m=content&c=index&a=lists&catid=159',
        'http://www.dagongcredit.com/index.php?m=content&c=index&a=lists&catid=79',
        'http://www.dagongcredit.com/index.php?m=content&c=index&a=lists&catid=80',
        'http://www.dagongcredit.com/index.php?m=content&c=index&a=lists&catid=81',
        'http://www.dagongcredit.com/index.php?m=content&c=index&a=lists&catid=82',
        'http://www.dagongcredit.com/index.php?m=content&c=index&a=lists&catid=83'
    ]
    data_type = 'official'
    download_timeout = 300

    def parse(self, response):
        ''' 入口. 拿到各个种类的评级公告入口 '''
        for cat_link in response.css('.youjian.lis a:not(.gy-active)::attr(href)').extract():
            yield scrapy.Request(url=response.urljoin(cat_link), callback=self.parse_page)

    def parse_page(self, response):
        ''' 每种评级公告, 拿到它们的翻页链接, 评级基本信息, 文件链接. '''
        # paging
        for pag_link in response.css('.pagination a:not(.a1)::attr(href)').extract():
            yield scrapy.Request(url=response.urljoin(pag_link), callback=self.parse_page)

        category = response.css('.gy-active::text')[-1].extract()
        # meta
        for li in response.css('.list.lh24.f14 li'):
            rating = li.css('.rt.rt-red::text').extract_first()
            name = li.css('.rt-a::text').extract_first()
            pub_time = li.css('.rt.rt-time::text').extract_first() + '-00-00-00'
            fet_time = datetime.datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')
            file_urls = [li.css('.rt-a::attr(href)').extract_first()]
            status = 'init'

            if file_urls == ['']:
                file_urls = []
                status = 'missing'
                self.logger.error('No url found for %s, check page %s' % (name, response.url))

            # 导出爬取信息, 交给pipeline下载文件
            yield items.CreditDownloaderItem(
                id_=category+'-'+name,
                name=name,
                source=self.name,
                category=category,
                rating=rating,
                pub_time=pub_time,
                fet_time=fet_time,
                files=[],
                file_urls=file_urls,
                status=status
            )
