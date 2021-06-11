# -*- coding: utf-8 -*-
import scrapy
from hw2.items import Hw2Item


class Hw2botSpider(scrapy.Spider):
    name = 'hw2bot'
    allowed_domains = ['quanshuwang.com']
    pagenum = 1
    start_urls = ['http://www.quanshuwang.com/list/5_%d.html' % pagenum]###用占位符形式较简便
    # missnum = 800###为了补上昨天宕掉的第26页###

    def parse(self, response):
        num = 100##################*用来设置scrapy.Request里的priority，防止漏爬&乱序####################
        for novel in response.xpath('//*[@id="navList"]/section/ul/li'):###不知道为什么这样只能出第一本书###是因为应该一直到li呀！你之前只到section或者ul怎么行呢，只循环一次呀，只有一个ul呀！# for n in range(1,33):#####用n循环有个问题是最后一页只有30个没有32个。所以还是用for book循环，到li就没问题了呀！
            num += -1
            item = Hw2Item()
            item['book'] = novel.xpath('span/a[1]/@title' ).get(),######拿出a标签的title属性要/@有斜杠！#######item[key]=value是一个字典的过程
            item['author'] = novel.xpath('span/a[2]/text()' ).get(),##########book.xpath是接着上面的section/ul/li往下
            # yield item#要注释掉不然会输出混乱#

        ##############对这本novel再点进去看它的详细信息bookintro，latestchapter和updatetime##############
            bookdetail_link = novel.xpath('span/a[1]/@href').get()
            yield scrapy.Request(bookdetail_link, meta={'item': item}, priority = num, callback = self.parse_bookdetail)
        #############*用priority解决乱序问题！优先级高的先被处理！哭了终于把这问题解决了qaq###################

        ########但是follow_all出来的内容是随机的排序，弃########
        # bookdetail_links = response.xpath('//*[@id="navList"]/section/ul/li/a/@href').getall()
        # for i in range(len(bookdetail_links)):
        #     yield  response.follow(bookdetail_links[i], priority = 100-i, callback = self.parse_bookdetail)
        #############或许这样加入priority可以解决乱序问题？使用这个能否提高爬虫速度？########################


        ##############下一页操作（一）################但是follow_all出来的内容是随机的排序，弃##############
        # pagination_links = response.xpath('//*[@id="pagelink"]/a[@class="next"]')#######单引号里面要双引号！
        # yield from response.follow_all(pagination_links,self.parse)
        #############同上的问题#################

        #############下一页操作（二）############################
        if self.pagenum < 128:
            self.pagenum += 1
            url = 'http://www.quanshuwang.com/list/5_%d.html' % self.pagenum   ####pagenum要加self.
            yield scrapy.Request(url, callback = self.parse)


    def parse_bookdetail(self,response):

        ##############用meta在不同parse函数(request)之间传递变量################
        item = response.meta['item']

        #####getall返回列表所以用“”.join转换成字符串#############不用and连接div下的text和div下br下的text！用div//text()就好啦！双斜杠！#####
        ##############\n无法在json中显示为换行怎么办：试一下<br/>##########乱码用replace处理##############
        item['bookintro'] = "\n".join("".join(response.xpath('//*[@id="waa"]//text()').getall()).replace("\xa0","").replace("\n"," ").split())

        ##############！列表list无法存入mysql，须','.join()转换成字符串，用时再.split(',')按逗号split成列表即可##################
        item['latestchapter'] = ','.join(response.xpath('//*[@id="container"]/div[2]/section/div/div[4]/div[1]/dl[3]/dd/ul/li/a/text()').getall()) ####有7个li里的a的text，不用占位符li[%d]！直接li/a/text()然后getall就可以了！！！！得到7个text的列表
        item['updatetime'] = ','.join(response.xpath('//*[@id="container"]/div[2]/section/div/div[4]/div[1]/dl[3]/dd/ul/li/text()' ).getall())  ####每个li里的text

        # self.missnum += 1###为了补上昨天宕掉的第26页###
        # item['id'] = str(self.missnum)###为了补上昨天宕掉的第26页###
        yield item

