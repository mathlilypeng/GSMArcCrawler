__author__ = 'yupeng'

import urllib2
import re
from objects import Brand, Phone
from scrapy.selector import Selector
from HTMLParser import HTMLParser

class GSMArc_Spider:
    def __init__(self):
        self.home_url = "http://www.gsmarc.com/all-brands"
        self.brandlist = [] # list of Brand object
        self.phonelist = [] # list of Phone object

    # get information of mobile phone brands, brand name and url
    def get_brands(self):
        unexpect_parser = HTMLParser()
        req = urllib2.Request(self.home_url)
        print "***Searching for mobile phone brands and manufacturers on the website %s " \
              "...***" % self.home_url
        # crawl the whole page
        response = urllib2.urlopen(req).read().decode("utf-8")
        # get the list of mobile phone brands & manufacturers
        sel = Selector(text=response)
        items = sel.xpath(r'//div[@class="brandlist"]//li')
        # collect information of brand name and brand url for all the brands
        print "----------%d Mobile Phone Brands and Manufacturers Detected:----------" %len(items)
        for i, item in  enumerate(items):
            #content = item.re(r'<a href="(http.*?)">.*?<span>(.*?)</span>')
            brand_url = item.xpath('a/@href').extract()
            brand_name = item.xpath('a/span/text()').extract()
            if brand_name and brand_url:
                newBrand = Brand()
                newBrand.set_url(brand_url[0])
                newBrand.set_name(brand_name[0])
                self.brandlist.append(newBrand)
                print "%d: %s" %(i+1, newBrand.get_name())
        print "-----------------------------------------------------------------------\n"

    # get information of mobile phones under a specific brand
    def get_phoneInf(self, brand):
        """
        :param brand: Brand object
        :return: void
        """
        print "***Searching for %s...***\n" %brand.get_name()
        req = urllib2.Request(brand.get_url())
        response = urllib2.urlopen(req).read().decode("utf-8")

        sel = Selector(text=response)
        items = sel.xpath('//div[@class="brand_listbox"]//li')
        for item in items:
            #content = item.re('<a href="(.*?)" title=".*?">.*?<span.*?>(.*?)</span>')
            phone_url = item.xpath('a/@href').extract()
            phone_id = item.xpath('a/span/text()').extract()
            if phone_url and phone_id:
                newPhone = Phone()
                newPhone.set_brand(brand.get_name())
                newPhone.set_url(phone_url[0].strip())
                newPhone.set_id(phone_id[0].strip().lower())
                self.phonelist.append(newPhone)
                print newPhone.get_id()

                # Collect detailed information of the phone
                self.get_details(newPhone)

            #self.get_details(newPhone)

    def get_details(self, phone):
        """
        :param phone: Phone object
        :return:
        """
        print "Detailed info of %s:" %phone.get_id()
        req = urllib2.Request(phone.get_url())
        response = urllib2.urlopen(req).read().decode("utf-8")

        #get the overview information of the phone
        sel = Selector(text=response)
        self.get_overviewInf(sel.xpath('//div[@class="overview"]/div[@class="ph_info"]/table//tr'))
        #phone.set_overview(self.overviewInf(sel.xpath('//div[@class="ph_info"]//tr')))

    def get_overviewInf(self, overview):
        """
        :param overview: html modular for phone overview
        :return: dictionary
        """
        overview_dict = dict()
        for item in overview:
            attr = item.xpath('th/text()')
            val = item.xpath('td')
            if attr and val:
                attr = attr.extract()[0].strip().lower().replace(' ','_')
                val = re.sub('<.*?>|\(|\)',"", val[-1].extract().strip().lower())

                if len(attr) == 0:
                    if('rating' in val):
                        attr = "score"
                        val = item.xpath('th/div/@title').extract()[0]
                    else:
                        print "Error Detected!! --%s" %item

                overview_dict[attr] = val
                print "%s, %s" %(attr, overview_dict.get(attr))





    def run(self):
        self.get_brands()
        self.get_phoneInf(self.brandlist[0])

myspider = GSMArc_Spider()
myspider.run()
