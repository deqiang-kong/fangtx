# **************************************************
# File Name: spiders/fang.py
# Author: kongdq
# Email: 452211588@qq.com
# Created: 2018-01
# Description: 地区信息数据爬去。包括省份，城市
# **************************************************

import scrapy
import re
from scrapy_redis.spiders import RedisSpider

from fangtx.items import NewHouseItem, ESFHouseItem
from fangtx.utils.strutil import getStrAll


class FangSpider(scrapy.Spider):
    # 爬虫名称
    name = "fang"
    # 可选，筛选器，允许域范围
    allowd_domains = ['fang.com']
    #
    redis_key = "fang:start_urls"

    start_urls = ['http://www.fang.com/SoufunFamily.htm']

    # 城市信息获取
    def parse(self, response):
        print("\n" + self.name + " ---------------start")
        trs = response.xpath("//div[@class='outCont']//tr")
        province = None
        for tr in trs:
            tds = tr.xpath(".//td[not(@class)]")
            province_td = tds[0]
            province_text = province_td.xpath(".//text()").get()
            # 省份信息获取
            province_text = re.sub(r"\s", "", province_text)

            if province_text:
                province = province_text

            # 排除国外其他
            if province == '其它':
                continue

            city_td = tds[1]
            city_links = city_td.xpath(".//a")
            for city_link in city_links:
                city = city_link.xpath(".//text()").get()
                city_url = city_link.xpath(".//@href").get()
                url_info = city_url.split("//")
                url0 = url_info[0]
                url1 = url_info[1]
                # 北京特殊处理
                if 'bj.' in url1:
                    new_house_url = 'http://newhouse.fang.com/house/s/'
                    esf_house_url = 'http://esf.fang.com/'
                else:
                    # 判断url尾部有没有'/'
                    temp = url1[-1]
                    if temp is not '/':
                        url1 = url1 + '/'
                    new_house_url = url0 + "//" + "newhouse." + url1 + "house/s/"
                    esf_house_url = url0 + "//" + "esf." + url1

                print('省份：' + province)
                print('城市：' + city)
                print(city + 'url：' + city_url)
                print(city + '新房：' + new_house_url)
                print(city + '二手：' + esf_house_url)

                # 设置要爬取的城市，便于测试
                crawlCity = ['北京']
                # 爬取指定城市信息
                if city in crawlCity:
                    # 新房信息：追加爬取的RUL,交给调度器
                    # yield scrapy.Request(new_house_url, callback=self.parse_newhouse, meta={"info": (province, city)})
                    # 二手房信息：追加爬取的RUL,交给调度器
                    yield scrapy.Request(esf_house_url, callback=self.parse_esf, meta={'info': (province, city)})

                # 新房信息：追加爬取的RUL,交给调度器
                # yield scrapy.Request(new_house_url, callback=self.parse_newhouse, meta={"info": (province, city)})
                # # 二手房信息：追加爬取的RUL,交给调度器
                # yield scrapy.Request(esf_house_url, callback=self.parse_esf, meta={'info': (province, city)})

        print("\n" + self.name + " ---------------end")

    page_new = 0
    index_new = 0
    page_esf = 0
    index_esf = 0

    # 新房数据获取
    def parse_newhouse(self, response):
        province, city = response.meta.get("info")
        print("\n" + city + " newhouse---------------start")
        lis = response.xpath("//div[contains(@class,'nl_con')]/ul/li")
        for li in lis:
            community = li.xpath(".//div[@class='nlcd_name']/a/text()").get()
            if community is None:
                continue
            community = community.strip()
            house_type_list = li.xpath(".//div[contains(@class,'house_type')]/a/text()").getall()
            house_type_list = list(map(lambda x: re.sub(r"\s", "", x), house_type_list))
            rooms = list(filter(lambda x: x.endswith("居"), house_type_list))

            area = "".join(li.xpath(".//div[contains(@class,'house_type')]/text()").getall())
            area = re.sub(r"\s|－|/", "", area)
            address = li.xpath(".//div[@class='address']/a/@title").get()
            district_text = "".join(li.xpath(".//div[@class='address']/a//text()").getall())
            try:
                district = re.search(r".*\[(.+)\].*", district_text).group(1)
            except Exception as e:
                print(district_text)
                district = ''
            sale = li.xpath(".//div[contains(@class,'fangyuan')]/span/text()").get()
            price = "".join(li.xpath(".//div[@class='nhouse_price']//text()").getall())
            price = re.sub(r"\s|广告", "", price)
            origin_url = li.xpath(".//div[@class='nlcd_name']/a/@href").get()

            item = NewHouseItem(community=community, rooms=getStrAll(rooms), area=area, address=address, district=district, sale=sale,
                                price=price, origin_url=origin_url, province=province, city=city)
            self.index_new = self.index_new + 1
            yield item

        # 下一页,交给调度器
        next_urls = lis.xpath("//div[@class='page']//a[@class='next']/@href").extract()
        print(next_urls)
        if len(next_urls) > 0:
            next_url = next_urls[-1]
            yield scrapy.Request(url=response.urljoin(next_url), callback=self.parse_newhouse,
                                 meta={"info": (province, city)})
        else:
            print("\n" + city + " newhouse-------没有数据了！！！！")

        self.page_new = self.page_new + 1
        print("page:" + str(self.page_new) + " index:" + str(self.index_new))
        print("\n" + city + " newhouse---------------end")

    #
    # 二手房数据获取
    def parse_esf(self, response):
        province, city = response.meta.get("info")
        print("\n" + city + " esf---------------start")
        dls = response.xpath("//div[@class='houseList']/dl")
        for dl in dls:
            item = ESFHouseItem(province=province, city=city)
            item['community'] = dl.xpath(".//p[@class='mt10']/a/span/text()").get()
            infos = dl.xpath(".//p[@class='mt12']/text()").getall()
            infos = list(map(lambda x: re.sub(r"\s", "", x), infos))
            for info in infos:
                if "厅" in info:
                    item['rooms'] = info
                elif '层' in info:
                    item['floor'] = info
                elif '向' in info:
                    item['toward'] = info
                else:
                    item['construct'] = info.replace("建筑年代：", "")
            item['address'] = dl.xpath(".//p[@class='mt10']/span/@title").get()
            item['area'] = dl.xpath(".//div[contains(@class,'area')]/p/text()").get()
            item['price'] = "".join(dl.xpath(".//div[@class='moreInfo']/p[1]//text()").getall())
            item['unit'] = "".join(dl.xpath(".//div[@class='moreInfo']/p[2]//text()").getall())
            detail_url = dl.xpath(".//p[@class='title']/a/@href").get()
            item['origin_url'] = response.urljoin(detail_url)
            yield item

        # 下一页,交给调度器
        next_url = response.xpath("//a[@id='PageControl1_hlk_next']/@href").get()
        yield scrapy.Request(url=response.urljoin(next_url), callback=self.parse_esf, meta={"info": (province, city)})
        self.page_esf = self.page_esf + 1
        print("page:" + str(self.page_esf))
        print("\n" + city + " esf---------------end")
