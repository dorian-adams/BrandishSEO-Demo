from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


@dataclass
class SEODataMixin:
    description: str
    solution: str
    tips: Optional[List[str]] = field(default_factory=list)


class H1Status(SEODataMixin, Enum):
    H1_PRESENT = (
        "The Heading One (H1) tag is present on the page.",
        (
            "Great job incorporating an H1 tag! This is an important SEO"
            " element that helps search engines better understand what the"
            " page is about."
        ),
    )
    H1_NOT_PRESENT = (
        "The Heading One (H1) tag is not present.",
        (
            "Add an H1 tag to better convey your page's relevance to your"
            " target keyword. In your code, the H1 tag should look like this:"
            " <h1>Your relevant and engaging title</h1>. "
        ),
        [
            (
                "Ensure your target keyword is contained within your H1 tag;"
                " however, be sure to avoid keyword stuffing, as it can"
                " negatively impact your SEO and user experience."
            ),
            (
                "Ideally, the H1 tag should be placed above the main content"
                " of your page to provide a clear and immediate indication of"
                " the page's topic to both users and search engines."
            ),
        ],
    )


class H1Multiplicity(SEODataMixin, Enum):
    SINGLE_H1_TAG = (
        (
            "A single H1 tag is in use, which provides the ideal structure for"
            " search engine optimization and user experience."
        ),
        (
            "Generally speaking, since the H1 tag represents the main title or"
            " primary topic, there should only be one H1 tag per page."
            " Therefore, with only one H1 tag detected, your page is on the"
            " right track to properly organizing its information."
        ),
    )
    MULTIPLE_H1_TAGS = (
        "Multiple H1 tags found.",
        (
            "Strongly consider limiting your H1 tag usage to once per page."
            " This can be corrected by changing all additional H1 tags"
            " referenced above to subheadings such as H2, H3, etc. Generally"
            " speaking, since the H1 tag represents the main title or primary"
            " topic, limiting its usage to once per page provides the clearest"
            " structure."
        ),
        [
            (
                "When reducing to a single H1 tag, choose the one that best"
                " represents the content of your page and includes your target"
                " keyword."
            ),
            (
                "Move additional H1 tags to subheadings, or eliminate them"
                " entirely if they don't enhance the organization or"
                " readability of your page."
            ),
        ],
    )


class H1KeywordStatus(SEODataMixin, Enum):
    KEYWORD_NOT_FOUND = (
        "Target keyword is missing from the H1 tag.",
        (
            "Incorporate your target keyword into your H1 tag; doing so is an"
            " easy way to enhance keyword relevancy."
        ),
        [
            (
                "When incorporating your keyword into your H1 tag, be sure to"
                " avoid keyword stuffing to maintain readability and SEO"
                " effectiveness."
            ),
            (
                "Keep in mind that the H1 tag, along with all other elements"
                " of the page, should always be written with your audience as"
                " the top priority. In other words, always write to impress"
                " humans first and foremost."
            ),
            (
                "Furthermore, when adding your keyword to the H1 tag, try to"
                " incorporate it within the first half of the title, if"
                " possible. However, writing titles that are easy to read and"
                " engaging is far more important than being overly nuanced"
                " about technical SEO."
            ),
        ],
    )
    KEYWORD_FRONT_LOADED = (
        (
            "Keyword is front-loaded. The target keyword is one of the primary"
            " (leading) words in the H1 tag."
        ),
        (
            "Your keyword is appropriately placed near the start of the title,"
            " rather than at the end. This makes it one of the leading words"
            " in the heading, thereby enhancing keyword relevance."
        ),
    )
    KEYWORD_NOT_FRONT_LOADED = (
        (
            "Keyword is not front-loaded. The target keyword is not placed as"
            " one of the primary (leading) words in the H1 tag."
        ),
        (
            "Consider placing your target keyword closer to the start of your"
            " title, ideally within the first half. This can enhance keyword"
            " relevancy. However, this is a minor ranking factor, so it's not"
            " worth compromising the quality of your title for better keyword"
            " placement. Only adjust if you can improve placement while still"
            " delivering a high-quality title that your audience will enjoy."
        ),
        [
            "Remember, while keyword placement—specifically front-loading your"
            " keyword in your main heading—is a factor, albeit a small one,"
            " you should always write for people. This means prioritizing"
            " readability and ensuring your title is engaging and informative"
            " for your audience. Move your keyword forward only if it can be"
            " done without degrading the user experience."
        ],
    )


class MetaTitleStatus(SEODataMixin, Enum):
    META_TITLE_PRESENT = (
        "The meta title is present on the page.",
        (
            "Great job incorporating a meta title! This is one of the most"
            " important on-page elements that can influence both your rankings"
            " and your click-through rate. This is because the meta title is"
            " displayed in search results, and a well-crafted one can entice"
            " users to click your link over other results."
        ),
    )
    META_TITLE_NOT_PRESENT = (
        "Meta title was not detected.",
        (
            "Add a meta title to your page to convey its primary topic to"
            " search engines and users in a concise and engaging manner. In"
            " your code, the meta title should look like this: <title>Your"
            " concise and enganging meta title with keyword</title>."
        ),
        [
            (
                "Ideally, the meta title should be located within the <head>"
                " section of your HTML document, providing a concise and"
                " relevant description of the page's content."
            ),
            (
                "It is essential to include a well-written and unique meta"
                " title on every page of your website."
            ),
        ],
    )


class MetaTitleMultiplicity(SEODataMixin, Enum):
    SINGLE_META_TITLE = (
        "A single meta title was detected, which is ideal.",
        (
            "Search engines display the meta title in search results, and only"
            " one can be used per page. Therefore, it is standard practice to"
            " incorporate a single meta title per page, which you have done."
        ),
    )
    MULTIPLE_META_TITLES = (
        "Multiple meta titles detected.",
        "Remove additional meta titles so that only one remains.",
    )


class MetaTitleLength(SEODataMixin, Enum):
    GREATER_THAN_REC_LENGTH = (
        "The meta title is longer than 60 characters.",
        (
            "Edit the meta title to 60 characters or fewer. This ensures that"
            " Google won't truncate your title, allowing it to be fully"
            " displayed in search results, which can improve visibility and"
            " click-through rates."
        ),
        [
            "When crafting your meta title, aim for brevity and clarity while"
            " maintaining relevance and engagement."
        ],
    )
    LESS_THAN_REC_LENGTH = (
        "The meta title is fewer than 51 characters.",
        (
            "Consider expanding the meta title to more than 51 characters but"
            " fewer than 60 characters. This range allows for a more engaging"
            " and keyword-relevant title."
        ),
        [
            "Expand your meta title to around 60 characters, using the"
            " additional space to add descriptive and compelling information."
        ],
    )
    WITHIN_REC_RANGE = (
        "The page's meta title falls within the recommended range.",
        (
            "The page's meta title is within 51-60 characters, which is ideal"
            " for both search engines and user engagement."
        ),
    )


class MetaTitleKeywordStatus(SEODataMixin, Enum):
    KEYWORD_PRESENT = (
        "The target keyword is present within the meta title.",
        (
            "Great job! Including the target keyword in your meta title helps"
            " improve search engine relevancy and attract clicks."
        ),
    )
    KEYWORD_NOT_PRESENT = (
        "The target keyword is missing from the meta title.",
        (
            "Incorporate your target keyword within your meta title. This is a"
            " crucial step in enhancing keyword relevancy."
        ),
        [
            (
                "Rephrase your meta title to naturally include the target"
                " keyword."
            ),
            (
                "Avoid keyword stuffing; make sure the meta title remains"
                " readable and engaging."
            ),
        ],
    )


class MetaTitleKeywordPosition(SEODataMixin, Enum):
    KEYWORD_FRONT_LOADED = (
        (
            "Keywod is front-loaded. The target keyword is one of the primary"
            " (leading) words in the meta title."
        ),
        (
            "Your keyword is appropriately placed near the start of the meta"
            " title rather than at the end. This makes it one of the leading"
            " words in the meta title, thereby enhancing keyword relevance."
        ),
    )
    KEYWORD_NOT_FRONT_LOADED = (
        (
            "Keyword is not front-loaded. The target keyword is not placed as"
            " one of the primary (leading) words in the meta title."
        ),
        (
            "Strongly consider placing your target keyword closer to the start"
            " of your meta title, ideally within the first half, as this can"
            " further enhance keyword relevancy."
        ),
        [
            "Remember, while keyword placement—specifically front-loading your"
            " keyword in your meta title—is important, you should always write"
            " for people. This means prioritizing readability and engagement."
            " Move your keyword forward only if it can be done without"
            " degrading readability."
        ],
    )


class MetaDescrriptionStatus(SEODataMixin, Enum):
    META_DESCRIPTION_PRESENT = (
        "The meta description is present on the page.",
        (
            "Great job incorporating a meta description! The meta description"
            " you set is often used by search engines to provide a brief"
            " summary of your page in search results."
        ),
    )
    META_DESCRIPTION_NOT_PRESENT = (
        "The meta description was not detected on the page.",
        (
            "Add a meta description that provides a brief summary of the page."
            " Ensure the summary is relevant to the page's contents, includes"
            " your target keyword along with secondary keywords, and most"
            " importantly, is written to engage and entice users to click your"
            " link in search results."
        ),
        [
            "Although search engines often dynamically generate a meta"
            " description based on page content, setting a meta description"
            " gives you the chance to entice click-throughs for when it is"
            " used. Therefore, it is best practice to set a meta description"
            " for every page you want to rank."
        ],
    )


class MetaDescriptionMultiplicity(SEODataMixin, Enum):
    SINGLE_META_DESC = (
        "A single meta description was detected, which is ideal.",
        (
            "One meta description was found, which is ideal, as each page"
            " should have only one meta description."
        ),
    )
    MULTIPLE_META_DESC = (
        "Multiple meta descriptions detected.",
        "Reduce to a single meta description.",
    )


class MetaDescriptionLength(SEODataMixin, Enum):
    GREATER_THAN_REC_LENGTH = (
        "The meta description is over 160 characters.",
        (
            "Consider editing the meta description to be fewer than 160"
            " characters. When editing, cut any unnecessary words and keep the"
            " most engaging and relevant parts. Being concise will help ensure"
            " that the most important details are always shown."
        ),
        [
            (
                "Google may truncate meta descriptions that are longer than"
                " 160 characters; therefore, it is important to keep them"
                " concise to ensure the most crucial information is displayed."
            ),
            (
                "Conciseness in meta descriptions matters. Your goal is to"
                " increase CTR, so avoid being overly detailed or stuffing"
                " keywords. Instead, focus on writing descriptions that"
                " encourage users to click through."
            ),
        ],
    )
    LESS_THAN_REC_LENGTH = (
        "The meta description is under 120 characters.",
        (
            "Consider expanding your meta description to 120 - 160 characters."
            " This allows you to provide more information that may entice"
            " users to click your link in the SERPs."
        ),
        [
            "Increasing the length of your meta description will not improve"
            " your rankings; however, it may give you more space to create a"
            " compelling summary that encourages users to click on your link."
        ],
    )
    WITHIN_REC_RANGE = (
        (
            "The length of the page's meta description falls within the"
            " recommended range."
        ),
        (
            "The meta description is of ideal length-concise enough to avoid"
            " being cut off, yet long enough to entice users to click-through."
        ),
    )


class MetaDescriptionKeywordStatus(SEODataMixin, Enum):
    KEYWORD_NOT_FOUND = (
        "The target keyword is missing from the meta description",
        (
            "Add your target keyword to your meta description. This will help"
            " indicate to users that your page contains information related to"
            " their search."
        ),
    )
    KEYWORD_FRONT_LOADED = (
        (
            "Keyword is front-loaded. The target keyword is one of the primary"
            " (leading) words in the meta description."
        ),
        (
            "The keyword is placed within the first half of the meta"
            " description, enhancing keyword relevancy."
        ),
    )
    KEYWORD_NOT_FRONT_LOADED = (
        (
            "Keyword is not front-loaded. The target keyword is not placed as"
            " one of the primary (leading) words in the meta description."
        ),
        (
            "Consider placing your target keyword closer to the start of your"
            " meta description, ideally within the first half, as this can"
            " quickly convey the relevance of your page to users as they read"
            " your description."
        ),
    )
