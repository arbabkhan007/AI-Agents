"""Check workbook XML and formula shape (not a substitute for Excel)."""
import re, sys, zipfile, xml.etree.ElementTree as ET
from pathlib import Path
import openpyxl
S='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
def parens(s):
 depth=0;i=0;quoted=False
 while i<len(s):
  c=s[i]
  if c=='"':
   if quoted and i+1<len(s) and s[i+1]=='"':i+=2;continue
   quoted=not quoted
  elif not quoted and c=='(':depth+=1
  elif not quoted and c==')':
   depth-=1
   if depth<0:return False
  i+=1
 return not quoted and depth==0

def run(path):
 path=Path(path);count=0;problems=[]
 with zipfile.ZipFile(path) as z:
  bad=z.testzip()
  if bad:problems.append(f'corrupt {bad}')
  sheets=[p for p in z.namelist() if re.fullmatch(r'xl/worksheets/sheet\d+\.xml',p)]
  styles = ET.fromstring(z.read('xl/styles.xml'))
  unlocked = {i for i, xf in enumerate(styles.find(S+'cellXfs'))
              if xf.find(S+'protection') is not None and xf.find(S+'protection').get('locked') == '0'}
  for name in sheets:
   root=ET.fromstring(z.read(name))
   if root.find(S+'sheetProtection') is None:problems.append(name+': no protection')
   for c in root.iter(S+'c'):
    form=c.find(S+'f')
    if form is None:continue
    count+=1;f=form.text or '';v=c.find(S+'v')
    if int(c.get('s','0')) in unlocked: problems.append(f'{name} {c.get("r")}: unlocked formula')
    clean=re.sub(r'"(?:[^"]|"")*"','""',f)
    if '#REF!' in f or '[[' in f or (v is not None and v.text=='None') or re.search(r'(?<=[\w\)\$])\s+(?:AND|OR)\s+(?=[\w\(\$])',clean,re.I) or not parens(f):
     problems.append(f'{name} {c.get("r")}: {f[:180]}')
  wb=openpyxl.load_workbook(path,read_only=True,data_only=False)
  if len(wb.sheetnames)!=len(sheets):problems.append('Sheet count mismatch')
  wb.close()
 print(f'{path.name}: {len(sheets)} protected sheets; {count:,} formulas; {len(problems)} issues',flush=True)
 for p in problems[:15]:print('  ',p,flush=True)
 return len(problems)
if __name__=='__main__':
 paths=sys.argv[1:]
 if not paths:raise SystemExit('Supply workbook filenames')
 errors=sum(run(p) for p in paths)
 raise SystemExit(1 if errors else 0)
