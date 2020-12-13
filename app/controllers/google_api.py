import gspread

from app import db
from app.logger import log
from app.models import Keyword


def parse_gsheet():
    log(log.INFO, "Parsing spreadsheet")
    gc = gspread.service_account(filename='gspread.json')
    sheet = gc.open_by_key('1ipB3a9uxaAF5JUYY3fuo-A4VublvPZCRIyjw3uDICl4')
    worksheet = sheet.sheet1
    keywords = []
    for value in worksheet.col_values(1):
        if value.isspace() or not value:
            continue
        verify_value = Keyword.query.filter(Keyword.word == value).first()
        if not verify_value:
            new_value = Keyword(word=value)
            db.session.add(new_value)
        keywords.append(value)
    db.session.commit()
    log(log.INFO, "Collected [%d] keywords", len(keywords))
    return keywords
