"""Daycare workbook generator, independently completed from an incomplete source.

Registers are intentionally simple: one transaction per ledger row, positive
amounts, and no automated authorization or staffing-compliance decisions.
"""
from __future__ import annotations

import datetime as dt
import os
from xlsxwriter import Workbook
from xlsxwriter.utility import xl_col_to_name
from .config import Config, AGE_BANDS

SHEET_ORDER = ['Dashboard', 'Getting Started', 'Settings & Lists', 'Child Enrollment',
    'Parent Database', 'Waitlist', 'Attendance', 'Tuition & Fees',
    'Invoices & Receipts', 'Daily Reports', 'Meal Tracker', 'Allergy & Medical',
    'Incident Reports', 'Staff Database', 'Staff Schedule', 'Payroll Tracker',
    'Classroom Management', 'Expense Tracker', 'Supply Inventory',
    'Parent Communication', 'Document Tracker', 'Monthly Reports', 'Annual Reports']

# (heading, kind, width); calculated columns use kind "formula:...".
SCHEMAS = {
'Child Enrollment': [('Child ID','id',15),('Child name','text',23),('Family ID','id',15),('Date of birth','date',15),('Start date','date',15),('Status','status_child',18),('Room','text',18),('Programme','text',18),('Schedule','text',22),('Notes','text',32)],
'Parent Database': [('Family ID','id',15),('Parent / guardian','text',24),('Phone','text',18),('Email','text',28),('Address','text',30),('Emergency contact','text',24),('Emergency phone','text',18),('Balance','formula:balance',16),('Notes','text',30)],
'Waitlist': [('Enquiry date','date',15),('Child name','text',23),('Parent / guardian','text',24),('Phone / email','text',28),('Desired start','date',15),('Programme','text',20),('Status','text',18),('Notes','text',32)],
'Attendance': [('Date','date',15),('Child ID','id',15),('Room','text',18),('Status','attendance',20),('Sign in','time',14),('Sign out','time',14),('Picked up by','text',24),('Notes','text',32)],
'Tuition & Fees': [('Effective from','date',15),('Fee / programme','text',24),('Basis','basis',18),('Amount','money',16),('Taxable?','yesno',14),('Notes','text',32)],
'Invoices & Receipts': [('Date','date',15),('Transaction ID','id',18),('Family ID','id',15),('Invoice reference','id',20),('Type','ledger',16),('Description','text',28),('Amount (+)','money_positive',17),('Due date','date',15),('Balance effect','formula:effect',17),('Cash effect','formula:cash',17),('Review','formula:review',20),('Notes','text',32)],
'Daily Reports': [('Date','date',15),('Child ID','id',15),('Meals / snacks','text',26),('Sleep / rest','text',24),('Activities','text',28),('Mood / notes','text',32),('Shared with family','yesno',18)],
'Meal Tracker': [('Date','date',15),('Child ID','id',15),('Meal','text',18),('Food served','text',30),('Amount / notes','text',30),('Recorded by','text',22)],
'Allergy & Medical': [('Child ID','id',15),('Category','text',20),('Details','text',36),('Action plan location','text',32),('Review date','date',15),('Contact / notes','text',32)],
'Incident Reports': [('Date','date',15),('Time','time',14),('Child ID','id',15),('Location','text',20),('Description','text',36),('Action taken','text',36),('Reported by','text',23),('Parent notified','yesno',17),('Follow-up','text',30)],
'Staff Database': [('Staff ID','id',15),('Staff name','text',24),('Role','text',20),('Phone','text',18),('Email','text',28),('Start date','date',15),('Status','text',18),('Hourly rate','money',16),('Notes','text',30)],
'Staff Schedule': [('Date','date',15),('Staff ID','id',15),('Room','text',18),('Start','time',14),('End','time',14),('Unpaid break (min)','number',20),('Scheduled hours','formula:hours',18),('Notes','text',32)],
'Payroll Tracker': [('Pay date','date',15),('Staff ID','id',15),('Period start','date',15),('Period end','date',15),('Regular hours','number',16),('Overtime hours','number',16),('Hourly rate','money',16),('OT multiplier','number',16),('Gross pay','formula:gross',16),('Employer costs','money',18),('Total cost','formula:paycost',16),('Notes','text',30)],
'Classroom Management': [('Room','text',20),('Age band','text',20),('Capacity','number',14),('Lead staff ID','id',16),('Notes','text',40)],
'Expense Tracker': [('Date','date',15),('Expense ID','id',16),('Category','text',20),('Vendor','text',24),('Description','text',30),('Amount','money_positive',16),('Payment method','text',18),('Notes','text',30)],
'Supply Inventory': [('Item','text',25),('Category','text',18),('On hand','number',14),('Reorder level','number',16),('Unit','text',14),('Supplier','text',24),('Unit cost','money',15),('Reorder?','formula:reorder',16),('Notes','text',30)],
'Parent Communication': [('Date','date',15),('Family ID','id',15),('Child ID','id',15),('Channel','text',18),('Topic','text',25),('Summary','text',38),('Follow-up date','date',17),('Status','text',18)],
'Document Tracker': [('Person ID','id',18),('Document','text',25),('Received','date',15),('Expiry','date',15),('Status','formula:doc',16),('Location / notes','text',38)],
}


def q(name):
    return "'" + name.replace("'", "''") + "'"


def build_workbook(path='Daycare Business Management Spreadsheet.xlsx', cfg=None):
    cfg = cfg or Config()
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    wb = Workbook(path)
    wb.set_properties({'title': cfg.product_name, 'author': cfg.author, 'company': cfg.author,
                       'subject': 'Childcare business management'})
    wb.set_calc_mode('auto')
    # Format conventions: blue-white inputs are unlocked; pale grey cells are formulas.
    fmt = {}
    def f(name, d): fmt[name] = wb.add_format(d)
    f('title', {'font_name':'Calibri','font_size':20,'bold':True,'font_color':'#FFFFFF','bg_color':'#194D56','valign':'vcenter'})
    f('subtitle', {'font_name':'Calibri','font_size':10,'font_color':'#E4F4EF','bg_color':'#194D56','valign':'vcenter'})
    f('note', {'font_name':'Calibri','font_size':10,'font_color':'#45616A','bg_color':'#EFF7F5','text_wrap':True,'valign':'vcenter'})
    f('header', {'font_name':'Calibri','font_size':10,'bold':True,'font_color':'#FFFFFF','bg_color':'#287B78','text_wrap':True,'valign':'vcenter','border':1,'border_color':'#DAEAE7'})
    base = {'font_name':'Calibri','font_size':10,'font_color':'#263F45','border':1,'border_color':'#E3EEEC','valign':'vcenter'}
    for name, extra in {
        'input': {'bg_color':'#FFFFFF','locked':False},
        'date': {'bg_color':'#FFFFFF','locked':False,'num_format':'dd-mmm-yyyy'},
        'time': {'bg_color':'#FFFFFF','locked':False,'num_format':'h:mm AM/PM'},
        'money': {'bg_color':'#FFFFFF','locked':False,'num_format':cfg.money_format},
        'number': {'bg_color':'#FFFFFF','locked':False,'num_format':'0.00'},
        'calc': {'bg_color':'#F1F6F5','font_color':'#365A5F'},
        'calc_money': {'bg_color':'#F1F6F5','font_color':'#365A5F','num_format':cfg.money_format},
        'calc_number': {'bg_color':'#F1F6F5','font_color':'#365A5F','num_format':'0.00'},
        'setting': {'bg_color':'#FFFFFF','locked':False},
        'setting_percent': {'bg_color':'#FFFFFF','locked':False,'num_format':'0.0%'},
        'label': {'bg_color':'#EAF4F1','bold':True},
        'card': {'bg_color':'#EAF4F1','bold':True,'font_size':14,'num_format':cfg.money_format},
        'card_num': {'bg_color':'#EAF4F1','bold':True,'font_size':14,'num_format':'0'},
    }.items(): f(name, dict(base, **extra))
    lists = {
        'status_child':['Enquiry','Waitlisted','Pending start','Active','On hold','Notice given','Withdrawn','Graduated'],
        'attendance':['Present','Late','Early pickup','Absent - sick','Absent - family','Absent - unexplained','Holiday - child','Centre closed','Not scheduled'],
        'basis':['Weekly','Monthly','Daily','Hourly','One-off'],
        'yesno':['Yes','No'],
        'ledger':['Invoice','Payment','Credit','Write-off','Refund','Deposit'],
    }
    counts = {s: max(5, int(cfg.rows.get(s, 100))) for s in SCHEMAS}
    def rng(sheet, col):
        return f"{q(sheet)}!${xl_col_to_name(col)}$7:${xl_col_to_name(col)}${6+counts[sheet]}"
    def formula(kind, r):
        led = 'Invoices & Receipts'
        if kind == 'balance':
            return f'=IF(A{r}="","",SUMIF({rng(led,2)},A{r},{rng(led,8)}))'
        if kind == 'effect':
            return f'=IF(OR(A{r}="",B{r}="",C{r}="",E{r}="",NOT(ISNUMBER(G{r})),G{r}<=0),"",IF(OR(E{r}="Invoice",E{r}="Refund"),G{r},IF(OR(E{r}="Payment",E{r}="Credit",E{r}="Write-off",E{r}="Deposit"),-G{r},0)))'
        if kind == 'cash':
            return f'=IF(OR(A{r}="",B{r}="",C{r}="",E{r}="",NOT(ISNUMBER(G{r})),G{r}<=0),"",IF(OR(E{r}="Payment",E{r}="Deposit"),G{r},IF(E{r}="Refund",-G{r},0)))'
        if kind == 'review':
            return (f'=IF(COUNTA(A{r}:H{r})=0,"",IF(OR(A{r}="",B{r}="",C{r}="",E{r}="",NOT(ISNUMBER(G{r})),G{r}<=0),"Complete row",'
                    f'IF(COUNTIF({rng("Parent Database",0)},C{r})<>1,"Check family ID",'
                    f'IF(COUNTIF({rng(led,1)},B{r})<>1,"Check transaction ID",'
                    f'IF(OR(E{r}="Invoice",E{r}="Payment",E{r}="Credit",E{r}="Write-off",E{r}="Refund",E{r}="Deposit"),"OK","Check type")))))')
        if kind == 'hours':
            return f'=IF(OR(D{r}="",E{r}=""),"",MAX(0,MOD(E{r}-D{r},1)*24-F{r}/60))'
        if kind == 'gross': return f'=IF(OR(B{r}="",G{r}=""),"",E{r}*G{r}+F{r}*G{r}*H{r})'
        if kind == 'paycost': return f'=IF(I{r}="","",I{r}+J{r})'
        if kind == 'reorder': return f'=IF(OR(A{r}="",C{r}="",D{r}=""),"",IF(C{r}<=D{r},"Reorder","OK"))'
        if kind == 'doc': return f'=IF(A{r}="","",IF(D{r}="","No expiry",IF(D{r}<TODAY(),"Expired",IF(D{r}<=TODAY()+\'Settings & Lists\'!$B$18,"Due soon","Current"))))'
        raise KeyError(kind)
    sheets = {name: wb.add_worksheet(name) for name in SHEET_ORDER}
    for name, ws in sheets.items():
        ws.hide_gridlines(2); ws.set_tab_color('#DCA854' if name in ('Dashboard','Getting Started','Settings & Lists') else '#4E9C95')
        ws.set_row(0,32); ws.set_row(1,23); ws.set_row(3,32)
        ws.merge_range('A1:H1', name.upper(), fmt['title'])
        ws.merge_range('A2:H2', 'CHILDCARE BUSINESS  /  Organize with clarity', fmt['subtitle'])
        ws.set_zoom(90); ws.set_landscape(); ws.fit_to_pages(1,0); ws.set_margins(.3,.3,.5,.5)
        ws.set_header('&LNovality Store&C' + name + '&RPage &P'); ws.set_footer('&LConfidential — store securely')
        ws.set_column('A:A',20); ws.set_column('B:H',18)
    notes = {
        'Invoices & Receipts':'One event per row. Enter tax in invoice totals. Review warnings; deposits are credits and must not also be entered as payments.',
        'Attendance':'Record actual attendance. Pickup names are notes only: independently verify authorization and identity before release.',
        'Staff Schedule':'Planned hours only. This does not check actual supervision, simultaneous coverage, breaks or legal ratios.',
        'Classroom Management':'Planning reference only; do not use as a live ratio or compliance check. Verify local rules and actual coverage independently.',
        'Allergy & Medical':'Sensitive working notes only; follow your official medical, emergency and safeguarding procedures.',
        'Incident Reports':'Sensitive working notes only; follow your official incident and safeguarding procedures.',
        'Payroll Tracker':'Enter approved hours, rate, overtime multiplier and employer costs manually. Estimates are not payroll or tax advice.',
        'Document Tracker':'Expiry alert is informational; verify required documents and retention rules independently.',
    }
    for name, schema in SCHEMAS.items():
        ws=sheets[name]; n=counts[name]
        note=notes.get(name, 'Enter information in white cells. Shaded cells calculate automatically. Use consistent IDs across sheets.')
        ws.merge_range('A4:H4',note,fmt['note']); ws.freeze_panes(6,2); ws.autofilter(5,0,5+n,len(schema)-1)
        ws.set_row(5,31)
        for col,(label,kind,width) in enumerate(schema):
            ws.set_column(col,col,width); ws.write(5,col,label,fmt['header'])
            if kind.startswith('formula:'):
                variant='calc_money' if kind in ('formula:balance','formula:effect','formula:cash','formula:gross','formula:paycost') else 'calc_number' if kind=='formula:hours' else 'calc'
                for row in range(6,6+n): ws.write_formula(row,col,formula(kind[8:],row+1),fmt[variant],0)
            else:
                variant=kind if kind in ('date','time','money','number') else 'money' if kind=='money_positive' else 'input'
                for row in range(6,6+n): ws.write_blank(row,col,None,fmt[variant])
                if kind in lists:
                    ws.data_validation(6,col,5+n,col,{'validate':'list','source':lists[kind], 'error_title':'Choose an option','error_message':'Select a value from the list.'})
                elif kind=='money_positive':
                    ws.data_validation(6,col,5+n,col,{'validate':'decimal','criteria':'>','value':0,'error_message':'Enter an amount greater than zero.'})
        if name == 'Invoices & Receipts':
            warning=wb.add_format({'bg_color':'#FCEBD7','font_color':'#8A4F16'})
            ws.conditional_format(6,10,5+n,10,{'type':'formula','criteria':'=AND($K7<>"",$K7<>"OK")','format':warning})
        ws.repeat_rows(0,5)
    # Settings: local assumptions are editable and never portrayed as legal defaults.
    ws=sheets['Settings & Lists']; ws.merge_range('A4:H4','Edit local settings and reference values. Ratios are examples, not legal guidance. Tax and rate references do not calculate invoices or payroll.',fmt['note'])
    settings=[('Centre name',cfg.centre.name),('Owner / director',cfg.centre.owner),('Currency code',cfg.currency_code),('Report year',cfg.year),('Licensed places',cfg.licensed_capacity),('Open days / week',cfg.open_days),('Opening hour (24h)',cfg.open_hour),('Closing hour (24h)',cfg.close_hour),('Tax rate',cfg.tax_rate),('Tax on tuition?',cfg.tax_on_tuition),('Tax on extras?',cfg.tax_on_extras),('Document warning days',cfg.document_warning_days),('Monthly revenue target',cfg.revenue_target_month),('Default hourly rate',cfg.default_hourly),('Overtime after hours',cfg.overtime_after_hours),('Payroll burden reference',cfg.payroll_burden),('Weeks open / year',cfg.weeks_open),('Full-time weekly fee reference',cfg.full_time_week),('Default billing basis reference',cfg.default_billing_basis),('Sibling discount reference',cfg.sibling_discount)]
    for idx,(label,value) in enumerate(settings,6):
        ws.write(idx,0,label,fmt['label']); ws.write(idx,1,value,fmt['setting_percent'] if label in ('Tax rate','Payroll burden reference','Sibling discount reference') else fmt['setting'])
    ws.set_column('A:A',28); ws.set_column('B:B',24); ws.set_column('D:H',19)
    for col,header in enumerate(['Age band','From months','To months (exclusive)','Children / adult','Group size reference'],3): ws.write(5,col,header,fmt['header'])
    for r,band in enumerate(AGE_BANDS,6):
        for c,v in enumerate(band,3): ws.write(r,c,v,fmt['setting'])
    ws.freeze_panes(6,1)
    # Operational guidance and privacy disclosures.
    ws=sheets['Getting Started']; ws.merge_range('A4:H4','START HERE  •  Designed for Excel desktop; save a protected copy before entering real data.',fmt['note']); ws.set_column('A:A',24); ws.set_column('B:H',17)
    guidance=[('01  Configure','Edit Settings & Lists and confirm local age bands and ratios with your regulator. The example values are not legal advice.'),
      ('02  Add people','Create unique family, child and staff IDs. Use the same ID consistently in every register. IDs are manual; duplicates are not prevented.'),
      ('03  Record activity','Enter attendance, schedules, fees, payroll and expenses in their registers. Add one row per event; filters are on row 6.'),
      ('04  Record money','Invoices & Receipts uses positive amounts: Invoice and Refund increase balance; Payment, Deposit, Credit and Write-off reduce it. Amounts include any applicable tax.'),
      ('05  Reconcile','A deposit is a credit when received, not a second payment when applied. Use one family ID per transaction; reconcile with bank and accounting records.'),
      ('06  Review','Resolve ledger review warnings. Reports are dated management summaries, not accounting. Exclude payroll from expenses to avoid double-counting costs.'),
      ('Safety first','Pickup names are notes, not authorization. Schedules and ratio examples do not establish actual supervision or licensing compliance.'),
      ('Privacy','Sheet password premium prevents accidental edits, not access. It is not encryption. Use encrypted, access-controlled storage, backups and a retention policy.'),
      ('Protection','White cells are editable; shaded formulas are locked. Unprotect with premium if needed. No messages, payments, filings or records are sent automatically.'),
      ('Scope','No medical, legal, tax, payroll or accounting advice. Verify every record and follow your own procedures; workbook capacities are finite.')]
    for i,(a,b) in enumerate(guidance,6):
        ws.set_row(i,40); ws.write(i,0,a,fmt['label']); ws.merge_range(i,1,i,7,b,fmt['note'])
    # Date-based report formulas; SUMIFS avoids volatile and modern-only functions.
    ws=sheets['Monthly Reports']; ws.merge_range('A4:H4','Report year comes from Settings. Net charges = invoices − credits − write-offs. Net cash = payments + deposits − refunds.',fmt['note']); ws.freeze_panes(6,1)
    headers=['Month','Invoices','Credits','Write-offs','Net charges','Net cash','Expenses','Payroll cost','Cash less costs']
    for c,h in enumerate(headers): ws.write(5,c,h,fmt['header']); ws.set_column(c,c,19)
    ws.set_row(5,28)
    def sumperiod(sheet, amountcol, datecol, r, typecol=None, typ=None):
        args=f'{rng(sheet,amountcol)},{rng(sheet,datecol)},">="&$A{r},{rng(sheet,datecol)},"<"&EDATE($A{r},1)'
        if typecol is not None: args+=f',{rng(sheet,typecol)},"{typ}"'
        return f'SUMIFS({args})'
    datefmt=wb.add_format({'font_name':'Calibri','bg_color':'#F1F6F5','num_format':'mmm yyyy','border':1,'border_color':'#E3EEEC'})
    for i in range(12):
        r=i+7; x=r-1; ws.write_formula(x,0,f'=DATE(\'Settings & Lists\'!$B$10,{i+1},1)',datefmt)
        for c,typ in [(1,'Invoice'),(2,'Credit'),(3,'Write-off')]: ws.write_formula(x,c,'='+sumperiod('Invoices & Receipts',6,0,r,4,typ),fmt['calc_money'])
        ws.write_formula(x,4,f'=B{r}-C{r}-D{r}',fmt['calc_money'])
        ws.write_formula(x,5,'='+sumperiod('Invoices & Receipts',9,0,r),fmt['calc_money'])
        ws.write_formula(x,6,'='+sumperiod('Expense Tracker',5,0,r),fmt['calc_money'])
        ws.write_formula(x,7,'='+sumperiod('Payroll Tracker',10,0,r),fmt['calc_money'])
        ws.write_formula(x,8,f'=F{r}-G{r}-H{r}',fmt['calc_money'])
    ws=sheets['Annual Reports']; ws.merge_range('A4:H4','Annual totals sum the 12 months on Monthly Reports; not an accrual profit-and-loss statement.',fmt['note']); ws.set_column('A:A',30); ws.set_column('B:B',22)
    for i,(label,col) in enumerate(zip(headers[1:], 'BCDEFGHI'),6): ws.write(i,0,label,fmt['label']); ws.write_formula(i,1,f'=SUM(\'Monthly Reports\'!{col}7:{col}18)',fmt['calc_money'])
    ws=sheets['Dashboard']; ws.merge_range('A4:H4','A simple overview of records and the selected reporting year. Review source registers and reconcile regularly.',fmt['note']); ws.set_column('A:A',29); ws.set_column('B:B',22); ws.set_column('D:D',26); ws.set_column('E:E',22)
    metrics=[('Active children',f'=COUNTIF({rng("Child Enrollment",5)},"Active")','card_num'),('Families',f'=COUNTA({rng("Parent Database",0)})','card_num'),('Total family balance',f'=SUM({rng("Invoices & Receipts",8)})','card'),('Selected year net charges',"='Annual Reports'!B10",'card'),('Selected year net cash',"='Annual Reports'!B11",'card'),('Selected year cash less costs',"='Annual Reports'!B14",'card')]
    for i,(label,form,style) in enumerate(metrics,6): ws.set_row(i,28); ws.write(i,0,label,fmt['label']); ws.write_formula(i,1,form,fmt[style])
    ws.merge_range('D7:H10','SUPERVISION & PICKUP\nThis workbook does not verify staffing coverage, ratios or pickup authorization. Follow your documented procedures.',fmt['note'])
    ws.merge_range('D12:H14','PRIVACY\nSheet protection is not encryption. Store sensitive records in an encrypted, access-controlled location.',fmt['note'])
    if cfg.include_sample_data:
        _sample(sheets,fmt,cfg,SCHEMAS)
    for ws in sheets.values():
        if cfg.protect_sheets: ws.protect(cfg.password,{'autofilter':True,'sort':True,'select_locked_cells':True,'select_unlocked_cells':True})
    sheets['Dashboard'].activate(); sheets['Dashboard'].set_first_sheet()
    wb.close()
    return path


def _sample(sheets, fmt, cfg, schemas):
    today=cfg.today; first=dt.date(today.year,today.month,1)
    def t(h,m=0): return dt.time(h,m)
    demo={
      'Child Enrollment': [['CHD-001','Avery Brooks','FAM-001',dt.date(today.year-3,4,15),first,'Active','Sunflower','Preschool','Full time','Example record'],['CHD-002','Milo Chen','FAM-002',dt.date(today.year-2,8,9),first,'Active','Willow','Toddler','3 days','Example record']],
      'Parent Database': [['FAM-001','Jordan Brooks','555-0101','jordan@example.com','Example address','Casey Brooks','555-0102',None,'Example record'],['FAM-002','Riley Chen','555-0111','riley@example.com','Example address','Taylor Chen','555-0112',None,'Example record']],
      'Waitlist': [[first,'Noah Lane','Morgan Lane','morgan@example.com',first,'Preschool','Contacted','Example enquiry']],
      'Attendance': [[today,'CHD-001','Sunflower','Present',t(8,15),t(16,30),'Jordan Brooks','Example only'],[today,'CHD-002','Willow','Present',t(8,30),t(15,45),'Riley Chen','Example only']],
      'Tuition & Fees': [[first,'Full-time tuition','Weekly',285,'No','Example rate'],[first,'Registration','One-off',95,'No','Example rate']],
      'Invoices & Receipts': [[first,'TX-001','FAM-001','INV-001','Invoice','Weekly tuition',100,first,None,None,None,'Demo: 100 − 30 = 70'],[first,'TX-002','FAM-001','INV-001','Payment','Bank payment',30,None,None,None,None,'Demo payment'],[first,'TX-003','FAM-002','INV-002','Invoice','Weekly tuition',200,first,None,None,None,'Demo invoice'],[first,'TX-004','FAM-002','','Deposit','Deposit received',40,None,None,None,None,'One credit; do not enter twice']],
      'Daily Reports': [[today,'CHD-001','Lunch and snack','Rested','Art and outdoor play','Happy day','Yes']],
      'Meal Tracker': [[today,'CHD-001','Lunch','Vegetables and rice','Ate most','STAFF-001']],
      'Allergy & Medical': [['CHD-001','Example only','No real medical data','See official records',None,'Replace with approved records']],
      'Incident Reports': [[today,t(10),'CHD-002','Play area','Example incident only','Followed centre procedure','STAFF-001','Yes','Example follow-up']],
      'Staff Database': [['STAFF-001','Alex Rivera','Educator','555-0121','alex@example.com',first,'Active',18,'Example staff']],
      'Staff Schedule': [[today,'STAFF-001','Sunflower',t(8),t(16),30,None,'Planned schedule only']],
      'Payroll Tracker': [[first,'STAFF-001',first,first,8,0,18,1.5,None,20,None,'Example only']],
      'Classroom Management': [['Sunflower','Preschool',20,'STAFF-001','Example only'],['Willow','Toddler',12,'STAFF-001','Example only']],
      'Expense Tracker': [[first,'EXP-001','Supplies','Example supplier','Art supplies',25,'Card','Example expense']],
      'Supply Inventory': [['Paper towels','Cleaning',4,5,'packs','Example supplier',6,None,'Example stock']],
      'Parent Communication': [[today,'FAM-001','CHD-001','In person','Daily update','Example note',None,'Complete']],
      'Document Tracker': [['CHD-001','Enrollment form',first,None,None,'Example only']],
    }
    for sheet,rows in demo.items():
        for r,values in enumerate(rows,6):
            for c,val in enumerate(values):
                if val is None or c>=len(schemas[sheet]) or schemas[sheet][c][1].startswith('formula:'): continue
                kind=schemas[sheet][c][1]
                style=fmt['date'] if kind=='date' else fmt['time'] if kind=='time' else fmt['money'] if kind.startswith('money') else fmt['number'] if kind=='number' else fmt['input']
                if isinstance(val,(dt.date,dt.time,dt.datetime)): sheets[sheet].write_datetime(r,c,val,style)
                else: sheets[sheet].write(r,c,val,style)
