__author__ = 'yupeng'

class Brand(object):

    def __init__(self):
        self.__Name = ""
        self.__Url = ""

    def set_name(self, brandName):
        self.__Name = brandName

    def set_url(self, url):
        self.__Url = url

    def get_name(self):
        return self.__Name

    def get_url(self):
        return self.__Url

class Phone(object):

    def __init__(self):
        self.__ID = ""
        self.__Url = ""
        self.__Brand = ""
        self.__Overview = dict()

    def set_id(self, id):
        self.__ID = id

    def set_url(self, url):
        self.__Url = url

    def set_brand(self, name):
        self.__Brand = name

    def get_id(self):
        return self.__ID

    def get_url(self):
        return self.__Url

    def get_brand(self):
        return self.__Brand

    def set_overview(self, overview):
        self.__Overview = overview

    def get_overview(self):
        return self.__Overview

    def set_rating(self, rating):
        self.__Rating = rating

    def get_rating(self):
        return self.__Rating

class Table(object):

    def __init__(self, table_name = "", col_name_list = tuple(), col_type_list = tuple()):
        self.table_name = table_name
        self.col_name_list = list(col_name_list)
        self.col_type_list = list(col_type_list)
