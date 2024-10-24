from dataclasses import dataclass, field
from functools import lru_cache
from typing import Callable, List, Optional

from bs4 import BeautifulSoup


@dataclass
class SEOCheckResult:
    error: bool
    description: str
    solution: Optional[str] = None
    code: Optional[str] = None


@dataclass
class SEOChecks:
    category: str
    category_results: List[SEOCheckResult] = field(default_factory=list)


@dataclass(eq=False)
class PageReport:
    html: str
    domain: str
    url: str
    keyword: str
    check_functions: List[Callable[[BeautifulSoup, str], SEOChecks]]
    page_results: List[SEOChecks] = field(default_factory=list)

    def generate_results(self):
        for seo_func in self.check_functions:
            self.page_results.append(seo_func(self.soup, self.keyword))

    @property
    @lru_cache(maxsize=None)
    def soup(self):
        return BeautifulSoup(self.html, "lxml")
