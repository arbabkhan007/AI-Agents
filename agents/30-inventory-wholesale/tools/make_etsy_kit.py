"""Create a listing kit: AI-generated text-free photos, Pillow-rendered text."""
from pathlib import Path
import shutil, zipfile
from PIL import Image, ImageDraw, ImageFont, ImageOps
R=Path(__file__).resolve().parent.parent
AS=R/'etsy/assets'; KIT=R/'etsy/kit'; OUT=KIT/'listing-images'; COPY=KIT/'listing-copy'; DL=R/'download'; S=2000
FONTS=Path('/usr/share/fonts/truetype/dejavu')
DARK='#25433d'; INK='#293a36'; TEAL='#4c7164'; COPPER='#b67f60'; CREAM='#f6f5ef'; WHITE='#fffefb'; MUTE='#5f6d67'; LINE='#dce4da'; SAGE='#e5ede5'; SAND='#f2e8dd';
def font(size,style='sans'):
 return ImageFont.truetype(str(FONTS/{'sans':'DejaVuSans.ttf','bold':'DejaVuSans-Bold.ttf','serif':'DejaVuSerif.ttf','serifbold':'DejaVuSerif-Bold.ttf'}[style]),size)
def fit(d,t,size,w,style='sans',minimum=24):
 while size>minimum and d.textlength(t,font=font(size,style))>w:size-=1
 assert d.textlength(t,font=font(size,style))<=w,(t,w,size)
 return font(size,style)
def text(d,x,y,t,size=40,fill=INK,style='sans',w=1700):d.text((x,y),t,font=fit(d,t,size,w,style),fill=fill)
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
def shadow(d,xy,r=26):
 x,y,X,Y=xy;d.rounded_rectangle((x+12,y+15,X+12,Y+15),r,fill='#d5d8cb');card(d,xy,r=r)
def photo(file):return ImageOps.fit(Image.open(AS/file).convert('RGB'),(S,S),method=Image.Resampling.LANCZOS)
def pill(d,x,y,label,fill=SAGE,color=TEAL):
 f=font(29,'bold');w=int(d.textlength(label,font=f))+58;d.rounded_rectangle((x,y,x+w,y+64),32,fill=fill);d.text((x+29,y+15),label,font=f,fill=color)
def footer(d):
 d.line((125,1860,1875,1860),fill=LINE,width=2);text(d,130,1882,'NOVALITY STORE',25,MUTE,'bold');f=font(25);t='DIGITAL EXCEL WORKBOOK';d.text((1870-d.textlength(t,font=f),1882),t,font=f,fill=MUTE)
def top(d,eyebrow,title,sub):
 text(d,130,78,eyebrow,30,COPPER,'bold');text(d,125,145,title,81,DARK,'serif',1740);text(d,130,270,sub,39,MUTE,'sans',1740);d.line((130,340,1870,340),fill=LINE,width=3)
def badge(d,x,y,n,label):
 d.ellipse((x,y,x+76,y+76),fill=SAGE);f=font(30,'bold');d.text((x+22,y+20),n,font=f,fill=TEAL);text(d,x+104,y+16,label,35,INK,'bold',1410)
def cover():
 im=photo('inventory-desk.png');d=ImageDraw.Draw(im);shadow(d,(110,115,1715,1030),35)
 text(d,180,170,'NOVALITY STORE  /  BUSINESS COLLECTION',28,COPPER,'bold',1400)
 text(d,172,255,'Inventory &',110,DARK,'serif',1420)
 text(d,172,393,'Wholesale Manager',100,DARK,'serif',1420)
 d.line((180,550,1535,550),fill=COPPER,width=3)
 text(d,180,588,'Keep stock, sales and orders',51,INK,'sans',1400)
 text(d,180,660,'in one considered workspace.',51,INK,'sans',1400)
 pill(d,180,780,'23 WORKSHEETS');pill(d,700,780,'DEMO + BLANK',SAND,COPPER)
 text(d,180,918,'DIGITAL EXCEL WORKBOOK  •  MANUAL ENTRY',30,MUTE,'bold',1400)
 shadow(d,(270,1150,1740,1735),25);d.rectangle((310,1190,1700,1260),fill=DARK)
 text(d,345,1209,'STOCK OVERVIEW  /  EXAMPLE',29,WHITE,'bold',1300)
 for i,(a,b) in enumerate([('IN STOCK','9 units'),('RESERVED','3 units'),('AVAILABLE','6 units')]):
  x=310+i*460;card(d,(x,1295,x+430,1490),CREAM,LINE,14);text(d,x+25,1320,a,27,TEAL,'bold',380);text(d,x+25,1385,b,48,DARK,'serif',375)
 text(d,350,1550,'Your numbers, organized with clarity.',41,DARK,'serif',1250)
 text(d,350,1655,'Illustrative example  •  Not a workbook screenshot',27,MUTE,'sans',1250)
 return im
def included():
 im=photo('packing-table.png');d=ImageDraw.Draw(im);shadow(d,(105,110,1895,1795),32)
 center(d,180,'WHAT YOU RECEIVE',32,COPPER,'bold');center(d,250,'Your complete workbook set',82,DARK,'serif');center(d,365,'Built for a more organized stockroom',39,MUTE)
 entries=[('01','DEMO WORKBOOK','Explore fictional products, customers, sales and purchase orders.'),('02','BLANK WORKBOOK','Enter your own records in the same 23-sheet workbook.'),('03','READ ME GUIDE','Understand setup, capacities, calculations and limitations.')]
 for i,(n,h,b) in enumerate(entries):
  y=480+i*260;card(d,(165,y,1835,y+215),CREAM,LINE,18);badge(d,210,y+35,n,h);lines=wrap(d,b,font(34),1410);assert len(lines)<=2
  for j,line in enumerate(lines):text(d,315,y+105+j*43,line,34,MUTE,'sans',1410)
 card(d,(165,1290,1835,1625),SAGE,SAGE,22);center(d,1365,'DESIGNED FOR EXCEL DESKTOP',44,DARK,'bold');center(d,1450,'Digital files  •  No macros  •  Manual entry',38,MUTE)
 center(d,1535,'Windows Excel opening and recalculation are unverified.',29,MUTE,'sans',1580)
 center(d,1690,'NOVALITY STORE',27,TEAL,'bold');return im
def map_page():
 im=Image.new('RGB',(S,S),CREAM);d=ImageDraw.Draw(im);top(d,'THE WORKBOOK','23 sheets, one workflow','The complete set of worksheets, grouped by task')
 groups=[('01   START','Dashboard  ·  Getting Started  ·  Settings & Lists'),('02   STOCK','Product & SKU Database  ·  Inventory Tracker  ·  Stock Movement Log'),('03   BUY','Supplier Database  ·  Purchase Orders'),('04   SELL','Wholesale Customer CRM  ·  Wholesale Pricing  ·  Wholesale Orders  ·  Retail Sales Tracker'),('05   PLAN & VALUE','Reorder Planner  ·  Inventory Valuation & COGS  ·  Product Performance'),('06   COUNT & STORE','Returns & Damaged Goods  ·  Warehouse Locations  ·  Stock Audit'),('07   REVIEW','Expense Tracker  ·  Profit Analysis  ·  Monthly Reports  ·  Annual Reports  ·  Printable Orders & Invoices')]
 for i,(a,b) in enumerate(groups):
  y=380+i*203;card(d,(130,y,1870,y+176),WHITE,LINE,16);text(d,165,y+21,a,30,TEAL,'bold',1580)
  lines=wrap(d,b,font(33),1590);assert len(lines)<=2
  for j,line in enumerate(lines):text(d,165,y+79+j*42,line,33,INK,'sans',1590)
 footer(d);return im

def feature(eyebrow,title,sub,tabletitle,headers,rows,benefits,note):
 im=Image.new('RGB',(S,S),CREAM);d=ImageDraw.Draw(im);top(d,eyebrow,title,sub);shadow(d,(130,385,1870,1060),26)
 text(d,170,425,tabletitle,40,DARK,'serif',1550);text(d,170,490,'ILLUSTRATIVE SELECTED FIELDS  /  NOT A SCREENSHOT',25,MUTE,'bold',1600)
 x=170;y=555;w=1660;d.rounded_rectangle((x,y,x+w,y+78),12,fill=DARK);cw=w/len(headers)
 for i,h in enumerate(headers):text(d,int(x+20+i*cw),y+23,h,29,WHITE,'bold',int(cw-30))
 for j,row in enumerate(rows):
  yy=y+78+j*88;d.rectangle((x,yy,x+w,yy+88),fill=WHITE if j%2==0 else '#f0f5ef',outline=LINE,width=1);assert len(row)==len(headers)
  for i,v in enumerate(row):text(d,int(x+20+i*cw),yy+25,str(v),31,INK,'sans',int(cw-32))
 text(d,170,962,note,27,MUTE,'sans',1600)
 for i,(h,b) in enumerate(benefits):
  yy=1110+i*220;card(d,(130,yy,1870,yy+185),WHITE,LINE,18);d.rounded_rectangle((160,yy+27,169,yy+157),5,fill=COPPER)
  text(d,205,yy+22,h,37,DARK,'bold',1570);lines=wrap(d,b,font(34),1550);assert len(lines)<=2,(h,lines)
  for j,line in enumerate(lines):text(d,205,yy+83+j*44,line,34,MUTE,'sans',1550)
 footer(d);return im

def dashboard():
 im=Image.new('RGB',(S,S),CREAM);d=ImageDraw.Draw(im);top(d,'YOUR BUSINESS AT A GLANCE','A clearer overview','Review the records, quantities and warnings you enter')
 tiles=[('PRODUCTS','A view of your SKUs'),('INVENTORY','Stock & availability'),('PURCHASES','Incoming orders'),('WHOLESALE','Orders & customers'),('SALES','Recorded transactions'),('PERFORMANCE','Costs & results')]
 for i,(a,b) in enumerate(tiles):
  x=130+i%2*885;y=400+i//2*300;card(d,(x,y,x+850,y+260),WHITE,LINE,22);d.rounded_rectangle((x+35,y+37,x+47,y+215),6,fill=COPPER)
  text(d,x+80,y+52,a,30,TEAL,'bold',720);text(d,x+80,y+120,b,45,DARK,'serif',715)
 card(d,(130,1375,1870,1740),SAGE,SAGE,26);text(d,180,1435,'A view built from your entries',53,DARK,'serif',1550)
 text(d,180,1530,'Review underlying records and reconcile your figures.',37,MUTE,'sans',1570)
 text(d,180,1600,'Illustrative layout; not a workbook screenshot.',31,MUTE,'sans',1570)
 footer(d);return im

def stock_math():
 im=photo('stock-shelf.png');d=ImageDraw.Draw(im);shadow(d,(105,95,1895,1820),32)
 center(d,155,'HOW STOCK IS DERIVED',31,COPPER,'bold');center(d,225,'A simple stock example',79,DARK,'serif');center(d,335,'Illustrative units  •  Not a workbook screenshot',34,MUTE)
 items=[('OPENING STOCK','10'),('ACCEPTED RECEIPTS','+ 4'),('FULFILLED SALES','− 3'),('SELLABLE RETURN','+ 1'),('WAREHOUSE DAMAGE','− 2'),('MANUAL ADJUSTMENT','− 1')]
 for i,(label,n) in enumerate(items):
  y=440+i*145;card(d,(190,y,1810,y+120),CREAM,LINE,16);text(d,235,y+34,label,33,DARK,'bold',1280)
  f=font(49,'serif');d.text((1740-d.textlength(n,font=f),y+23),n,font=f,fill=TEAL)
 for i,(n,label) in enumerate([('9','IN STOCK'),('3','RESERVED'),('6','AVAILABLE')]):
  x=190+i*550;card(d,(x,1370,x+520,1615),SAGE,SAGE,20);text(d,x+32,1404,n,75,DARK,'serif',450);text(d,x+32,1525,label,28,TEAL,'bold',450)
 center(d,1695,'Based on entries, not a live warehouse connection.',30,MUTE);return im

def limits():
 im=photo('packing-table.png');d=ImageDraw.Draw(im);shadow(d,(100,95,1900,1835),35)
 center(d,155,'BEFORE YOU PURCHASE',31,COPPER,'bold');center(d,220,'A few important details',78,DARK,'serif')
 entries=[('01','EXCEL DESKTOP','Windows Excel opening and recalculation are unverified; test a copy before use.'),('02','MANUAL ORGANIZER','No marketplace, bank, shipping or inventory system sync.'),('03','KEEP ROWS & KEYS STABLE','Filter; do not sort, move, insert or delete populated rows or rename linked SKUs.'),('04','FIXED PREPARED CAPACITY','300 products, 500 PO lines and 600 wholesale order lines by default.'),('05','CHECK YOUR FIGURES','Costs can change historically. Sheet protection is not encryption.')]
 for i,(n,h,b) in enumerate(entries):
  y=360+i*230;card(d,(165,y,1835,y+202),CREAM,LINE,17);badge(d,205,y+26,n,h);lines=wrap(d,b,font(31),1410);assert len(lines)<=2
  for j,line in enumerate(lines):text(d,310,y+92+j*42,line,31,MUTE,'sans',1410)
 center(d,1595,'Not accounting, tax or legal advice.',34,DARK,'bold');center(d,1675,'Read the included guide before relying on results.',31,MUTE)
 center(d,1750,'NOVALITY STORE  /  DIGITAL DOWNLOAD',25,TEAL,'bold');return im
PAGES=[
('01-cover',cover),('02-whats-included',included),('03-sheet-guide',map_page),('04-dashboard',dashboard),
('05-product-skus',lambda:feature('A HOME FOR YOUR CATALOGUE','Products & SKUs','Organize the details for every stocked variant','PRODUCT & SKU DATABASE',['SKU','Product','Unit cost','Opening'],[['CND-01','Candle - small','$10.00','10'],['CND-02','Candle - large','$15.00','5'],['JAR-01','Ceramic jar','$8.00','12']],[('ONE SKU PER VARIANT','Enter product details, prices, opening stock and opening value.'),('KEEP YOUR KEYS STABLE','Use unique SKUs and keep the same code once other rows reference it.'),('CHECK BEFORE SELLING','The workbook flags duplicate SKUs; correct them to keep lookups clear.')],'Fictional example  •  Enter your own stock and prices')),
('06-stock-example',stock_math),
('07-purchase-orders',lambda:feature('BUYING & RECEIVING','Purchase orders','Keep a record of ordered and received stock','PURCHASE ORDERS',['PO number','SKU','Ordered','Received'],[['PO-001','CND-01','20','4'],['PO-002','JAR-01','15','15']],[('RECORD THE ORDER','Enter supplier, quantity, unit cost, freight and expected date.'),('RECEIVE IN PARTS','Update the one received cell to the cumulative quantity.'),('REVIEW DUPLICATES','Only the first matching PO/SKU line contributes to stock; fix alerts.')],'Illustrative fields  •  Same delivery under different POs is not detected')),
('08-suppliers',lambda:feature('YOUR SUPPLY NETWORK','Supplier database','Keep supplier details and purchasing context together','SUPPLIER DATABASE',['Supplier ID','Supplier','Terms','Lead time'],[['SUP-001','Willow Supply','Net 30','14 days'],['SUP-002','Oak Studio','Prepaid','21 days']],[('SAVE SUPPLIER DETAILS','Record contacts, terms and other relevant purchasing information.'),('REVIEW PURCHASE ACTIVITY','See calculated order and delivery measures based on entered data.'),('CHECK OPEN PURCHASES','Monitor outstanding order quantities and values in one place.')],'Fictional example  •  Update supplier information manually')),
('09-wholesale-pricing',lambda:feature('TRADE RELATIONSHIPS','Wholesale & pricing','Organize customers, prices and quantity breaks','WHOLESALE PRICING',['SKU','Wholesale','Tier 1 qty','Tier 1 price'],[['CND-01','$18.00','12','$17.00'],['JAR-01','$14.00','12','$13.00']],[('KEEP CUSTOMER RECORDS','Track terms, discounts and customer information in the CRM.'),('SET QUANTITY BREAKS','Enter your own wholesale prices and quantity thresholds.'),('REVIEW THE MARGIN','Compare pricing against cost and your own floor price.')],'Illustrative example  •  Prices and assumptions may affect historical results')),
('10-wholesale-orders',lambda:feature('FROM ORDER TO DESPATCH','Wholesale orders','Track order lines and reserved quantities','WHOLESALE ORDERS',['Order','SKU','Qty','Status'],[['WO-001','CND-01','3','Confirmed'],['WO-002','JAR-01','5','Shipped']],[('RECORD ORDER LINES','Enter customers, SKUs, quantities and fulfilment status.'),('SEPARATE RESERVATIONS','Confirmed through packed orders reserve stock; shipping reduces it.'),('CHECK BEFORE PROMISING','Review shortfall and reconcile with your actual stock records.')],'Fictional example  •  No automatic order import or fulfilment')),
('11-retail-sales',lambda:feature('DAY-TO-DAY SALES','Retail sales tracker','Record sales, shipping and fee assumptions','RETAIL SALES TRACKER',['Sale','SKU','Qty','Status'],[['SO-001','CND-01','2','Delivered'],['SO-002','JAR-01','1','Shipped']],[('ENTER SALES MANUALLY','Use one row per item sold and select the relevant channel.'),('REVIEW FEES & COSTS','See calculations based on your entered prices and assumptions.'),('KEEP A CLEAR RECORD','Use cancelled for an order that never shipped; check the guide.')],'Illustrative example  •  No marketplace or payment sync')),
('12-reorder-planner',lambda:feature('PLAN WHAT COMES NEXT','Reorder planner','Review stock levels and replenishment signals','REORDER PLANNER',['SKU','Available','On order','Min level'],[['CND-01','6','16','8'],['JAR-01','12','0','5']],[('SEE WHAT IS AVAILABLE','Compare stock after reservations with your minimum levels.'),('CONSIDER LEAD TIME','Reorder calculations use the settings and history you provide.'),('MAKE THE DECISION','Verify supplier dates and quantities before placing an order.')],'Illustrative example  •  Suggested values are not automatic orders')),
('13-stock-movements',lambda:feature('KEEP THE HISTORY','Stock movement log','Give adjustments and losses a reason','STOCK MOVEMENT LOG',['SKU','Type','Quantity','Reason'],[['CND-01','Adjustment','−1','Count correction'],['JAR-01','Damaged','2','Breakage']],[('RECORD MANUAL CHANGES','Log damage, loss, samples and signed stock adjustments.'),('EXPLAIN THE CHANGE','Add dates, reasons and references for later review.'),('AVOID DOUBLE COUNTING','Purchases, sales and returns have their own registers.')],'Fictional example  •  Record each stock event once')),
('14-returns',lambda:feature('WHAT COMES BACK','Returns & damaged goods','Record condition, refunds and the source of a return','RETURNS & DAMAGED GOODS',['SKU','Source','Condition','Qty'],[['CND-01','Retail customer','As new','1'],['JAR-01','Own warehouse','Damaged','2']],[('CUSTOMER RETURNS','Sellable units add back; unsellable units are not subtracted twice.'),('WAREHOUSE DAMAGE','Unsellable own-warehouse items reduce stock.'),('SUPPLIER & COURIER CASES','Review and enter any appropriate stock adjustment separately.')],'Illustrative example  •  Refunds do not update every revenue or tax report')),
('15-locations-audit',lambda:feature('COUNT & STORE','Locations & stock audit','Compare your placement records and physical counts','STOCK AUDIT',['SKU','System at count','Counted','Variance'],[['CND-01','10','8','−2'],['JAR-01','12','12','0']],[('TRACK STORAGE LOCATIONS','Maintain bin quantities manually and review differences from stock.'),('SNAPSHOT BEFORE COUNTING','Type the system quantity at count time and the physical count.'),('POST APPROVED ADJUSTMENTS','Enter the signed correction on the movement log once.')],'Illustrative example  •  Bin quantities are placement records')),
('16-inventory-valuation',lambda:feature('A CONSISTENT COST VIEW','Inventory valuation','Review an approximate current average cost','INVENTORY VALUATION & COGS',['Opening units','Opening value','Received units','Received value'],[['10','$100.00','4','$80.00']],[('CURRENT CUMULATIVE AVERAGE','Opening and accepted receipts build the average cost used in reports.'),('LATER PURCHASES CAN CHANGE IT','The current cost is applied to past sales; it is not a dated ledger.'),('RECONCILE YOUR ACCOUNTS','Use reports for management and discuss accounting treatment with an adviser.')],'Illustrative example  •  Average cost: $180 ÷ 14 = $12.8571')),
('17-reports-printables',lambda:feature('SEE THE BIGGER PICTURE','Reports & printables','Review recorded activity and prepare documents','PRINTABLE ORDERS & INVOICES',['Document','Prepared lines','Use'],[['Purchase order','14','Review before sending'],['Wholesale invoice','14','Review totals & tax'],['Picking list','16','Check stock details']],[('REVIEW PERFORMANCE','Explore monthly, annual and product-level management summaries.'),('PREPARE DOCUMENTS','Enter an ID to populate the prepared printable lines.'),('CHECK CAPACITY & ACCURACY','Extra lines are omitted; check completeness, totals and tax before sending.')],'Illustrative summary  •  Not a compliant invoicing or accounting service')),
('18-important-details',limits)]
FILES={
'01-titles.txt':'''ETSY TITLE OPTIONS — choose one

Inventory Spreadsheet, Wholesale Order Manager Excel Template, SKU Tracker, Purchase Orders and Stock Control

Small Business Inventory Spreadsheet, Wholesale Order Tracker, Product SKU Database and Stock Management Excel Template

Inventory and Wholesale Spreadsheet, Retail Sales Tracker, Reorder Planner, Pricing and Stock Audit Excel Workbook
''',
'02-tags.txt':'''ETSY TAGS — 13 suggestions, maximum 20 characters each

inventory worksheet
wholesale order
stock tracker excel
inventory manager
sku tracker
purchase order log
small business excel
stock management
retail sales tracker
inventory template
wholesale pricing
reorder spreadsheet
stock audit template
''',
'03-description.txt':'''ULTIMATE INVENTORY & WHOLESALE ORDER MANAGER — EXCEL WORKBOOK

Keep your products, purchase orders, stock movements and sales together in one manual Excel workbook. Explore the demo with fictional data, then use the blank version to organize your own small business records.

WHAT YOU RECEIVE
• Demo .xlsx workbook with fictional products and transactions
• Blank .xlsx workbook with the same 23 worksheets and empty registers
• README guide with setup instructions, capacity and important limitations
• Digital download only — no physical item will be shipped

WHAT YOU CAN ORGANIZE
• Product and SKU database, opening quantities and calculated stock
• Suppliers, purchase orders, received quantities and stock adjustments
• Wholesale customers, price breaks, orders and reserved quantities
• Retail sales, fee assumptions, returns and warehouse placement records
• Reorder planning, stock counts, current average costs and estimated profit
• Monthly and annual reports, plus printable PO, invoice and picking list templates

HOW IT WORKS
Open the blank workbook in Microsoft Excel desktop, save your own copy and allow it to recalculate. Update Settings & Lists and add unique SKUs with opening quantity and total opening value. Enter purchase receipts, wholesale orders, retail sales, returns and adjustments manually. Review stock, reservations, alerts and reports against your actual records.

PLEASE READ BEFORE PURCHASE
This is a manual organizer. It does not sync with marketplaces, shipping services, banks or inventory software, import orders, take payments or update live stock. Check actual inventory and reconcile reports before making business decisions.

Designed with Excel 2010-compatible functions for Excel desktop. Windows Excel opening, repair-free behavior and recalculation have not been verified. Test a copy in your Excel version before relying on it; other spreadsheet applications are untested. Formula values need recalculation when opened.

IDs and mirrored sheets depend on row positions. Do not sort, move, insert or delete populated register rows, change ID prefixes after use, rename referenced SKUs or clear referenced trigger fields. Filter instead and resolve duplicate SKU alerts. Default prepared capacities include 300 products, 500 purchase-order lines, 600 wholesale-order lines and 900 retail sales. Other sheets have fixed limits too.

Enter each purchase-order/SKU pair once and update received quantity cumulatively. Duplicate rows are flagged and only the first matching line contributes to stock and open balance; the same physical delivery under different PO numbers cannot be detected. For stock counts, manually record the system quantity at count time before posting any approved adjustment.

Valuation uses a current cumulative average, not a dated perpetual moving-average ledger. Later purchases, price or fee changes can alter historical results. Refunds do not automatically reduce every revenue or tax report. The printable PO and invoice show up to 14 lines each and the picking list up to 16; check for omitted lines, totals and tax before sending. The workbook is not accounting, tax, legal or inventory compliance advice.

The sheet-protection password is premium. Protection is not encryption; keep sensitive records secure and backed up. Listing image tables are illustrative designs, not literal workbook screenshots.
''',
'04-key-features.txt':'''KEY FEATURES

• 23 sheets in a demo and a blank Excel workbook
• Product and SKU database with calculated inventory
• Purchase order receipts, suppliers and stock movement log
• Wholesale customers, price breaks, order lines and reservations
• Retail sales, returns, warehouse locations and stock audits
• Reorder planner, current cumulative average valuation and estimated profit
• Monthly and annual reports, plus printable order documents
• Prepared capacity: 300 products, 500 PO lines, 600 wholesale-order lines, 900 retail sales
• Locked formulas and unlocked prepared inputs; no macros
• Manual entries only; no marketplace or inventory sync

Windows Excel opening and recalculation have not been verified. Read the guide for costing, stock and operating limitations.
''',
'05-faq.txt':'''FREQUENTLY ASKED QUESTIONS

Q: What is included?
A: One ZIP containing demo and blank .xlsx files plus a README guide. There is no physical product.

Q: What software do I need?
A: The files are intended for Microsoft Excel desktop. Windows Excel opening, repair-free behavior and recalculation have not been verified. Test a copy in your version before relying on it; other spreadsheet applications are untested.

Q: Does the workbook sync with my store, warehouse or bank?
A: No. Enter or paste records manually. There is no marketplace, shipping, bank or inventory integration and no payment processing.

Q: How is stock worked out?
A: The Inventory Tracker derives stock from opening quantity, accepted purchase receipts, sales, sellable returns, damage and adjustments. Confirmed wholesale orders reserve stock separately. Results depend on complete, accurate entries.

Q: How do partial deliveries work?
A: Enter one PO/SKU line and update its received cell with the cumulative quantity. Duplicate PO/SKU rows are flagged and only the first contributes to stock and open balance. Different PO numbers for the same physical delivery cannot be detected. The single received date does not preserve a history of each shipment.

Q: Can I sort the registers or change SKUs?
A: Do not sort, move, insert or delete populated register rows. IDs and some mirrored sheets depend on row position. Use filters; do not rename referenced SKUs, change ID prefixes after use or clear trigger fields on referenced rows.

Q: How are stock counts handled?
A: Manually enter the system quantity at count time as a snapshot, then enter the physical count. Post approved differences once on the Stock Movement Log.

Q: Does it calculate historical COGS exactly?
A: No. It uses the current cumulative average, not a dated perpetual moving-average ledger. Later entries or changes to assumptions can change earlier figures. Refunds do not update all revenue and tax reports. Reconcile with your accountant.

Q: Can I print any size order?
A: The printable PO and invoice display up to 14 lines each; the picking list displays up to 16. Verify completeness, totals and tax treatment before use.

Q: Is sheet protection encryption?
A: No. Password premium protects formulas from accidental edits; it does not encrypt the file. Use secure, access-controlled storage and backups.
''',
'06-how-to-use.txt':'''HOW TO USE

1. Download and unzip CUSTOMER-DOWNLOAD.zip. Open the blank workbook in Excel desktop and save your working copy. Allow formulas to recalculate.
2. Read Getting Started and the README. Enter business details and review reporting year, fees, tax assumptions, tiers, lists and other settings.
3. Add unique product SKUs, opening quantities and total opening values. Enter suppliers, wholesale customers and price breaks as required.
4. Enter one PO/SKU line per order, updating its received quantity cumulatively. Record wholesale order lines and retail sales manually. Review reserved and available stock.
5. Record returns and stock movements once, using the appropriate source, condition and status. Keep bin quantities updated manually.
6. For each stock audit, type the system quantity at count time and the counted quantity. Post an approved difference once as a movement and record its ID.
7. Review alerts, stock, profitability and reports against actual records. Check printable line limits, totals and tax before sending anything.

Do not sort, move, insert or delete populated register rows. Do not change ID prefixes or rename referenced SKUs. Filter instead. Password: premium. Protection is not encryption.
''',
'07-listing-attributes.txt':'''SUGGESTED LISTING DETAILS

Product type: Digital download
Buyer file: One ZIP with demo .xlsx, blank .xlsx and README guide
Intended application: Microsoft Excel desktop
Worksheets: 23 per workbook
Prepared capacity: 300 products, 500 PO lines, 600 wholesale-order lines, 900 retail sales
Macros: None (.xlsx)
Delivery: Digital only; no physical product
Brand: Novality Store
Compatibility disclosure: Designed with Excel 2010-compatible functions. Windows Excel opening, repair-free behavior and recalculation are unverified; other spreadsheet applications are untested.

Choose Etsy category and available attributes at publication. Confirm current platform rules, image counts and digital-file specifications. Illustrative tables are not workbook screenshots.
''',
'08-keywords.txt':'''SEARCH PHRASES & AUDIENCE

inventory management spreadsheet; small business inventory Excel template; wholesale order manager; SKU stock tracker; purchase order spreadsheet; wholesale customer organizer; retail sales tracker; reorder planner; stock audit spreadsheet; inventory valuation and COGS.

Potential audience: independent product sellers, small-batch brands and small wholesale businesses seeking a manual Excel organizer.

Avoid claims of real-time sync, warehouse integration, automatic marketplace imports, payment processing, verified Windows Excel compatibility, encrypted customer data, certified accounting or tax compliance, perpetual historical costing or guaranteed profits.
'''
}
def main():
 if KIT.exists():shutil.rmtree(KIT)
 OUT.mkdir(parents=True);COPY.mkdir()
 for name,fn in PAGES:
  fn().save(OUT/(name+'.jpg'),'JPEG',quality=91,subsampling=0,optimize=True);print(name,flush=True)
 for name,body in FILES.items():(COPY/name).write_text(body,encoding='utf-8')
 titles=[s for s in FILES['01-titles.txt'].splitlines() if s and not s.startswith('ETSY')];tags=[s for s in FILES['02-tags.txt'].splitlines() if s and not s.startswith('ETSY')]
 assert len(titles)==3 and all(len(s)<=140 for s in titles),[(len(s),s) for s in titles]
 assert len(tags)==13 and len(set(tags))==13 and all(len(s)<=20 for s in tags),[(len(s),s) for s in tags]
 shutil.copy2(DL/'inventory-wholesale-management-spreadsheet.zip',KIT/'CUSTOMER-DOWNLOAD.zip')
 (KIT/'SELLER-START-HERE.txt').write_text('''INVENTORY & WHOLESALE ETSY LISTING KIT — FOR THE SELLER

1. Review the listing-copy folder; choose one title and 13 tags. Confirm every claim against the workbook and its README.
2. Choose from the 18 square JPEG listing-images. Product visuals and tables are illustrative and are not literal Excel screenshots. Confirm Etsy's current listing image requirements before upload.
3. Upload CUSTOMER-DOWNLOAD.zip as the buyer's product, not the entire seller kit. It is an unchanged copy of the demo workbook, blank workbook and README package. Generator source is separate and is not inside the buyer ZIP.
4. Test both customer workbooks in Windows Excel for opening, repair messages and recalculation before selling. This has not been verified; keep the compatibility disclosure until actual successful testing.
5. Keep the manual-only operation, row and SKU restrictions, fixed capacity, duplicate receipt, historical costing and print limits clear. The workbook is not a synced inventory service or certified accounting system.
6. Photo backgrounds were AI-generated without text. All visible type, mockups and example tables were added separately.
''',encoding='utf-8')
 out=DL/'inventory-wholesale-etsy-listing-kit.zip'
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
  for p in sorted(KIT.rglob('*')):
   if p.is_file():z.write(p,p.relative_to(KIT))
 for part in range(3):
  sheet=Image.new('RGB',(1500,1000),'white')
  for i,(name,_) in enumerate(PAGES[part*6:part*6+6]):
   with Image.open(OUT/(name+'.jpg')) as im:sheet.paste(im.resize((500,500)),((i%3)*500,(i//3)*500))
  sheet.save(R/'etsy'/f'qa-{part+1}.jpg',quality=90)
 print('Saved',out,out.stat().st_size)
if __name__=='__main__':main()
