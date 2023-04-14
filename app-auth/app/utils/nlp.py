from typing import Any, Dict, Iterable, List, Optional, Tuple, TypeVar, Union
import spacy
from spacy.matcher import Matcher, PhraseMatcher
from spacy.tokenizer import Tokenizer

nlp = spacy.load("en_core_web_md")

prefix_re = spacy.util.compile_prefix_regex(nlp.Defaults.prefixes)
suffix_re = spacy.util.compile_suffix_regex(nlp.Defaults.suffixes)
custom_infixes = [r"-"]
infix_re = spacy.util.compile_infix_regex(list(nlp.Defaults.infixes) + custom_infixes)

nlp.tokenizer = Tokenizer(
    nlp.vocab,
    prefix_search=prefix_re.search,
    suffix_search=suffix_re.search,
    infix_finditer=infix_re.finditer,
    token_match=None,
)


def extract_department(nlp_doc):
    matcher = Matcher(nlp.vocab)
    pattern = [{"LEMMA": {"IN": ["China"]}}, {"POS": {"IN": ["PROPN", "NOUN"]}}]
    matcher.add("Department", [pattern])
    matches = matcher(nlp_doc)
    for match_id, start, end in matches:
        span = nlp_doc[start:end]
        return span.text, start


def extract_asset(nlp_doc):
    matcher = Matcher(nlp.vocab)
    pattern1 = [{"LOWER": {"REGEX": r"cn.*"}}]
    pattern2 = [{"LEMMA": {"IN": ["Host"]}}]
    matcher.add("Asset2", [pattern1, pattern2])
    matches = matcher(nlp_doc)

    if not matches:
        return None, None

    for match_id, start, end in matches:
        span = nlp_doc[start:end]
        asset_n = nlp_doc[span.start].nbor()
        if span.text == "Host":
            return asset_n.text, span.start
        if not str(asset_n.text).startswith("China"):
            if (
                asset_n.pos_ == "NOUN"
                or asset_n.pos_ == "NUM"
                or asset_n.pos_ == "PROPN"
            ):
                return f"{span.text}-{asset_n.text}", start
        return span.text, start


def extract_case_num(nlp_doc):
    matcher = Matcher(nlp.vocab)
    pattern = [{"TEXT": {"REGEX": "^INC\d*"}}]
    matcher.add("CaseNum", [pattern])
    matches = matcher(nlp_doc)
    for match_id, start, end in matches:
        span = nlp_doc[start:end]
        return span.text


def extract_source(nlp_doc):
    matcher = Matcher(nlp.vocab)
    pattern = [{"LEMMA": {"IN": ["S1"]}}, {"POS": "PROPN"}]
    matcher.add("Source", [pattern])
    matches = matcher(nlp_doc)
    for match_id, start, end in matches:
        span = nlp_doc[start:end]
        return span.text, end
    return "Unknow", 0


def remove_hyphen(text):
    return text.strip().strip("-")


def process_subject(texts: str):
    """
    will parse subject for ticket props:
    1. source
    2. asset name
    3. case num
    4. reason/cause
    5. department
    """
    source = asset = case_num = department = reason = "unknown"

    doc = nlp(texts)
    clearn_sub = " ".join(
        token.text
        for token in doc
        if not token.is_punct
        and not token.is_currency
        and not token.is_digit
        and not token.is_punct
        and not token.is_space
        and not token.is_stop
    )

    sub_doc = nlp(clearn_sub)
    # print(sub_doc)
    # for token in sub_doc:
    #     print(token, token.idx, token.pos_)

    try:
        case_num = extract_case_num(sub_doc)
        department, reason_pos_end = extract_department(sub_doc)
        source, reason_start = extract_source(sub_doc)

        asset, reason_end = extract_asset(sub_doc)

        if not asset:
            asset = "-"
            reason_end = reason_pos_end

        reason = sub_doc[reason_start:reason_end]

        parsed = {
            "department": remove_hyphen(department),
            "case_num": remove_hyphen(case_num),
            "source": remove_hyphen(source),
            "asset": remove_hyphen(asset),
            "reason": remove_hyphen(reason.text),
        }
        return parsed
    except Exception as e:
        print(e)
        return False


if __name__ == "__main__":
    import json

    text1 = "RE: S1 STAR - Exposed Public Service- RPC Suspicious Connection - CN142-203FSE01 - China REST - INC14133471 - #143692"
    print(process_subject(text1))
    text2 = 'RE: S1 Vigilance - Treat Potentially Malicious File :   CN-BSCH2NRKN3 - China CORP - INC14194487 - #150339"'
    print(process_subject(text2))
    text3 = "Fw: RE: S1 Vigilance – Suspicious Detection Inquiry:  CN51416GSC01 - China REST - INC14144183 -#144817"
    print(process_subject(text3))
    text4 = "Exposed Pubic service VNC and Keberos Suspicious Connection - CN-C02FT44BML7H - China CORP - INC14229008-#148288"
    print(process_subject(text4))
    text4 = "S1 STAR – Suspicious Detection Inquiry : MobaRTE[.]exe -CNNKGL7G8CP93 - China CORP - INC14255177 - #159137"
    print(process_subject(text4))
    text4 = "S1 STAR - Treat Potentially Malicious File - kprcycleaner:  CN-HGHL46HM5Q2 – China CORP - INC14229992 - #152765"
    print(process_subject(text4))

    abnormal_text1 = "S1 Vigilance - Threat Infected USB - Kingston DataTraveler 3.0 - China REST - INC14213534 - #152421"
    print(process_subject(abnormal_text1))

    abnormal_text2 = "RE: S1 Vigilance - Suspicious Detection Inquiry - Defence Evasion: Removing host from domain - Host: cn52226MDS01 - Site: China REST - INC14240055 - #162109"
    print(process_subject(abnormal_text2))

    abnormal_text3 = "S1 Vigilance – Suspicious Detection Inquiry Firewall Settings Modification: CN-SHELPF474PJZ – China CORP - INC14286393 - #171315"
    print(process_subject(abnormal_text3))
