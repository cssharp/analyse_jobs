# coding=utf-8
import ConfigParser
import re


class Config(object):
    def __init__(self, config_file_name):
        self.cf = ConfigParser.ConfigParser()
        self.re_config_file(config_file_name)
        self.cf.read(config_file_name)

        key_search_word_list = self.cf.get('common', 'key_search_word_list').split(',')
        custom_black_list = self.cf.get('common', 'custom_black_list').split(',')

        self.key_search_word_list = (key.strip() for key in key_search_word_list)
        self.custom_black_list = (key.strip() for key in custom_black_list)
        self.yx = self.cf.get('common', 'yx')
        self.total_thread = self.cf.getint('thread', 'total_thread')

        self.file = self.cf.get('db','file')
        self.result_file = self.cf.get('db','result_file')
    def re_config_file(self,config_file_name):
        content = open(config_file_name).read()
        #Window下用记事本打开配置文件并修改保存后，编码为UNICODE或UTF-8的文件的文件头
        #会被相应的加上\xff\xfe（\xff\xfe）或\xef\xbb\xbf，然后再传递给ConfigParser解析的时候会出错
        #，因此解析之前，先替换掉
        content = re.sub(r"\xfe\xff","", content)
        content = re.sub(r"\xff\xfe","", content)
        content = re.sub(r"\xef\xbb\xbf","", content)
        open(config_file_name, 'w').write(content)


