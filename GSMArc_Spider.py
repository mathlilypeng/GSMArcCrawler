__author__ = 'yupeng'

import urllib2
import re
from objects import Brand, Phone
from scrapy.selector import Selector


class GSMArcSpider:
    def __init__(self):
        self.home_url = "http://www.gsmarc.com/all-brands"
        self.brandlist = []  # list of Brand object
        self.phonelist = []  # list of Phone object

    # get information of mobile phone brands, brand name and url
    def get_brands(self):
        req = urllib2.Request(self.home_url)
        print "***Searching for mobile phone brands and manufacturers on the website %s " \
              "...***" % self.home_url
        # crawl the whole page
        response = urllib2.urlopen(req).read().decode("utf-8")
        # get the list of mobile phone brands & manufacturers
        sel = Selector(text=response, type="html")
        items = sel.xpath('//div[@class="brandlist"]//li')
        # collect information of brand name and brand url for all the brands
        print "----------%d Mobile Phone Brands and Manufacturers Detected:----------" % len(items)
        for i, item in enumerate(items):
            # content = item.re(r'<a href="(http.*?)">.*?<span>(.*?)</span>')
            brand_url = item.xpath('a/@href').extract()
            brand_name = item.xpath('a/img/@alt').extract()
            if brand_url and brand_name:
                new_brand = Brand()
                new_brand.set_url(brand_url[0])
                new_brand.set_name(brand_name[0].strip().lower())
                self.brandlist.append(new_brand)
                print "%d: %s" % (i + 1, new_brand.get_name())
        print "-----------------------------------------------------------------------\n"

    # get information of mobile phones under a specific brand
    def get_phone_info(self, brand):
        """
        :param brand: Brand object
        :return: void
        """
        print "***Searching for %s...***\n" % brand.get_name()
        req = urllib2.Request(brand.get_url())
        response = urllib2.urlopen(req).read().decode("utf-8")

        sel = Selector(text=response, type="html")
        items = sel.xpath('//div[@class="brand_listbox"]//li')
        for item in items:
            # content = item.re('<a href="(.*?)" title=".*?">.*?<span.*?>(.*?)</span>')
            phone_url = item.xpath('a/@href').extract()
            phone_id = item.xpath('a/span/text()').extract()
            if phone_url and phone_id:
                new_phone = Phone()
                new_phone.set_brand(brand.get_name())
                new_phone.set_url(phone_url[0].strip())
                new_phone.set_id(phone_id[0].strip().lower())

                print "---Detailed info for %s:---" % new_phone.get_id()

                # Collect detailed information of the phone
                self.get_phone_details(new_phone)
                print "------------------------------------------------"
                self.phonelist.append(new_phone)

    def get_phone_details(self, phone):
        """
        :param phone: Phone object
        :return:
        """
        req = urllib2.Request(phone.get_url())
        response = urllib2.urlopen(req).read().decode("utf-8")
        sel = Selector(text=response, type="html")

        # get the overview information of the phone
        phone.set_overview(self.get_phone_overview_inf(sel.xpath('//div[@class="overview"]/'
                                                                 'div[@class="ph_info"]/table')))
        # get the Popularity and Rating info
        phone.set_rating(self.get_rating_info(sel.xpath('//div[@class="ph_rateing"]')))

        # get the Specifications
        for info_row in sel.xpath('//div[@class="info_row"]'):
            if info_row.xpath('.//table'):
                print "\n"
                self.get_table_info(info_row)

    # get the overview information for the selected mobile phone
    def get_phone_overview_inf(self, overview):
        """
        :rtype : dict
        :param overview: xpath object for overview table, which contains the information of mobile phone overview
        :return: a dictionary for mobile phone overview
        """
        overview_dict = dict()

        for tr in overview.xpath('.//tr'):
            key = tr.xpath('th/text()')
            val = tr.xpath('.//td[2]//text()')
            flag = False  # Denote whether the key and val is valid, the default value is False

            if key and val:
                key = key.extract()[0].strip().lower().replace(' ', '_')
                if key:
                    val = val.extract()[0].strip().lower()
                    flag = True
                else:
                    if "overall_rating" in tr.xpath('th/div/@id').extract():
                        key = "overall_rating"
                        val = ' out of '.join(tr.xpath('th/span//span/text()').extract())
                        flag = True

            else:
                tmp = tr.xpath('td[contains(span, "Device Colors")]')
                if tmp:
                    key = "colors"
                    val = re.sub('<.*?>|\(|\)', '', tmp.xpath('.//span[2]')[0].extract().strip().lower())
                    flag = True

            if flag:
                overview_dict[key] = val
                print "%s: %s" % (key, val)
        return overview_dict

    def get_rating_info(self, ratings):
        """
        :param ratings: xpath object for popularity and rating modular
        :return: a dictionary with rating info
        """
        keys = ratings.xpath('div/@class').extract()
        vals = ratings.xpath('div/p/b/text()').extract()

        for i, key in enumerate(keys):
            vals[i] = re.sub('\(|\)|\s+', '', vals[i])
            print "%s: %s" % (key, vals[i])
        return dict(zip(keys, vals))

    # get the network & platforms information for the selected phone
    def get_table_info(self, info_row):
        """
        :param info_row:  xpath object for table node, which contains information for a table
        :return: a dictinary containing the information of network & platforms
        """
        title = info_row.xpath('h3/text()')[0].extract()
        print title
        table = info_row.xpath('div[@class="info_data"]/table')
        keys = []
        for item in table.xpath('tr/th/text()').extract():
            keys.append(item.strip().lower().replace(' ', '_'))
        # vals = [item.xpath('.//text()') for item in network_n_platforms.xpath('tr//td[2]')]
        vals = [''.join(val.extract()).strip().lower() for val in
                (item.xpath('.//text()') for item in table.xpath('tr//td[2]'))]

        for i, key in enumerate(keys):
            print "%s: %s" % (key, vals[i])

        return title, dict(zip(keys, vals))

    def run(self):
        self.get_brands()
        self.get_phone_info(self.brandlist[1])


myspider = GSMArcSpider()
myspider.run()
