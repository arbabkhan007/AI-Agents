"""Independent OOXML integrity, protection and formula checks."""
import sys,zipfile,re,xml.etree.ElementTree as ET, openpyxl
from openpyxl.utils.protection import hash_password
N={'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
for path in sys.argv[1:]:
 print(path, flush=True); nformula=0
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None
  for name in z.namelist():
   if not (name.startswith('xl/worksheets/sheet') and name.endswith('.xml')): continue
   tree=ET.fromstring(z.read(name)); prot=tree.find('x:sheetProtection',N)
   assert prot is not None and prot.get('password')==hash_password('premium'),name
   # 1 means disallowed under OOXML sheetProtection.
   assert prot.get('insertRows','1')=='1' and prot.get('deleteRows','1')=='1' and prot.get('sort','1')=='1', (name,prot.attrib)
   for c in tree.findall('.//x:c',N):
    f=c.find('x:f',N)
    if f is None: continue
    nformula+=1
    formula=f.text or ''
    assert '#REF!' not in formula and '[[' not in formula,(name,c.get('r'),formula)
    assert not re.search(r'\b(?:XLOOKUP|FILTER|UNIQUE|SORT|IFS|MAXIFS|TEXTJOIN)\s*\(', formula, re.I),formula
    clean=re.sub(r'"(?:[^"]|"")*"','""',formula)
    assert not re.search(r'(?<=[\w\)\$])\s+(?:AND|OR)\s+(?=[\w\(\$])',clean,re.I),formula
    v=c.find('x:v',N);assert v is None or v.text!='None',(name,c.get('r'))
    assert c.get('t')!='e',(name,c.get('r'))
 w=openpyxl.load_workbook(path)
 assert len(w.sheetnames)==23
 for s in w:
  for row in s.iter_rows():
   for c in row:
    if c.data_type=='f':assert c.protection.locked,(s.title,c.coordinate)
 assert "OFFSET(" not in w.defined_names['CustomerList'].attr_text
 if 'Blank' in path:
  sheet,ref=next(w.defined_names['BusinessName'].destinations);assert w[sheet][ref].value in (None, "")
 print(f'  {len(w.sheetnames)} protected sheets, {nformula:,} locked formulas, XML checks passed',flush=True)
 del w
