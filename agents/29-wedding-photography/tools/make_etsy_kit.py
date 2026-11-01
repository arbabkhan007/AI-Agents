"""Build a seller-ready Etsy kit. Backgrounds are AI images; typography is Pillow-rendered."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import shutil, zipfile

ROOT=Path(__file__).resolve().parent.parent
ASSETS=ROOT/'etsy/assets'; KIT=ROOT/'etsy/kit'; OUT=KIT/'listing-images'; COPY=KIT/'listing-copy'; DL=ROOT/'download'; S=2000
FONTS=Path('/usr/share/fonts/truetype/dejavu')
INK='#3d302b'; DARK='#4a352e'; ROSE='#a65e72'; SAGE='#7d8970'; GOLD='#b99777'; CREAM='#faf6f1'; WHITE='#fffcf9'; MUTE='#786b64'; BLUSH='#f3e5e3'; LINE='#e7dad1'; GREEN='#eaf0e7'
def font(size,style='sans'):
 return ImageFont.truetype(str(FONTS/{'sans':'DejaVuSans.ttf','bold':'DejaVuSans-Bold.ttf','serif':'DejaVuSerif.ttf','serifbold':'DejaVuSerif-Bold.ttf'}[style]),size)
def fit(d,t,size,w,style='sans',minimum=23):
 while size>minimum and d.textlength(t,font=font(size,style))>w:size-=1
 assert d.textlength(t,font=font(size,style))<=w,(t,w)
 return font(size,style)
def text(d,x,y,t,size=40,fill=INK,style='sans',w=1700):
 d.text((x,y),t,font=fit(d,t,size,w,style),fill=fill)
def center(d,y,t,size=40,fill=INK,style='sans',w=1700):
 f=fit(d,t,size,w,style);d.text(((S-d.textlength(t,font=f))/2,y),t,font=f,fill=fill)
def wrap(d,t,f,w):
 lines=[];line=''
 for word in t.split():
  n=(line+' '+word).strip()
  if d.textlength(n,font=f)<=w:line=n
  else:
   assert line,(word,w);lines.append(line);line=word
 if line:lines.append(line)
 return lines
def card(d,xy,fill=WHITE,outline=LINE,r=22):d.rounded_rectangle(xy,r,fill=fill,outline=outline,width=2)
def shadow(d,xy,r=28):
 x,y,X,Y=xy;d.rounded_rectangle((x+12,y+16,X+12,Y+16),r,fill='#ddcfc8');card(d,xy,r=r)
def photo(file):return ImageOps.fit(Image.open(ASSETS/file).convert('RGB'),(S,S),method=Image.Resampling.LANCZOS)
def pill(d,x,y,label,fill=BLUSH,color=ROSE):
 f=font(28,'bold');w=int(d.textlength(label,font=f))+54;d.rounded_rectangle((x,y,x+w,y+60),30,fill=fill);d.text((x+27,y+14),label,font=f,fill=color)
def footer(d):
 d.line((125,1860,1875,1860),fill=LINE,width=2);text(d,130,1883,'NOVALITY STORE',25,MUTE,'bold');f=font(25);t='DIGITAL EXCEL WORKBOOK';d.text((1870-d.textlength(t,font=f),1883),t,font=f,fill=MUTE)
def top(d,eyebrow,title,sub):
 text(d,130,90,eyebrow,28,ROSE,'bold');text(d,125,145,title,79,DARK,'serif',1740);text(d,130,270,sub,37,MUTE,'sans',1740);d.line((130,340,1870,340),fill=LINE,width=3)
def badge(d,x,y,n,label):
 d.ellipse((x,y,x+76,y+76),fill=BLUSH);f=font(30,'bold');d.text((x+23,y+20),n,font=f,fill=ROSE);text(d,x+104,y+17,label,35,INK,'bold',680)
def cover():
 im=photo('linen-details.png');d=ImageDraw.Draw(im)
 shadow(d,(125,115,1635,1055),35)
 text(d,200,172,'NOVALITY STORE  /  BUSINESS COLLECTION',28,ROSE,'bold',1330)
 text(d,190,250,'Wedding Photographer',90,DARK,'serif',1360)
 text(d,190,370,'Business Manager',100,DARK,'serif',1370)
 d.line((198,532,1470,532),fill=GOLD,width=3)
 text(d,198,575,'A thoughtful Excel workbook',48,INK,'sans',1200)
 text(d,198,650,'for the work behind every wedding.',48,INK,'sans',1300)
 pill(d,198,770,'23 WORKSHEETS');pill(d,670,770,'DEMO + BLANK',GREEN,SAGE)
 text(d,198,918,'DIGITAL DOWNLOAD  •  MANUAL ENTRY',30,MUTE,'bold',1260)
 shadow(d,(315,1160,1760,1725),25)
 d.rectangle((355,1210,1720,1280),fill=DARK)
 text(d,386,1228,'WEDDING BUSINESS  /  OVERVIEW',27,WHITE,'bold',1250)
 for i,(a,b) in enumerate([('CLIENTS','Connections'),('BOOKINGS','Your dates'),('WORKFLOW','The details')]):
  x=355+i*453;card(d,(x,1310,x+423,1475),CREAM,LINE,12);text(d,x+25,1330,a,23,ROSE,'bold',370);text(d,x+25,1390,b,35,DARK,'serif',370)
 text(d,390,1530,'From first enquiry to final gallery',40,DARK,'serif',1180)
 text(d,390,1630,'Illustrative preview  •  Not a workbook screenshot',25,MUTE,'sans',1200)
 return im
def included():
 im=photo('wedding-details.png');d=ImageDraw.Draw(im);shadow(d,(105,120,1895,1790),34)
 center(d,178,'WHAT IS INCLUDED',32,ROSE,'bold');center(d,245,'Your complete workbook set',81,DARK,'serif');center(d,365,'Thoughtful tools for a creative business',37,MUTE)
 entries=[('01','DEMO WORKBOOK','Explore a filled example with fictional records.'),('02','BLANK WORKBOOK','Start fresh with prepared rows and editable settings.'),('03','SETUP GUIDE','Read the workflow, assumptions and important limits.')]
 for i,(n,h,b) in enumerate(entries):
  y=490+i*260;card(d,(175,y,1825,y+215),CREAM,LINE,20);badge(d,220,y+36,n,h);text(d,325,y+110,b,35,MUTE,'sans',1380)
 card(d,(175,1310,1825,1625),BLUSH,BLUSH,20)
 center(d,1375,'A DIGITAL PRODUCT FOR EXCEL DESKTOP',42,DARK,'bold');center(d,1455,'No physical item  •  No macros  •  Manual entry',36,MUTE)
 center(d,1530,'Opening and recalculation in Windows Excel are unverified.',29,MUTE,'sans',1550)
 center(d,1690,'NOVALITY STORE',26,ROSE,'bold');return im
def sheetmap():
 im=Image.new('RGB',(S,S),CREAM);d=ImageDraw.Draw(im);top(d,'THE WORKBOOK','23 worksheets, one workflow','Designed to keep wedding business details together')
 groups=[('01  BEGIN','Dashboard  ·  Getting Started  ·  Settings & Lists'),('02  ATTRACT','Client CRM  ·  Lead Tracker  ·  Marketing Calendar'),('03  BOOK','Booking Calendar  ·  Wedding Bookings  ·  Packages & Pricing'),('04  PREPARE','Contracts & Documents  ·  Payments & Invoices  ·  Client Questionnaire'),('05  PHOTOGRAPH','Wedding Timeline  ·  Shot List Manager  ·  Photographer & Staff'),('06  DELIVER','Editing Workflow  ·  Gallery & Delivery  ·  Reviews & Referrals'),('07  RUN THE BUSINESS','Equipment Inventory  ·  Travel & Mileage  ·  Expense Tracker  ·  Profit Analysis  ·  Monthly & Annual Reports')]
 for i,(a,b) in enumerate(groups):
  y=390+i*200;card(d,(130,y,1870,y+172),WHITE,LINE,16);text(d,165,y+23,a,30,ROSE,'bold',1580)
  lines=wrap(d,b,font(32),1600);assert len(lines)<=2
  for j,line in enumerate(lines):text(d,165,y+80+j*42,line,32,INK,'sans',1600)
 footer(d);return im

def feature(eyebrow,title,sub,tabletitle,headers,rows,benefits,note):
 im=Image.new('RGB',(S,S),CREAM);d=ImageDraw.Draw(im);top(d,eyebrow,title,sub)
 shadow(d,(130,385,1870,1035),26)
 text(d,170,424,tabletitle,39,DARK,'serif',1550);text(d,170,485,'ILLUSTRATIVE SELECTED FIELDS  /  NOT A SCREENSHOT',24,MUTE,'bold',1600)
 x=170;y=545;w=1660;d.rounded_rectangle((x,y,x+w,y+76),12,fill=DARK)
 widths=[w/len(headers)]*len(headers)
 for i,h in enumerate(headers):text(d,int(x+20+sum(widths[:i])),y+22,h,27,WHITE,'bold',int(widths[i]-30))
 for j,row in enumerate(rows):
  yy=y+76+j*83;d.rectangle((x,yy,x+w,yy+83),fill=WHITE if j%2==0 else '#f9f2ef',outline=LINE,width=1)
  assert len(row)==len(headers)
  for i,v in enumerate(row):text(d,int(x+20+sum(widths[:i])),yy+24,str(v),29,INK,'sans',int(widths[i]-32))
 text(d,170,940,note,26,MUTE,'sans',1600)
 for i,(h,b) in enumerate(benefits):
  yy=1100+i*220;card(d,(130,yy,1870,yy+185),WHITE,LINE,18)
  d.rounded_rectangle((158,yy+27,165,yy+158),4,fill=GOLD)
  text(d,200,yy+23,h,36,DARK,'bold',1580)
  lines=wrap(d,b,font(33),1570);assert len(lines)<=2,(h,lines)
  for j,line in enumerate(lines):text(d,200,yy+83+j*44,line,33,MUTE,'sans',1570)
 footer(d);return im

def overview():
 im=Image.new('RGB',(S,S),CREAM);d=ImageDraw.Draw(im);top(d,'YOUR STUDIO AT A GLANCE','A clearer overview','Review the records and reminders you enter')
 tiles=[('ENQUIRIES','Follow the journey'),('WEDDINGS','See upcoming dates'),('CONTRACTS','Review status'),('PAYMENTS','Watch what is owed'),('DELIVERY','Track the workflow'),('EXPENSES','Review business costs')]
 for i,(a,b) in enumerate(tiles):
  x=130+i%2*885;y=405+i//2*300;card(d,(x,y,x+850,y+260),WHITE,LINE,24);d.rounded_rectangle((x+35,y+37,x+47,y+215),6,fill=GOLD)
  text(d,x+80,y+52,a,30,ROSE,'bold',720);text(d,x+80,y+120,b,46,DARK,'serif',715)
 card(d,(130,1385,1870,1745),BLUSH,BLUSH,26);text(d,180,1440,'A view built from your entries',53,DARK,'serif',1550)
 for i,line in enumerate(['Track booked work, upcoming tasks and money in one place.', 'Review the selected year and underlying records before making decisions.']):text(d,180,1535+i*63,line,34,MUTE,'sans',1570)
 footer(d);return im

def important():
 im=photo('linen-details.png');d=ImageDraw.Draw(im);shadow(d,(100,95,1900,1835),35)
 center(d,155,'BEFORE YOU PURCHASE',31,ROSE,'bold');center(d,220,'A few important details',78,DARK,'serif')
 info=[('01','EXCEL DESKTOP','Intended for Microsoft Excel; Windows opening and recalculation are unverified.'),('02','MANUAL ORGANIZER','No calendar, email or bank sync; no payment collection or contract signing.'),('03','KEEP IDS IN PLACE','Filter rows; do not sort, move, insert or delete populated register rows.'),('04','FIXED PREPARED RANGES','200 booking rows by default. Package price changes can affect older bookings.'),('05','PROTECT YOUR DATA','Sheet password is premium; protection is not encryption. Back up your files.')]
 for i,(n,h,b) in enumerate(info):
  y=360+i*230;card(d,(165,y,1835,y+202),CREAM,LINE,17);badge(d,205,y+26,n,h)
  lines=wrap(d,b,font(31),1410);assert len(lines)<=2
  for j,line in enumerate(lines):text(d,310,y+92+j*42,line,31,MUTE,'sans',1410)
 center(d,1595,'Test a copy before relying on the workbook.',35,DARK,'bold');center(d,1675,'Not legal, tax or accounting advice.',31,MUTE)
 center(d,1750,'NOVALITY STORE  /  DIGITAL DOWNLOAD',25,ROSE,'bold');return im

PAGES=[
('01-cover',cover),('02-whats-included',included),('03-worksheet-map',sheetmap),('04-dashboard',overview),
('05-leads-and-clients',lambda:feature('FROM ENQUIRY TO RELATIONSHIP','Leads & client CRM','A considered space for enquiries and couple details','LEAD TRACKER',['Enquiry','Source','Status','Follow-up'],[['Avery & Sam','Referral','Contacted','12 Nov'],['Mia & Noah','Website','Proposal sent','18 Nov']], [('FOLLOW EACH ENQUIRY','Record source, status, consultation and follow-up details.'),('KEEP CLIENT NOTES','Store relevant contact and wedding details in Client CRM.'),('REVIEW THE FUNNEL','See which enquiries are open, booked or lost from the information entered.')],'Fictional example  •  Enter updates manually')),
('06-booking-calendar',lambda:feature('A VIEW OF THE DIARY','Booking calendar','Review wedding dates and manually entered clashes','WEDDING BOOKINGS',['Booking','Wedding date','Status','Date clash'],[['WED-0001','20 Jun 2027','Confirmed','No'],['WED-0002','04 Sep 2027','Pencilled in','No']],[('KEEP THE DATE VISIBLE','Record bookings and review the calendar using your own entries.'),('SPOT CONFLICTS','Date and photographer clash flags compare records in the workbook.'),('CHECK LIVE AVAILABILITY','There is no calendar sync; verify your actual diary independently.')],'Fictional example  •  No live calendar connection')),
('07-wedding-bookings',lambda:feature('THE HEART OF THE WORKBOOK','Wedding bookings','Connect the details that belong to each wedding','WEDDING BOOKINGS',['Booking ID','Client ID','Package','Status'],[['WED-0001','CLT-0001','Classic','Confirmed'],['WED-0002','CLT-0002','Premium','Pencilled in']],[('LINK THE DETAILS','Use the generated Booking ID on related register rows.'),('SEE WHAT NEEDS ATTENTION','Review contract, payment and delivery indicators from entered data.'),('KEEP IDENTIFIERS STABLE','Filter instead of sorting or moving populated rows.')],'Illustrative fields  •  IDs depend on row position')),
('08-packages-pricing',lambda:feature('MAKE YOUR OFFER CLEAR','Packages & pricing','Organize your services and pricing assumptions','PACKAGES & PRICING',['Package','Hours','List price','Still selling'],[['Classic','8','$1,800','Yes'],['Premium','10','$2,500','Yes']],[('BUILD YOUR PACKAGES','Enter inclusions, coverage, prices and cost assumptions.'),('COMPARE THE NUMBERS','Review calculated price, estimated costs and margin.'),('PRESERVE HISTORIC PRICING','Create a new package name for new prices; changes affect linked bookings.')],'Illustrative example  •  The blank workbook needs your packages')),
('09-contracts-questionnaire',lambda:feature('PREPARE WITH CONFIDENCE','Paperwork & planning','Record the details you have sent and received','CONTRACTS & DOCUMENTS',['Booking','Document','Status','Stored at'],[['WED-0001','Wedding contract','Sent','Studio folder'],['WED-0001','Model release','Signed','Studio folder']],[('TRACK DOCUMENT STATUS','Record dates, status and where you keep your files.'),('PREPARE THE DETAILS','Use the questionnaire view for recorded wedding information.'),('YOUR OWN DOCUMENTS','This workbook does not create, send or sign contracts.')],'Illustrative example  •  Not legal advice')),
('10-payments',lambda:feature('FOLLOW THE MONEY','Payments & invoices','Keep a manual record of amounts due and received','PAYMENTS & INVOICES',['Booking','Stage','Amount due','Received'],[['WED-0001','Booking deposit','$540','$540'],['WED-0001','Final payment','$1,260','—']],[('RECORD EACH INSTALMENT','Enter due dates, amounts, receipts and processing fees.'),('SEE WHAT IS STILL DUE','Review calculated balances and late-payment flags.'),('REFUNDS ARE NEGATIVE','Record refunds as negative amounts; no payments are processed here.')],'Fictional example  •  Manual entries only')),
('11-wedding-timeline',lambda:feature('BE READY FOR THE DAY','Wedding timeline','Bring the moments and people into one running order','WEDDING TIMELINE',['Booking','Moment','Start','Who'],[['WED-0001','Getting ready','10:00','Lead photographer'],['WED-0001','Ceremony','14:00','Lead photographer']],[('ORGANIZE THE DAY','Record events, times, locations and who covers them.'),('WORK FROM CEREMONY TIME','Prepared timing helpers reference the booking details.'),('REVIEW WITH YOUR TEAM','Update the plan manually as the wedding schedule changes.')],'Illustrative example  •  Enter timeline rows for each wedding')),
('12-shot-list',lambda:feature('CAPTURE WHAT MATTERS','Shot list manager','A practical place for the moments not to miss','SHOT LIST MANAGER',['Booking','Shot','Must-have','Status'],[['WED-0001','Family portraits','Yes','To do'],['WED-0001','Venue details','No','To do']],[('LIST IMPORTANT SHOTS','Organize shots by wedding, group and priority.'),('NOTE PEOPLE & DETAILS','Capture practical information for each photo.'),('MARK THE OUTCOME','Update shot status as work progresses; review missed must-haves.')],'Illustrative example  •  No photos are stored in the workbook')),
('13-team-editing',lambda:feature('A SMOOTHER WORKFLOW','Team & editing','Keep people and post-production details together','EDITING WORKFLOW',['Booking','Stage','Hours','Due'],[['WED-0001','Editing','12','18 Jul'],['WED-0002','Culling','4','02 Oct']],[('MANAGE YOUR TEAM','Record photographer and staff details, roles and rates.'),('TRACK POST-PRODUCTION','Enter editing stage, hours and delivery-related dates.'),('RECORD ACTUAL COSTS','Operational estimates do not automatically become expense entries.')],'Illustrative example  •  Update progress manually')),
('14-gallery-reviews',lambda:feature('AFTER THE WEDDING','Gallery & reviews','Track delivery, after-sales and client feedback','GALLERY & DELIVERY',['Booking','Status','Print sales','Review'],[['WED-0001','Delivered','$100','Yes'],['WED-0002','Not created','—','No']],[('RECORD THE DELIVERY','Track the gallery link, delivery, expiry and archive status.'),('CAPTURE AFTER-SALES','Enter print and other extra sales separately from booking add-ons.'),('REVIEW & REFERRALS','Record requests, received reviews and referral details manually.')],'Illustrative example  •  The workbook does not host galleries')),
('15-equipment-travel',lambda:feature('ON THE PRACTICAL SIDE','Equipment & travel','Track your gear and wedding-day journeys','TRAVEL & MILEAGE',['Booking','Destination','Miles','Purpose'],[['WED-0001','Wedding venue','42','Wedding day'],['WED-0002','Photo location','25','Venue visit']],[('KEEP A KIT INVENTORY','Record equipment details, purchase information and status.'),('RECORD EACH JOURNEY','Track mileage and travel details by Booking ID.'),('ENTER COSTS SEPARATELY','Travel estimates do not automatically become actual expenses.')],'Fictional example  •  Mileage settings are editable')),
('16-marketing',lambda:feature('FIND THE RIGHT CLIENTS','Marketing calendar','Record what you share and where enquiries come from','MARKETING CALENDAR',['Campaign','Platform','Status','Spend'],[['MKT-0001','Instagram','Published','$25'],['MKT-0002','Website','Scheduled','$0']],[('PLAN YOUR CONTENT','Keep campaign and publication information organized.'),('FOLLOW THE SOURCE','Record lead sources and link campaigns where appropriate.'),('REVIEW YOUR ACTIVITY','Results depend on what you enter; no platforms are connected.')],'Fictional example  •  No automatic posting or analytics sync')),
('17-expenses-profit',lambda:feature('KNOW YOUR NUMBERS','Expenses & profit','Review entered costs alongside your bookings','EXPENSE TRACKER',['Category','Booking','Amount','Business use'],[['Second shooters','WED-0001','$400','100%'],['Insurance','—','$200','100%']],[('RECORD COSTS ONCE','Enter actual expenses and link wedding costs to a Booking ID.'),('ANALYZE A WEDDING','Add a Profit Analysis row per booking to review revenue and cost.'),('UNDERSTAND THE LIMITS','Management figures use assumptions and are not tax or accounting advice.')],'Fictional example  •  Review the guide for profit conventions')),
('18-important-details',important)]
FILES={
'01-titles.txt':'''ETSY TITLE OPTIONS — choose one

Wedding Photographer Spreadsheet, Photography Business Manager Excel Template, Booking Tracker, Client CRM and Workflow

Wedding Photography Business Spreadsheet, Client Booking Calendar, Payments and Shot List Excel Organizer

Photographer Business Manager Excel Template, Wedding Client Tracker, Pricing, Timeline and Profit Spreadsheet
''',
'02-tags.txt':'''ETSY TAGS — 13 suggestions, maximum 20 characters each

wedding photographer
photography business
photographer planner
wedding photo crm
photography tracker
booking spreadsheet
wedding workflow
client crm template
photo business excel
wedding shot list
photography pricing
photo invoice log
photography planner
''',
'03-description.txt':'''WEDDING PHOTOGRAPHER BUSINESS MANAGER — EXCEL WORKBOOK

From the first enquiry to the final gallery, keep the details of your wedding photography business organized in one thoughtfully designed manual Excel workbook. Explore the fictional demo first, then use the blank version for your own records.

WHAT YOU RECEIVE
• Demo .xlsx workbook with fictional example records
• Blank .xlsx workbook with the same 23 worksheets and empty registers
• README guide covering setup, capacity and important limitations
• Digital download only — no physical item will be shipped

WHAT YOU CAN ORGANIZE
• Leads, client details, packages, bookings and a booking calendar
• Contract and questionnaire tracking, payment entries and invoice balances
• Wedding-day timelines, shot lists, team information and editing progress
• Gallery delivery, reviews and referrals, equipment, travel and marketing
• Expenses, booking-level profit analysis, dashboard and monthly/annual reports

HOW IT WORKS
Open the blank workbook in Microsoft Excel desktop, save your own copy and allow formulas to recalculate. Review Settings & Lists, enter your packages and clients, then add bookings. Use each generated Booking ID on related records. Enter progress, payments, sales and expenses manually; review the dashboard and reports against the underlying records.

IMPORTANT BEFORE PURCHASE
This is a manual organizer. It does not sync with your calendar, email, bank or payment provider; take payments; host galleries; or generate, send or execute contracts. It does not replace professional legal, tax or accounting advice.

Designed using Excel 2010-compatible functions for Excel desktop. Opening, repair-free behavior and recalculation in Windows Excel have not been verified. Test a copy in your Excel version before relying on it; other spreadsheet applications are untested. Formula values need recalculation when opened.

IDs are based on row position: do not sort, move, insert or delete populated register rows, or change ID prefixes after use. Filter instead. Do not clear a trigger field on a referenced row. The standard workbook has 200 wedding bookings, 300 clients and 400 leads; other registers also have fixed prepared ranges. See the guide for details.

Package prices and shared settings are live lookups, so changes may affect past bookings. Create a new package name for new prices and retain historical package rows. Enter actual costs once on Expense Tracker; operational team, editing and travel estimates do not automatically become expenses. Gallery after-sales can be included in Profit Analysis but omitted from booking-based annual totals. Check the guide and reconcile your figures.

Sheets are protected with password premium; formula cells are locked and prepared inputs are unlocked. Sheet protection is not encryption. Store sensitive information securely and keep backups.

Listing image tables are illustrative designs, not screenshots of the workbook.
''',
'04-key-features.txt':'''KEY FEATURES

• 23 worksheets in a demo and a blank Excel workbook
• Lead, client, booking and calendar records
• Editable packages and pricing assumptions
• Contract status, questionnaire and payment tracking
• Wedding timeline, shot list, staff and editing workflow
• Gallery, reviews, equipment, travel and marketing records
• Expense tracker, profit analysis and management reports
• 200 booking rows, 300 clients and 400 leads by default
• Protected formulas and unlocked prepared inputs
• Manual entry; no macros or external integrations

Intended for Excel desktop. Windows Excel opening and recalculation have not been verified. See the README for assumptions and operating limits.
''',
'05-faq.txt':'''FREQUENTLY ASKED QUESTIONS

Q: What files will I receive?
A: A ZIP containing a demo workbook, a blank workbook and a README guide. There is no physical product.

Q: What software is needed?
A: The files are intended for Microsoft Excel desktop. Opening, repair-free behavior and recalculation in Windows Excel have not been verified. Test a copy in your version before relying on the workbooks. Other spreadsheet applications are untested.

Q: Does this sync with Google Calendar, a bank or my gallery provider?
A: No. The workbook is a manual organizer and does not connect to external services, host galleries, send reminders or take payments.

Q: Does it create or sign contracts?
A: No. It records the document status and where you store it. Use your own documents and seek appropriate legal advice.

Q: How many weddings can I enter?
A: The standard workbook has 200 prepared wedding booking rows, 300 client rows and 400 lead rows. Other registers have their own fixed capacities. Do not enter records beyond the prepared range.

Q: Can I sort my records?
A: Do not sort, move, insert or delete populated register rows. Generated IDs depend on row position. Use filters instead and do not clear a referenced row's trigger field.

Q: Can I change a package price?
A: Yes, but prices are live lookups and the change can affect historical booking figures. Preserve the old package and create a new name for new prices.

Q: Is the spreadsheet a tax or accounting system?
A: No. Profit reports use management assumptions and can differ in timing or treatment. The guide explains the conventions; reconcile your figures and consult a qualified professional.

Q: Is my client data encrypted?
A: No. Sheet protection password premium helps prevent accidental edits but does not encrypt the file. Use secure, access-controlled storage and backups.
''',
'06-how-to-use.txt':'''HOW TO USE

1. Download and unzip CUSTOMER-DOWNLOAD.zip. Open the blank workbook in Excel desktop and save a working copy. Allow it to recalculate.
2. Read the README and Getting Started. Update studio details, reporting year, currency, tax assumptions, rates, targets and lists.
3. Enter packages, clients and leads, then add weddings in Wedding Bookings. Use generated Booking IDs in related tabs.
4. Enter contract and payment status, timeline and shot details, editing, delivery and other updates manually. Use the workbook to review your own recorded information.
5. Record actual wedding expenses once against the correct Booking ID and add one Profit Analysis row per booking to analyze. Processing fees entered in Payments should not be duplicated in Expense Tracker.
6. Review the chosen year, differences in reporting scope and the guide's profit assumptions. Reconcile figures with your records.

Filter rather than sort, move, insert or delete populated register rows. Keep historical package names and avoid changing ID prefixes after use. Password: premium. Sheet protection is not encryption.
''',
'07-listing-attributes.txt':'''SUGGESTED LISTING DETAILS

Product type: Digital download
Buyer file: One ZIP with a demo .xlsx, blank .xlsx and README guide
Intended application: Microsoft Excel desktop
Worksheets: 23 per workbook
Default capacity: 200 wedding bookings, 300 clients, 400 leads
Macros: None (.xlsx)
Delivery: Digital only; no physical product
Brand: Novality Store
Compatibility disclosure: Designed with Excel 2010-compatible functions. Windows Excel opening, repair-free behavior and recalculation are unverified; other spreadsheet applications are untested.

Choose the Etsy category and available attributes that best match your listing. Confirm Etsy's current digital-file and image specifications before publication. Listing artwork is illustrative, not literal screenshots.
''',
'08-keywords.txt':'''SEARCH PHRASES & AUDIENCE

wedding photographer spreadsheet; photography business manager; photographer client tracker; wedding booking spreadsheet; photography CRM Excel; wedding timeline organizer; wedding shot list template; photography package pricing; photography expense tracker; wedding photographer profit spreadsheet.

Potential audience: independent wedding photographers and small photography studios who want a manual Excel organizer.

Do not claim real-time sync, automatic contract generation or signing, automatic payment processing, verified Windows Excel compatibility, encryption, accounting certification, tax compliance, guaranteed earnings or automatic customer communications.
'''
}
def main():
 if KIT.exists():shutil.rmtree(KIT)
 OUT.mkdir(parents=True);COPY.mkdir()
 for name,fn in PAGES:
  image=fn();image.save(OUT/(name+'.jpg'),'JPEG',quality=91,subsampling=0,optimize=True);print(name,flush=True)
 for name,body in FILES.items():(COPY/name).write_text(body,encoding='utf-8')
 titles=[x for x in FILES['01-titles.txt'].splitlines() if x and not x.startswith('ETSY')];tags=[x for x in FILES['02-tags.txt'].splitlines() if x and not x.startswith('ETSY')]
 assert len(titles)==3 and all(len(x)<=140 for x in titles),[(len(x),x) for x in titles]
 assert len(tags)==13 and all(len(x)<=20 for x in tags) and len(set(tags))==13,[(len(x),x) for x in tags]
 shutil.copy2(DL/'wedding-photographer-business-manager.zip',KIT/'CUSTOMER-DOWNLOAD.zip')
 (KIT/'SELLER-START-HERE.txt').write_text('''WEDDING PHOTOGRAPHER ETSY LISTING KIT — FOR THE SELLER

1. Choose one title and the 13 tags from listing-copy. Review the description, FAQ and attributes against the actual workbook before publishing.
2. Select listing images from the 18 square JPEGs in listing-images. The styled tables are illustrative and not workbook screenshots. Check Etsy's current image requirements at upload time.
3. Upload CUSTOMER-DOWNLOAD.zip as the buyer's digital file, not this whole seller kit. It is an unchanged copy of the workbook package: demo, blank and README. The source generator is a separate optional download and is not in the customer ZIP.
4. Test the customer workbooks in Windows Excel for opening, repair messages and recalculation before selling. That test has not been performed. Keep compatibility disclosures until verified.
5. Keep the manual-only, row-based ID, fixed range, historical pricing, data privacy and financial limitations clear to buyers. The tool is not a calendar integration, contract platform or accounting service.
6. Backgrounds were AI-generated; all visible listing typography and illustrative tables were drawn separately. Do not represent the illustrations as screenshots.
''',encoding='utf-8')
 out=DL/'wedding-photographer-etsy-listing-kit.zip'
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
  for p in sorted(KIT.rglob('*')):
   if p.is_file():z.write(p,p.relative_to(KIT))
 for part in range(3):
  sheet=Image.new('RGB',(1500,1000),'white')
  for i,(name,_) in enumerate(PAGES[part*6:part*6+6]):
   im=Image.open(OUT/(name+'.jpg')).resize((500,500));sheet.paste(im,((i%3)*500,(i//3)*500))
  sheet.save(ROOT/'etsy'/f'qa-{part+1}.jpg',quality=90)
 print('Saved',out, out.stat().st_size)
if __name__=='__main__':main()
