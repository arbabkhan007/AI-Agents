"""Build the daycare Etsy listing kit. Backgrounds are AI photos without text;
all typography and illustrative (not screenshot) tables are rendered using PIL.
Install Pillow, then run from any directory: python tools/make_etsy_kit.py
"""
from pathlib import Path
import shutil, zipfile
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=Path(__file__).resolve().parent.parent
KIT=ROOT/'etsy'/'kit'; OUT=KIT/'listing-images'; COPY=KIT/'listing-copy'
ASSETS=ROOT/'etsy'/'assets'; DOWNLOAD=ROOT/'download'; S=2000
INK='#183F40'; DEEP='#194D56'; TEAL='#287B78'; SAGE='#DDEEE8'; CREAM='#F8F6EF'; GOLD='#E5BA70'; MUTED='#57716F'; WHITE='#FFFFFF'; LINE='#DAE9E4'; RED='#8A4F30'
FONT=Path('/usr/share/fonts/truetype/dejavu')
def sans(n): return ImageFont.truetype(str(FONT/'DejaVuSans.ttf'),n)
def bold(n): return ImageFont.truetype(str(FONT/'DejaVuSans-Bold.ttf'),n)
def serif(n): return ImageFont.truetype(str(FONT/'DejaVuSerif-Bold.ttf'),n)
def fit(d,s,factory,sz,width,minsz=22):
    while sz>minsz and d.textlength(s,font=factory(sz))>width: sz-=2
    return factory(sz)
def center(d,y,s,f,fill=INK): d.text(((S-d.textlength(s,font=f))/2,y),s,font=f,fill=fill)
def wrap(d,text,font,w):
    lines=[]; line=''
    for word in text.split():
        trial=(line+' '+word).strip()
        if d.textlength(trial,font=font)<=w: line=trial
        else:
            if line: lines.append(line)
            line=word
    if line: lines.append(line)
    return lines
def box(d,xy,fill=WHITE,outline=LINE,r=30,w=3): d.rounded_rectangle(xy,r,fill=fill,outline=outline,width=w)
def bg_photo(name,dim=.35):
    image=ImageOps.fit(Image.open(ASSETS/name).convert('RGB'),(S,S),method=Image.Resampling.LANCZOS)
    return Image.blend(image,Image.new('RGB',(S,S),DEEP),dim)
def top(d,title,sub):
    d.rectangle((0,0,S,290),fill=DEEP)
    center(d,75,title,fit(d,title,serif,102,1770),WHITE)
    center(d,202,sub,fit(d,sub,sans,43,1750),SAGE)
    d.rectangle((0,290,S,300),fill=GOLD)
def footer(d,text='NOVALITY STORE  ·  DIGITAL EXCEL WORKBOOK'):
    center(d,1880,text,fit(d,text,bold,32,1800),MUTED)
def card(d,x,y,w,h,title,body):
    box(d,(x,y,x+w,y+h)); d.rounded_rectangle((x+24,y+27,x+36,y+h-27),6,fill=GOLD)
    d.text((x+65,y+30),title,font=fit(d,title,bold,45,w-115),fill=DEEP)
    lines=wrap(d,body,sans(37),w-130)
    assert len(lines)<=3, (title,lines)
    for i,line in enumerate(lines): d.text((x+65,y+98+i*51),line,font=sans(37),fill=MUTED)
def pill(d,x,y,text):
    f=bold(31); w=int(d.textlength(text,font=f))+52
    d.rounded_rectangle((x,y,x+w,y+61),30,fill=SAGE)
    d.text((x+26,y+11),text,font=f,fill=DEEP)
    return w
def table(d,title,headers,rows,small='ILLUSTRATIVE VIEW  •  SAMPLE DATA'):
    # Stylized representation based on real workbook columns and example rows.
    x=110; y=360; w=1780; h=690
    box(d,(x,y,x+w,y+h),WHITE,LINE,30)
    d.text((x+50,y+34),title,font=fit(d,title,bold,48,w-100),fill=DEEP)
    d.text((x+50,y+108),small,font=bold(25),fill=MUTED)
    d.rounded_rectangle((x+40,y+170,x+w-40,y+225),12,fill='#EFF5F3')
    d.text((x+65,y+181),'SELECTED FIELDS  /  SIMPLIFIED EXAMPLE',font=bold(25),fill=MUTED)
    yy=y+250; cols=len(headers); cw=(w-100)/cols
    d.rectangle((x+50,yy,x+w-50,yy+83),fill=TEAL)
    for i,head in enumerate(headers):
        f=fit(d,head,bold,32,cw-24,24); d.text((x+62+i*cw,yy+22),head,font=f,fill=WHITE)
    yy+=83
    for j,row in enumerate(rows):
        d.rectangle((x+50,yy+j*86,x+w-50,yy+(j+1)*86),fill=WHITE if j%2==0 else '#F1F7F5',outline=LINE,width=1)
        for i,word in enumerate(row):
            f=fit(d,str(word),sans,33,cw-24,22); d.text((x+62+i*cw,yy+j*86+23),str(word),font=f,fill=INK)
    return y+h

def sheet_image(title,sub,table_title,headers,rows,cards,caution=None):
    img=Image.new('RGB',(S,S),CREAM); d=ImageDraw.Draw(img); top(d,title,sub)
    table(d,table_title,headers,rows)
    for idx,(t,b) in enumerate(cards): card(d,110,1100+idx*228,1780,200,t,b)
    if caution:
        box(d,(110,1795,1890,1852),SAGE,SAGE,r=14)
        center(d,1806,caution,fit(d,caution,bold,26,1680),DEEP)
    footer(d); return img

def cover():
    im=bg_photo('childcare-room.jpg',.39); d=ImageDraw.Draw(im)
    box(d,(130,145,1870,1155),CREAM,CREAM,42)
    center(d,220,'DAYCARE & CHILDCARE',fit(d,'DAYCARE & CHILDCARE',bold,58,1550),TEAL)
    center(d,330,'BUSINESS',serif(158),DEEP)
    center(d,520,'MANAGEMENT',serif(140),DEEP)
    center(d,700,'SPREADSHEET',serif(121),DEEP)
    center(d,900,'Organize your childcare business in Excel',sans(51),MUTED)
    for x,big,small in [(190,'23','WORKSHEETS'),(755,'2','EXCEL FILES'),(1320,'1','SIMPLE SYSTEM')]:
        box(d,(x,1250,x+490,1520),WHITE,WHITE,30)
        f=serif(88); d.text((x+(490-d.textlength(big,font=f))/2,1283),big,font=f,fill=TEAL)
        f=bold(31); d.text((x+(490-d.textlength(small,font=f))/2,1434),small,font=f,fill=MUTED)
    center(d,1660,'ENROLLMENT  ·  ATTENDANCE  ·  TUITION  ·  REPORTS',fit(d,'ENROLLMENT  ·  ATTENDANCE  ·  TUITION  ·  REPORTS',bold,40,1720),WHITE)
    center(d,1840,'NOVALITY STORE  |  DIGITAL DOWNLOAD',bold(34),WHITE); return im

def included():
    im=Image.new('RGB',(S,S),CREAM); d=ImageDraw.Draw(im); top(d,'WHAT YOU RECEIVE','A practical starting point for your childcare business')
    for i,(h,b) in enumerate([('01  DEMO WORKBOOK','Explore a worked example with sample families, a ledger, schedules and reports.'),('02  BLANK WORKBOOK','Start fresh with the same 23 sheets and empty business registers.'),('03  QUICK-START GUIDE','Learn the setup, transaction rules, capacities and important limitations.')]):
        card(d,125,370+i*280,1750,235,h,b)
    box(d,(125,1255,1875,1660),SAGE,SAGE)
    center(d,1300,'BUILT FOR EXCEL',serif(75),DEEP)
    center(d,1420,'No macros  ·  No subscription  ·  Digital files',sans(42),INK)
    center(d,1510,'Workbook formulas are designed for Excel 2010+',sans(39),MUTED)
    center(d,1580,'Windows Excel opening has not yet been verified.',sans(34),MUTED)
    footer(d); return im

def tabmap():
    im=Image.new('RGB',(S,S),CREAM); d=ImageDraw.Draw(im); top(d,'23 WORKSHEETS','The full workbook, organized in one place')
    groups=[('START & OVERVIEW','Dashboard  ·  Getting Started  ·  Settings & Lists'),('FAMILIES & ENROLLMENT','Child Enrollment  ·  Parent Database  ·  Waitlist  ·  Attendance'),('BILLING & DAILY CARE','Tuition & Fees  ·  Invoices & Receipts  ·  Daily Reports  ·  Meal Tracker'),('HEALTH & PEOPLE','Allergy & Medical  ·  Incident Reports  ·  Staff Database  ·  Staff Schedule'),('OPERATIONS','Payroll Tracker  ·  Classroom Management  ·  Expense Tracker  ·  Supply Inventory'),('FOLLOW-UP & REPORTS','Parent Communication  ·  Document Tracker  ·  Monthly Reports  ·  Annual Reports')]
    for i,(h,b) in enumerate(groups): card(d,110,340+i*236,1780,208,h,b)
    footer(d); return im

def dashboard():
    im=Image.new('RGB',(S,S),CREAM); d=ImageDraw.Draw(im); top(d,'YOUR BUSINESS AT A GLANCE','A simple overview from the registers')
    d.text((130,350),'ILLUSTRATIVE VIEW  •  OCTOBER 2026 DEMO',font=bold(29),fill=MUTED)
    stats=[('ACTIVE CHILDREN','2'),('FAMILY BALANCE','$230'),('NET CHARGES','$300'),('NET CASH','$70'),('CASH LESS COSTS','−$119'),('FAMILIES','2')]
    for i,(label,value) in enumerate(stats):
        x=120+(i%2)*900; y=425+(i//2)*290
        box(d,(x,y,x+850,y+252)); d.rectangle((x,y,x+850,y+11),fill=TEAL)
        d.text((x+48,y+43),label,font=fit(d,label,bold,35,750),fill=MUTED)
        d.text((x+48,y+100),value,font=serif(86),fill=DEEP)
    card(d,120,1350,1750,245,'REVIEW THE SOURCE REGISTERS','Selected-year totals summarize manual entries. Reconcile the ledger and bank records regularly.')
    footer(d); return im

def balance_story():
    im=bg_photo('toys.jpg',.43); d=ImageDraw.Draw(im)
    box(d,(105,120,1895,1825),CREAM,CREAM,38)
    center(d,180,'A SIMPLE BALANCE',serif(95),DEEP)
    center(d,305,'A payment is counted once, not twice',sans(46),MUTED)
    for i,(value,label) in enumerate([('$100','INVOICE'),('− $30','PAYMENT'),('$70','FAMILY BALANCE')]):
        x=170+i*565
        box(d,(x,450,x+530,760),WHITE,LINE)
        f=serif(87); d.text((x+(530-d.textlength(value,font=f))/2,510),value,font=f,fill=TEAL)
        f=bold(29); d.text((x+(530-d.textlength(label,font=f))/2,660),label,font=f,fill=MUTED)
    center(d,810,'ONE LEDGER  ·  ONE BALANCE EFFECT PER EVENT',bold(36),DEEP)
    for i,(a,b) in enumerate([('ENTER POSITIVE AMOUNTS','Choose the transaction type; a formula applies its balance effect.'),('DEPOSITS ARE CREDITS','Do not record the same deposit again as a payment when applied.'),('RECONCILE REGULARLY','Resolve ledger warnings and compare with bank and family records.')]):
        card(d,170,910+i*235,1660,205,a,b)
    center(d,1665,'Illustrative sample  ·  Amounts are entered manually',sans(35),MUTED)
    center(d,1890,'NOVALITY STORE  ·  DIGITAL DOWNLOAD',bold(34),WHITE)
    return im

def howto():
    im=bg_photo('desk-planning.jpg',.33); d=ImageDraw.Draw(im)
    box(d,(105,105,1895,1780),CREAM,CREAM,38)
    center(d,160,'READY TO GET STARTED?',fit(d,'READY TO GET STARTED?',serif,89,1650),DEEP)
    center(d,295,'Open the blank file and make it your own',sans(45),MUTED)
    for i,(a,b) in enumerate([('01  OPEN & SAVE','Download the files and save your own blank copy in Excel.'),('02  SET YOUR DETAILS','Edit centre information, reporting year and local reference values.'),('03  ADD YOUR RECORDS','Use consistent IDs for families, children and staff; enter one event per row.'),('04  REVIEW & RECONCILE','Check review warnings and compare totals with your records.')]): card(d,170,390+i*247,1660,215,a,b)
    center(d,1460,'IMPORTANT',bold(40),TEAL)
    for i,line in enumerate(['Sheet protection is not encryption. Store sensitive data securely.',
                              'No live staffing, pickup authorization or compliance checks.',
                              'Tax, payroll and discounts require manual entry.']):
        center(d,1530+i*62,line,fit(d,line,sans,36,1550),MUTED)
    center(d,1840,'NOVALITY STORE  ·  DIGITAL DOWNLOAD',bold(34),WHITE); return im

PAGES=[
('01-cover',cover),('02-whats-included',included),('03-all-23-tabs',tabmap),('04-dashboard',dashboard),
('05-child-enrollment',lambda:sheet_image('CHILD ENROLLMENT','Keep essential enrollment details together','CHILD ENROLLMENT',['Child ID','Child name','Family ID','Status','Room'],[['CHD-001','Avery Brooks','FAM-001','Active','Sunflower'],['CHD-002','Milo Chen','FAM-002','Active','Willow']], [('A PLACE FOR EVERY CHILD','Record start dates, programme, schedule and status in one register.'),('LINK BY FAMILY ID','Use the same family ID across enrollment, parent records and the ledger.'),('PREPARED FOR 150 CHILDREN','Enter your own data in white cells; use filters to find records.') ])),
('06-parent-database',lambda:sheet_image('FAMILIES & WAITLIST','Organize the people behind each enrollment','PARENT DATABASE',['Family ID','Parent / guardian','Phone','Balance'],[['FAM-001','Jordan Brooks','555-0101','$70.00'],['FAM-002','Riley Chen','555-0111','$160.00']], [('FAMILY CONTACT DETAILS','Keep guardian contact and emergency contact details together.'),('A CLEAR FAMILY BALANCE','The balance sums signed ledger effects once; deposits are credits.'),('TRACK NEW ENQUIRIES','Use the separate Waitlist sheet for enquiry and desired start dates.')],'Store sensitive family information in encrypted, access-controlled storage.')),
('07-attendance',lambda:sheet_image('ATTENDANCE','A daily register for arrivals and departures','ATTENDANCE',['Date','Child ID','Room','Status','Sign in','Sign out'],[['31 Oct 2026','CHD-001','Sunflower','Present','8:15 AM','4:30 PM'],['31 Oct 2026','CHD-002','Willow','Present','8:30 AM','3:45 PM']], [('LOG THE DAY','Record the date, child ID, room, status, times and notes.'),('SEE THE PATTERN','Filter your register by date, room or attendance status.'),('PICKUP NOTES ONLY','The recorded name does not establish identity or authorization.')],'Always verify pickup identity and authorization independently.')),
('08-invoices-receipts',lambda:sheet_image('INVOICES & RECEIPTS','One clear ledger for family transactions','INVOICES & RECEIPTS',['Date','Family ID','Type','Amount','Effect'],[['01 Oct 2026','FAM-001','Invoice','$100.00','+$100.00'],['01 Oct 2026','FAM-001','Payment','$30.00','−$30.00']], [('RECORD ONE EVENT PER ROW','Enter invoices, payments, deposits, credits, write-offs and refunds.'),('AUTOMATIC BALANCE EFFECT','Charges and refunds increase the balance; payments and credits reduce it.'),('REVIEW YOUR ENTRIES','A review column flags incomplete rows, duplicate transaction IDs and family ID issues.')],'Enter tax manually in invoice amounts; reconcile with your accounting records.')),
('09-family-balance',balance_story),
('10-daily-care',lambda:sheet_image('DAILY CARE NOTES','A little structure for everyday updates','DAILY REPORTS',['Date','Child ID','Meals / snacks','Sleep / rest'],[['31 Oct 2026','CHD-001','Lunch and snack','Rested']], [('DAILY REPORTS','Record activities, mood and whether the update was shared with the family.'),('MEAL TRACKER','Log food served, meal and notes in a dedicated register.'),('MANUAL RECORDS','Nothing is sent automatically; follow your centre’s procedures.') ])),
('11-medical-incidents',lambda:sheet_image('CARE & INCIDENT NOTES','Keep working notes organized in one place','INCIDENT REPORTS',['Date','Child ID','Location','Parent notified'],[['31 Oct 2026','CHD-002','Play area','Yes']], [('ALLERGY & MEDICAL','Record a category, relevant notes and the location of the official action plan.'),('INCIDENT REPORTS','Document date, location, action, parent notification and follow-up.'),('SENSITIVE INFORMATION','Use appropriate access controls and your official safeguarding procedures.')],'These working notes do not replace medical or safeguarding records.')),
('12-staff-schedule',lambda:sheet_image('STAFF & SCHEDULES','Plan staffing records and shifts','STAFF SCHEDULE',['Date','Staff ID','Room','Start','End','Hours'],[['31 Oct 2026','STAFF-001','Sunflower','8:00 AM','4:00 PM','7.50']], [('STAFF DATABASE','Keep staff IDs, roles, contacts and hourly rates in one register.'),('PLANNED HOURS','Enter start, end and unpaid break minutes to calculate scheduled hours.'),('NOT A COVERAGE CHECK','Schedules do not verify actual supervision or live staffing ratios.')],'Independently verify actual staffing and local requirements.')),
('13-payroll',lambda:sheet_image('PAYROLL TRACKER','A simple cost worksheet for your records','PAYROLL TRACKER',['Staff ID','Regular hrs','OT hrs','Rate','Gross pay'],[['STAFF-001','8.00','0.00','$18.00','$144.00']], [('ENTER APPROVED HOURS','Record regular and overtime hours, hourly rate and overtime multiplier.'),('ADD EMPLOYER COSTS','Enter employer costs manually; the sheet adds these to gross pay.'),('REVIEW BEFORE PAYROLL','This is a planning record, not a payroll processing or tax service.') ])),
('14-classrooms',lambda:sheet_image('CLASSROOM PLANNING','Keep room reference details together','CLASSROOM MANAGEMENT',['Room','Age band','Capacity','Lead staff ID'],[['Sunflower','Preschool','20','STAFF-001'],['Willow','Toddler','12','STAFF-001']], [('ROOM REFERENCE','Record room, age band, capacity, lead staff ID and notes.'),('EDIT LOCAL PARAMETERS','Age-band and ratio values in Settings are reference examples only.'),('SUPERVISION COMES FIRST','This sheet does not calculate or certify real-time compliance.')],'Verify local rules and actual supervision independently.')),
('15-expenses-supplies',lambda:sheet_image('EXPENSES & SUPPLIES','Track operational spending and stock levels','SUPPLY INVENTORY',['Item','Category','On hand','Reorder level','Reorder?'],[['Paper towels','Cleaning','4','5','Reorder']], [('RECORD EXPENSES','Log dated expenses with category, vendor, amount and payment method.'),('WATCH STOCK LEVELS','Enter on-hand and reorder quantities for an automatic reminder.'),('AVOID DOUBLE-COUNTING','Do not enter payroll as an expense if it is also in Payroll Tracker.') ])),
('16-communication-documents',lambda:sheet_image('COMMUNICATION & DOCUMENTS','A manual follow-up record for your centre','DOCUMENT TRACKER',['Person ID','Document','Received','Expiry','Status'],[['CHD-001','Enrollment form','01 Oct 2026','—','No expiry']], [('PARENT COMMUNICATION','Log the channel, topic, summary, follow-up date and status.'),('DOCUMENT TRACKER','Record received and expiry dates; formula alerts indicate when a document is due.'),('MANUAL FOLLOW-UP','The workbook does not send messages or verify document requirements.') ])),
('17-monthly-annual',lambda:sheet_image('MONTHLY & ANNUAL REPORTS','Read back your entries by reporting year','MONTHLY REPORTS',['Month','Invoices','Net charges','Net cash','Costs'],[['Oct 2026','$300.00','$300.00','$70.00','$189.00']], [('MONTHLY SUMMARY','Review invoices, credits, write-offs, cash received and costs by month.'),('ANNUAL TOTALS','The annual report sums the months for the selected settings year.'),('MANAGEMENT SUMMARY ONLY','These reports are not a formal accrual profit-and-loss statement.') ])),
('18-how-to-use',howto)]

FILES={
'01-titles.txt': '''ETSY TITLE OPTIONS (choose one)\n\nDaycare Business Spreadsheet, Childcare Management Excel Template, Enrollment Attendance Tuition and Staff Tracker\n\nChildcare Management Spreadsheet, Daycare Enrollment and Attendance Tracker, Tuition Ledger and Staff Schedule Excel\n\nDaycare Excel Template, Childcare Business Organizer, Parent Database, Attendance, Invoices, Staff and Expense Tracker\n''',
'02-tags.txt': '''ETSY TAGS — 13 tags, each 20 characters or fewer\n\ndaycare spreadsheet\nchildcare template\ndaycare tracker\nchild care excel\ndaycare enrollment\nattendance tracker\nchildcare business\nchildcare planner\npreschool planner\ntu ition tracker\nparent database\ndaycare accounting\nstaff schedule\n'''.replace('tu ition','tuition'),
'03-description.txt': '''DAYCARE & CHILDCARE BUSINESS MANAGEMENT SPREADSHEET\n\nBring family records, attendance, tuition transactions, staff details and day-to-day business notes together in one Excel workbook. This 23-tab digital template is designed to help childcare providers organize their records, with a demo workbook to explore and a blank version to make your own.\n\nWHAT YOU RECEIVE\n• Daycare-Demo.xlsx — example records, dated October 2026\n• Daycare-Blank.xlsx — the same 23 tabs with empty registers\n• READ ME.txt — setup, transaction rules, capacity and important limitations\n\nWHAT YOU CAN ORGANIZE\n• Child enrollment, family contacts, waitlist and attendance\n• Fee references, invoices, payments, deposits, credits and refunds\n• Daily reports, meals, medical notes and incident working notes\n• Staff records, planned schedules and payroll cost entries\n• Room reference information, expenses and supply inventory\n• Parent communication log, documents, monthly and annual summaries\n\nHOW IT WORKS\nOpen the blank workbook in Microsoft Excel and save a copy. Edit Settings & Lists, create consistent family, child and staff IDs, then enter records in the white cells. Formula cells are shaded and locked to help avoid accidental changes. Use the ledger Review column and reconcile all transactions with your financial records.\n\nPLEASE NOTE BEFORE PURCHASE\nThis is a digital download; no physical product is shipped. Formulas are designed for Excel 2010-compatible functions, but opening without a repair message in Windows Excel has not yet been independently verified. Use Microsoft Excel desktop and confirm compatibility before relying on it. No macros, subscriptions, automated messages, payment processing or integrations are included.\n\nTax, tuition, discounts and employer payroll costs are entered manually. The report is a management summary, not an accounting or payroll service. Room and schedule records do not verify actual staffing coverage, ratios or regulatory compliance. Pickup names are notes, not authorization. Follow your own local, medical and safeguarding procedures.\n\nChild and family information is sensitive. Worksheet protection (password premium) is not encryption or access control; store your copy in an encrypted, access-controlled location. Prepared row capacities are listed in the included guide.\n''',
'04-key-features.txt': '''KEY FEATURES\n\n• 23 worksheets for day-to-day organization\n• Example and blank Excel workbooks plus guide\n• Family balances from one signed transaction ledger\n• Editable reference settings, age bands and sample ratios\n• Planned staff hours, entered payroll costs and spending logs\n• Monthly and annual transaction summaries\n• Filters, dropdowns, protected formulas and unlocked inputs\n• No macros, automated messages, payments or integrations\n\nNot a live ratio, pickup authorization, payroll or compliance system.\n''',
'05-faq.txt': '''FREQUENTLY ASKED QUESTIONS\n\nQ: What do I receive?\nA: A demo workbook, a blank workbook and a plain-text guide in a ZIP download.\n\nQ: What software do I need?\nA: Microsoft Excel desktop is the intended application. Formulas use Excel 2010-compatible functions, but the files have not yet been opened and tested in Windows Excel; verify before relying on them. Other apps are not tested.\n\nQ: Does it send messages or take payments?\nA: No. All communications and financial transactions are recorded manually.\n\nQ: Does it determine staffing compliance or authorize pickup?\nA: No. These are planning and note-taking records, not supervision, identity or authorization checks. Follow your local rules and procedures.\n\nQ: Are tax and payroll calculated automatically?\nA: No. Enter tax-inclusive invoice totals and employer payroll costs manually. Gross pay is calculated from entered hours and rates; verify all payroll calculations independently.\n\nQ: Are my records encrypted by the sheet password?\nA: No. Sheet protection helps prevent accidental formula edits. Store personal information in an encrypted, access-controlled location.\n\nQ: How many records fit?\nA: The guide lists capacities, including 150 children, 200 families, 2,000 attendance rows and 700 ledger rows. Formulas cover only the prepared ranges.\n''',
'06-how-to-use.txt': '''HOW TO USE\n\n1. Download and unzip your files. Open Daycare-Blank.xlsx in Excel desktop and save your own copy. Allow formulas to recalculate.\n2. Read Getting Started. Edit the centre name, reporting year and local reference settings.\n3. Add unique family, child and staff IDs consistently across registers.\n4. Enter each ledger event once using a positive amount and its appropriate transaction type. Resolve Review warnings and reconcile with other records.\n5. Add expenses, payroll costs, attendance, schedules and other records. Do not also record payroll as an expense or it will be counted twice in reports.\n6. Review Monthly Reports and Annual Reports. Keep sensitive records encrypted, access-controlled and backed up.\n\nSheet protection password: premium. It is not encryption.\n''',
'07-listing-attributes.txt': '''SUGGESTED LISTING DETAILS\n\nProduct type: Digital download\nFiles for customer: One ZIP containing two .xlsx files and one .txt guide\nIntended software: Microsoft Excel desktop\nWorksheets: 23 per workbook\nMacro-enabled: No (.xlsx)\nDelivery: Instant digital download; no physical item\nAuthor / brand: Novality Store\nCompatibility disclosure: Formula functions designed for Excel 2010+, Windows Excel opening not yet verified. Other software not tested.\n\nSeller: choose the most accurate Etsy category and attributes offered at publishing time. Confirm Etsy's current digital-file and listing-image rules before upload.\n''',
'08-keywords.txt': '''SEARCH PHRASES & AUDIENCE\n\ndaycare management spreadsheet; childcare business organizer; preschool record tracker; family balance ledger; enrollment and attendance Excel template; daycare staff schedule; childcare expense tracker; nursery administration workbook; parent communication log; daycare document tracker.\n\nPotential audience: daycare centres, home childcare providers, preschool administrators and small childcare businesses seeking a manual Excel organizer.\n\nAvoid claiming live ratio compliance, pickup authorization, medical record certification, automated payroll, encryption, integrations or compatibility beyond what has been tested.\n''',
}

def main():
    if KIT.exists(): shutil.rmtree(KIT)
    OUT.mkdir(parents=True); COPY.mkdir()
    for name,fn in PAGES:
        path=OUT/(name+'.jpg'); fn().save(path,'JPEG',quality=90,subsampling=0,optimize=True)
        print(path.name)
    for name,text in FILES.items(): (COPY/name).write_text(text,encoding='utf-8')
    titles=[x for x in FILES['01-titles.txt'].splitlines() if x and not x.startswith('ETSY')]
    tags=[x for x in FILES['02-tags.txt'].splitlines() if x and not x.startswith('ETSY')]
    assert len(titles)==3 and all(len(x)<=140 for x in titles),[(len(x),x) for x in titles]
    assert len(tags)==13 and all(len(x)<=20 for x in tags),[(len(x),x) for x in tags]
    shutil.copy2(DOWNLOAD/'daycare-business-spreadsheet.zip',KIT/'CUSTOMER-DOWNLOAD.zip')
    (KIT/'SELLER-START-HERE.txt').write_text('''DAYCARE ETSY LISTING KIT — FOR THE SELLER\n\n1. Review listing-copy and choose your title and tags.\n2. Select the listing images you want to upload; the 18 square images are alternatives for your listing, not the customer download. Their spreadsheet views are illustrative, not literal screenshots.\n3. Upload CUSTOMER-DOWNLOAD.zip as your digital product file. It contains the demo workbook, blank workbook and guide. Do not upload this whole listing kit as the buyer product.\n4. Before selling, test the files in Windows Excel, especially for repair messages, and confirm all listing claims and Etsy rules. The copy discloses that this test is outstanding.\n5. The photo backgrounds are AI-generated; all visible lettering and illustrations were typeset separately.\n''',encoding='utf-8')
    out=DOWNLOAD/'daycare-business-etsy-kit.zip'
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(KIT.rglob('*')):
            if p.is_file(): z.write(p,p.relative_to(KIT))
    print('Wrote',out)
    # Contact sheets are developer QA artifacts, kept outside the deliverable.
    imgs=[Image.open(OUT/(n+'.jpg')).resize((400,400)) for n,_ in PAGES]
    for i in range(3):
        sheet=Image.new('RGB',(1200,800),'white')
        for j,im in enumerate(imgs[i*6:(i+1)*6]): sheet.paste(im,((j%3)*400,(j//3)*400))
        sheet.save(ROOT/'etsy'/f'qa-{i+1}.jpg',quality=90)
if __name__=='__main__': main()
