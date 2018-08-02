import glob
import json
from itertools import chain

from bs4 import BeautifulSoup
from flashtext import KeywordProcessor

KEYWORD_MAPPINGS = {
    "learning resources": ["learning"],
    "tutorials": ["tutorial", "learning"],
    "reviews": ["review", "learning"],
    "tools": ["tool"],
    "research": ["research"],
    "gan": ["gan"],
    "gans": ["gan"],
    "rstats": ["rstats"],
    "rstat": ["rstats"],
    "dataviz": ["dataviz"],
    "visualization": ["dataviz"],
    "python": ["python"],
    "rl": ["rl"],
    "nlp": ["nlp"],
    "ethics": ["ethics"],
    "miscellaneous": ["misc"]
}
KEYWORD_PROCESSOR = KeywordProcessor()
for k, v in KEYWORD_MAPPINGS.items():
    KEYWORD_PROCESSOR.add_keyword(k, v)


def extract_tags(headline):
    # Make all lowercase
    headline = headline.lower()
    # Extract keywords
    tags_found = list(set(
        chain.from_iterable(KEYWORD_PROCESSOR.extract_keywords(headline))))
    return tags_found


def parse_file(filename):
    current_headline, current_sub_headline = None, None
    base_tags, current_tags = None, None
    chunks, text_buffer = [], ""
    with open(filename) as f:
        for line in f.readlines():
            # Handles Headers
            if line.startswith("## "):
                if current_headline is not None:
                    chunks.append((
                        text_buffer, current_tags,
                        current_headline,
                        current_sub_headline
                    ))
                text_buffer = ""
                current_headline = line[3:].strip()
                current_sub_headline = ""
                current_tags = extract_tags(current_headline)
                base_tags = current_tags
                if len(current_tags) > 0:
                    print(current_headline, current_tags)
                continue
            # Handles Sub-Headers
            if line.startswith("### "):
                if len(text_buffer.strip()) > 0:
                    chunks.append((
                        text_buffer, current_tags,
                        current_headline,
                        current_sub_headline
                    ))
                    text_buffer = ""
                current_sub_headline = line[4:].strip()
                current_tags = base_tags + extract_tags(
                    current_sub_headline
                )
                if len(current_tags) > 0:
                    print(current_sub_headline, current_tags)
                continue
            # Skip until the first headline appears
            if current_headline is None:
                continue
            # Append to buffer
            text_buffer += line
    chunks.append((
        text_buffer, current_tags,
        current_headline, current_sub_headline
    ))
    return chunks


def parse_chunks(chunks, date):
    collections = []
    for chunk, tags, headline, sub_headline in chunks:
        chunk = chunk.strip()
        if len(chunk) == 0:
            continue
        bs = BeautifulSoup(chunk, 'html.parser')
        for tweet in bs.find_all("amp-twitter"):
            collections.append({
                "tid": tweet["data-tweetid"],
                "no_conversation": tweet.has_attr("data-conversation"),
                "date": date,
                "tags": tags,
                "headline": headline,
                "sub-headline": sub_headline
            })
    return collections


def main():
    collections = []
    for filename in glob.glob("_posts/*.md"):
        date = filename.split("/")[1][:10]
        print("\n %s %s" % (filename, date))
        chunks = parse_file(filename)
        collections += parse_chunks(chunks, date)
    with open("tweets.json", "w") as f:
        json.dump(collections, f)


if __name__ == "__main__":
    main()
