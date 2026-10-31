"""Create an Etsy seller kit for the independently built rental workbook.
AI imagery is text-free; Pillow renders all typography and illustrations.
Run with Pillow: python tools/make_etsy_kit.py
"""
from pathlib import Path
import shutil, zipfile
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=Path(__file__).resolve().parent.parent
ASSETS=ROOT/'etsy/assets'; KIT=ROOT/'etsy/kit'; OUT=KIT/'listing-images'; COPY=KIT/'listing-copy'; DL=ROOT/'download'; S=2000
FONT=Path('/usr/share/fonts/truetype/dejavu')
DEEP='#173E49'; INK='#223C43'; TEAL='#24777A'; MINT='#E0F0ED'; LIGHT='#F7F5EE'; WHITE='#FFFFFF'; MUTED='#5B7172'; LINE='#D9E7E2'; ORANGE='#CB7858'; SAND='#F4E6D4'
def font(size,style='regular'):
 return ImageFont.truetype(str(FONT/{'regular':'DejaVuSans.ttf','bold':'DejaVuSans-Bold.ttf','serif':'DejaVuSerif-Bold.ttf'}[style]),size)
def fit(d,text,size,width,style='bold',minimum=22):
 while size>minimum and d.textlength(text,font=font(size,style))>width:size-=2
 assert d.textlength(text,font=font(size,style))<=width,(text,width,size)
 return font(size,style)
def center(d,y,text,size,fill=INK,style='regular',width=1760):
 f=fit(d,text,size,width,style);d.text(((S-d.textlength(text,font=f))/2,y),text,font=f,fill=fill)
def wrap(d,text,f,width):
 out=[];line=''
 for word in text.split():
  candidate=(line+' '+word).strip()
  if d.textlength(candidate,font=f)<=width:line=candidate
  else:
   assert line,word
   out.append(line);line=word
 if line:out.append(line)
 return out
def box(d,xy,fill=WHITE,outline=LINE,r=28,width=3):d.rounded_rectangle(xy,r,fill=fill,outline=outline,width=width)
def photo(name,dim=0):
 im=ImageOps.fit(Image.open(ASSETS/name).convert('RGB'),(S,S),method=Image.Resampling.LANCZOS)
 return Image.blend(im,Image.new('RGB',(S,S),DEEP),dim) if dim else im
def bar(d,title,sub):
 d.rectangle((0,0,S,285),fill=DEEP);center(d,54,title,94,WHITE,'serif');center(d,184,sub,42,MINT,width=1800);d.rectangle((0,285,S,296),fill=ORANGE)
def footer(d,color=MUTED):center(d,1895,'NOVALITY STORE  /  DIGITAL EXCEL WORKBOOK',28,color,'bold',width=1800)
def card(d,x,y,w,h,title,body):
 box(d,(x,y,x+w,y+h));d.rounded_rectangle((x+26,y+27,x+37,y+h-27),5,fill=ORANGE)
 d.text((x+66,y+26),title,font=fit(d,title,42,w-125),fill=DEEP)
 lines=wrap(d,body,font(36),w-140);assert len(lines)<=3,(title,lines)
 for i,line in enumerate(lines):d.text((x+66,y+91+i*49),line,font=font(36),fill=MUTED)
def table(d,title,headers,rows):
 x=110;y=340;w=1780;box(d,(x,y,x+w,y+700))
 d.text((x+45,y+28),title,font=fit(d,title,49,w-90),fill=DEEP)
 d.text((x+45,y+100),'ILLUSTRATIVE  /  SELECTED FIELDS  /  NOT A SCREENSHOT',font=font(25,'bold'),fill=MUTED)
 d.rectangle((x+45,y+158,x+w-45,y+235),fill=TEAL);cw=(w-90)/len(headers)
 for i,h in enumerate(headers):d.text((x+59+i*cw,y+176),h,font=fit(d,h,30,cw-25,minimum=19),fill=WHITE)
 for j,row in enumerate(rows):
  assert len(row)==len(headers);yy=y+235+j*82;d.rectangle((x+45,yy,x+w-45,yy+82),fill=WHITE if j%2==0 else '#F0F7F5',outline=LINE,width=1)
  for i,v in enumerate(row):d.text((x+59+i*cw,yy+22),str(v),font=fit(d,str(v),30,cw-25,'regular',18),fill=INK)
 for i,(a,b) in enumerate([('01','ENTER'),('02','ORGANIZE'),('03','REVIEW')]):
  px=x+45+i*560;py=y+560;box(d,(px,py,px+520,py+90),MINT,MINT,14)
  d.text((px+22,py+24),a,font=font(30,'bold'),fill=TEAL);d.text((px+95,py+24),b,font=font(30,'bold'),fill=DEEP)
 return y+700
def detail(title,sub,tname,heads,rows,cards,caution=None):
 im=Image.new('RGB',(S,S),LIGHT);d=ImageDraw.Draw(im);bar(d,title,sub);table(d,tname,heads,rows)
 assert len(cards)==3
 for i,(a,b) in enumerate(cards):card(d,110,1085+i*224,1780,192,a,b)
 if caution:
  box(d,(110,1780,1890,1850),MINT,MINT,14);center(d,1798,caution,27,DEEP,'bold')
 footer(d);return im
def cover():
 im=photo('hero.png',.20);d=ImageDraw.Draw(im)
 box(d,(105,110,1410,1360),LIGHT,LIGHT,38)
 d.text((165,175),'SHORT-TERM RENTAL',font=fit(d,'SHORT-TERM RENTAL',56,1170),fill=TEAL)
 for y,text in [(285,'RENTAL'),(470,'BUSINESS'),(655,'MANAGER')]:d.text((155,y),text,font=fit(d,text,144,1180,'serif'),fill=DEEP)
 d.text((165,870),'EXCEL SPREADSHEET',font=fit(d,'EXCEL SPREADSHEET',51,1160),fill=ORANGE)
 for i,line in enumerate(['Organize bookings, turnovers','and your rental records.']):d.text((165,965+i*70),line,font=font(49),fill=INK)
 box(d,(165,1175,1320,1275),MINT,MINT,18);d.text((202,1200),'MANUAL ENTRY  •  NO PLATFORM SYNC',font=fit(d,'MANUAL ENTRY  •  NO PLATFORM SYNC',34,1090),fill=DEEP)
 for i,(n,l) in enumerate([('20','WORKSHEETS'),('2','EXCEL FILES'),('1','PRACTICAL KIT')]):
  x=105+i*590;box(d,(x,1485,x+555,1745),WHITE,WHITE,22)
  f=font(76,'serif');d.text((x+40,1525),n,font=f,fill=TEAL);d.text((x+40,1645),l,font=font(30,'bold'),fill=MUTED)
 footer(d,WHITE);return im
def included():
 im=photo('desk.png',.15);d=ImageDraw.Draw(im);box(d,(90,100,1910,1835),LIGHT,LIGHT,38)
 center(d,160,'WHAT YOU RECEIVE',92,DEEP,'serif');center(d,285,'A practical set of files for rental hosts',43,MUTED)
 for i,(h,b) in enumerate([('01   DEMO WORKBOOK','Explore fictional properties, bookings, sample transactions and reports.'),('02   BLANK WORKBOOK','Start your own records with the same 20 prepared worksheets.'),('03   READ ME & SOURCE','Setup instructions, limitations and the Python generator are included.')]):card(d,150,400+i*255,1700,218,h,b)
 box(d,(150,1220,1850,1675),MINT,MINT)
 center(d,1265,'DESIGNED FOR EXCEL DESKTOP',65,DEEP,'serif');center(d,1375,'Digital files  •  No macros  •  Manual entry',40,INK)
 center(d,1465,'Windows Excel opening and recalculation',37,MUTED);center(d,1520,'have not yet been verified.',37,MUTED)
 center(d,1610,'Please test before relying on the workbook.',32,DEEP,'bold');footer(d,WHITE);return im
def map_page():
 im=Image.new('RGB',(S,S),LIGHT);d=ImageDraw.Draw(im);bar(d,'20 WORKSHEETS','The included workbook, organized by workflow')
 groups=[('START & OVERVIEW','Dashboard  ·  Getting Started  ·  Settings & Lists'),('PROPERTIES & BOOKINGS','Property Database  ·  Booking Tracker  ·  Booking Calendar'),('GUEST EXPERIENCE','Guest Database  ·  Check-in & Check-out  ·  Reviews Tracker'),('CLEANING & TURNOVERS','Cleaning Schedule  ·  Turnover Checklist'),('OPERATIONS & FINANCE','Platform Revenue & Fees  ·  Expense Tracker  ·  Supplies Inventory'),('MAINTENANCE & PEOPLE','Maintenance Log  ·  Staff & Vendors'),('PERFORMANCE & REPORTS','Tax Summary  ·  Occupancy & Performance  ·  Monthly Reports  ·  Annual Reports')]
 for i,(a,b) in enumerate(groups):card(d,110,330+i*211,1780,183,a,b)
 footer(d);return im
def overview():
 im=Image.new('RGB',(S,S),LIGHT);d=ImageDraw.Draw(im);bar(d,'HOSTING AT A GLANCE','One manual workbook for the details behind each stay')
 d.text((120,350),'ILLUSTRATIVE DASHBOARD THEMES  /  NOT A SCREENSHOT',font=font(26,'bold'),fill=MUTED)
 themes=[('PROPERTIES','Active listings'),('BOOKINGS','Recorded stays'),('CLASHES','Rows to review'),('REVENUE','Estimated net'),('COSTS','Entered expenses'),('PAYOUTS','Bank deposits')]
 for i,(a,b) in enumerate(themes):
  x=115+i%2*900;y=420+i//2*290;box(d,(x,y,x+850,y+245));d.rectangle((x,y,x+850,y+12),fill=TEAL);d.text((x+42,y+44),a,font=font(33,'bold'),fill=MUTED);d.text((x+42,y+110),b,font=fit(d,b,59,755,'serif'),fill=DEEP)
 card(d,115,1350,1750,225,'REVIEW THE UNDERLYING RECORDS','All figures depend on the entries and assumptions you provide. Reconcile with statements regularly.')
 box(d,(115,1650,1865,1800),MINT,MINT);center(d,1695,'MANUAL ENTRIES  •  NO LIVE PLATFORM CONNECTION',34,DEEP,'bold');footer(d);return im
def formula_page():
 im=photo('interior.png',.26);d=ImageDraw.Draw(im);box(d,(100,90,1900,1820),LIGHT,LIGHT,38)
 center(d,150,'A SIMPLE PAYOUT EXAMPLE',80,DEEP,'serif');center(d,265,'Illustrative demo booking  •  BKG-0001',42,MUTED)
 for i,(big,label) in enumerate([('$580.00','GROSS BEFORE TAX'),('− $17.40','PLATFORM FEE'),('$562.60','EXPECTED PAYOUT')]):
  x=155+i*570;box(d,(x,405,x+530,695),WHITE,LINE)
  f=fit(d,big,66,465,'serif');d.text((x+(530-d.textlength(big,font=f))/2,460),big,font=f,fill=TEAL)
  f=fit(d,label,25,480);d.text((x+(530-d.textlength(label,font=f))/2,600),label,font=f,fill=MUTED)
 center(d,750,'SPLIT DEPOSITS ARE SUMMED BY BOOKING',35,DEEP,'bold')
 for i,(t,b) in enumerate([('RECORD EACH DEPOSIT ONCE','In the sample, $200.00 plus $362.60 equals $562.60 received.'),('REVIEW THE DIFFERENCE','The expected amount and difference repeat on each payout row; do not sum those columns.'),('CHECK ACTUAL STATEMENTS','Rates and tax settings are assumptions. Actual platform payouts can differ.')]):card(d,155,845+i*234,1690,205,t,b)
 center(d,1660,'Example assumes a 3% fee and no self-remitted tax.',32,MUTED);footer(d,WHITE);return im
def howto():
 im=photo('desk.png',.23);d=ImageDraw.Draw(im);box(d,(100,90,1900,1820),LIGHT,LIGHT,38)
 center(d,150,'GET STARTED IN EXCEL',82,DEEP,'serif');center(d,270,'A straightforward manual workflow',43,MUTED)
 steps=[('01  SET YOUR ASSUMPTIONS','Enter the report year and review platform fees and tax settings.'),('02  ADD YOUR RECORDS','Create properties, guests and vendors, then enter bookings and blocks.'),('03  MANAGE EACH STAY','Track arrival tasks, cleaning and operational notes against booking IDs.'),('04  RECONCILE & REVIEW','Enter payouts and costs, resolve warnings, and review your reports.'),('05  KEEP IDS STABLE','Filter populated registers; do not sort, insert, delete or move rows.')]
 for i,(h,b) in enumerate(steps):card(d,155,375+i*240,1690,205,h,b)
 center(d,1655,'No sync  •  No payment processing  •  No automatic messages',31,MUTED,'bold');footer(d,WHITE);return im
def limits():
 im=Image.new('RGB',(S,S),LIGHT);d=ImageDraw.Draw(im);bar(d,'PLEASE READ BEFORE BUYING','Clear expectations for a manual digital product')
 items=[('MICROSOFT EXCEL DESKTOP','Intended software. Windows Excel opening and recalculation have not been verified.'),('NO PLATFORM SYNC','Calendar and booking data must be entered manually and checked on each platform.'),('FIXED PREPARED CAPACITY','30 properties and 900 booking rows by default. The 14-day view shows the first 12 properties.'),('ESTIMATES, NOT ADVICE','Reports and tax amounts are simplified management estimates, not accounting or tax advice.'),('STABLE RECORD IDS','Do not sort, insert, delete or move populated register rows; use filters.'),('PROTECTION IS NOT ENCRYPTION','Password premium protects formulas from accidental editing; secure your own files.')]
 for i,(h,b) in enumerate(items):card(d,110,345+i*245,1780,210,h,b)
 footer(d);return im
PAGES=[
('01-cover',cover),('02-whats-included',included),('03-worksheet-map',map_page),('04-dashboard-overview',overview),
('05-property-register',lambda:detail('PROPERTY DATABASE','Keep the essentials for each listing together','PROPERTY DATABASE',['Property ID','Property name','Status','Nightly rate','Cleaning fee'],[['PRP-01','Harbour View Loft','Active','$165.00','$85.00'],['PRP-02','Pine Ridge Cabin','Active','$395.00','$180.00']],[('CENTRAL PROPERTY RECORDS','Store the address, status, pricing, capacity and other notes for each property.'),('USE CONSISTENT IDS','Use the generated property ID in bookings and other records.'),('HISTORICAL ASSUMPTIONS','Changing property prices can change booking estimates unless override fields are used.')],'Example figures are fictional and editable.')),
('06-booking-tracker',lambda:detail('BOOKING TRACKER','A structured record of reservations and blocks','BOOKING TRACKER',['Booking ID','Property ID','Status','Check-in','Check-out'],[['BKG-0017','PRP-01','Confirmed','28 Oct 2026','02 Nov 2026'],['BKG-0018','PRP-01','Confirmed','02 Nov 2026','04 Nov 2026']],[('STAY DETAILS','Enter property, guest, platform, status and arrival and departure dates.'),('REVIEW OVERLAPS','The clash column flags conflicts among entries recorded in this workbook.'),('REVENUE ESTIMATES','Nights, room revenue, platform fees and expected payout are calculated from inputs.')],'Same-day checkout and check-in are not a date overlap.')),
('07-booking-calendar',lambda:detail('BOOKING CALENDAR','A monthly view and a 14-day overview','CALENDAR CONCEPT',['Property','Date','Status'],[['PRP-01','28 Oct 2026','Occupied'],['PRP-01','29 Oct 2026','Occupied'],['PRP-01','02 Nov 2026','Occupied']],[('SELECT A PROPERTY & MONTH','Review a selected property one day at a time using the booking rows.'),('NEXT 14 DAYS','The summary view covers the first 12 properties in the property register.'),('MANUAL DATA ONLY','Bookings and blocks must be entered here; this calendar does not sync.')],'Always verify live availability on every platform.')),
('08-guest-database',lambda:detail('GUEST DATABASE','Keep guest details and completed stay counts together','GUEST DATABASE',['Guest ID','Guest name','Country','Marketing consent'],[['GST-0001','Rebecca Thorne','United States','Yes'],['GST-0002','Dai Nguyen','United States','No']],[('GUEST DETAILS','Record contact information, country, consent preference and notes.'),('USE GUEST IDS','Link booking rows to the relevant guest ID for consistent records.'),('PROTECT PERSONAL DATA','Store the workbook in encrypted, access-controlled storage; sheet protection is not encryption.')],'All examples are fictional.')),
('09-checkin-checkout',lambda:detail('CHECK-IN & CHECK-OUT','Manually track important guest communications','CHECK-IN & CHECK-OUT',['Booking ID','Directions sent','Access sent','Checked out','Inspected'],[['BKG-0001','Yes','Yes','Yes','Yes']],[('PRE-ARRIVAL','Log whether directions, access, Wi-Fi, rules and welcome details were sent.'),('DEPARTURE & INSPECTION','Record checkout messages, checkout, inspection and photo completion.'),('MANUAL FOLLOW-UP','The workbook records your status choices; it does not send messages.')],'Select Yes or No as you complete each step.')),
('10-cleaning-turnover',lambda:detail('CLEANING & TURNOVERS','Keep a practical record of cleaning tasks','CLEANING SCHEDULE',['Booking ID','Cleaner ID','Status','Laundry','Completion'],[['BKG-0001','VND-001','Complete','Yes','100%']],[('AUTOMATIC ROW LINK','Eligible booking rows appear in the same position on Cleaning Schedule.'),('NINE TASK FLAGS','Record bedroom, bathroom, kitchen, living areas, floors and other turnover tasks.'),('PRINTABLE CHECKLIST','Print a separate turnover checklist; it does not update the schedule automatically.')],'Do not sort, insert, delete or move populated booking rows.')),
('11-split-payouts',formula_page),
('12-expense-tracker',lambda:detail('EXPENSE TRACKER','Record operating costs once for management reports','EXPENSE TRACKER',['Date','Property ID','Category','Amount','Count in profit?'],[['01 Oct 2026','PRP-01','Repairs','$94.00','Yes'],['01 Oct 2026','PRP-01','Cleaning','$60.00','Yes']],[('CATEGORIZE COSTS','Enter dates, property IDs, amounts, vendor details and tax categories.'),('CHOOSE WHAT TO INCLUDE','Set Count in profit? to Yes for expenses you want in the management summary.'),('AVOID DOUBLE COUNTING','Cleaning and maintenance tabs are operational; enter actual costs here once.')],'Expense classification should be reviewed with your adviser.')),
('13-supplies-maintenance',lambda:detail('SUPPLIES & MAINTENANCE','A manual view of stock and property issues','SUPPLIES INVENTORY',['Item','In stock','Minimum','Unit cost','Order now?'],[['Toilet rolls','4','6','$8.40','Order now'],['Bath towels','24','12','$11.00','OK']],[('STOCK LEVELS','Track quantities, minimums and unit costs; low stock is flagged.'),('MAINTENANCE LOG','Record priority, vendor, dates, status, costs and warranty details.'),('EXPENSES ARE SEPARATE','Record actual repair and supply costs in Expense Tracker if they belong in reports.')],'Inventory and job updates are entered manually.')),
('14-reviews-vendors',lambda:detail('REVIEWS & VENDORS','Keep feedback and service contacts organized','STAFF & VENDORS',['Vendor ID','Name','Role','Pay basis'],[['VND-001','Priya Raman','Cleaner','Per turnover']],[('REVIEW SCORES','Capture overall and detailed ratings, reply status and notes against a booking ID.'),('VENDOR INFORMATION','Keep role, contact details, rate and insurance-expiry information together.'),('NO AUTOMATED FOLLOW-UP','Track records manually; the workbook does not send replies or reminders.')],'Fictional example information shown.')),
('15-occupancy-performance',lambda:detail('OCCUPANCY & PERFORMANCE','Understand room revenue across the reporting year','ILLUSTRATIVE CALCULATION',['Booked nights','Available nights','Room revenue','ADR','RevPAR'],[['3','28','$495.00','$165.00','$17.68']],[('MONTHLY NIGHT ALLOCATION','Stays crossing a month are allocated by their individual nights.'),('ADR & REVPAR','Both use room revenue excluding cleaning and extra fees.'),('REVIEW CLASHES','Overlapping stays or blocks are not deduplicated; resolve warnings before relying on results.')],'Illustrative figures; not an actual workbook screenshot.')),
('16-reports-tax',lambda:detail('MONTHLY & ANNUAL REPORTS','Bring your entries together in one place','REPORT TIMING',['Measure','Grouped by','Purpose'],[['Room revenue','Stay nights','Performance'],['Net booked revenue','Check-in month','Estimate'],['Bank payouts','Payout date','Cash record']],[('MONTHLY & YEARLY VIEWS','Review nights, occupancy, room revenue, estimated net and costs for the chosen year.'),('DIFFERENT TIMING BASES','Room revenue, booked revenue, expenses and payouts use different dates.'),('TAX SUMMARY','Categorize entered expenses for review; the result is not formal tax advice.')],'Reconcile with bank and platform records.')),
('17-important-details',limits),('18-how-to-use',howto)]
FILES={
'01-titles.txt':'''ETSY TITLE OPTIONS — choose one

Short Term Rental Spreadsheet, Vacation Rental Management Excel Template, Booking Tracker, Airbnb Host Organizer

Airbnb Host Spreadsheet, Short Term Rental Booking and Expense Tracker, Vacation Rental Management Excel Template

Vacation Rental Excel Spreadsheet, Property Booking Calendar, Guest Tracker, Cleaning Schedule and Payout Organizer
''',
'02-tags.txt':'''ETSY TAGS — 13 suggestions, each 20 characters or fewer

rental spreadsheet
short term rental
vacation rental
rental host planner
airbnb spreadsheet
booking tracker
rental management
host excel template
cleaning schedule
rental expense log
property organizer
rental calendar
payout tracker
''',
'03-description.txt':'''SHORT-TERM RENTAL MANAGEMENT SPREADSHEET

Bring your properties, bookings, guest information, turnovers and financial records together in one manual Excel workbook. This 20-worksheet digital template gives hosts a structured place to record their day-to-day operations, with a demo workbook to explore and a blank copy for their own records.

WHAT YOU RECEIVE
• Rental-Demo.xlsx — fictional example bookings, properties, tasks and transactions
• Rental-Blank.xlsx — the same 20 worksheets with empty registers
• README.md — setup instructions, capacity, assumptions and important limitations
• Python generator and regression-test source files

WHAT YOU CAN ORGANIZE
• Property details, pricing assumptions, bookings and owner/maintenance blocks
• A monthly property calendar and 14-day view of the first 12 properties
• Guest contacts, manual arrival/departure checks and review records
• Cleaning schedules, a printable turnover checklist and vendor details
• Payout entries, split deposits, expenses, supplies and maintenance notes
• Night-based occupancy, room revenue, ADR and RevPAR, plus monthly and annual summaries

HOW IT WORKS
Open the blank workbook in Microsoft Excel desktop, save your own copy and allow formulas to recalculate. Review Settings & Lists and enter the rates on each property row. Create property, guest and vendor records, then add bookings and blocks using their IDs. Review clash warnings, enter actual payouts and costs, and reconcile against your platform and bank statements.

PLEASE READ BEFORE PURCHASE
This is a digital download; no physical item is shipped. The workbook is intended for Microsoft Excel desktop, but opening and recalculation in Windows Excel have not yet been verified. Test in your own Excel version before relying on the file. Other spreadsheet applications are untested.

This is a manual template: there is no Airbnb, Vrbo or other platform sync, API or iCal connection; no live availability, payment processing or automatic messages. Verify availability directly on every platform. Airbnb is mentioned descriptively; this product is not affiliated with or endorsed by Airbnb.

The default workbook has room for 30 properties and 900 bookings; see the guide for other capacities. IDs depend on row positions and cleaning tasks mirror booking rows. Do not sort, insert, delete or move populated register rows; use filters instead. The 14-day view shows only the first 12 properties.

Revenue, platform fees and self-remitted tax are simplified estimates. Platform fee and property setting changes can recalculate historic estimates. ADR and RevPAR use room revenue excluding cleaning and extra fees. Monthly room revenue is allocated by stay night; net booked revenue uses check-in month, while costs and bank payouts use their own dates. Reports are not accounting or tax advice.

The sheet password is premium. It helps prevent accidental formula edits but is not encryption. Store guest information in an encrypted, access-controlled location and follow your local privacy rules.
''',
'04-key-features.txt':'''KEY FEATURES

• 20 worksheets in each workbook
• Demo and blank Excel files, guide and generator source
• 30 property rows and 900 booking rows by default
• Booking clash warnings based on manually entered records
• Monthly property calendar and 14-day view of the first 12 properties
• Guest, check-in/out, cleaning, supplies and maintenance logs
• Split-payout totals by booking and manual expense records
• Cross-month stay-night allocation; ADR and RevPAR exclude cleaning and extras
• Monthly and annual management summaries, not formal tax/accounting reports
• Protected formula cells and unlocked entry cells; no macros or platform sync

Intended for Excel desktop. Windows Excel opening and recalculation have not been verified.
''',
'05-faq.txt':'''FREQUENTLY ASKED QUESTIONS

Q: What do I receive?
A: One ZIP with a demo workbook, blank workbook, README, and Python generator and test source files.

Q: Which software do I need?
A: The workbooks are intended for Microsoft Excel desktop. Opening and recalculation in Windows Excel have not yet been verified; test in your own version before relying on the files. Other spreadsheet applications are untested.

Q: Does the calendar sync with Airbnb, Vrbo or iCal?
A: No. All data is entered manually. Clash warnings cover only the records entered in the workbook. Verify live availability directly on every platform.

Q: Can I record split payouts?
A: Yes. Enter each actual net bank deposit once with its booking ID. The total received and variance are shown per booking and repeat for reference; do not sum these repeated columns.

Q: Does the workbook calculate taxes and platform fees exactly?
A: No. It uses simplified assumptions and editable platform rates. Costs, taxes and payouts require independent review and reconciliation. Consult a qualified professional about tax treatment.

Q: Does sheet protection encrypt my guest data?
A: No. The password premium prevents accidental formula edits, not unauthorized access. Use encrypted, access-controlled storage.

Q: Can I sort or insert rows?
A: Do not sort, insert, delete or move populated register rows. IDs are based on physical row positions, and cleaning tasks are linked to booking row positions. Filter instead.

Q: How many properties and bookings can I enter?
A: The default workbook prepares 30 property rows and 900 booking rows. The 14-day view displays the first 12 properties. See the guide for other capacities.
''',
'06-how-to-use.txt':'''HOW TO USE

1. Download and unzip CUSTOMER-DOWNLOAD.zip. Open Rental-Blank.xlsx in Excel desktop and save a working copy. Allow formulas to recalculate.
2. Read Getting Started and README. Set the reporting year, platform fee percentages and tax assumptions in Settings & Lists.
3. Add properties, guests and vendors. Enter actual nightly rates and cleaning fees on property rows; the settings defaults are reference values and do not fill those rows automatically.
4. Enter bookings and blocks manually using stable IDs. Verify availability directly on every platform and resolve clash warnings.
5. Log check-in/out steps and cleaning tasks. Enter actual bank deposits once in Platform Revenue & Fees and actual costs once in Expense Tracker.
6. Review monthly and annual summaries. Reconcile statements; keep sensitive data encrypted and backed up.

Do not sort, insert, delete or move populated register rows. Filter instead. Sheet protection password: premium. It is not encryption.
''',
'07-listing-attributes.txt':'''SUGGESTED LISTING DETAILS

Product type: Digital download
Buyer file: One ZIP with two .xlsx workbooks, README.md, Python generator and test source
Intended application: Microsoft Excel desktop
Worksheets: 20 per workbook
Default capacity: 30 property rows, 900 booking rows
Macro-enabled: No (.xlsx)
Delivery: Digital only; no physical item
Author / brand: Novality Store
Compatibility disclosure: Designed with Excel 2010-compatible functions. Opening and recalculation in Windows Excel have not been verified; other apps untested.

Choose the appropriate Etsy category and available attributes at publication time. Confirm Etsy's current digital-file and listing-image requirements before upload. This template is not affiliated with Airbnb or any booking platform.
''',
'08-keywords.txt':'''SEARCH PHRASES & AUDIENCE

short term rental spreadsheet; vacation rental management Excel template; Airbnb host spreadsheet; rental booking tracker; guest database; property calendar spreadsheet; rental cleaning schedule; vacation rental payout tracker; short term rental expense log; rental occupancy and ADR.

Potential audience: independent hosts, co-hosts and small short-term rental operators who want a manual Excel organizer.

Avoid claims of real-time calendar sync, guaranteed platform compatibility, verified Windows Excel operation, automatic messaging or payment processing, encryption, tax compliance or accounting certification.
'''
}
def main():
 if KIT.exists():shutil.rmtree(KIT)
 OUT.mkdir(parents=True);COPY.mkdir()
 for name,fn in PAGES:
  fn().save(OUT/(name+'.jpg'),'JPEG',quality=90,subsampling=0,optimize=True);print(name)
 for name,text in FILES.items():(COPY/name).write_text(text,encoding='utf-8')
 titles=[x for x in FILES['01-titles.txt'].splitlines() if x and not x.startswith('ETSY')];tags=[x for x in FILES['02-tags.txt'].splitlines() if x and not x.startswith('ETSY')]
 assert len(titles)==3 and all(len(x)<=140 for x in titles),[(len(x),x) for x in titles]
 assert len(tags)==13 and all(len(x)<=20 for x in tags) and len(set(tags))==13,[(len(x),x) for x in tags]
 shutil.copy2(DL/'airbnb-rental-management-spreadsheet.zip',KIT/'CUSTOMER-DOWNLOAD.zip')
 (KIT/'SELLER-START-HERE.txt').write_text('''SHORT-TERM RENTAL ETSY LISTING KIT — FOR THE SELLER

1. Read listing-copy and select one title and 13 tags. Confirm the listing details and current Etsy policies before publishing.
2. Select from the 18 square listing image alternatives. They contain illustrative tables and are not literal workbook screenshots. Verify the image count and specifications accepted by Etsy at listing time.
3. Upload CUSTOMER-DOWNLOAD.zip as the digital product file. It is the original customer package with the demo workbook, blank workbook, README and Python source. Do not upload the whole seller kit as the buyer product.
4. Test the customer workbooks in Windows Excel for repair messages and recalculation before selling. This test has not yet been performed; the listing copy and images disclose that limitation. Update the disclosures only after actual successful testing.
5. The workbook is manual, not a platform integration, accounting service or encrypted database. Verify every claim and the included guide. Airbnb is mentioned descriptively; this product is not affiliated with the platform.
6. Image backgrounds were AI-generated without text; all visible typography and example tables were drawn separately.
''',encoding='utf-8')
 out=DL/'airbnb-rental-etsy-listing-kit.zip'
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(KIT.rglob('*')):
   if p.is_file():z.write(p,p.relative_to(KIT))
 for part in range(3):
  sheet=Image.new('RGB',(1500,1000),'white')
  for i,(name,_) in enumerate(PAGES[part*6:part*6+6]):
   im=Image.open(OUT/(name+'.jpg')).resize((500,500));sheet.paste(im,((i%3)*500,(i//3)*500))
  sheet.save(ROOT/'etsy'/f'qa-{part+1}.jpg',quality=90)
 print('Saved',out,'bytes',out.stat().st_size)
if __name__=='__main__':main()
