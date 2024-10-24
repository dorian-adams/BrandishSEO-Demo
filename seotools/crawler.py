from urllib.parse import urlsplit

import requests

from seotools.seo_checks import (
    analyze_h_tag,
    analyze_meta_description,
    analyze_meta_title,
)

from .http import http_client
from .report_dataclasses import PageReport


class Crawler:
    def __init__(self, url, keyword):
        self.conn_error = None
        self.url = url if urlsplit(url).scheme else f"http://{url}"
        self.parse = urlsplit(self.url)
        self.domain = self.parse.netloc
        self.keyword = keyword.lower()

    def _html(self):
        try:
            response = http_client.get(self.url)
            return response.text
        except requests.exceptions.RequestException as e:
            self.conn_error = e
            return None

    def crawl_page(self):
        html = self._html()
        if html is None:
            return None

        seo_check_functions = [
            analyze_h_tag,
            analyze_meta_title,
            analyze_meta_description,
        ]
        page = PageReport(
            html=html,
            domain=self.domain,
            url=self.url,
            keyword=self.keyword,
            check_functions=seo_check_functions,
        )
        page.generate_results()
        return page.page_results

    def crawl_site(self):
        pass
