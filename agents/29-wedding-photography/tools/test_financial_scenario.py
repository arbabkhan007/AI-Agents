"""Evaluate a small known scenario (optional: pip install formulas openpyxl)."""
import datetime as dt
import os
import sys
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import formulas
import openpyxl
from openpyxl.utils import get_column_letter
from wedding_photography_spreadsheet.build import REGISTER_MODULES, build_workbook
from wedding_photography_spreadsheet.config import Config

cfg=Config(include_sample_data=False, rows_override=12, tax_rate=.1,
           tax_on_packages=True, _today=dt.date(2026,11,1))
spec={m.NAME:m.spec(cfg) for m in REGISTER_MODULES}
def col(sheet,key):
    return get_column_letter(next(i for i,c in enumerate(spec[sheet].columns,1) if c.key==key))
with tempfile.TemporaryDirectory(prefix='wedding-test-') as tmp:
    path=os.path.join(tmp,'scenario.xlsx')
    build_workbook(path,cfg)
    w=openpyxl.load_workbook(path)
    def put(sheet,row,**values):
        for key,v in values.items(): w[sheet][f'{col(sheet,key)}{row}']=v
    put('Client CRM',5,name='Example Client')
    put('Packages & Pricing',5,name='Example Package',base_price=1000,hours=8,photographers=1)
    put('Wedding Bookings',5,client='CLT-0001',wedding_date=dt.datetime(2026,6,20),status='Confirmed',package='Example Package')
    put('Payments & Invoices',5,booking='WED-0001',amount=1100,received=500,fee=10)
    put('Payments & Invoices',6,booking='WED-0001',amount=-100,received=-40)
    put('Payments & Invoices',7,booking='WED-0001')
    put('Expense Tracker',5,date=dt.datetime(2026,3,1),category='Second shooters',booking='WED-0001',amount=100,business_pct=.5)
    put('Expense Tracker',6,date=dt.datetime(2026,3,1),category='Insurance',amount=200)
    put('Expense Tracker',7,date=dt.datetime(2026,3,1),category='Camera equipment',booking='WED-0001',amount=500,tax_category='Capital / asset')
    put('Gallery & Delivery',5,booking='WED-0001',print_sales=100)
    put('Profit Analysis',5,booking='WED-0001')
    put('Contracts & Documents',5,booking='WED-0001',doc_type='Model release',status='Signed')
    put('Contracts & Documents',6,booking='WED-0001',doc_type='Wedding contract',status='Sent')
    put('Reviews & Referrals',5,booking='WED-0001',status='Requested')
    w.save(path)
    expected={
      ('Wedding Bookings','tax',5):100, ('Wedding Bookings','total_value',5):1100,
      ('Wedding Bookings','profit',5):940, ('Wedding Bookings','contract_state',5):'Outstanding',
      ('Payments & Invoices','status',6):'Part paid', ('Payments & Invoices','is_paid',6):'No',
      ('Payments & Invoices','is_paid',7):'No', ('Expense Tracker','profit_cost',5):50,
      ('Expense Tracker','profit_cost',7):0, ('Gallery & Delivery','review_in',5):'No',
      ('Profit Analysis','after_sales',5):100, ('Profit Analysis','direct_total',5):60,
      ('Profit Analysis','overhead_share',5):200, ('Profit Analysis','revenue',5):1100,
      ('Profit Analysis','net_profit',5):840,
    }
    wanted={(sheet.upper(),f'{col(sheet,key)}{row}'):value for (sheet,key,row),value in expected.items()}
    solution=formulas.ExcelModel().loads(path).finish().calculate()
    seen={}
    for key,value in solution.items():
        if '!' not in key or ']' not in key: continue
        sheet,_,coord=key.partition('!')
        cell=(sheet.split(']')[-1].rstrip("'").upper(),coord.replace('$',''))
        if cell in wanted: seen[cell]=value.value[0,0]
    assert seen.keys()==wanted.keys(), (seen.keys(),wanted.keys())
    for cell,expected_value in wanted.items():
        actual=seen[cell]
        assert actual==expected_value,(cell,expected_value,actual)
        print(cell,actual)
    print('All scenario assertions passed.')
