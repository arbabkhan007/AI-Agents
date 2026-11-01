"""Structural release checks. Requires openpyxl and xlsxwriter; does not replace Excel testing."""
import os, re, sys, zipfile, xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import openpyxl
from openpyxl.utils.protection import hash_password
from wedding_photography_spreadsheet.build import REGISTER_MODULES, SHEET_ORDER
from wedding_photography_spreadsheet.config import Config

MAIN='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
QUOTED=re.compile(r'"(?:[^"]|"")*"')
INFIX=re.compile(r'(?<=[\w\)\$])\s+(?:AND|OR)\s+(?=[\w\(\$])',re.I)
MODERN=re.compile(r'\b(?:XLOOKUP|FILTER|SORT|UNIQUE|IFS|MAXIFS|MINIFS|TEXTJOIN)\s*\(',re.I)

def check(path,blank):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        count=0
        for name in z.namelist():
            if not name.endswith(('.xml','.rels')): continue
            raw=z.read(name)
            assert b'<v>None</v>' not in raw, name
            root=ET.fromstring(raw)
            if name.startswith('xl/worksheets/sheet') and name.endswith('.xml'):
                for f in root.iter(MAIN+'f'):
                    t=QUOTED.sub('""',f.text or '')
                    assert not INFIX.search(t),(name,t)
                    assert not MODERN.search(t),(name,t)
                    count+=1
    w=openpyxl.load_workbook(path)
    assert w.sheetnames==SHEET_ORDER
    assert w.properties.creator=='Novality Store'
    assert all(s.protection.sheet and s.protection.password==hash_password('premium') for s in w)
    cfg=Config(); checked=0
    for m in REGISTER_MODULES:
        spec=m.spec(cfg); ws=w[m.NAME]
        for ci,c in enumerate(spec.columns,1):
            for row in range(spec.first_data_row,spec.last_data_row+1):
                cell=ws.cell(row,ci)
                if c.formula is None:
                    assert not cell.protection.locked,(m.NAME,cell.coordinate,'input locked')
                    if blank: assert cell.value is None,(m.NAME,cell.coordinate,'blank populated')
                else:
                    assert cell.data_type=='f' and cell.protection.locked,(m.NAME,cell.coordinate,'formula missing or unlocked')
                checked+=1
    print(f'{os.path.basename(path)}: {count:,} XML formulas; {checked:,} prepared register cells checked; XML, protections, Excel-2010 function scan and blank inputs OK')

if __name__=='__main__':
    for p in sys.argv[1:]: check(p,'Blank' in os.path.basename(p))
