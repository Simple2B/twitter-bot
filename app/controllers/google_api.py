import os

import gspread

from app import db
from app.logger import log
from app.models import Keyword, ExclusionKeyword


def parse_gsheet():
    log(log.INFO, "Parsing spreadsheet")
    gc = gspread.service_account(filename='gspread.json')
    sheet = gc.open_by_key(os.environ.get("SPREADSHEET_ID", 'No Google Spreadsheet ID selected'))
    exclusion_sheet = sheet.worksheet('Exclusion')
    keyword_sheet = sheet.worksheet('Force Appear')

    # Parse Force Appear sheet and add keywords to DB
    keywords = []
    for value in keyword_sheet.col_values(1):
        if value.isspace() or not value:
            continue
        verify_value = Keyword.query.filter(Keyword.word == value).first()
        if not verify_value:
            new_value = Keyword(word=value)
            db.session.add(new_value)
        keywords.append(value)
    log(log.INFO, "Collected [%d] keywords", len(keywords))

    # Parse Exclusion sheet and add keywords to DB
    exclusion_keywords = []
    for value in exclusion_sheet.col_values(1):
        if value.isspace() or not value:
            continue
        verify_value = ExclusionKeyword.query.filter(ExclusionKeyword.word == value).first()
        if not verify_value:
            new_value = ExclusionKeyword(word=value)
            db.session.add(new_value)
        exclusion_keywords.append(value)
    log(log.INFO, "Collected [%d] exclusion keywords", len(exclusion_keywords))
    db.session.commit()
    return keywords, exclusion_keywords
