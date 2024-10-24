from dataclasses import dataclass

from .report_dataclasses import SEOCheckResult, SEOChecks
from .seo_descriptions import (
    H1KeywordStatus,
    H1Multiplicity,
    H1Status,
    MetaDescriptionKeywordStatus,
    MetaDescriptionLength,
    MetaDescriptionMultiplicity,
    MetaDescrriptionStatus,
    MetaTitleKeywordPosition,
    MetaTitleKeywordStatus,
    MetaTitleLength,
    MetaTitleMultiplicity,
    MetaTitleStatus,
)


def analyze_h_tag(soup, keyword):
    """
    Analyze h1 tags.
    Counts the number of h1 tags on a page.
    Ensures proper syntax is being used.
    """
    MAX_REC_H1_TAGS = 1

    h1 = soup.find_all("h1")
    h1_results = SEOChecks(category="H1 Tags")

    if not h1:
        h1_results.category_results.append(
            SEOCheckResult(
                error=True,
                description=H1Status.H1_NOT_PRESENT.description,
                solution=H1Status.H1_NOT_PRESENT.solution,
                code="N/A",
            )
        )
        return h1_results

    main_h1 = h1[0]
    main_h1_html = str(main_h1)
    main_h1_content = main_h1.text.strip().lower()
    main_h1_len = len(main_h1_content)

    h1_results.category_results.append(
        SEOCheckResult(
            error=False,
            description=H1Status.H1_PRESENT.description,
            solution=H1Status.H1_PRESENT.solution,
            code=main_h1_html,
        )
    )

    if main_h1_len > MAX_REC_H1_TAGS:
        for h1_tag in h1[1:]:
            h1_results.category_results.append(
                SEOCheckResult(
                    error=True,
                    description=H1Multiplicity.MULTIPLE_H1_TAGS.description,
                    solution=H1Multiplicity.MULTIPLE_H1_TAGS.solution,
                    code=str(h1_tag),
                )
            )
    else:
        h1_results.category_results.append(
            SEOCheckResult(
                error=False,
                description=H1Multiplicity.SINGLE_H1_TAG.description,
                solution=H1Multiplicity.SINGLE_H1_TAG.solution,
                code=main_h1_html,
            )
        )

    if keyword not in main_h1_content:
        h1_results.category_results.append(
            SEOCheckResult(
                error=True,
                description=H1KeywordStatus.KEYWORD_NOT_FOUND.description,
                solution=H1KeywordStatus.KEYWORD_NOT_FOUND.solution,
                code=main_h1_html,
            )
        )
    elif keyword not in main_h1_content[: main_h1_len // 2]:
        h1_results.category_results.append(
            SEOCheckResult(
                error=True,
                description=H1KeywordStatus.KEYWORD_NOT_FRONT_LOADED.description,
                solution=H1KeywordStatus.KEYWORD_NOT_FRONT_LOADED.solution,
                code=main_h1_html,
            )
        )
    else:
        h1_results.category_results.append(
            SEOCheckResult(
                error=False,
                description=H1KeywordStatus.KEYWORD_FRONT_LOADED.description,
                solution=H1KeywordStatus.KEYWORD_FRONT_LOADED.solution,
                code=main_h1_html,
            )
        )
    return h1_results


def analyze_meta_title(soup, keyword):
    """
    Analyze meta titles
    Check for proper meta title length and keyword usage
    Ensure only one meta title exists for the page
    """

    MAX_RECOMMENDED_LEN = 60
    MIN_RECOMMENDED_LEN = 30
    MAX_NUM_OF_TITLES = 1

    titles = soup.find_all("title")
    meta_title_results = SEOChecks(category="Meta Title")

    if not titles:
        meta_title_results.category_results.append(
            SEOCheckResult(
                error=True,
                description=MetaTitleStatus.META_TITLE_NOT_PRESENT.description,
                solution=MetaTitleStatus.META_TITLE_NOT_PRESENT.solution,
                code="N/A",
            )
        )
        return meta_title_results

    main_title_tag = titles[0]
    main_title_html = str(main_title_tag)
    main_title_content = main_title_tag.get_text().strip().lower()
    main_title_len = len(main_title_content)

    meta_title_results.category_results.append(
        SEOCheckResult(
            error=False,
            description=MetaTitleStatus.META_TITLE_PRESENT.description,
            solution=MetaTitleStatus.META_TITLE_PRESENT.solution,
            code=main_title_html,
        )
    )

    if len(titles) > MAX_NUM_OF_TITLES:
        for title in titles[1:]:
            meta_title_results.category_results.append(
                SEOCheckResult(
                    error=True,
                    description=MetaTitleMultiplicity.MULTIPLE_META_TITLES.description,
                    solution=MetaTitleMultiplicity.MULTIPLE_META_TITLES.solution,
                    code=str(title),
                )
            )
    else:
        meta_title_results.category_results.append(
            SEOCheckResult(
                error=False,
                description=MetaTitleMultiplicity.SINGLE_META_TITLE.description,
                solution=MetaTitleMultiplicity.SINGLE_META_TITLE.solution,
                code=main_title_html,
            )
        )

    if main_title_len > MAX_RECOMMENDED_LEN:
        meta_title_results.category_results.append(
            SEOCheckResult(
                error=True,
                description=MetaTitleLength.GREATER_THAN_REC_LENGTH.description,
                solution=MetaTitleLength.GREATER_THAN_REC_LENGTH.solution,
                code=main_title_html,
            )
        )
    elif main_title_len < MIN_RECOMMENDED_LEN:
        meta_title_results.category_results.append(
            SEOCheckResult(
                error=True,
                description=MetaTitleLength.LESS_THAN_REC_LENGTH.description,
                solution=MetaTitleLength.LESS_THAN_REC_LENGTH.solution,
                code=main_title_html,
            )
        )
    else:
        meta_title_results.category_results.append(
            SEOCheckResult(
                error=False,
                description=MetaTitleLength.WITHIN_REC_RANGE.description,
                solution=MetaTitleLength.WITHIN_REC_RANGE.solution,
                code=main_title_html,
            )
        )

    if keyword not in main_title_content:
        meta_title_results.category_results.append(
            SEOCheckResult(
                error=True,
                description=MetaTitleKeywordStatus.KEYWORD_NOT_PRESENT.description,
                solution=MetaTitleKeywordStatus.KEYWORD_NOT_PRESENT.solution,
                code=main_title_html,
            )
        )
        return meta_title_results
    else:
        meta_title_results.category_results.append(
            SEOCheckResult(
                error=False,
                description=MetaTitleKeywordStatus.KEYWORD_PRESENT.description,
                solution=MetaTitleKeywordStatus.KEYWORD_PRESENT.solution,
                code=main_title_html,
            )
        )

    if keyword not in main_title_content[: main_title_len // 2]:
        meta_title_results.category_results.append(
            SEOCheckResult(
                error=True,
                description=MetaTitleKeywordPosition.KEYWORD_NOT_FRONT_LOADED.description,
                solution=MetaTitleKeywordPosition.KEYWORD_NOT_FRONT_LOADED.solution,
                code=main_title_html,
            )
        )
    else:
        meta_title_results.category_results.append(
            SEOCheckResult(
                error=False,
                description=MetaTitleKeywordPosition.KEYWORD_FRONT_LOADED.description,
                solution=MetaTitleKeywordPosition.KEYWORD_FRONT_LOADED.solution,
                code=main_title_html,
            )
        )
    return meta_title_results


def analyze_meta_description(soup, keyword):
    """
    Analyze meta description
    Check for proper meta description length and keyword usage.
    Ensure only one meta description exists for the page.
    """

    MAX_REC_META_DESC_TAGS = 1
    MAX_REC_CONTENT_LEN = 160
    MIN_REC_CONTENT_LEN = 120

    meta_description_results = SEOChecks(category="Meta Description")
    descriptions = soup.find_all("meta", attrs={"name": "description"})

    if not descriptions:
        meta_description_results.category_results.append(
            SEOCheckResult(
                error=True,
                description=MetaDescrriptionStatus.META_DESCRIPTION_NOT_PRESENT.description,
                solution=MetaDescrriptionStatus.META_DESCRIPTION_NOT_PRESENT.solution,
                code="N/A",
            )
        )
        return meta_description_results

    main_description = descriptions[0]
    main_description_html = str(main_description)
    main_description_content = main_description.get("content").strip().lower()
    main_description_len = len(main_description_content)

    meta_description_results.category_results.append(
        SEOCheckResult(
            error=False,
            description=MetaDescrriptionStatus.META_DESCRIPTION_PRESENT.description,
            solution=MetaDescrriptionStatus.META_DESCRIPTION_PRESENT.solution,
            code=main_description_html,
        )
    )

    if len(descriptions) > MAX_REC_META_DESC_TAGS:
        for desc in descriptions[1:]:
            meta_description_results.category_results.append(
                SEOCheckResult(
                    error=True,
                    description=MetaDescriptionMultiplicity.MULTIPLE_META_DESC.description,
                    solution=MetaDescriptionMultiplicity.MULTIPLE_META_DESC.solution,
                    code=str(desc),
                )
            )
    else:
        meta_description_results.category_results.append(
            SEOCheckResult(
                error=False,
                description=MetaDescriptionMultiplicity.SINGLE_META_DESC.description,
                solution=MetaDescriptionMultiplicity.SINGLE_META_DESC.solution,
                code=main_description_html,
            )
        )

    if main_description_len > MAX_REC_CONTENT_LEN:
        meta_description_results.category_results.append(
            SEOCheckResult(
                error=True,
                description=MetaDescriptionLength.GREATER_THAN_REC_LENGTH.description,
                solution=MetaDescriptionLength.GREATER_THAN_REC_LENGTH.solution,
                code=main_description_html,
            )
        )
    elif main_description_len < MIN_REC_CONTENT_LEN:
        meta_description_results.category_results.append(
            SEOCheckResult(
                error=True,
                description=MetaDescriptionLength.LESS_THAN_REC_LENGTH.description,
                solution=MetaDescriptionLength.LESS_THAN_REC_LENGTH.solution,
                code=main_description_html,
            )
        )
    else:
        meta_description_results.category_results.append(
            SEOCheckResult(
                error=False,
                description=MetaDescriptionLength.WITHIN_REC_RANGE.description,
                solution=MetaDescriptionLength.WITHIN_REC_RANGE.solution,
                code=main_description_html,
            )
        )

    if keyword not in main_description_content:
        meta_description_results.category_results.append(
            SEOCheckResult(
                error=True,
                description=MetaDescriptionKeywordStatus.KEYWORD_NOT_FOUND.description,
                solution=MetaDescriptionKeywordStatus.KEYWORD_NOT_FOUND.solution,
                code=main_description_html,
            )
        )
    elif keyword not in main_description_content[: main_description_len // 2]:
        meta_description_results.category_results.append(
            SEOCheckResult(
                error=True,
                description=MetaDescriptionKeywordStatus.KEYWORD_NOT_FRONT_LOADED.description,
                solution=MetaDescriptionKeywordStatus.KEYWORD_NOT_FRONT_LOADED.solution,
                code=main_description_html,
            )
        )
    else:
        meta_description_results.category_results.append(
            SEOCheckResult(
                error=False,
                description=MetaDescriptionKeywordStatus.KEYWORD_FRONT_LOADED.description,
                solution=MetaDescriptionKeywordStatus.KEYWORD_FRONT_LOADED.solution,
                code=main_description_html,
            )
        )
    return meta_description_results
