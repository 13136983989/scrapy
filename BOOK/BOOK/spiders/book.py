# -*- coding: utf-8 -*-
import scrapy
import json
from copy import deepcopy

class BookSpider(scrapy.Spider):
    name = 'book'
    allowed_domains = ['bookschina.com']
    start_urls = ['http://www.bookschina.com/books/kinder/']

    # 页数

    page = 0

    def parse(self, response):
        dt_list = response.xpath('//body/div/div/h2[1]')      #/h2[1] 只爬取第一个大分类
        # 遍历大分类
        print('*'*100)
        for dt in dt_list:
            item = {}

            item['category'] = dt.xpath('./a/text()').extract_first()  #大分类
            #print(item['category'])     #查看大类

            em_list = dt.xpath('./following-sibling::*[1]/li') #小分类

            for em in em_list:
                item['small_category'] = em.xpath('./a/text()').extract_first()
                #print(item['small_category'])    #查看小类
                small_link = 'http://www.bookschina.com' + em.xpath('./a/@href').extract_first()  #小分类跳转链接
                yield scrapy.Request(small_link, callback=self.parse_book, meta={'book': deepcopy(item)})


    def parse_book(self, response):

        item = response.meta['book']

        list_book = response.xpath('//*[@id="container"]/div/div/div/ul')  #页面所有的书

        #遍历解析：
        for book in list_book[:5]:
            #书名
            item['name'] = book.xpath('.//li/div/h2/a/text()').extract_first()

            item['author'] = book.xpath('.//li/div/div[1]/a[1]/text()').extract_first()

            item['store'] = book.xpath('.//li/div/div[1]/a[2]/text()').extract_first()

            item['price'] =book.xpath('.//li/div/div[2]/span[1]/text()').extract_first().strip('¥')

            item['dafault_image'] = book.xpath('.//li/div/a/img/@data-original').extract_first()

            print(item)   #查看item数据

            yield item

            # 发送请求图书的价格
            #yield scrapy.Request(price_url, callback=self.parse_price, meta={'book': deepcopy(item)})

            # item['name'] = book.xpath('.//li/div/h2/a/text()').extract_first()
            #
            # item['author'] = book.xpath('.//li/div/div[1]/a[1]/text()').extract_first()
            #
            # item['store'] = book.xpath('.//li/div/div[1]/a[2]/text()').extract_first()
            #
            # item['price'] =book.xpath('.//li/div/div[2]/span[1]/text()').extract_first()
            #                 #book.xpath('.//li/div/div[2]/span[1]/text()').extract_first()
            #
            # item['dafault_image'] = book.xpath('.//li/div/a/img/@data-original').extract_first()
            #


        # 只爬取 前4页-为了快速看结果
        self.page += 1
        if self.page > 4:
            return

        # 列表翻页
        # 1. 取出  下一页 标签 的 URL 网址不齐全
        next_url = response.xpath('//li[@class = "next"]//@href').extract_first()

        #print(next_url)

        # 2. 发送 下一页的请求 可以
        if next_url:  # 判断结束 如果 next_url 为none 就结束了
            yield response.follow(
                next_url,
                callback=self.parse_book,
                meta={'book': deepcopy(item)}
            )
