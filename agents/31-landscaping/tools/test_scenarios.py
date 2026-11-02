"""Run a small end-to-end calculation scenario using the optional formulas engine."""
import os, tempfile, datetime, contextlib, io
import openpyxl, formulas
from openpyxl.utils.cell import range_boundaries, get_column_letter
from landscaping_spreadsheet.build import build_workbook
from landscaping_spreadsheet.config import Config

def run():
    with tempfile.TemporaryDirectory() as d:
        path=os.path.join(d,'scenario.xlsx')
        build_workbook(path,Config(include_sample_data=False,rows_override=30,_today=datetime.date(2026,11,2)))
        w=openpyxl.load_workbook(path)
        def cell(name, i=0):
            sheet, ref=next(w.defined_names[name].destinations)
            col,row,_,_=range_boundaries(ref)
            return w[sheet].cell(row+i,col)
        def setv(name,val,i=0): cell(name,i).value=val
        # One material intentionally appears after a blank row.
        setv('MatName','Mulch',2); setv('MatOpening',5,2); setv('MatCostUnit',10,2)
        setv('JobDate',46328); setv('JobStatus','Completed'); setv('JobHoursTyped',2)
        setv('RouteDate',46328); setv('RouteCrew','Crew A')
        for i,t in enumerate([10/24,8/24,8/24,None]):
            setv('JobDate',46328,i); setv('JobCrew','Crew A',i)
            if t is not None: setv('JobStartTime',t,i)
        # Purchase inventory once; allocate part of it to the job as usage.
        for i,movement,quantity,amount in [(0,'Purchase',10,100),(1,'Usage',3,30)]:
            for name,value in [('ExpDate',46328),('ExpCategory','Materials'),('ExpMaterial','MAT-0003'),('ExpMovement',movement),('ExpQuantity',quantity),('ExpAmount',amount),('ExpJob','JOB-00001')]:setv(name,value,i)
        setv('ProfitMonth','2026-11')
        # Overnight non-job shift: 22:00 to 02:00 with a half-hour break.
        setv('TimeDate',46328); setv('TimeStartTime',22/24); setv('TimeEndTime',2/24); setv('TimeBreakMins',30)
        # Payment belongs to its last paid date, not invoice date.
        setv('InvDate',46326); setv('InvPaid',75);setv('InvPaidDate',46328)
        cells={name:(cell(name,i).parent.title,cell(name,i).coordinate) for name,i in [('MatId',2),('MatPurchased',2),('MatUsed',2),('MatOnHand',2),('ExpPeriodCost',0),('ExpPeriodCost',1),('ExpAllocatedCost',0),('ExpAllocatedCost',1),('JobExpenseCost',0),('JobLabourFallback',0),('TimeHours',0),('ProfitCollected',0),('ProfitMaterials',0),('ProfitLabour',0)]}
        cells['ExpPeriodCostUsage']=(cell('ExpPeriodCost',1).parent.title,cell('ExpPeriodCost',1).coordinate)
        cells['ExpAllocatedCostUsage']=(cell('ExpAllocatedCost',1).parent.title,cell('ExpAllocatedCost',1).coordinate)
        cells['ExpPeriodCost']=(cell('ExpPeriodCost',0).parent.title,cell('ExpPeriodCost',0).coordinate)
        cells['ExpAllocatedCost']=(cell('ExpAllocatedCost',0).parent.title,cell('ExpAllocatedCost',0).coordinate)
        for i in range(4):
            c=cell('JobRouteMatch',i); cells[f'Route{i}']=(c.parent.title,c.coordinate)
        w.save(path)
        with contextlib.redirect_stderr(io.StringIO()):
            sol=formulas.ExcelModel().loads(path).finish().calculate()
        values={}
        for key,value in sol.items():
            if '!' not in key or ']' not in key: continue
            sheet,_,coord=key.partition('!');sheet=sheet.split(']')[-1].rstrip("'").upper();coord=coord.replace('$','')
            for name,(sh,co) in cells.items():
                if (sheet,coord)==(sh.upper(),co):values[name]=value.value[0,0]
        expected={'MatId':'MAT-0003','MatPurchased':10,'MatUsed':3,'MatOnHand':12,'ExpPeriodCost':100,'ExpPeriodCostUsage':0,'ExpAllocatedCost':0,'ExpAllocatedCostUsage':30,'JobExpenseCost':30,'JobLabourFallback':76,'TimeHours':3.5,'ProfitCollected':75,'ProfitMaterials':100,'ProfitLabour':209,'Route0':3,'Route1':1,'Route2':2,'Route3':4}
        for name,exp in expected.items():
            val=values.get(name); print(name,repr(val),'expected',exp)
            assert val==exp,(name,val,exp)
        print('All scenario assertions passed.')
if __name__=='__main__': run()
