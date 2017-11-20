# -*- coding: utf-8 -*-


# 爬取指定BD贴吧所有帖子的所有图片
import requests
import re


class Tieba(object):
    """
    贴吧图片爬虫
    """
    def __init__(self):
        """
        贴吧属性
        """
        self.base_url = "http://tieba.baidu.com/f"
        self.user_agent = {"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko"}
        self.name = raw_input('请输入想爬取的贴吧的名字：')
        self.keys = {'kw': self.name}
        self.post_nu = 0

    def get_pn_range(self):
        """
        获得一个贴吧的最大页码
        """
        result = requests.get(url=self.base_url, params=self.keys, headers=self.user_agent)
        str_re = result.content
        re_rule1 = r'''pn=(.*?)" class="last pagination-item "'''
        last_pn = int(re.findall(re_rule1, str_re)[0])
        pn_range = last_pn / 50 + 1
        # <span class="red_text">252514</span>
        re_rule2 = '''<span class="red_text">(.*?)</span>'''
        post_nu = int(re.findall(re_rule2, str_re)[0])
        return pn_range, post_nu

    def download_img(self, imgs_url_list, page_nu):
        """
        下载图片
        """
        print '+++开始下载第%d个帖子第%d页里的图片++++' %(self.post_nu, page_nu)
        for img in imgs_url_list:
            result = requests.get(img, headers=self.user_agent)
            str_re = result.content
            img_name = str(self.post_nu) + '-' + img[-17:]
            with open(img_name, 'wb') as f:
                f.write(str_re)
            print '---图片%s下载完成---' %img_name
        if not len(imgs_url_list):
            print '+++第%d个帖子第%d页里没有图片++++\n' %(self.post_nu, page_nu)
            return
        print '+++第%d个帖子第%d页里的图片下载完成++++\n' %(self.post_nu, page_nu)

    def get_imgs_url(self, post_list):
        """
        获得图片的url并下载
        """
        page_nu = 0
        for post in post_list:
            result = requests.get(post, headers=self.user_agent)
            str_re = result.content
            re_rule = r'''<img class="BDE_Image" src="(.*?)".*?>'''
            imgs_url_list = re.findall(re_rule, str_re, re.S)
            page_nu += 1
            self.download_img(imgs_url_list, page_nu)

    def get_post_urls(self, post_urls_list):
        """
        得到一个帖子的所有url列表
        """
        re_rule = r'''<li class="l_pager pager_theme_5 pb_list_pager">.*<a href=".*pn=(\d*?)">尾页</a>.*</li>'''
        page_urls_list = list()
        for post_url in post_urls_list:
            # print post_url
            str_re = requests.get(post_url, headers=self.user_agent).content
            page_pn = re.findall(re_rule, str_re, re.S)
            # print page_pn
            if len(page_pn) == 0:
                post_list = [post_url]
            else:
                post_list = [post_url + '?pn=' + str(pn) for pn in range(1, int(page_pn[0]) + 1)]
            page_urls_list.append(post_list)
            self.post_nu += 1
            print '-------------------------------------'
            print "-------第%d个帖子里共有%d页--------" %(self.post_nu, len(post_list))
            print '-------------------------------------'
            # print post_list
            self.get_imgs_url(post_list)

    def get_page_urls(self):
        """
        获得贴吧首框每一页里每个帖子(排除广告贴)的url列表
        """
        pn_range, post_nu = self.get_pn_range()
        for pn in range(0, pn_range):
            self.keys = {'kw': self.name, 'pn': pn * 50}
            result = requests.get(url=self.base_url, params=self.keys, headers=self.user_agent)
            str_re = result.content
            re_rule = r'''li class=" j_thread_list clearfix" data-field='{&quot;id&quot;:(.*?),'''
            page_list = re.findall(re_rule, str_re)
            print "\n-贴吧-%s一共有%d页,%d个帖子\n" %(self.name, pn_range, post_nu)
            post_urls_list = ['http://tieba.baidu.com/p/' + nu for nu in page_list]
            # print post_urls_list
            self.get_post_urls(post_urls_list)


if __name__ == "__main__":
    tieba = Tieba()
    tieba.get_page_urls()
