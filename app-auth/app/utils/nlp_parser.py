from typing import Any, Dict, Iterable, List, Optional, Tuple, TypeVar, Union
import spacy
from spacy.matcher import Matcher, PhraseMatcher
from spacy.util import compile_infix_regex
from spacy.tokenizer import Tokenizer
from spacy.tokens import Span, Doc
import re

nlp = spacy.load("en_core_web_md")

terms = [
    "File Name",
    "Threat ID",
    "Threat URL",
    "File Path",
    "Process User",
    "Signature Status",
    "Originating Process",
    "SHA1",
    "Engine",
    "Detection Type",
    "EndpointName",
    "Account Scope",
    "Site Scope",
    "Group Scope",
    "Operating System",
    "Agent Version",
    "Policy",
    "Last logged in user",
    "Last logged-in user",
    "subscription Time",
]


# Custom infixes, remove '-' infix between letters
def custom_tokenizer(nlp):
    inf = list(nlp.Defaults.infixes)  # Default infixes
    inf.remove(
        r"(?<=[0-9])[+\-\*^](?=[0-9-])"
    )  # Remove the generic op between numbers or between a number and a -
    inf = tuple(inf)  # Convert inf to tuple
    infixes = inf + tuple(
        [r"(?<=[0-9])[+*^](?=[0-9-])", r"(?<=[0-9])-(?=-)"]
    )  # Add the removed rule after subtracting (?<=[0-9])-(?=[0-9]) pattern
    infixes = [
        x for x in infixes if "-|–|—|--|---|——|~" not in x
    ]  # Remove - between letters rule
    infix_re = compile_infix_regex(infixes)

    return Tokenizer(
        nlp.vocab,
        prefix_search=nlp.tokenizer.prefix_search,
        suffix_search=nlp.tokenizer.suffix_search,
        infix_finditer=infix_re.finditer,
        token_match=nlp.tokenizer.token_match,
        rules=nlp.Defaults.tokenizer_exceptions,
    )


nlp.tokenizer = custom_tokenizer(nlp)


def find_kb_text(doc: Doc) -> Doc:
    matcher = Matcher(nlp.vocab)
    pattern = [{"LEMMA": {"IN": ["threat", "Threat"]}}]
    matcher.add("threat", [pattern])
    matches = matcher(doc)

    kb_start = 0

    for match_id, start, end in matches:
        span = doc[start:end]
        span_2 = doc[span.start].nbor()
        span_3 = doc[span.start + 1].nbor()
        if span_2.text == "URL" and span_3.text == "example":
            kb_start = start

    mail_content = doc[kb_start:]
    # find start of kb via regex
    regx = r"Alert Information: ?(.*)"

    # remove all new line and empty line
    text = mail_content.text.replace("\n", " ").replace("\r", " ")
    kb_str = re.search(regx, text)
    if kb_str is None:
        return None

    return nlp(kb_str.group())


def match_keyword(doc, keyword: list[str]):
    matcher = Matcher(nlp.vocab)
    pattern = [{"LEMMA": {"IN": keyword}}]
    matcher.add(" ".join(keyword), [pattern])
    matches = matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]
        print(span.text, span.label_, start, end)
        return span.text, start


def match_terms(doc, terms: list[str]) -> Dict:
    patterns = [nlp.make_doc(text) for text in terms]
    matcher = PhraseMatcher(nlp.vocab)
    matcher.add("Threat_Info", patterns)

    matches = matcher(doc)
    prev_end = None
    prev_label = None
    term_pos = {}
    for match_id, start, end in matches:
        span = doc[start:end]
        # print(span.text, span.label_, start, end)

        if prev_end is not None and start - prev_end > 1:
            term_pos[prev_label] = (prev_end, start)
        prev_end = end
        prev_label = span.text

    if prev_end is not None:
        term_pos[prev_label] = (prev_end, len(doc))

    # replace term with value
    for term, pos in term_pos.items():
        start, end = pos
        # if this is last term, split by ' ' and return first word
        if end == len(doc):
            term_pos[term] = doc[start:].text.strip(": ").split(" ")[0]
        else:
            term_pos[term] = doc[start:end].text.strip(": ")

    return term_pos


def parse_threat_file(text: str):
    # check if no key word for kb, return None
    kb_key_words = [
        "Threat URL example",
        "Analysis",
        "Recommendations",
        "Alert Information",
    ]
    if all([word not in text for word in kb_key_words]):
        return None

    doc = nlp(text)
    kb_doc = find_kb_text(doc)

    if not kb_doc:
        return None
    else:
        return match_terms(kb_doc, terms)


if __name__ == "__main__":
    test_file = "test_nlp_parser1.txt"
    with open(test_file, "r") as f:
        test_str = f.read()
        print(parse_threat_file(test_str))
