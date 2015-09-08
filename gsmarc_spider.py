__author__ = 'yupeng'

import urllib2
import re
import sqlite3 as sqlite
from objects import Brand, Phone, Table
from scrapy.selector import Selector
import utils


class GSMArcSpider:
    def __init__(self):
        self.home_url = "http://www.gsmarc.com/all-brands"
        self.db_name = "data/gsmarc_data.db"
        self.brandlist = []  # list of Brand object
        self.__connection = self.__cursor = None
        self.__table_dict = dict()

    ## Create SQLite database file and tables
    def prepare_db(self):
        # Connect to the DB and create the tables if they don't exist
        self.__connection = sqlite.connect(self.db_name)
        self.__cursor = self.__connection.cursor()

        table_list = utils.get_table_name_list(self.__cursor)
        for table in table_list:
            table_info = utils.get_table_frame_info(self.__cursor, table)
            self.__table_dict[table] = table_info

            self.__cursor.execute('CREATE TABLE IF NOT EXISTS %s (%s)' % (table_info.table_name,
                                        ','.join(item for item in (' '.join(pair) for pair in
                                                zip(['"'+key+'"' for key in table_info.col_name_list],
                                                    table_info.col_type_list)))))
        self.__connection.commit()

    ## Clean up all stuff. Commit everything, end connections etx.
    def clean_up(self):
        self.__connection.commit()
        self.__connection.close()

    ## get information of mobile phone brands, brand name and url
    def get_brands(self):
        req = urllib2.Request(self.home_url)
        print "***Searching for mobile phone brands and manufacturers on the website %s " \
              "...***" % self.home_url
        # crawl the whole page
        response = ""
        try:
            response = urllib2.urlopen(req).read()
        except urllib2.HTTPError, e:
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
            return

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

    ## get information of mobile phones of a specific brand
    def crawl_phone_info(self, brand):
        """
        :param brand: Brand object
        :return: void
        """
        req = urllib2.Request(brand.get_url())
        response = ""
        try:
            response = urllib2.urlopen(req).read()
        except urllib2.HTTPError, e:
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
            return

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

                print "Crawling infomation of %s (%s)..." % (new_phone.get_id(), new_phone.get_brand())

                # Collect detailed information of the phone
                self.get_phone_details(new_phone)
        print '\n'

    ## get the detailed information of a specifice phone mobile phone
    def get_phone_details(self, phone):
        """
        :param phone: Phone object
        :return:
        """
        req = urllib2.Request(phone.get_url())
        response = urllib2.urlopen(req).read().decode("utf-8")
        sel = Selector(text=response, type="html")

        # crawl the overview information of the phone
        self.crawl_table_info(phone, sel.xpath('//div[@class="overview"]/'
                                                     'div[@class="ph_info"]/table'), 'overview')
        # crawl the Popularity and Rating info
        self.crawl_table_info(phone, sel.xpath('//div[@class="ph_rateing"]'), 'ratings')

        # crawl the Specifications

        for info_row in sel.xpath('//div[@class="info_row"]'):
            if info_row.xpath('.//table'):
                self.crawl_table_info(phone, info_row, 'specifications')

    def crawl_table_info(self, phone, modular, table_name):
        '''
        :param phone:
        :param modular:
        :return:
        '''

        key_list, val_list, table_name = self.extract_table_values( phone, modular, table_name)

        try:
            self.__cursor.execute('INSERT OR REPLACE INTO %s (%s) VALUES (%s)' \
                                % (table_name, ','.join(['"'+'"' for key in key_list]), ','.join(val_list)))
            self.__connection.commit()
        except sqlite.OperationalError:
            existed_cols = set(self.__table_dict.get(table_name, Table()).col_name_list)

            for i, key in enumerate(key_list):
                if key not in existed_cols:
                    self.__cursor.execute('ALTER TABLE %s ADD COLUMN "%s" %s' % (table_name, key, 'TEXT') )
                    self.__table_dict.get(table_name, Table()).col_name_list.append(key)
                    self.__table_dict.get(table_name, Table()).col_type_list.append("TEXT")

            self.__cursor.execute('INSERT OR REPLACE INTO %s (%s) VALUES (%s)' \
                                     % (table_name, ','.join(['"'+key+'"' for key in key_list]), ','.join(val_list)))
            self.__connection.commit()

    def extract_table_values(self, phone, modular, table_name):
        '''
        :param modular:
        :param table_name:
        :return:
        '''
        key_list = ['id', 'brand']
        val_list = ['"%s"' % phone.get_id(), '"%s"' % phone.get_brand()]
        if table_name == 'overview':
            for tr in modular.xpath('.//tr'):
                key = tr.xpath('th/text()')
                val = tr.xpath('.//td[2]//text()')
                flag = False  # Denote whether the key and val is valid, the default value is False

                if key and val:
                    key = utils.valid_col_name(key.extract()[0])
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
                        key = "device_colors"
                        val = re.sub('<.*?>|\(|\)', '', tmp.xpath('.//span[2]')[0].extract().strip().lower())
                        flag = True

                if flag:
                    key_list.append(key)
                    val_list.append('"'+val+'"')
        elif table_name == 'ratings':
            keys = [utils.valid_col_name(key)for key in modular.xpath('div/@class').extract()]
            vals = modular.xpath('div/p/b/text()').extract()

            for i, key in enumerate(keys):
                vals[i] = re.sub('\(|\)|\s+', '', vals[i])

            key_list.extend(keys)
            val_list.extend(['"'+val+'"' for val in vals])
        else:
            table_name = utils.valid_table_name(modular.xpath('h3/text()')[0].extract())
            table = modular.xpath('div[@class="info_data"]/table')
            key_list  += [utils.valid_col_name(item) for item in table.xpath('tr/th/text()').extract()]
            val_list  += ['"'+''.join(val.extract()).strip().lower()+'"' for val in
                    (item.xpath('.//text()') for item in table.xpath('tr//td[2]'))]

        return key_list, val_list, table_name

    def run(self):
        self.prepare_db()
        self.get_brands()

        i = 1
        length = len(self.brandlist)
        while self.brandlist:
            brand = self.brandlist.pop(0)
            print "Searching for %s (%d/%d)..." % (brand.get_name(), i, length)
            self.crawl_phone_info(brand)
            i += 1
        self.clean_up()


myspider = GSMArcSpider()
myspider.run()
