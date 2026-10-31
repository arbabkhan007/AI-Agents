#!/usr/bin/env python3
"""Build a 20-sheet short-term rental management workbook.

An independently implemented generator based on the supplied specification.
It does not reproduce all 37 original modules; see README for differences.
"""
import argparse, datetime as dt, os
import xlsxwriter
from xlsxwriter.utility import xl_col_to_name

SHEETS=['Dashboard','Getting Started','Settings & Lists','Property Database','Booking Tracker','Booking Calendar','Guest Database','Check-in & Check-out','Cleaning Schedule','Turnover Checklist','Platform Revenue & Fees','Expense Tracker','Supplies Inventory','Maintenance Log','Reviews Tracker','Staff & Vendors','Tax Summary','Occupancy & Performance','Monthly Reports','Annual Reports']
# Header, type, column width. Input IDs are row-generated: don't sort or insert rows.
SCHEMAS={
'Property Database':[('Property ID','f:property_id',15),('Property name','text',25),('Address','text',30),('City / area','text',20),('Status','property_status',19),('Ownership','text',22),('Listed since','date',15),('Nightly rate','money',16),('Cleaning fee','money',16),('Cleaning cost','money',16),('Security deposit','money',17),('Min nights','number',14),('Sleeps','number',12),('Check-in time','time',15),('Check-out time','time',15),('Notes','text',30)],
'Booking Tracker':[('Booking ID','f:booking_id',15),('Property ID','property_id',15),('Guest ID','guest_id',15),('Platform','platform',20),('Status','booking_status',20),('Booked on','date',15),('Check-in','date',15),('Check-out','date',15),('Nights','f:nights',12),('Rate override','money',16),('Rate used','f:rate',16),('Room discount','money',16),('Room revenue','f:room',16),('Cleaning override','money',18),('Cleaning fee','f:cleanfee',16),('Extra fees','money',16),('Gross before tax','f:gross',18),('Commission %','f:commission',15),('Processing %','f:processing',15),('Platform fees','f:fees',16),('Host tax due','f:tax',16),('Net revenue','f:net',16),('Expected payout','f:expected',18),('Clashes','f:clash',14),('Review','f:booking_review',30),('Notes','text',30)],
'Guest Database':[('Guest ID','f:guest_id',15),('Guest name','text',24),('Email','text',30),('Phone','text',20),('Country','text',18),('Marketing consent','yesno',20),('Completed stays','f:stays',18),('Completed nights','f:guest_nights',18),('Notes','text',32)],
'Check-in & Check-out':[('Booking ID','booking_id',15),('Property ID','f:from_booking_b',15),('Guest ID','f:from_booking_c',15),('Arrival','f:from_booking_g',15),('Departure','f:from_booking_h',15),('Directions sent','yesno',16),('Access sent','yesno',16),('Wi-Fi sent','yesno',15),('Rules sent','yesno',15),('Welcome sent','yesno',17),('Checkout notes sent','yesno',20),('Checked out','yesno',16),('Inspected','yesno',16),('Photographed','yesno',17),('Steps complete','f:arrival_steps',17),('Notes','text',30)],
'Cleaning Schedule':[('Booking ID','f:clean_booking',16),('Property ID','f:clean_property',16),('Check-out','f:clean_date',15),('Cleaner ID','vendor_id',16),('Clean date override','date',20),('Clean date','f:clean_date_used',16),('Status','clean_status',20),('Bedrooms','yesno',13),('Bathrooms','yesno',13),('Kitchen','yesno',13),('Living','yesno',13),('Floors','yesno',13),('Laundry','yesno',13),('Rubbish','yesno',13),('Restock','yesno',13),('Inspection','yesno',15),('Completion','f:clean_completion',16),('Estimated clean cost','f:clean_cost',20),('Notes','text',30)],
'Platform Revenue & Fees':[('Booking ID','booking_id',16),('Payout date','date',15),('Bank net amount','money',18),('Statement ref','text',20),('Expected payout','f:payout_expected',18),('Total received for booking','f:payout_total',23),('Difference vs expected','f:payout_variance',23),('Review','f:payout_review',25),('Notes','text',30)],
'Expense Tracker':[('Expense ID','f:expense_id',16),('Date','date',15),('Property ID','property_id',16),('Category','expense_category',23),('Vendor','text',22),('Description','text',30),('Amount','money',16),('Tax category','tax_category',22),('Count in profit?','yesno',19),('Receipt ref','text',20),('Notes','text',30)],
'Supplies Inventory':[('Item','text',24),('Property ID','property_id',16),('Unit','text',14),('In stock','number',14),('Minimum','number',14),('Unit cost','money',15),('Stock value','f:stock_value',16),('Order now?','f:stock_alert',15),('Supplier','text',25),('Notes','text',30)],
'Maintenance Log':[('Job ID','f:maintenance_id',16),('Reported','date',15),('Property ID','property_id',16),('Category','text',20),('Description','text',32),('Priority','priority',14),('Vendor ID','vendor_id',16),('Scheduled','date',15),('Completed','date',15),('Status','maint_status',18),('Estimate','money',15),('Actual cost','money',15),('Warranty until','date',17),('Warranty days left','f:warranty',20),('Notes','text',30)],
'Reviews Tracker':[('Booking ID','booking_id',16),('Review date','date',15),('Overall','rating',13),('Cleanliness','rating',15),('Accuracy','rating',14),('Check-in','rating',14),('Communication','rating',18),('Location','rating',14),('Value','rating',13),('Detail average','f:review_avg',17),('Replied?','yesno',15),('Review / notes','text',36)],
'Staff & Vendors':[('Vendor ID','f:vendor_id',16),('Name','text',24),('Role','text',20),('Company','text',23),('Phone','text',18),('Email','text',28),('Rate','money',14),('Pay basis','text',20),('Insurance expires','date',19),('Days remaining','f:insurance',18),('Notes','text',30)],
'Occupancy & Performance':[('Property ID','f:perf_property',16),('Month','f:perf_month',16),('Listed nights','f:listed',17),('Blocked nights','f:blocked',18),('Available nights','f:available',18),('Booked nights','f:booked',17),('Occupancy','f:occupancy',16),('Room revenue','f:period_room',18),('ADR','f:adr',16),('RevPAR','f:revpar',16),('Notes','text',30)]}
DEFAULTS={'Property Database':30,'Booking Tracker':900,'Guest Database':400,'Check-in & Check-out':900,'Cleaning Schedule':900,'Platform Revenue & Fees':900,'Expense Tracker':700,'Supplies Inventory':300,'Maintenance Log':300,'Reviews Tracker':600,'Staff & Vendors':60,'Occupancy & Performance':360}
EXPENSES=['Cleaning','Laundry','Utilities - electric','Utilities - gas','Utilities - water','Internet & TV','Maintenance','Repairs','Furniture','Appliances','Guest amenities','Welcome basket','Insurance','Property taxes','Mortgage interest','Rent','Service charge','Supplies','Management fees','Co-host fees','Marketing & photography','Software & subscriptions','Licences & permits','Accounting & legal','Travel & mileage','Bank & card fees','Guest refunds','Miscellaneous']
LISTS={'yesno':['Yes','No'],'property_status':['Active','Inactive','Under maintenance','Seasonal closure','Being set up','Sold / ended'],'booking_status':['Inquiry','Confirmed','Checked in','Completed','Cancelled','Owner block','Maintenance block'],'clean_status':['Not scheduled','Scheduled','In progress','Complete','Complete - issues','Skipped','Cancelled'],'maint_status':['Reported','Quoted','Scheduled','In progress','Complete','Waiting on parts','Waiting on owner','Cancelled'],'priority':['Urgent','High','Normal','Low'],'tax_category':['Operating expense','Capital / asset','Financing cost','Owner drawing','Not deductible','Review with accountant']}
PLATFORMS=[('Airbnb',.03,0),('Vrbo',.05,.03),('Booking.com',.15,0),('Expedia',.15,0),('Direct booking',0,.029),('Returning guest',0,.029),('Corporate / relocation',0,.02),('Other',.10,0)]

def parse():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('-o','--output',default='output/Airbnb & Short-Term Rental Management Spreadsheet.xlsx');p.add_argument('--blank',action='store_true');p.add_argument('--no-protect',action='store_true');p.add_argument('--password',default='premium');p.add_argument('--author',default='Novality Store');p.add_argument('--business');p.add_argument('--owner');p.add_argument('--currency',default='$');p.add_argument('--currency-code',default='USD');p.add_argument('--year',type=int);p.add_argument('--nightly',type=float,default=185);p.add_argument('--cleaning-fee',type=float,default=95);p.add_argument('--cleaning-cost',type=float,default=65);p.add_argument('--deposit',type=float,default=300);p.add_argument('--min-nights',type=int,default=2);p.add_argument('--tax',type=float,default=0);p.add_argument('--tax-self',action='store_true');p.add_argument('--occupancy-target',type=float,default=72);p.add_argument('--adr-target',type=float,default=195);p.add_argument('--revenue-target',type=float,default=14000);p.add_argument('--properties',type=int,default=4);p.add_argument('--rows',type=int,default=900);p.add_argument('--today',type=dt.date.fromisoformat,default=dt.date.today());p.add_argument('--quiet',action='store_true')
 a=p.parse_args()
 if a.rows<30 or a.rows>3000: p.error('--rows must be between 30 and 3000')
 if not 0<=a.tax<=100 or not 0<=a.occupancy_target<=100: p.error('percentages must be between 0 and 100')
 if not 1<=a.properties<=30: p.error('--properties must be between 1 and 30')
 return a

def build(a):
 os.makedirs(os.path.dirname(os.path.abspath(a.output)),exist_ok=True)
 w=xlsxwriter.Workbook(a.output);w.set_properties({'title':'Airbnb & Short-Term Rental Management Spreadsheet','author':a.author,'company':a.author});w.set_calc_mode('auto')
 F={}; base={'font_name':'Calibri','font_size':10,'font_color':'#243D45','border':1,'border_color':'#DFECEC','valign':'vcenter'}
 def add(k,d):F[k]=w.add_format(d)
 add('title',{'font_name':'Calibri','font_size':20,'bold':1,'font_color':'white','bg_color':'#113A4C','valign':'vcenter'})
 add('sub',{'font_name':'Calibri','font_size':10,'font_color':'#E4F4F2','bg_color':'#113A4C','valign':'vcenter'})
 add('note',{'font_name':'Calibri','font_size':10,'font_color':'#415E64','bg_color':'#EAF5F4','text_wrap':1,'valign':'vcenter'})
 add('header',{'font_name':'Calibri','font_size':10,'bold':1,'font_color':'white','bg_color':'#1C6E78','border':1,'border_color':'#DAE8E8','text_wrap':1,'valign':'vcenter'})
 money='"'+a.currency.replace('"','')+'"#,##0.00;[Red]-"'+a.currency.replace('"','')+'"#,##0.00'
 for k,d in {'input':{'locked':False,'bg_color':'#FFFFFF'},'date':{'locked':False,'bg_color':'#FFFFFF','num_format':'dd-mmm-yyyy'},'time':{'locked':False,'bg_color':'#FFFFFF','num_format':'h:mm AM/PM'},'money':{'locked':False,'bg_color':'#FFFFFF','num_format':money},'number':{'locked':False,'bg_color':'#FFFFFF','num_format':'0.00'},'percent':{'locked':False,'bg_color':'#FFFFFF','num_format':'0.0%'},'calc':{'bg_color':'#F0F6F5'},'calc_money':{'bg_color':'#F0F6F5','num_format':money},'calc_percent':{'bg_color':'#F0F6F5','num_format':'0.0%'},'calc_date':{'bg_color':'#F0F6F5','num_format':'dd-mmm-yyyy'},'label':{'bold':True,'bg_color':'#E5F1F0'},'big':{'bold':True,'font_size':15,'bg_color':'#E5F1F0','num_format':money}}.items():add(k,dict(base,**d))
 ws={name:w.add_worksheet(name) for name in SHEETS}; counts={s:(n if s in ('Property Database','Occupancy & Performance') else max(12,round(n*a.rows/900))) for s,n in DEFAULTS.items()};counts['Cleaning Schedule']=counts['Booking Tracker']
 def rng(s,c):return "'"+s+"'!$"+xl_col_to_name(c)+'$7:$'+xl_col_to_name(c)+'$'+str(counts[s]+6)
 B=lambda c:rng('Booking Tracker',c); P=lambda c:rng('Property Database',c); E=lambda c:rng('Expense Tracker',c); V=lambda c:rng('Platform Revenue & Fees',c)
 # Settings positions: B7.. and platform table E7:G16.
 def lookup(prop,col):return f'IFERROR(INDEX({P(col)},MATCH({prop},{P(0)},0)),0)'
 def f(kind,r):
  trigger={'property_id':('B','PRP-',2),'booking_id':('G','BKG-',4),'guest_id':('B','GST-',4),'expense_id':('B','EXP-',4),'maintenance_id':('B','MNT-',3),'vendor_id':('B','VND-',3)}
  if kind in trigger:
   c,pre,d=trigger[kind];return f'=IF({c}{r}="","","{pre}"&TEXT(ROW()-6,"'+('0'*d)+'"))'
  if kind=='nights':return f'=IF(OR(G{r}="",H{r}="",H{r}<=G{r}),"",H{r}-G{r})'
  if kind=='rate':return f'=IF(G{r}="","",IF(J{r}<>"",J{r},{lookup(f"B{r}",7)}))'
  if kind=='room':return f'=IF(G{r}="","",IF(AND(ISNUMBER(I{r}),OR(E{r}="Confirmed",E{r}="Checked in",E{r}="Completed")),MAX(0,I{r}*K{r}-L{r}),0))'
  if kind=='cleanfee':return f'=IF(G{r}="","",IF(AND(ISNUMBER(I{r}),OR(E{r}="Confirmed",E{r}="Checked in",E{r}="Completed")),IF(N{r}<>"",N{r},{lookup(f"B{r}",8)}),0))'
  if kind=='gross':return f'=IF(G{r}="","",IF(AND(ISNUMBER(I{r}),OR(E{r}="Confirmed",E{r}="Checked in",E{r}="Completed")),ROUND(M{r}+O{r}+P{r},2),0))'
  if kind in ('commission','processing'):
   col='F' if kind=='commission' else 'G';return f'=IF(G{r}="","",IFERROR(INDEX(\'Settings & Lists\'!${col}$7:${col}$16,MATCH(D{r},\'Settings & Lists\'!$E$7:$E$16,0)),0))'
  if kind=='fees':return f'=IF(G{r}="","",ROUND(Q{r}*(R{r}+S{r}),2))'
  if kind=='tax':return f'=IF(G{r}="","",IF(\'Settings & Lists\'!$B$17="Self",ROUND(M{r}*\'Settings & Lists\'!$B$16,2),0))'
  if kind=='net':return f'=IF(G{r}="","",ROUND(Q{r}-T{r},2))'
  if kind=='expected':return f'=IF(G{r}="","",ROUND(V{r}+U{r},2))'
  if kind=='clash':return f'=IF(OR(B{r}="",I{r}="",NOT(OR(E{r}="Confirmed",E{r}="Checked in",E{r}="Completed",E{r}="Owner block",E{r}="Maintenance block"))),"",COUNTIFS({B(1)},B{r},{B(6)},"<"&H{r},{B(7)},">"&G{r},{B(4)},"Confirmed")+COUNTIFS({B(1)},B{r},{B(6)},"<"&H{r},{B(7)},">"&G{r},{B(4)},"Checked in")+COUNTIFS({B(1)},B{r},{B(6)},"<"&H{r},{B(7)},">"&G{r},{B(4)},"Completed")+COUNTIFS({B(1)},B{r},{B(6)},"<"&H{r},{B(7)},">"&G{r},{B(4)},"Owner block")+COUNTIFS({B(1)},B{r},{B(6)},"<"&H{r},{B(7)},">"&G{r},{B(4)},"Maintenance block")-1)'
  if kind=='booking_review':return f'=IF(COUNTA(B{r}:H{r})=0,"",IF(OR(B{r}="",G{r}="",H{r}="",E{r}=""),"Complete booking",IF(COUNTIF({P(0)},B{r})<>1,"Check property ID",IF(H{r}<=G{r},"Check dates",IF(X{r}>0,"DOUBLE BOOKED",IF(AND(OR(E{r}="Confirmed",E{r}="Checked in",E{r}="Completed"),COUNTIF(\'Settings & Lists\'!$E$7:$E$16,D{r})<>1),"Check platform","OK"))))))'
  if kind in ('stays','guest_nights'):
   sumx=f'COUNTIFS({B(2)},A{r},{B(4)},"Completed")' if kind=='stays' else f'SUMIFS({B(8)},{B(2)},A{r},{B(4)},"Completed")';return f'=IF(B{r}="","",{sumx})'
  if kind.startswith('from_booking_'):
   idx={'b':1,'c':2,'g':6,'h':7}[kind[-1]];return f'=IF(A{r}="","",IFERROR(INDEX({B(idx)},MATCH(A{r},{B(0)},0)),""))'
  if kind=='arrival_steps':return f'=IF(A{r}="","",COUNTIF(F{r}:N{r},"Yes")/9)'
  if kind=='clean_booking':return f'=IF(OR(\'Booking Tracker\'!A{r}="",NOT(OR(\'Booking Tracker\'!E{r}="Confirmed",\'Booking Tracker\'!E{r}="Checked in",\'Booking Tracker\'!E{r}="Completed"))),"",\'Booking Tracker\'!A{r})'
  if kind=='clean_property':return f'=IF(A{r}="","",\'Booking Tracker\'!B{r})'
  if kind=='clean_date':return f'=IF(A{r}="","",\'Booking Tracker\'!H{r})'
  if kind=='clean_date_used':return f'=IF(A{r}="","",IF(E{r}="",C{r},E{r}))'
  if kind=='clean_completion':return f'=IF(A{r}="","",COUNTIF(H{r}:P{r},"Yes")/9)'
  if kind=='clean_cost':return f'=IF(A{r}="","",{lookup(f"B{r}",9)})'
  if kind=='payout_expected':return f'=IF(A{r}="","",IFERROR(INDEX({B(22)},MATCH(A{r},{B(0)},0)),""))'
  if kind=='payout_total':return f'=IF(A{r}="","",SUMIF({V(0)},A{r},{V(2)}))'
  if kind=='payout_variance':return f'=IF(OR(A{r}="",E{r}=""),"",ROUND(F{r}-E{r},2))'
  if kind=='payout_review':return f'=IF(A{r}="","",IF(COUNTIF({B(0)},A{r})<>1,"Check booking ID",IF(OR(B{r}="",C{r}=""),"Complete payment row","OK")))'
  if kind=='stock_value':return f'=IF(A{r}="","",D{r}*F{r})'
  if kind=='stock_alert':return f'=IF(OR(A{r}="",D{r}="",E{r}=""),"",IF(D{r}<=E{r},"Order now","OK"))'
  if kind=='warranty':return f'=IF(OR(B{r}="",M{r}=""),"",M{r}-TODAY())'
  if kind=='insurance':return f'=IF(OR(B{r}="",I{r}=""),"",I{r}-TODAY())'
  if kind=='review_avg':return f'=IF(COUNT(D{r}:I{r})=0,"",ROUND(AVERAGE(D{r}:I{r}),2))'
  if kind=='perf_property':
   idx=(r-7)//12+1;return f'=IF(INDEX({P(0)},{idx})="","",INDEX({P(0)},{idx}))'
  if kind=='perf_month':return f'=IF(A{r}="","",DATE(\'Settings & Lists\'!$B$10,{(r-7)%12+1},1))'
  if kind=='listed':return f'=IF(A{r}="","",IF({lookup(f"A{r}",4)}<>"Active",0,MAX(0,EDATE(B{r},1)-MAX(B{r},IF({lookup(f"A{r}",6)}=0,B{r},{lookup(f"A{r}",6)})))))'
  # Allocate each night in the intersection [check-in, check-out) and month.
  if kind in ('booked','blocked','period_room'):
   status=f'(({B(4)}="Confirmed")+({B(4)}="Checked in")+({B(4)}="Completed"))' if kind!='blocked' else f'(({B(4)}="Owner block")+({B(4)}="Maintenance block"))'
   ci=B(6);co=B(7); end=f'EDATE(B{r},1)'; start=f'EDATE(B{r},1)-C{r}'; overlap=f'IF(({ci}<{end})*({co}>{start}),IF({co}<{end},{co},{end})-IF({ci}>{start},{ci},{start}),0)'
   factor=f'IFERROR({B(12)}/IF({B(8)}>0,{B(8)},1),0)*' if kind=='period_room' else ''
   return f'=IF(A{r}="","",IF(C{r}<=0,0,ROUND(SUMPRODUCT(({B(1)}=A{r})*{status}*{factor}{overlap}),2)))'
  if kind=='available':return f'=IF(A{r}="","",MAX(0,C{r}-D{r}))'
  if kind=='occupancy':return f'=IF(OR(A{r}="",E{r}<=0),"",F{r}/E{r})'
  if kind=='adr':return f'=IF(OR(A{r}="",F{r}<=0),"",ROUND(H{r}/F{r},2))'
  if kind=='revpar':return f'=IF(OR(A{r}="",E{r}<=0),"",ROUND(H{r}/E{r},2))'
  raise KeyError(kind)
 for name,s in ws.items():
  s.hide_gridlines(2);s.set_tab_color('#E2703A' if name in ('Dashboard','Getting Started','Settings & Lists') else '#3F97A0');s.set_zoom(90);s.set_row(0,34);s.set_row(1,24);s.set_row(3,34);s.set_column('A:H',18);s.merge_range('A1:H1',name.upper(),F['title']);s.merge_range('A2:H2','SHORT-TERM RENTAL MANAGER  /  Organize your portfolio',F['sub']);s.set_landscape();s.fit_to_pages(1,0);s.set_header('&LNovality Store&C'+name+'&RPage &P');s.set_footer('&LPrivate - store securely')
 for name, col, defined in [('Property Database',0,'PropertyIDs'),('Guest Database',0,'GuestIDs'),('Booking Tracker',0,'BookingIDs'),('Staff & Vendors',0,'VendorIDs')]: w.define_name(defined,'='+rng(name,col))
 w.define_name('PlatformNames',"='Settings & Lists'!$E$7:$E$16");w.define_name('ExpenseCategories',"='Settings & Lists'!$H$7:$H$34")
 for name,schema in SCHEMAS.items():
  s=ws[name]; n=counts[name]; note='White cells are editable. Shaded cells calculate. Use IDs consistently; filter rather than sort or insert rows.'
  if name=='Booking Tracker':note='Enter each booking or block manually. Clash checks cover entered rows only; verify all platform calendars independently.'
  if name=='Cleaning Schedule':note='Jobs mirror booking row positions. Enter task updates here; do not sort, insert, delete or move booking rows after adding updates.'
  if name=='Platform Revenue & Fees':note='Enter actual net bank deposits once per row; split payouts are summed by booking. Review the total difference, not each payment alone.'
  if name=='Occupancy & Performance':note='Per-night allocations across month boundaries. Current Active status and listed date define availability; review overlaps and inactive history.'
  s.merge_range('A4:H4',note,F['note']);s.freeze_panes(6,2);s.autofilter(5,0,5+n,len(schema)-1);s.set_row(5,32);s.repeat_rows(0,5)
  for col,(label,kind,width) in enumerate(schema):
   s.set_column(col,col,width);s.write(5,col,label,F['header'])
   if kind.startswith('f:'):
    k=kind[2:];sty='calc_money' if k in ('rate','room','cleanfee','gross','fees','tax','net','expected','payout_expected','payout_total','payout_variance','clean_cost','stock_value','period_room','adr','revpar') else 'calc_percent' if k in ('commission','processing','occupancy','clean_completion','arrival_steps') else 'calc_date' if k in ('perf_month','clean_date','clean_date_used','from_booking_g','from_booking_h') else 'calc'
    for i in range(6,6+n):s.write_formula(i,col,f(k,i+1),F[sty],0)
   else:
    sty=kind if kind in ('date','time','money','number') else 'number' if kind=='rating' else 'input'
    for i in range(6,6+n):s.write_blank(i,col,None,F[sty])
    if kind in LISTS:s.data_validation(6,col,5+n,col,{'validate':'list','source':LISTS[kind]})
    if kind in ('property_id','guest_id','vendor_id','booking_id','platform','expense_category'):
     named={'property_id':'PropertyIDs','guest_id':'GuestIDs','vendor_id':'VendorIDs','booking_id':'BookingIDs','platform':'PlatformNames','expense_category':'ExpenseCategories'}[kind]
     s.data_validation(6,col,5+n,col,{'validate':'list','source':'='+named})
    if kind=='rating':s.data_validation(6,col,5+n,col,{'validate':'decimal','criteria':'between','minimum':1,'maximum':5})
  warn=w.add_format({'bg_color':'#FCE3D7','font_color':'#A73C25'})
  if name=='Booking Tracker':s.conditional_format(6,24,5+n,24,{'type':'text','criteria':'containing','value':'DOUBLE BOOKED','format':warn})
 # Settings
 s=ws['Settings & Lists'];s.merge_range('A4:H4','Defaults are examples, not platform terms. Fees and rates are editable and changes recalculate past bookings.',F['note']);s.set_column('A:A',28);s.set_column('B:B',24);s.set_column('E:H',22)
 vals=[('Business name',a.business or ('' if a.blank else 'Harbour & Pine Stays')),('Owner / host',a.owner or ('' if a.blank else 'Nadia Whitlock')),('Currency code',a.currency_code),('Report year',a.year or a.today.year),('Default nightly rate',a.nightly),('Default cleaning fee',a.cleaning_fee),('Default cleaning cost',a.cleaning_cost),('Default security deposit',a.deposit),('Default minimum nights',a.min_nights),('Lodging tax rate',a.tax/100),('Tax remitted by','Self' if a.tax_self else 'Platform'),('Occupancy target',a.occupancy_target/100),('ADR target',a.adr_target),('Monthly revenue target',a.revenue_target),('Demo properties target',a.properties)]
 for i,(label,val) in enumerate(vals,6):s.write(i,0,label,F['label']);s.write(i,1,val,F['percent'] if label in ('Lodging tax rate','Occupancy target') else F['input'])
 s.data_validation('B17',{'validate':'list','source':['Self','Platform']});s.write_row('E6',['Platform','Commission','Processing fee'],F['header'])
 for i in range(10):
  values=PLATFORMS[i] if i<len(PLATFORMS) else ('',None,None)
  for j,v in enumerate(values):
   if v is None:s.write_blank(6+i,4+j,None,F['percent'] if j else F['input'])
   else:s.write(6+i,4+j,v,F['percent'] if j else F['input'])
 s.write('H6','Expense categories',F['header'])
 for i,cat in enumerate(EXPENSES,6):s.write(i,7,cat,F['input'])
 # Guide
 s=ws['Getting Started'];s.merge_range('A4:H4','START HERE  •  Manual workbook, no platform connection or automated messages.',F['note']);s.set_column('A:A',26);s.set_column('B:H',18)
 guide=[('01  Configure','Set business name, report year, fee percentages and tax assumptions on Settings. Default figures are examples, not your platform contract.'),('02  Add records','Create properties, guests and staff first. IDs are generated from physical row position: never sort, move, insert or delete populated register rows.'),('03  Bookings','Add bookings and blocks manually. The clash indicator checks only entered rows. Confirm availability directly with every platform before accepting a booking.'),('04  Cleaning','Cleaning rows mirror their Booking Tracker rows. Enter cleaner, status and nine tasks on the aligned row. Do not move or delete bookings after logging cleaning.'),('05  Payouts','Enter net bank deposits once each. Split payouts may use multiple rows; total received and difference are calculated per booking, not added together.'),('06  Costs','Expense Tracker is the sole financial cost source: enter cleaning, repairs and other actual costs there once. Cleaning / maintenance tabs are operational only.'),('07  Reporting','Room revenue is nightly rate less room discount. ADR and RevPAR exclude cleaning and extras. Nights and room revenue are allocated by overlap into each month.'),('Reporting basis','Net booked revenue is grouped by check-in month, expenses by date and bank payouts by bank date. These are management estimates, not formal financial statements.'),('Safety & privacy','Never rely on the workbook as a live calendar. Sheet protection password premium prevents accidental edits, not unauthorized access or encryption.'),('Other limits','No sync, iCal, APIs, payment processing or messages. Fee changes recalculate old estimates. Tax and legal treatment must be checked with a qualified professional.')]
 for i,(label,text) in enumerate(guide,6):s.set_row(i,42);s.write(i,0,label,F['label']);s.merge_range(i,1,i,7,text,F['note'])
 # Calendar: one selected property and the first 12 property rows for a fortnight.
 s=ws['Booking Calendar'];s.merge_range('A4:H4','MANUAL ENTRIES ONLY — no platform sync. Verify each platform calendar before confirming dates.',F['note']);s.set_column('A:A',25);s.set_column('B:P',13)
 s.write('A7','Property ID',F['label']);s.write('B7','' if a.blank else 'PRP-01',F['input']);s.data_validation('B7',{'validate':'list','source':'=PropertyIDs'});s.write('A8','Month',F['label']);s.write_datetime('B8',a.today.replace(day=1),F['date'])
 s.write_row('A10',['Date','Status','Arrivals','Departures'],F['header'])
 def day_count(prop,date,status):return f'COUNTIFS({B(1)},{prop},{B(6)},"<="&{date},{B(7)},">"&{date},{B(4)},"{status}")'
 def state(prop,date):
  earning='+'.join(day_count(prop,date,x) for x in ['Confirmed','Checked in','Completed']);blocks='+'.join(day_count(prop,date,x) for x in ['Owner block','Maintenance block'])
  return f'IF(({earning})+({blocks})>1,"CLASH",IF(({blocks})>0,"Blocked",IF(({earning})>0,"Occupied","Available")))'
 for i in range(31):
  r=11+i;s.write_formula(r-1,0,f'=IF(ROW()-10<=DAY(EDATE(DATE(YEAR($B$8),MONTH($B$8),1),1)-1),DATE(YEAR($B$8),MONTH($B$8),ROW()-10),"")',F['calc_date']);s.write_formula(r-1,1,f'=IF(OR($B$7="",A{r}=""),"",{state("$B$7",f"A{r}")})',F['calc']);
  for c,datecol in [(2,6),(3,7)]:s.write_formula(r-1,c,f'=IF(OR($B$7="",A{r}=""),"",COUNTIFS({B(1)},$B$7,{B(datecol)},A{r},{B(4)},"Confirmed")+COUNTIFS({B(1)},$B$7,{B(datecol)},A{r},{B(4)},"Checked in")+COUNTIFS({B(1)},$B$7,{B(datecol)},A{r},{B(4)},"Completed"))',F['calc'])
 s.write('A45','NEXT 14 DAYS',F['header']);s.write('A46','Property',F['header'])
 for i in range(14):s.write_formula(45,i+1,f'=TODAY()+{i}',F['calc_date'])
 for j in range(12):
  r=47+j;s.write_formula(r-1,0,f'=IF(INDEX({P(0)},{j+1})="","",INDEX({P(0)},{j+1}))',F['calc'])
  for i in range(14):
   col=xl_col_to_name(i+1);s.write_formula(r-1,i+1,f'=IF($A{r}="","",{state(f"$A{r}",f"{col}$46")})',F['calc'])
 for cell_range in ('B11:B41','B47:O58'):
  for label,bg,fg in [('Available','#E4F4ED','#21684A'),('Occupied','#DCEFF1','#196372'),('Blocked','#FDECCC','#8B5A12'),('CLASH','#FCE0D9','#A43125')]:
   s.conditional_format(cell_range,{'type':'text','criteria':'containing','value':label,'format':w.add_format({'bg_color':bg,'font_color':fg})})
 s.freeze_panes(10,1)
 # Printable static checklist (manual; does not write flags back).
 s=ws['Turnover Checklist'];s.merge_range('A4:H4','Print and mark by hand; enter the nine completion flags in Cleaning Schedule. This printable does not write back.',F['note']);s.set_column('A:A',30);s.set_column('B:H',18)
 s.write('A7','Property / address',F['label']);s.merge_range('B7:H7','',F['input']);s.write('A8','Date / cleaner',F['label']);s.merge_range('B8:H8','',F['input'])
 tasks=['Bedrooms: change linen and dust','Bathrooms: clean and replenish','Kitchen: clean surfaces and appliances','Living areas: reset and dust','Floors: vacuum / mop','Laundry and linen: restock','Rubbish: empty bins','Supplies: replenish','Final inspection: doors, lights and safety']
 for i,t in enumerate(tasks,10):s.write(i,0,'☐',F['input']);s.merge_range(i,1,i,7,t,F['label']);s.set_row(i,27)
 s.write('A22','Issues / sign-off',F['label']);s.merge_range('B22:H23','',F['input']);s.print_area('A1:H23')
 # Monthly and annual reports use performance for nights and date-based transaction sums for money.
 s=ws['Monthly Reports'];s.merge_range('A4:H4','Nights and room revenue allocated per night. Net booked revenue by check-in date; expenses by date; payouts by bank date.',F['note']);s.set_column('A:A',18);s.set_column('B:I',18);s.freeze_panes(6,1)
 headers=['Month','Listed nights','Blocked nights','Available nights','Booked nights','Occupancy','Room revenue','ADR','RevPAR','Net booked revenue','Expenses counted','Estimated net less costs','Bank payouts']
 for c,h in enumerate(headers):s.write(5,c,h,F['header']);s.set_column(c,c,20)
 s.set_row(5,32)
 perf=lambda c:rng('Occupancy & Performance',c)
 for i in range(12):
  r=7+i;s.write_formula(r-1,0,f'=DATE(\'Settings & Lists\'!$B$10,{i+1},1)',F['calc_date'])
  for c,pc in [(1,2),(2,3),(3,4),(4,5),(6,7)]:s.write_formula(r-1,c,f'=SUMIF({perf(1)},$A{r},{perf(pc)})',F['calc_money'] if c==6 else F['calc'])
  for c,form in [(5,f'=IF(D{r}=0,"",E{r}/D{r})'),(7,f'=IF(E{r}=0,"",G{r}/E{r})'),(8,f'=IF(D{r}=0,"",G{r}/D{r})')]:s.write_formula(r-1,c,form,F['calc_percent'] if c==5 else F['calc_money'])
  cond=f'{B(6)},">="&A{r},{B(6)},"<"&EDATE(A{r},1)';s.write_formula(r-1,9,f'=SUMIFS({B(21)},{cond})',F['calc_money'])
  s.write_formula(r-1,10,f'=SUMIFS({E(6)},{E(1)},">="&A{r},{E(1)},"<"&EDATE(A{r},1),{E(8)},"Yes")',F['calc_money'])
  s.write_formula(r-1,11,f'=J{r}-K{r}',F['calc_money']);s.write_formula(r-1,12,f'=SUMIFS({V(2)},{V(1)},">="&A{r},{V(1)},"<"&EDATE(A{r},1))',F['calc_money'])
 s=ws['Annual Reports'];s.merge_range('A4:H4','Selected year totals. Estimated revenue is attributed to check-in; payouts and expenses are attributed to their dates.',F['note']);s.set_column('A:A',31);s.set_column('B:B',22)
 for i,(label,col) in enumerate([('Listed nights','B'),('Blocked nights','C'),('Available nights','D'),('Booked nights','E'),('Room revenue','G'),('Net booked revenue','J'),('Expenses counted','K'),('Estimated net less costs','L'),('Bank payouts','M')],6):s.write(i,0,label,F['label']);s.write_formula(i,1,f'=SUM(\'Monthly Reports\'!{col}7:{col}18)',F['calc_money'] if i>=10 else F['calc'])
 for i,(label,form,style) in enumerate([('Occupancy','=IF(B9=0,"",B10/B9)','calc_percent'),('ADR','=IF(B10=0,"",B11/B10)','calc_money'),('RevPAR','=IF(B9=0,"",B11/B9)','calc_money')],16):s.write(i,0,label,F['label']);s.write_formula(i,1,form,F[style])
 # Tax summary is a categorisation aid, not a tax calculation.
 s=ws['Tax Summary'];s.merge_range('A4:H4','Management summary only, not tax advice. Classification and deductibility vary by jurisdiction; check with your adviser.',F['note']);s.set_column('A:A',30);s.set_column('B:B',22)
 for i,(label,col) in enumerate([('Net booked revenue','J'),('Counted expenses','K'),('Estimated net less costs','L'),('Bank payouts','M')],6):s.write(i,0,label,F['label']);s.write_formula(i,1,f'=SUM(\'Monthly Reports\'!{col}7:{col}18)',F['calc_money'])
 s.write('A13','Expense treatment',F['header']);s.write('B13','Selected year amount',F['header'])
 for j,cat in enumerate(LISTS['tax_category'],14):s.write(j-1,0,cat,F['label']);s.write_formula(j-1,1,f'=SUMIFS({E(6)},{E(7)},A{j},{E(1)},">="&DATE(\'Settings & Lists\'!$B$10,1,1),{E(1)},"<"&DATE(\'Settings & Lists\'!$B$10+1,1,1))',F['calc_money'])
 # Dashboard
 s=ws['Dashboard'];s.merge_range('A4:H4','Manual overview. Booking and payout figures are estimates, not live platform data.',F['note']);s.set_column('A:A',30);s.set_column('B:B',22);s.set_column('D:H',20)
 metrics=[('Active properties',f'=COUNTIF({P(4)},"Active")','calc'),('Bookings recorded',f'=COUNT({B(6)})','calc'),('Booking rows with clashes',f'=COUNTIF({B(23)},">0")','calc'),('Annual room revenue',"='Annual Reports'!B11",'calc_money'),('Annual net booked revenue',"='Annual Reports'!B12",'calc_money'),('Annual costs counted',"='Annual Reports'!B13",'calc_money'),('Annual estimated net less costs',"='Annual Reports'!B14",'calc_money'),('Annual bank payouts',"='Annual Reports'!B15",'calc_money')]
 for i,(label,form,style) in enumerate(metrics,6):s.set_row(i,29);s.write(i,0,label,F['label']);s.write_formula(i,1,form,F[style])
 s.merge_range('D7:H10','BOOKING SAFETY\nThis file does not sync with platforms. Check each listing directly; the clash flag only sees the rows entered here.',F['note']);s.merge_range('D12:H15','FINANCIAL NOTE\nPayout estimates are not bank receipts. Enter actual costs once on Expense Tracker and reconcile statements.',F['note']);s.merge_range('D17:H19','PRIVACY\nSheet password premium is not encryption. Protect guest information with encrypted, access-controlled storage.',F['note'])
 chart=w.add_chart({'type':'column'});chart.add_series({'name':'Room revenue','categories':"='Monthly Reports'!$A$7:$A$18",'values':"='Monthly Reports'!$G$7:$G$18",'fill':{'color':'#42A5A4'},'border':{'none':True}});chart.set_title({'name':'Monthly room revenue'});chart.set_legend({'none':True});chart.set_chartarea({'border':{'none':True},'fill':{'color':'#FFFFFF'}});chart.set_plotarea({'border':{'none':True}});chart.set_size({'width':680,'height':280});s.insert_chart('D21',chart)
 if not a.blank:sample(ws,F,SCHEMAS,a)
 for s in ws.values():
  if not a.no_protect:s.protect(a.password,{'autofilter':True,'sort':False,'select_locked_cells':True,'select_unlocked_cells':True})
 ws['Dashboard'].activate();ws['Dashboard'].set_first_sheet();w.close();return counts

def sample(ws,F,schemas,a):
 today=a.today;first=today.replace(day=1)
 def month(back):
  n=first.year*12+first.month-1-back;return dt.date(n//12,n%12+1,1)
 def t(h,m=0):return dt.time(h,m)
 props=[['Harbour View Loft','14 Quayside Walk','Portland','Active','Owned outright',month(14),165,85,60,250,2,3,t(15),t(11),'Sample only'],['Pine Ridge Cabin','2 Pine Ridge Road','Mount Hood','Active','Owned with mortgage',month(14),395,180,135,600,3,8,t(16),t(10),'Sample only'],['Old Mill Townhouse','71 Old Mill Lane','Portland','Active','Rental arbitrage',month(14),210,110,80,300,2,5,t(15),t(11),'Sample only'],['Creekside Bungalow','9 Creekside Avenue','Hood River','Active','Owned with mortgage',month(14),185,95,70,300,2,4,t(15),t(11),'Sample only']]
 data={'Property Database':[[None]+x for x in props[:a.properties]],'Guest Database':[[None,'Rebecca Thorne','rebecca@example.com','555-0101','United States','Yes',None,None,'Sample guest'],[None,'Dai Nguyen','dai@example.com','555-0102','United States','No',None,None,'Sample guest'],[None,'Marion Esseltine','marion@example.com','555-0103','United States','No',None,None,'Sample guest'],[None,'Amira Sadiq','amira@example.com','555-0104','United States','Yes',None,None,'Sample guest']],
 'Staff & Vendors':[[None,'Priya Raman','Cleaner','Raman Turnovers','555-0142','priya@example.com',65,'Per turnover',today+dt.timedelta(days=142),None,'Sample vendor']],
 'Supplies Inventory':[['Toilet rolls','','pack',4,6,8.4,None,None,'Example supplier','Sample supply'],['Bath towels','PRP-01','each',24,12,11,None,None,'Example supplier','Sample supply']],
 'Maintenance Log':[[None,first,'PRP-01','Plumbing','Dripping tap','Normal','VND-001',first,first,'Complete',80,94,today+dt.timedelta(days=365),None,'Cost recorded in Expense Tracker']],
 'Expense Tracker':[[None,first,'PRP-01','Repairs','Example contractor','Tap repair',94,'Operating expense','Yes','INV-001','Actual cost'],[None,first,'PRP-01','Cleaning','Example cleaner','Turnover cleaning',60,'Operating expense','Yes','INV-002','Enter once'],[None,first,'','Software & subscriptions','Example vendor','Booking software',39,'Operating expense','Yes','INV-003','Shared portfolio cost']],
 'Reviews Tracker':[['BKG-0001',first,5,5,5,5,5,4,5,None,'Yes','Example review']],
 'Check-in & Check-out':[['BKG-0001',None,None,None,None,'Yes','Yes','Yes','Yes','Yes','Yes','Yes','Yes','Yes',None,'Example stay']]
 }
 rows=[]
 for back in (3,2,1,0):
  m=month(back)
  for i in range(min(a.properties,4)):
   checkin=m+dt.timedelta(days=4+i*4);checkout=checkin+dt.timedelta(days=3+i%2)
   status='Completed' if checkout<today else 'Confirmed'
   row=[None,f'PRP-{i+1:02}',f'GST-{i+1:04}',['Airbnb','Vrbo','Booking.com','Direct booking'][i],status,checkin-dt.timedelta(days=20),checkin,checkout,None,None,None,0,None,None,None,0,None,None,None,None,None,None,None,None,None,'Example booking']
   rows.append(row)
 # A cross-month reservation, plus same-day adjacent booking, useful for calendar review.
 start=first+dt.timedelta(days=27);end=start+dt.timedelta(days=5)
 rows += [[None,'PRP-01','GST-0001','Airbnb','Confirmed',first,start,end,None,None,None,0,None,None,None,0,None,None,None,None,None,None,None,None,None,'Cross-month example'],[None,'PRP-01','GST-0002','Direct booking','Confirmed',first,end,end+dt.timedelta(days=2),None,170,None,0,None,None,None,0,None,None,None,None,None,None,None,None,None,'Same-day turnaround example']]
 data['Booking Tracker']=rows
 # First booking is 3 nights at 165, cleaning 85, Airbnb 3%: expected 562.60.
 data['Platform Revenue & Fees']=[['BKG-0001',month(3)+dt.timedelta(days=9),200,'PO-01A',None,None,None,None,'First split'],['BKG-0001',month(3)+dt.timedelta(days=10),362.60,'PO-01B',None,None,None,None,'Second split']]
 data['Cleaning Schedule']=[[None,None,None,'VND-001',None,None,'Complete','Yes','Yes','Yes','Yes','Yes','Yes','Yes','Yes','Yes',None,None,'Example task completion']]
 for name,rows in data.items():
  for r,row in enumerate(rows,6):
   for c,val in enumerate(row):
    if val is None or c>=len(schemas[name]) or schemas[name][c][1].startswith('f:'):continue
    kind=schemas[name][c][1];style=F[kind] if kind in ('date','time','money','number') else F['number'] if kind=='rating' else F['input']
    if isinstance(val,(dt.date,dt.time,dt.datetime)):ws[name].write_datetime(r,c,val,style)
    else:ws[name].write(r,c,val,style)

if __name__=='__main__':
 a=parse();cnt=build(a)
 if not a.quiet: print('Created',os.path.abspath(a.output),'with',len(SHEETS),'sheets; register capacities:',cnt)
 else:print(a.output)
