import gspread

from app.logger import log


def parse_gsheet():
    log(log.INFO, "Parsing spreadsheet")
    gc = gspread.service_account(filename='gspread.json')
    sheet = gc.open_by_key('1ipB3a9uxaAF5JUYY3fuo-A4VublvPZCRIyjw3uDICl4')
    worksheet = sheet.sheet1
    keywords = []
    for value in worksheet.col_values(1):
        if value.isspace() or not value:
            continue
        keywords.append(value)
    return keywords
