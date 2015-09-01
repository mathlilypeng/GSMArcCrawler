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
        sel = Selector(text=response)
        items = sel.xpath(r'//div[@class="brandlist"]//li')
        # collect information of brand name and brand url for all the brands
        print "----------%d Mobile Phone Brands and Manufacturers Detected:----------" % len(items)
        for i, item in enumerate(items):
            # content = item.re(r'<a href="(http.*?)">.*?<span>(.*?)</span>')
            brand_url = item.xpath('a/@href').extract()
            brand_name = item.xpath('a/span/text()').extract()
            if brand_name and brand_url:
                new_brand = Brand()
                new_brand.set_url(brand_url[0])
                new_brand.set_name(brand_name[0])
                self.brandlist.append(new_brand)
                print "%d: %s" % (i + 1, new_brand.get_name())
        print "-----------------------------------------------------------------------\n"

    # get information of mobile phones under a specific brand
    def get_phone_inf(self, brand):
        """
        :param brand: Brand object
        :return: void
        """
        print "***Searching for %s...***\n" % brand.get_name()
        req = urllib2.Request(brand.get_url())
        response = urllib2.urlopen(req).read().decode("utf-8")

        sel = Selector(text=response)
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
                self.phonelist.append(new_phone)
                print "---Detailed info for %s:---" % new_phone.get_id()

                # Collect detailed information of the phone
                self.get_phone_details(new_phone)
                print "--------------------------"

                # self.get_phone_details(new_phone)

    def get_phone_details(self, phone):
        """
        :param phone: Phone object
        :return:
        """
        req = urllib2.Request(phone.get_url())
        response = urllib2.urlopen(req).read().decode("utf-8")

        # get the overview information of the phone
        sel = Selector(text=response)
        tmp = self.get_phone_overview_inf(sel.xpath('//div[@class="overview"]/'
                                                    'div[@class="ph_info"]/table//tr'))
        phone.set_overview(tmp)

        # get the Network & Platforms information
        sel = Selector(text=response)
        self.get_table_info(sel.xpath('//div[@class="grid_17 alpha omega"]'
                                      '/div[@class="info_row"]/div[@class="info_data"]/table'))

        # get the sepecifications
        sel = Selector(text=response)
        tables = sel.xpath('//div[@id="full_specification"]//div/table')

        for table in tables:
            self.get_table_info(table)

    # get the overview information for the selected mobile phone
    def get_phone_overview_inf(self, overview):
        """
        :param overview: a list of xpath objects, which contains the information of mobile phone overview
        :return: a dictionary for mobile phone overview
        """
        overview_dict = dict()
        for item in overview:
            attr = item.xpath('th/text()')
            val = item.xpath('td')
            if attr and val:
                attr = attr.extract()[0].strip().lower().replace(' ', '_')
                val = re.sub('<.*?>|\(|\)', '', val[-1].extract().strip().lower())

                if len(attr) == 0:
                    if 'rating' in val:
                        attr = "numOfRatings"
                        val = re.sub('ratings|rating', "", val).strip()
                        attr2 = "score"
                        val2 = item.xpath('th/div/@title').extract()[0]
                        overview_dict[attr2] = val2
                    else:
                        print "Unexpected Attribute Detected!\n --%s" % item

                overview_dict[attr] = val
                print "%s: %s" % (attr, overview_dict.get(attr))

            else:
                if 'device color' in re.sub('<.*?>', '', val.xpath('span')[0].extract()).strip().lower():
                    attr = 'device_color'
                    val = re.sub('<.*?>', '', val.xpath('span')[-1].extract()).strip().lower()
                    overview_dict[attr] = val
                    print "%s: %s" % (attr, val)
                else:
                    print re.sub('<.*?>', '', val.xpath('span')[0].extract()).strip().lower()
                    print "Unexpected Attribute Detected!\n --%s" % item

        return overview_dict

    # get the network & platforms information for the selected phone
    def get_table_info(self, table):
        """
        :param table:  xpath object for table node, which contains information for a table
        :return: a dictinary containing the information of network & platforms
        """
        keys = [item.strip().lower() for item in table.xpath('tr/th/text()').extract()]
        # vals = [item.xpath('.//text()') for item in network_n_platforms.xpath('tr//td[2]')]
        vals = [''.join(val.extract()).strip().lower() for val in
                (item.xpath('.//text()') for item in table.xpath('tr//td[2]'))]
        print "\n"

        for i, key in enumerate(keys):
            print "%s: %s" % (key, vals[i])

        return dict(zip(keys, vals))

    def run(self):
        self.get_brands()
        self.get_phone_inf(self.brandlist[4])


myspider = GSMArcSpider()
myspider.run()
