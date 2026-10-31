#!/usr/bin/env python3
"""Structural checks and independent formula-engine regression tests; not Windows Excel."""
import datetime as dt, re, sys, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
import openpyxl
from openpyxl.utils.datetime import to_excel
from formulas import Parser
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from build_airbnb_workbook import SHEETS
workbooks = root/'download' if (root/'download').is_dir() else root.parent

for name in ('Rental-Demo.xlsx','Rental-Blank.xlsx'):
 path=workbooks/name
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None
  for n in z.namelist():
   if n.endswith(('.xml','.rels')):ET.fromstring(z.read(n))
   if n.startswith('xl/worksheets/sheet') and n.endswith('.xml'):
    txt=z.read(n).decode();assert '<v>None</v>' not in txt and '#REF!' not in txt and '_xlfn.' not in txt
    for formula in re.findall(r'<f(?:\s[^>]*)?>(.*?)</f>',txt):
     assert not re.search(r'\s(?:AND|OR)\s',formula)
 w=openpyxl.load_workbook(path)
 assert w.sheetnames==SHEETS and len(w.sheetnames)==20
 assert all(s.protection.sheet for s in w)
 assert w['Booking Tracker']['G7'].protection.locked is False and w['Booking Tracker']['M7'].protection.locked is True
 assert w['Settings & Lists']['F7'].protection.locked is False
 assert w['Cleaning Schedule']['D7'].protection.locked is False and w['Cleaning Schedule']['A7'].protection.locked is True
 assert len(w['Booking Tracker'].merged_cells.ranges)==3
 if 'Blank' in name:assert w['Booking Tracker']['G7'].value is None and w['Guest Database']['B7'].value is None
 else:assert w['Booking Tracker']['B7'].value=='PRP-01' and w['Guest Database']['B7'].value=='Rebecca Thorne'
 print(name,'structure and protection OK')

def evaluate(sheet,cell,values):
 f=Parser().ast(wb[sheet][cell].value)[1].compile()
 out=f(*[values[k] for k in f.inputs]);
 # formulas returns numpy arrays with one item in some cases
 try:return out.item()
 except AttributeError:return out
wb=openpyxl.load_workbook(workbooks/'Rental-Demo.xlsx')
assert evaluate('Booking Tracker','I7',{'G7':100,'H7':103})==3
assert evaluate('Booking Tracker','I7',{'G7':100,'H7':100})==''
assert evaluate('Booking Tracker','M7',{'G7':100,'E7':'Confirmed','I7':3,'K7':165,'L7':0})==495
assert evaluate('Booking Tracker','M7',{'G7':100,'E7':'Cancelled','I7':3,'K7':165,'L7':0})==0
assert evaluate('Booking Tracker','Q7',{'G7':100,'E7':'Confirmed','I7':3,'M7':495,'O7':85,'P7':0})==580
assert abs(evaluate('Booking Tracker','T7',{'G7':100,'Q7':580,'R7':.03,'S7':0})-17.4)<1e-8
assert abs(evaluate('Booking Tracker','V7',{'G7':100,'Q7':580,'T7':17.4})-562.6)<1e-8
total=evaluate('Platform Revenue & Fees','F7',{"'PLATFORM REVENUE & FEES'!A7:A906":['BKG-0001','BKG-0001','BKG-0002'],"'PLATFORM REVENUE & FEES'!C7:C906":[200,362.6,400],'A7':'BKG-0001'})
assert abs(total-562.6)<1e-8
assert evaluate('Platform Revenue & Fees','G7',{'A7':'BKG-0001','E7':562.6,'F7':total})==0
serial=lambda y,m,d:to_excel(dt.datetime(y,m,d))
base={"'BOOKING TRACKER'!B7:B906":['PRP-01','PRP-01','PRP-01','PRP-02'],"'BOOKING TRACKER'!E7:E906":['Confirmed','Owner block','Cancelled','Completed'],"'BOOKING TRACKER'!G7:G906":[serial(2026,10,29),serial(2026,10,3),serial(2026,10,8),serial(2026,10,1)],"'BOOKING TRACKER'!H7:H906":[serial(2026,11,3),serial(2026,10,5),serial(2026,10,10),serial(2026,10,5)],"'BOOKING TRACKER'!I7:I906":[5,2,2,4],"'BOOKING TRACKER'!M7:M906":[500,0,0,400],"'PROPERTY DATABASE'!A7:A36":[['PRP-01'],['PRP-02']],"'PROPERTY DATABASE'!G7:G36":[[serial(2026,1,1)],[serial(2026,1,1)]],'A16':'PRP-01','B16':serial(2026,10,1),'C16':31}
assert evaluate('Occupancy & Performance','D16',base)==2
assert evaluate('Occupancy & Performance','F16',base)==3
assert evaluate('Occupancy & Performance','H16',base)==300
base['C16']=2 # Property became available on October 30.
assert evaluate('Occupancy & Performance','F16',base)==2
assert evaluate('Occupancy & Performance','H16',base)==200
base['C16']=0
assert evaluate('Occupancy & Performance','F16',base)==0
assert evaluate('Occupancy & Performance','I16',{'A16':'PRP-01','F16':3,'H16':300})==100
assert evaluate('Occupancy & Performance','J16',{'A16':'PRP-01','E16':29,'H16':300})==10.34
clash={"'BOOKING TRACKER'!B7:B906":['PRP-01','PRP-01','PRP-01'],"'BOOKING TRACKER'!E7:E906":['Confirmed','Confirmed','Cancelled'],"'BOOKING TRACKER'!G7:G906":[100,102,100],"'BOOKING TRACKER'!H7:H906":[102,104,104],'B7':'PRP-01','E7':'Confirmed','G7':100,'H7':102,'I7':2}
assert evaluate('Booking Tracker','X7',clash)==0 # Checkout and check-in on same day do not conflict.
clash["'BOOKING TRACKER'!G7:G906"][1]=101
assert evaluate('Booking Tracker','X7',clash)==1
print('Formula-engine checks passed: rates, tax-excluded ADR, cross-month nights, availability, clashes and split payouts.')
