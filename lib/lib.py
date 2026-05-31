#-*- coding: utf-8 -*-
from re import findall
from camoufox.sync_api import Camoufox
from .useragent import useragent
from .tmp import load


def _proxy_dict(proxy_str):
    if not proxy_str:
        return None
    if '://' not in proxy_str:
        proxy_str = f'http://{proxy_str}'
    return {"server": proxy_str}


def _css_selector(class_tag):
    return 'a.' + '.'.join(class_tag.split())


class Parser(object):

    def __init__(
        self,
        dork,
        URL,
        pattern,
        class_tag,
        proxy=None,
        user_agent=None,
        output_cb=None,
    ):
        self.dork = dork
        self.URL = URL
        self._pattern = pattern
        self.class_tag = class_tag
        self.proxy = proxy
        self.user_agent = user_agent or useragent()
        self.output_cb = output_cb or print
        self._list = []

    def __dir__(self):
        return list(set(self._list))

    def _harvest(self, content):
        for url in findall(self._pattern, content):
            if 'www.google.com' in self.URL:
                self._list.append(url)
            else:
                self._list.append(url[:-1])

    def request(self):
        proxy = _proxy_dict(self.proxy)
        selector = _css_selector(self.class_tag)
        with Camoufox(headless=True, proxy=proxy) as browser:
            page = browser.new_page()
            page.goto(self.URL, timeout=15000)
            page.fill('input[name="q"]', self.dork)
            page.press('input[name="q"]', 'Enter')
            page.wait_for_load_state('networkidle', timeout=15000)
            self._harvest(page.content())
            for link in page.query_selector_all(selector):
                try:
                    load()
                    href = link.get_attribute('href')
                    if href:
                        page.goto(f'{self.URL}{href}', timeout=15000)
                        page.wait_for_load_state('networkidle', timeout=15000)
                        self._harvest(page.content())
                except Exception as e:
                    self.output_cb(str(e))
