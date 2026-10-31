"""Structural and formula regression checks; requires openpyxl and formulas.

These do not replace opening the files in Microsoft Excel.
"""
import datetime as dt
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

import formulas
import openpyxl
from openpyxl.utils.protection import hash_password
from openpyxl.utils.datetime import to_excel

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from daycare_business_spreadsheet.build import SHEET_ORDER, SCHEMAS


def calc(expr, values):
    fn = formulas.Parser().ast(expr)[1].compile()
    return fn(*[values[str(k)] for k in fn.inputs]).item()


def check(path, demo):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        for name in z.namelist():
            if name.endswith(('.xml', '.rels')):
                data = z.read(name)
                ET.fromstring(data)
                assert b'<v>None</v>' not in data
                if name.startswith('xl/worksheets/sheet'):
                    assert not re.search(rb'\s(?:AND|OR)\s', data)
    book = openpyxl.load_workbook(path, data_only=False)
    assert book.sheetnames == SHEET_ORDER
    assert book.properties.creator == 'Novality Store'
    assert book.calculation.fullCalcOnLoad
    assert all(ws.protection.sheet for ws in book.worksheets)
    assert all(ws.protection.password == hash_password('premium') for ws in book.worksheets) # Excel's legacy hash for premium
    for name,schema in SCHEMAS.items():
        ws=book[name]
        for c,(_,kind,_) in enumerate(schema,1):
            cell=ws.cell(7,c)
            assert cell.protection.locked == kind.startswith('formula:'), (name,cell.coordinate)
            if kind.startswith('formula:'): assert cell.data_type == 'f'
    ledger=book['Invoices & Receipts']
    assert (ledger['B7'].value == 'TX-001') == demo
    assert (book['Child Enrollment']['A7'].value == 'CHD-001') == demo
    effect=ledger['I7'].value
    cash=ledger['J7'].value
    def evaluate(expr, typ, amount):
        return calc(expr, {'A7':46326,'B7':'TX-1','C7':'F1','E7':typ,'G7':amount})
    tests={'Invoice':(100,0), 'Payment':(-100,100), 'Credit':(-100,0),
           'Write-off':(-100,0), 'Refund':(100,-100), 'Deposit':(-100,100)}
    for typ,(balance,cash_effect) in tests.items():
        assert evaluate(effect,typ,100)==balance,(typ,evaluate(effect,typ,100))
        assert evaluate(cash,typ,100)==cash_effect
    assert evaluate(effect,'Invoice',100)+evaluate(effect,'Payment',30)==70
    assert sum(evaluate(effect,t,a) for t,a in [('Invoice',100),('Deposit',30),('Credit',10),('Write-off',5),('Refund',5)])==60
    assert sum(evaluate(cash,t,a) for t,a in [('Deposit',30),('Payment',20),('Refund',5)])==45
    # The family balance references ONLY the signed balance effect, no second payment deduction.
    bal=book['Parent Database']['H7'].value
    assert 'SUMIF(' in bal and '$I$7:' in bal and 'Payment' not in bal
    if demo:
        ids=['FAM-001','FAM-001','FAM-002','FAM-002']
        effects=[100,-30,200,-40]
        bf=formulas.Parser().ast(bal)[1].compile()
        assert bf(ids,effects,'FAM-001').item()==70
        assert bf(ids,effects,'FAM-002').item()==160
        serial=to_excel(dt.datetime(2026,10,1))
        values={'A7:A706':[serial]*4,'E7:E706':['Invoice','Payment','Invoice','Deposit'],
                'G7:G706':[100,30,200,40],'J7:J706':[0,30,0,40],'A16':serial}
        for cell, expected in [('B16',300),('F16',70)]:
            fn=formulas.Parser().ast(book['Monthly Reports'][cell].value)[1].compile()
            assert fn(*[next(v for k,v in values.items() if k in str(n)) for n in fn.inputs]).item()==expected
    assert book['Monthly Reports']['A7'].value == "=DATE('Settings & Lists'!$B$10,1,1)"
    assert book['Dashboard']['B9'].value.startswith('=SUM(')
    assert book['Invoices & Receipts']['K7'].data_type == 'f'
    assert book['Classroom Management']['A7'].value != 'Live ratio'
    book.close()

if __name__ == '__main__':
    check(os.path.join(ROOT,'download','Daycare-Demo.xlsx'),True)
    check(os.path.join(ROOT,'download','Daycare-Blank.xlsx'),False)
    print('PASS: XML, 23 tabs, protection, formula locking, demo/blank, ledger and family balance regression')
