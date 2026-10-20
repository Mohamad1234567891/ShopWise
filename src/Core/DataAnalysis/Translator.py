"""
This file is part of ShopWise, an open-source multi-region, multi-store
price-comparison and product-search engine.

Copyright (c) 2026 Muhammed Bekiroğlu and the ShopWise contributors.

Original ShopWise repository: https://github.com/Mohamad1234567891/ShopWise

Muhammed Bekiroğlu (ShopWise team leader and top contributor) YouTube channel:
    https://www.youtube.com/@ALShajaraComputerScienceInstit

Licensed under the Mozilla Public License 2.0 with Additional Attribution
Terms — see the LICENSE file.
-------------------------------------------------------------------------------------------------------------------------------

Review translation. Detects the language of every review with langdetect and translates non-English reviews to English with cached Argos Translate models, falling back to the original text whenever a model is missing or a translation fails.
"""

import time
from collections import defaultdict
from langdetect import detect, DetectorFactory, LangDetectException
import argostranslate.translate

# Make language detection more consistent between runs.
DetectorFactory.seed = 0


def translate_reviews_to_english(reviews):
    start = time.perf_counter()

    installed_languages = {
        language.code: language
        for language in argostranslate.translate.get_installed_languages()
    }

    english = installed_languages.get("en")
    if english is None:
        raise RuntimeError(
            "English translation language is not installed in Argos."
        )

    # Cache translation objects and detected languages.
    translators = {}
    language_cache = {}
    results = [None] * len(reviews)
    grouped = defaultdict(list)

    # Detect languages first and group reviews by source language.
    for index, review in enumerate(reviews):
        if not isinstance(review, str) or not review.strip():
            results[index] = review
            continue

        text = review.strip()

        try:
            language = language_cache.get(text)
            if language is None:
                language = detect(text)
                language_cache[text] = language

            if language == "en":
                results[index] = review
            else:
                grouped[language].append((index, text))

        except LangDetectException:
            results[index] = review

    # Translate each language group using a cached translator.
    for source_language, items in grouped.items():
        source = installed_languages.get(source_language)

        if source is None:
            print(f"No Argos model installed for {source_language} -> en")
            for index, _ in items:
                results[index] = reviews[index]
            continue

        key = (source_language, "en")

        try:
            if key not in translators:
                translators[key] = source.get_translation(english)

            translator = translators[key]

            for index, text in items:
                try:
                    results[index] = translator.translate(text)
                except Exception as error:
                    print(f"Failed to translate review {index}: {error}")
                    results[index] = reviews[index]

        except Exception as error:
            print(f"Could not initialize {source_language} -> en: {error}")
            for index, _ in items:
                results[index] = reviews[index]

    elapsed = time.perf_counter() - start
    print(f"Processed {len(reviews)} reviews in {elapsed:.2f} seconds")

    return results