"""Evaluate core stock arithmetic in an independent formula engine (optional)."""
import datetime as dt, os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import openpyxl, formulas
from openpyxl.utils import get_column_letter
from inventory_wholesale_spreadsheet.config import Config
from inventory_wholesale_spreadsheet.build import REGISTER_MODULES, build_workbook
cfg=Config(include_sample_data=False,rows_override=8,_today=dt.date(2026,11,1))
spec={m.NAME:m.spec(cfg) for m in REGISTER_MODULES}
def col(sheet,key): return get_column_letter(next(i for i,c in enumerate(spec[sheet].columns,1) if c.key==key))
with tempfile.TemporaryDirectory(prefix='inventory-test-') as td:
 path=os.path.join(td,'scenario.xlsx');build_workbook(path,cfg);w=openpyxl.load_workbook(path)
 def put(sheet,row,**values):
  for key,v in values.items():w[sheet][f'{col(sheet,key)}{row}']=v
 put('Product & SKU Database',5,sku='SKU1',name='Product',cost=10,opening_qty=10,opening_value=100,status='Active')
 put('Product & SKU Database',7,sku='SKU2',name='Gap product',cost=5,opening_qty=5,opening_value=25,status='Active')
 put('Purchase Orders',5,po_id='PO1',sku='SKU1',qty=20,unit_cost=20,received=4,status='Partially Received')
 put('Purchase Orders',6,po_id='PO1',sku='SKU1',qty=20,unit_cost=20,received=4,status='Partially Received')
 put('Retail Sales Tracker',5,sale_id='S1',sku='SKU1',qty=2,status='Refunded')
 put('Wholesale Orders',5,order_id='O1',sku='SKU1',qty=1,status='Returned')
 put('Wholesale Orders',6,order_id='O2',sku='SKU1',qty=3,status='Confirmed')
 put('Returns & Damaged Goods',5,sku='SKU1',qty=1,source='Retail customer',condition='As new',refund=20)
 put('Returns & Damaged Goods',6,sku='SKU1',qty=1,source='Retail customer',condition='Damaged')
 put('Returns & Damaged Goods',7,sku='SKU1',qty=2,source='Own warehouse',condition='Damaged')
 put('Stock Movement Log',5,sku='SKU1',qty=-1,type='Adjustment')
 put('Stock Audit',5,sku='SKU1',system_qty=10,counted_qty=8,posted='Yes')
 w.save(path)
 expected={('Inventory Tracker','received',5):4,('Inventory Tracker','sold',5):3,
 ('Inventory Tracker','returned',5):1,('Inventory Tracker','damaged',5):2,
 ('Inventory Tracker','adjusted',5):-1,('Inventory Tracker','current',5):9,
 ('Inventory Tracker','reserved',5):3,('Inventory Tracker','available',5):6,
 ('Inventory Tracker','on_order',5):16,('Inventory Tracker','avg_cost',5):12.8571,
 ('Inventory Tracker','sku',7):'SKU2',('Inventory Tracker','current',7):5,
 ('Purchase Orders','dup_line',5):2,('Purchase Orders','valid_line',5):1,
 ('Purchase Orders','valid_line',6):0,('Purchase Orders','received_value',6):0,
 ('Stock Audit','variance',5):-2,('Returns & Damaged Goods','profit_effect',5):7.14,
 ('Returns & Damaged Goods','profit_effect',6):0,('Returns & Damaged Goods','profit_effect',7):25.71}
 wanted={(sheet.upper(),f'{col(sheet,key)}{row}'):v for (sheet,key,row),v in expected.items()}
 sol=formulas.ExcelModel().loads(path).finish().calculate(); seen={}
 for k,v in sol.items():
  if '!' not in k or ']' not in k:continue
  sh,_,coord=k.partition('!');key=(sh.split(']')[-1].rstrip("'").upper(),coord.replace('$',''))
  if key in wanted:seen[key]=v.value[0,0]
 assert wanted.keys()==seen.keys(),(wanted.keys(),seen.keys())
 for key,want in wanted.items():
  actual=seen[key]
  assert (abs(actual-want)<0.00001 if isinstance(want,(float,int)) else actual==want),(key,want,actual)
  print(key,actual)
 print('All stock and costing scenario assertions passed.')
