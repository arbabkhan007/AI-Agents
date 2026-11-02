"""Make a photo-based Etsy listing kit. Text and diagrams are typeset, not AI generated."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import shutil,zipfile
R=Path(__file__).resolve().parent.parent
A=R/'etsy-assets'; K=R/'etsy-kit'; IMG=K/'listing-images'; COPY=K/'listing-copy'; DL=R/'download'; S=2000
DARK='#173c32'; DARKER='#102c25'; GREEN='#3e6852'; SAGE='#e3ebe1'; GOLD='#af8050'; INK='#263c32'; MUTED='#637268'; CREAM='#f6f5ef'; WHITE='#fffefa'; LINE='#d8e2d8'; PEACH='#f3e9dd'
FP=Path('/usr/share/fonts/truetype/dejavu')
def font(size,style='sans'):
 return ImageFont.truetype(str(FP/{'sans':'DejaVuSans.ttf','bold':'DejaVuSans-Bold.ttf','serif':'DejaVuSerif.ttf','serifbold':'DejaVuSerif-Bold.ttf'}[style]),size)
def fit(d,t,size,width,style='sans',minimum=20):
 while size>minimum and d.textlength(t,font=font(size,style))>width:size-=1
 assert d.textlength(t,font=font(size,style))<=width,(t,width,size)
 return font(size,style)
def text(d,x,y,t,size=40,color=INK,style='sans',width=1740):d.text((x,y),t,font=fit(d,t,size,width,style),fill=color)
def center(d,y,t,size=40,color=INK,style='sans',width=1740):
 f=fit(d,t,size,width,style);d.text(((S-d.textlength(t,font=f))/2,y),t,font=f,fill=color)
def wrap(d,t,f,width):
 lines=[];current=''
 for word in t.split():
  line=(current+' '+word).strip()
  if d.textlength(line,font=f)<=width:current=line
  else:
   assert current,(word,width);lines.append(current);current=word
 if current:lines.append(current)
 return lines
def card(d,xy,fill=WHITE,outline=LINE,r=24):d.rounded_rectangle(xy,r,fill=fill,outline=outline,width=2)
def shadow(d,xy,r=28):
 x,y,X,Y=xy;d.rounded_rectangle((x+12,y+16,X+12,Y+16),r,fill='#cad1c5');card(d,xy,WHITE,LINE,r)
def photo(filename):return ImageOps.fit(Image.open(A/filename).convert('RGB'),(S,S),method=Image.Resampling.LANCZOS)
def pill(d,x,y,label,fill=SAGE,color=GREEN):
 f=font(28,'bold');w=int(d.textlength(label,font=f))+64;d.rounded_rectangle((x,y,x+w,y+65),32,fill=fill);d.text((x+32,y+16),label,font=f,fill=color)
def header(d,eyebrow,title,sub):
 text(d,125,70,eyebrow,30,GOLD,'bold');text(d,120,138,title,82,DARK,'serif',1750);text(d,125,260,sub,38,MUTED,'sans',1740);d.line((125,335,1875,335),fill=LINE,width=3)
def footer(d,num=''):
 d.line((125,1860,1875,1860),fill=LINE,width=2);text(d,125,1884,'NOVALITY STORE',26,MUTED,'bold');f=font(26);t='DIGITAL EXCEL WORKBOOK'+('  /  '+num if num else '');d.text((1875-d.textlength(t,font=f),1884),t,font=f,fill=MUTED)
def table(d,box,title,headers,rows):
 x,y,X,Y=box;shadow(d,box);text(d,x+45,y+34,title,38,DARK,'serif',X-x-90);text(d,x+45,y+100,'ILLUSTRATIVE EXAMPLE  /  NOT A SCREENSHOT',24,MUTED,'bold',X-x-90)
 left=x+40;right=X-40;width=right-left;top=y+160;cw=width/len(headers);d.rounded_rectangle((left,top,right,top+75),12,fill=DARK)
 for i,h in enumerate(headers):text(d,int(left+18+i*cw),top+21,h,27,WHITE,'bold',int(cw-28))
 for j,row in enumerate(rows):
  yy=top+75+j*81;d.rectangle((left,yy,right,yy+81),fill=WHITE if j%2==0 else '#f0f5ef',outline=LINE,width=1)
  for i,v in enumerate(row):text(d,int(left+18+i*cw),yy+23,str(v),31,INK,'sans',int(cw-30))
def cover():
 im=photo('hero.png');d=ImageDraw.Draw(im);shadow(d,(95,105,1695,1035),32)
 text(d,165,160,'NOVALITY STORE  /  BUSINESS COLLECTION',29,GOLD,'bold',1450)
 text(d,158,238,'Landscaping &',108,DARK,'serif',1430);text(d,158,375,'Lawn Care',113,DARK,'serif',1430);text(d,160,510,'Business Manager',80,DARK,'serif',1430)
 d.line((165,630,1490,630),fill=GOLD,width=3);text(d,165,670,'A calmer way to organize your work.',47,INK,'sans',1430)
 pill(d,165,770,'23 WORKSHEETS');pill(d,650,770,'DEMO + BLANK',PEACH,GOLD)
 text(d,165,920,'DIGITAL EXCEL WORKBOOK  •  MANUAL ENTRY',28,MUTED,'bold',1440)
 table(d,(225,1135,1775,1730),'THE WORKING DAY',['CLIENT','SERVICE','CREW','STATUS'],[['Oak Avenue','Lawn care','Crew A','Scheduled'],['Willow Lane','Hedge trim','Crew B','Completed'],['Maple Court','Maintenance','Crew A','Scheduled']])
 text(d,275,1790,'Fictional data  •  Illustration, not a workbook screenshot',26,DARK,'bold',1500)
 return im
def included():
 im=photo('workspace.png');d=ImageDraw.Draw(im);shadow(d,(100,95,1900,1815),32);center(d,155,'WHAT YOU RECEIVE',31,GOLD,'bold');center(d,235,'Your workbook set',90,DARK,'serif');center(d,350,'Everything you need to get started',39,MUTED)
 rows=[('01','WORKED DEMO','Explore 23 worksheets using fictional landscaping data.'),('02','BLANK WORKBOOK','Build your own records in the same connected workbook.'),('03','QUICK START GUIDE','Follow setup steps and understand costing and limitations.')]
 for i,(n,h,b) in enumerate(rows):
  y=470+i*260;card(d,(165,y,1835,y+215),CREAM,LINE,20);d.ellipse((210,y+35,286,y+111),fill=SAGE);text(d,226,y+54,n,29,GREEN,'bold',54);text(d,325,y+35,h,38,DARK,'bold',1450)
  for j,line in enumerate(wrap(d,b,font(35),1380)):text(d,325,y+100+j*46,line,35,MUTED,'sans',1400)
 card(d,(165,1300,1835,1595),SAGE,SAGE,22);center(d,1350,'DESIGNED FOR EXCEL DESKTOP',42,DARK,'bold');center(d,1430,'Digital files  •  No macros  •  Manual entry',36,MUTED);center(d,1505,'Windows Excel opening is unverified.',30,MUTED)
 center(d,1690,'NOVALITY STORE',28,GREEN,'bold');return im
def workflow():
 im=Image.new('RGB',(S,S),CREAM);d=ImageDraw.Draw(im);header(d,'ONE CONNECTED WORKSPACE','23 sheets, one workflow','An overview of the workbook, grouped by purpose')
 groups=[('01   START','Dashboard  ·  Getting Started  ·  Settings & Lists'),('02   CUSTOMERS & PRICING','Customer CRM  ·  Property Database  ·  Service Catalog  ·  Quote Calculator'),('03   THE WORK','Job & Work Orders  ·  Route Planner  ·  Recurring Contracts'),('04   PEOPLE & ASSETS','Crew Database  ·  Crew Schedule  ·  Timesheets & Payroll  ·  Equipment Inventory'),('05   RECORD THE COSTS','Vehicle & Fuel Tracker  ·  Materials Inventory  ·  Expense Tracker'),('06   GET PAID & REVIEW','Invoice & Payments  ·  Customer Feedback  ·  Seasonal Planner'),('07   UNDERSTAND RESULTS','Profit Analysis  ·  Monthly Reports  ·  Annual Reports')]
 for i,(h,b) in enumerate(groups):
  y=380+i*203;card(d,(125,y,1875,y+176),WHITE,LINE,18);text(d,165,y+20,h,30,GREEN,'bold',1650)
  lines=wrap(d,b,font(33),1600);assert len(lines)<=2
  for j,line in enumerate(lines):text(d,165,y+78+j*42,line,33,INK,'sans',1600)
 footer(d,'03');return im
def feature(num,eyebrow,title,sub,tabletitle,headers,rows,benefits,note):
 im=Image.new('RGB',(S,S),CREAM);d=ImageDraw.Draw(im);header(d,eyebrow,title,sub);table(d,(125,385,1875,1060),tabletitle,headers,rows);text(d,170,955,note,27,MUTED,'sans',1600)
 for i,(h,b) in enumerate(benefits):
  y=1105+i*218;card(d,(125,y,1875,y+182),WHITE,LINE,18);d.rounded_rectangle((160,y+28,170,y+152),5,fill=GOLD);text(d,205,y+22,h,36,DARK,'bold',1550)
  lines=wrap(d,b,font(34),1550);assert len(lines)<=2,(num,h,lines)
  for j,line in enumerate(lines):text(d,205,y+81+j*43,line,34,MUTED,'sans',1550)
 footer(d,num);return im
def overview():
 im=Image.new('RGB',(S,S),CREAM);d=ImageDraw.Draw(im);header(d,'YOUR BUSINESS AT A GLANCE','See the bigger picture','Review a dashboard built from your own entries')
 tiles=[('CUSTOMERS','Contacts & properties'),('JOBS','Scheduled & completed'),('QUOTES','Pricing & follow-up'),('CREW','Time & availability'),('MATERIALS','Stock & alerts'),('FINANCES','Invoices & profit')]
 for i,(a,b) in enumerate(tiles):
  x=125+i%2*888;y=395+i//2*300;card(d,(x,y,x+850,y+260),WHITE,LINE,22);d.rounded_rectangle((x+35,y+37,x+47,y+215),6,fill=GOLD);text(d,x+80,y+50,a,30,GREEN,'bold',710);text(d,x+80,y+120,b,43,DARK,'serif',710)
 card(d,(125,1370,1875,1740),SAGE,SAGE,24);text(d,175,1435,'Clarity starts with good records.',54,DARK,'serif',1600);text(d,175,1530,'Enter your data and review the underlying details.',36,MUTED,'sans',1600);text(d,175,1605,'Illustrative layout; not a workbook screenshot.',30,MUTED,'sans',1600);footer(d,'04');return im
def limits():
 im=photo('landscape.png');d=ImageDraw.Draw(im);shadow(d,(100,95,1900,1835),35);center(d,150,'BEFORE YOU PURCHASE',31,GOLD,'bold');center(d,220,'A few important details',80,DARK,'serif')
 entries=[('01','DESKTOP EXCEL','Windows Excel opening and recalculation are unverified; test a copy before relying on it.'),('02','MANUAL ORGANIZER','No automatic booking, invoice sending, payments or software sync.'),('03','KEEP ROWS STABLE','Filter; do not sort, move, insert or delete rows, or change ID prefixes after linking.'),('04','FIXED PREPARED CAPACITY','1,500 jobs, 600 invoices, 600 expenses and 900 timesheets; other limits apply.'),('05','REVIEW YOUR FIGURES','Management estimates are not accounting, tax or payroll advice.')]
 for i,(n,h,b) in enumerate(entries):
  y=360+i*230;card(d,(165,y,1835,y+202),CREAM,LINE,18);text(d,205,y+26,n,31,GOLD,'bold',80);text(d,325,y+22,h,37,DARK,'bold',1450)
  lines=wrap(d,b,font(34),1410);assert len(lines)<=2
  for j,line in enumerate(lines):text(d,325,y+83+j*43,line,34,MUTED,'sans',1410)
 center(d,1595,'Digital download only  •  No physical item',35,GREEN,'bold');center(d,1685,'Illustrations are not workbook screenshots.',30,MUTED);return im

FEATURES=[
('05','KNOW YOUR CLIENTS','Customers & properties','Keep contact and site details together','CUSTOMERS & PROPERTIES',['CLIENT','PROPERTY','DETAIL'],[['Oak Avenue','Oak Avenue','Lawn & access'],['Willow Lane','Willow Lane','Gate code']],[('ONE CUSTOMER, MULTIPLE SITES','Create customer and property records with linked IDs.'),('KEEP SITE NOTES HANDY','Record access, lawn size, distance and useful site details.'),('CHOOSE IDs CAREFULLY','Verify that the selected property belongs to the customer.')],'Fictional data  •  Manual record entry'),
('06','BUILD A BETTER QUOTE','Quote calculator','Review the inputs behind your proposed price','QUOTE INPUTS',['INPUT','EXAMPLE','PURPOSE'],[['Labour','2 crew hours','Time estimate'],['Materials','$30','Your cost'],['Travel','12 miles','Round-trip basis']],[('START WITH THE PROPERTY','Use site size, service details and your rates to build a quote.'),('REVIEW COST & MARGIN','See estimates for labour, materials, travel and overhead.'),('CONTROL THE FINAL PRICE','Use the prepared input cells and review the printable quote.')],'Illustrative example  •  Pricing is not professional advice'),
('07','ORGANIZE THE VISIT','Jobs & work orders','A dedicated row for each visit','JOB & WORK ORDERS',['JOB','SERVICE','CREW','STATUS'],[['JOB-00001','Lawn care','Crew A','Scheduled'],['JOB-00002','Hedge trim','Crew B','Completed']],[('RECORD THE DETAILS','Connect the customer, property, service and crew manually.'),('MARK COMPLETED WORK','Completed jobs feed the management revenue figures.'),('COMPARE COSTS','Review estimated costs alongside allocated job costs.')],'Fictional data  •  Jobs are created manually'),
('08','PLAN THE DAY','Route planner','Put the chosen crew and stops on a printable page','ROUTE PLANNER',['STOP','START','SITE','SERVICE'],[['1','08:00','Oak Avenue','Lawn care'],['2','10:30','Maple Court','Maintenance']],[('SELECT A DATE & CREW','See matching jobs in start-time order, with ties in row order.'),('PRINT A CREW SHEET','The prepared route block displays up to 14 stops.'),('REVIEW BEFORE HEADING OUT','All statuses can appear; this is not GPS or route optimization.')],'Fictional data  •  Stops beyond 14 are not displayed'),
('09','KEEP REPEAT WORK VISIBLE','Recurring contracts','See the next suggested visit and agreement details','RECURRING CONTRACTS',['CONTRACT','FREQUENCY','PRICE','NEXT'],[['CON-0001','Every 2 weeks','$90','Review date'],['CON-0002','Monthly','$120','Review date']],[('RECORD THE AGREEMENT','Track the frequency, terms and price for recurring work.'),('REVIEW WHAT IS DUE','The next suggested date follows the last completed visit.'),('BOOK VISITS YOURSELF','The workbook flags visits; it does not create jobs automatically.')],'Fictional data  •  A planning aid, not a booking service'),
('10','PUT THE TEAM TO WORK','Crew & schedule','Organize people, availability and planned shifts','CREW SCHEDULE',['PERSON','DAY','TASK','HOURS'],[['Crew member 1','Monday','Mowing','7.5'],['Crew member 2','Monday','Hedge trim','6.0']],[('MAINTAIN CREW RECORDS','Keep roles and your loaded cost rates in one place.'),('PLAN THE WEEK','Enter schedule lines and review who is assigned.'),('KEEP IT CURRENT','Plans are manual; confirm changes with your crew.')],'Illustrative fields  •  No employee scheduling sync'),
('11','RECORD THE HOURS','Timesheets & payroll','Turn recorded time into useful cost estimates','TIMESHEETS',['EMPLOYEE','JOB','HOURS','TASK'],[['EMP-001','JOB-00001','4.0','Lawn care'],['EMP-002','JOB-00002','3.0','Hedge trim']],[('ENTER TIME BY PERSON','Use start and finish times or enter hours directly.'),('ALLOCATE JOB HOURS','Connect a Job ID to feed labour costs into that job.'),('REVIEW OVERTIME','Enter lines chronologically; overtime is a planning indicator, not payroll.')],'Fictional data  •  No payslips or payroll processing'),
('12','KEEP MATERIALS MOVING','Materials inventory','Record purchases and usage against material IDs','MATERIALS INVENTORY',['MATERIAL','OPENING','BOUGHT','USED'],[['Mulch','5','10','3'],['Grass seed','4','6','2']],[('SET UP EACH MATERIAL','Enter opening stock, unit costs and reorder levels.'),('RECORD STOCK MOVEMENTS','Use Expense Tracker for purchases, usage and wastage.'),('REVIEW AVAILABILITY','Illustrative example: 5 + 10 − 3 = 12 on hand.')],'Illustrative values  •  No automatic supplier connection'),
('13','LOOK AFTER YOUR EQUIPMENT','Equipment & vehicles','Keep a record of the machines and costs behind the work','ASSET RECORDS',['ASSET','RECORD','REVIEW'],[['Mower','Engine hours','Service due'],['Work truck','Fuel expense','Monthly cost']],[('TRACK MACHINES','Record equipment status, hours and service dates.'),('LOG VEHICLE COSTS','Enter fuel and other vehicle expenses in the tracker.'),('AVOID DOUBLE ENTRY','Do not enter the same vehicle costs again as expenses.')],'Illustrative fields  •  Enter maintenance and costs manually'),
('14','STAY ON TOP OF PAYMENTS','Invoices & payments','Track amounts billed, paid and outstanding','INVOICE REGISTER',['INVOICE','TOTAL','PAID','DUE'],[['INV-00001','$200','$100','$100'],['INV-00002','$150','$150','$0']],[('RECORD THE INVOICE','Enter the invoice and link the relevant customer and job.'),('UPDATE PAYMENTS','Enter cumulative paid amount and the last payment date.'),('CHECK THE DETAILS','The workbook cannot send invoices or take payments.')],'Illustrative values  •  Not a separate payment ledger'),
('15','UNDERSTAND YOUR COSTS','Expenses & profit','Review management figures with your own records','COST OVERVIEW',['CATEGORY','PERIOD COST','JOB COST'],[['Material purchase','Included','Not allocated'],['Material usage','Excluded','If job-linked']],[('RECORD COSTS ONCE','Separate stock purchases from usage to avoid double counting.'),('COMPARE MANAGEMENT FIGURES','Period reports and job allocations use different cost bases.'),('RECONCILE WITH AN ADVISER','Revenue is completed-job charges, not necessarily cash received.')],'Illustrative treatment  •  Not accounting or tax advice'),
('16','REVIEW YOUR SEASON','Reports & seasonal planning','See the results of your entries across the year','MONTHLY REVIEW',['MONTH','VISITS','REVENUE','COSTS'],[['March','12','$1,800','$1,050'],['April','18','$2,700','$1,500']],[('EXPLORE MONTHLY RESULTS','Choose the report month and review activity and costs.'),('LOOK ACROSS THE YEAR','Use annual reports and seasonal planning to compare periods.'),('UNDERSTAND THE BASIS','Partial payments are grouped by the invoice’s last paid date.')],'Fictional data  •  Management estimates, not accounting reports'),
('17','READY TO PRINT','Quotes, invoices & routes','Create a clear printout from selected records','PRINTABLE BLOCKS',['DOCUMENT','SELECT','THEN'],[['Quote','Quote ID','Review & print'],['Invoice','Invoice ID','Review & print'],['Crew route','Date + crew','Review & print']],[('CHOOSE YOUR RECORD','The printable blocks sit below the Route Planner.'),('PREVIEW BEFORE PRINTING','Select the relevant block and use Excel Print Selection.'),('SEND IT YOURSELF','The workbook does not email documents or take payments.')],'Illustrative example  •  Print layout needs testing in your Excel')]

def main():
 IMG.mkdir(parents=True,exist_ok=True);COPY.mkdir(parents=True,exist_ok=True)
 images=[('01-cover',cover),('02-whats-included',included),('03-workbook-map',workflow),('04-dashboard',overview)]+[(x[0]+'-'+slug,lambda x=x:feature(*x)) for x,slug in zip(FEATURES,['customers-properties','quote-calculator','job-work-orders','route-planner','recurring-contracts','crew-schedule','timesheets','materials-inventory','equipment-vehicles','invoices-payments','expenses-profit','reports-seasonal','printable-documents'])]+[('18-important-details',limits)]
 assert len(images)==18
 for name,build in images:
  im=build();im.save(IMG/(name+'.jpg'),quality=93,subsampling=0,optimize=True);print(name,flush=True)
 shutil.copy2(DL/'landscaping-business-manager.zip',K/'landscaping-business-manager.zip')
 COPY_DOCS={
 '01-titles.txt':'''ETSY TITLE OPTIONS — choose one

Landscaping Business Spreadsheet, Lawn Care Manager Excel Template, Job Tracker, Quote Calculator and Customer CRM

Lawn Care Business Spreadsheet, Landscaping Quote Calculator, Crew Schedule, Invoice Tracker and Job Profit Excel Template

Landscaping Business Planner Excel Spreadsheet, Lawn Care CRM, Route Planner, Timesheets, Invoices and Materials Tracker
''',
 '02-tags.txt':'''ETSY TAGS — 13 suggestions

landscaping excel
lawn care planner
landscape business
lawn care business
landscaping tracker
lawn care template
landscaping crm
lawn quote template
crew scheduling
job cost tracker
lawn route planner
landscape invoice
business spreadsheet
''',
 '03-description.txt':'''LANDSCAPING & LAWN CARE BUSINESS MANAGER — EXCEL WORKBOOK

Organize the day-to-day details of your lawn care or landscaping business in one connected Excel workbook. Explore the fictional demo, then enter your own records in the blank workbook.

WHAT YOU RECEIVE
• Demo Excel workbook with fictional records
• Blank Excel workbook with the same 23 worksheets
• Quick-start guide covering setup, costing, capacity and limitations
• Digital download only — no physical item will be shipped

WHAT YOU CAN ORGANIZE
• Customers, site details, service catalog and quote estimates
• Job and work orders, recurring contracts and a printable crew route
• Crew records, schedules and timesheets with overtime indicators
• Equipment, vehicle costs and material stock movements
• Invoices, payment balances, expenses and customer feedback
• Job costing, seasonal planning and monthly and annual management reports
• Printable quote, invoice and route blocks in the Route Planner sheet

HOW IT WORKS
Open the blank workbook in Microsoft Excel desktop, save a copy and allow a full recalculation. Enter your business settings, rates, services, customers, sites, crew and materials. Create jobs and contracts manually; enter timesheets, stock movements, invoices and expenses as they happen. Review the dashboard and management reports against your records.

IMPORTANT BEFORE PURCHASING
This is a manual organizer. It does not create bookings, send invoices, take payments, sync with accounting or scheduling services, optimize routes or navigate. The printable route shows at most 14 stops per selected crew and day and can include all job statuses. Review it before printing.

Designed using Excel 2010-compatible formulas for desktop Excel. File structure and reduced-size formula scenarios were checked, but Windows Excel opening, repair-free behavior, recalculation and print layout have not been verified. Test a copy in your version before relying on it; other spreadsheet applications are untested. Formula values need recalculation on opening.

The workbook has fixed prepared rows: 1,500 jobs, 600 invoices, 600 expenses and 900 timesheets; other sheets have their own limits. IDs depend on row positions. Do not sort, move, insert or delete register rows, reuse historical IDs or change ID prefixes after linking. Use filters and keep backups. Select the correct customer, property and job yourself; their relationship is not automatically enforced.

Period reports count completed-job revenue by job date, not necessarily amounts invoiced or collected. Inventory purchase costs appear in period reports while usage can be allocated to jobs; these are different management cost bases, not an accounting inventory ledger. Payments are cumulative per invoice and grouped by the last paid date, so partial payments across months need a separate ledger. Timesheet overtime is allocated in row order and is a planning indicator, not payroll or legal advice. Read the included guide and reconcile figures with your adviser.

Sheets are protected with password premium to reduce accidental formula edits; protection is not encryption. Default currency number formats are USD-style; changing the settings symbol does not automatically change every cell format. Listing tables are illustrative designs, not workbook screenshots. No accounting, tax, payroll or legal advice is provided.
''',
 '04-key-features.txt':'''KEY FEATURES

• 23 worksheets in both a demo and blank Excel workbook
• Customer CRM, property database, service catalog and quote calculator
• Job records, recurring contract reminders and a 14-stop printable route
• Crew database, schedule and timesheets with overtime indicators
• Equipment, vehicle costs, materials inventory and expense tracker
• Invoice balances, feedback, seasonal planner and management reports
• Printable quote and invoice blocks on the Route Planner sheet
• Fixed prepared capacity: 1,500 jobs, 600 invoices, 600 expenses, 900 timesheets
• Protected formulas, unlocked prepared input cells, no macros
• Manual entry only; no booking, navigation, payments or software sync

Windows Excel opening and recalculation are unverified. Read the included guide for cost, payment, compatibility and operating limitations.
''',
 '05-faq.txt':'''FREQUENTLY ASKED QUESTIONS

Q: What is included?
A: A ZIP with demo and blank .xlsx workbooks plus a quick-start guide. No physical product is shipped.

Q: What software do I need?
A: The workbooks are designed for desktop Microsoft Excel with Excel 2010-compatible formulas. Windows Excel opening, recalculation and printing have not been verified; test a copy before relying on it. Other spreadsheet applications are untested.

Q: Does it automatically book visits or send invoices?
A: No. Enter jobs and invoice information manually. Contracts suggest a next visit, and the printable documents can be reviewed and printed, but the workbook does not send, book or process payments.

Q: Is the route planner GPS?
A: No. It orders matching jobs by start time, shows up to 14 stops per selected crew and day and may include every job status. It does not optimize or navigate.

Q: Can I track partial payments?
A: You can enter a cumulative paid amount and the date of the last payment. Partial payments across different months cannot be split by actual payment date; maintain a separate ledger for cash reporting.

Q: Does it run payroll?
A: No. Timesheet and overtime estimates are for planning and job costing only; enter rows chronologically and use a payroll professional or service.

Q: Can I sort or add rows?
A: Prepared capacity is fixed and IDs depend on row position. Filter instead; do not sort, insert, delete, move or reuse historical rows, or change ID prefixes after linking.

Q: How do I unlock a sheet?
A: The sheet-protection password is premium. Protection is meant to prevent accidental changes, not provide security or encryption.
''',
 '06-upload-guide.txt':'''SELLER UPLOAD GUIDE

1. Create an Etsy digital listing and upload landscaping-business-manager.zip as the buyer's file. This is the exact workbook package supplied in this kit.
2. Choose a title from 01-titles.txt, use the 13 tags in 02-tags.txt, and adapt the description and FAQs to your shop policies and local requirements.
3. Upload the listing images in numbered order, choosing the strongest images within Etsy's current image limit. They are 2000 x 2000 JPEGs. Tables and dashboard designs are illustrative and labeled as such; they are not screenshots.
4. Verify the listing category, pricing, customer support, policies, language and software requirements before publishing. Do not promise compatibility, integrations or automation that have not been tested.
5. Download your published file, inspect the ZIP, and test on the Excel version you plan to support. Windows Excel opening, recalculation and printing were not available for verification during creation.

The source code is not included in the buyer ZIP. Change the product package only after testing, and update the listing if features or limitations change.
''',
 '07-image-guide.txt':'''LISTING IMAGE GUIDE

01 Cover — landscaping business manager
02 Contents — demo, blank and guide
03 Workbook map — all 23 worksheets
04 Dashboard overview
05 Customers and properties
06 Quote calculator
07 Jobs and work orders
08 Route planner and 14-stop limit
09 Recurring contract reminders
10 Crew and scheduling
11 Timesheets and payroll indicators
12 Materials inventory
13 Equipment and vehicle tracker
14 Invoice and payment tracking
15 Expense and profit methods
16 Reports and seasonal planning
17 Printable quote, invoice and route blocks
18 Important limitations

All workbook tables are newly typeset illustrative examples, not screenshots. The photography is AI-generated and the typography is rendered separately. Use only the number of images Etsy currently permits and keep the limitations visible in your listing description.
''',
 '08-social-captions.txt':'''OPTIONAL SOCIAL CAPTIONS

1. From customer details to crew schedules, keep your landscaping business records together. Explore the demo and make the blank Excel workbook your own. Manual entry required.

2. Quotes, jobs, materials and invoices in one workbook. A practical planning tool for lawn care owners who prefer working in Excel. Read the product guide for capacity and limitations.

3. Make the busy season easier to review: track visits, hours, costs and outstanding invoices in a 23-sheet Excel workbook. No automatic booking, sync or payment processing.

Suggested hashtags: #LandscapingBusiness #LawnCareBusiness #SmallBusinessTools #ExcelTemplate #BusinessOrganization
'''}
 for name,body in COPY_DOCS.items():(COPY/name).write_text(body,encoding='utf-8')
 with zipfile.ZipFile(DL/'landscaping-etsy-listing-kit.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(K.rglob('*')):
   if p.is_file():z.write(p,p.relative_to(K))
 print('Built kit:',DL/'landscaping-etsy-listing-kit.zip')
if __name__=='__main__':main()
