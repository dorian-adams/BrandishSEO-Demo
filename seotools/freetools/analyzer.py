"""
SEO Analysis tool used in view: ``seo_tools`` at /free-seo-tool/
WIP
"""

import math
import re
from concurrent.futures.thread import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup
from requests.exceptions import InvalidURL


class PageAnalyzer:
    """
    SEO page analyzer.

    Crawls a given URL and holds any SEO issues found in ``results``.
    """

    def __init__(self, url, keyword):
        self.domain = None
        self.source = None
        self.clean_url(url)
        self.keyword = keyword.lower()
        self.soup = BeautifulSoup(self.source, "lxml")
        self.tips = []
        self.results = {
            "h1_tasks": list(self.h_tag(self.soup.find_all("h1"))),
            "meta_title_tasks": list(
                self.meta_title(self.soup.find_all("title"))
            ),
            "broken_link_tasks": list(
                self.broken_links(self.soup.find_all("a"))
            ),
            "meta_description_tasks": list(
                self.meta_description(self.soup.find_all("meta"))
            ),
        }

    def clean_url(self, url):
        prefix = ["http://", "https://"]
        if not any(x in url for x in prefix):
            url = f"http://{url}"
        try:
            r = requests.get(url, timeout=40)
            self.source = r.text
        except:
            return

        domain = re.match(r"(?:http://|https://)([^/]*)", r.url)
        self.domain = domain.group(0)
        return

    def h_tag(self, h1):
        """
        Analyze h1 tags.
        Counts the number of h1 tags on a page.
        Ensures proper syntax is being used.
        """
        errors = []
        h1_error = {"type": "H1 Error"}
        # Tips
        multiple_tip = (
            "It's best to use one h1 tag per page and it should typically serves as the main "
            "heading of the page or article. Reduce to one h1 tag and ensure keyword is used within it."
        )

        if not h1:
            errors.append(
                {
                    **h1_error,
                    "solution": "Implement an H1 tag.",
                    "error": "H1 tag not found.",
                }
            )
            return errors

        # If more than one h1 tag is present, find total count
        if len(h1) > 1:
            for h1_tag in h1[1:]:
                errors.append(
                    {
                        **h1_error,
                        "solution": "Remove or change to subheading 2, 3, etc",
                        "error": str(h1_tag.string),
                    }
                )

        # Get the first h1 tag, all further analysis will be on it alone.
        main_heading = h1[0].text
        lower_heading = main_heading.lower()

        # Check keyword usage
        if self.keyword not in lower_heading:
            errors.append(
                {
                    **h1_error,
                    "solution": f"Add keyword: {self.keyword} to your H1 tag.",
                    "error": main_heading,
                }
            )
        else:
            heading_split = lower_heading.split()
            if (
                self.keyword
                not in heading_split[: math.trunc(len(main_heading) / 2)]
            ):  # Must be present in the first half
                errors.append(
                    {
                        **h1_error,
                        "solution": f"Place keyword: {self.keyword} closer to the start.",
                        "error": main_heading,
                    }
                )
        return errors

    def meta_title(self, titles):
        """
        Analyze meta titles
        Check for proper meta title length and keyword usage
        Ensure only one meta title exists for the page
        """

        # Tips
        no_title = ""
        short_title = ""
        long_title = ""
        missing_keyword = ""
        keyword_placement = ""
        keyword_stuffing = ""

        errors = []
        title_error = {"type": "Meta Title Error"}

        # Check if meta title is present.
        if not titles:
            errors.append(
                {
                    **title_error,
                    "solution": "Add a meta title to the page.",
                    "error": "Meta title not found.",
                }
            )
            return errors

        # Grab only the meta title tag and not various other forms of title tags by checking syntax
        clean_titles = []
        for title in titles:
            # Convert to string to check html syntax
            str_title = str(title)
            if str_title.startswith("<title>") and str_title.endswith(
                "</title>"
            ):
                # Strip html code, convert to string and append to clean list
                title = title.string
                title = str(title)
                clean_titles.append(title)

        # Check if multiple meta titles are present
        if len(clean_titles) > 1:
            for meta_title in clean_titles[
                1:
            ]:  # Only grab the additional meta titles as errors
                errors.append(
                    {
                        **title_error,
                        "solution": "Remove additional meta title.",
                        "error": meta_title,
                    }
                )

        # In case of multiple, base primary analysis on first element only
        title_string = clean_titles[0]
        if len(title_string) > 60:
            errors.append(
                {
                    **title_error,
                    "solution": "Meta title length is too long, shorten to 60 characters.",
                    "error": title_string,
                }
            )
        elif len(title_string) < 30:
            errors.append(
                {
                    **title_error,
                    "solution": "Meta title is too short, increase to around 60 characters.",
                    "error": title_string,
                }
            )

        if self.keyword not in title_string.lower():
            errors.append(
                {
                    **title_error,
                    "solution": "Put target keyword in title.",
                    "error": title_string,
                }
            )
            return errors

        title_split = title_string.lower().split()
        if (
            self.keyword not in title_split[: math.trunc(len(title_split) / 2)]
        ):  # Keyword should be in first half
            errors.append(
                {
                    **title_error,
                    "solution": "Place target keyword in first half of meta title.",
                    "error": title_string,
                }
            )

        return errors

    def meta_description(self, descriptions):
        """
        Analyze meta description
        Check for proper meta description length and keyword usage.
        Ensure only one meta description exists for the page.
        """
        errors = []
        description_error = {"type": "Meta Description Error"}
        description = [
            desc.get("content")
            for desc in descriptions
            if desc.get("name") == "description"
        ]

        if not description:
            errors.append(
                {
                    **description_error,
                    "error": "Meta Description not found.",
                    "solution": f"Implement meta description & include your target keyword: {self.keyword}",
                }
            )
            return errors

        if len(description) > 1:
            for meta_desc in description[1:]:
                errors.append(
                    {
                        **description_error,
                        "error": meta_desc,
                        "solution": "Remove additional meta descriptions, until you "
                        "have only one left.",
                    }
                )

        description = description[0]
        description_lower = description.lower()
        description_split = description_lower.split()

        if len(description) > 160:
            errors.append(
                {
                    **description_error,
                    "error": description,
                    "solution": "Description length is too long. Reduce to 160 characters maximum.",
                }
            )
        elif len(description) < 90:
            errors.append(
                {
                    **description_error,
                    "error": description,
                    "solution": "Description length is too short. Increase to around 160 characters.",
                }
            )

        if self.keyword not in description_lower:
            errors.append(
                {
                    **description_error,
                    "error": description,
                    "solution": f"Incorporate target keyword {self.keyword} into the description.",
                }
            )
        elif (
            self.keyword
            not in description_split[: math.trunc(len(description_split) / 2)]
        ):
            errors.append(
                {
                    **description_error,
                    "error": description,
                    "solution": "Increase keyword relevance by including it near the start"
                    "of the description.",
                }
            )

        return errors

    def content_analysis(self):
        pass

    def broken_links(self, links):
        broken_links = []
        link_error = {"type": "Broken Link Error"}
        href_links = [link.get("href") for link in links]

        def _validate_url(link):
            if link.startswith("#") or link.startswith("../"):
                return
            if "javascript" in link:
                return
            if link.startswith("/"):
                link = self.domain + link
            elif "http" not in link:
                link = f"http://{link}"
            try:
                r = requests.head(link, timeout=2.0)
                r.raise_for_status()
            except TimeoutError:
                broken_links.append(
                    {
                        **link_error,
                        "error": link,
                        "solution": f"URL: {link} took too long to respond.",
                    }
                )
            except ConnectionError:
                broken_links.append(
                    {
                        **link_error,
                        "error": link,
                        "solution": f"Connection failed at, {link}. Check server status.",
                    }
                )
            except InvalidURL:
                broken_links.append(
                    {
                        **link_error,
                        "error": link,
                        "solution": f"URL is invalid, please check {link} for typos.",
                    }
                )
            except Exception as e:
                broken_links.append(
                    {
                        "type": "Broken Link",
                        "error": link,
                        "solution": f"Failed to resolve url. Error: {e}",
                    }
                )

        with ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(_validate_url, href_links)

        return broken_links
