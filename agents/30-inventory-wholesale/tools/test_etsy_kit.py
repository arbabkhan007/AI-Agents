"""Check seller package, image files, listing text and exact buyer ZIP."""
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
from hashlib import sha256
from PIL import Image
root=Path(__file__).resolve().parent.parent
with ZipFile(root/'download/inventory-wholesale-etsy-listing-kit.zip') as z:
 assert z.testzip() is None
 names=z.namelist();imgs=[x for x in names if x.startswith('listing-images/')];copies=[x for x in names if x.startswith('listing-copy/')]
 assert len(names)==28 and len(imgs)==18 and len(copies)==8
 for name in imgs:
  with Image.open(BytesIO(z.read(name))) as image:
   assert image.size==(2000,2000) and image.format=='JPEG';image.verify()
 original=(root/'download/inventory-wholesale-management-spreadsheet.zip').read_bytes()
 assert sha256(z.read('CUSTOMER-DOWNLOAD.zip')).digest()==sha256(original).digest()
 with ZipFile(BytesIO(original)) as buyer:
  assert buyer.testzip() is None
  assert len(buyer.namelist())==3 and sum(n.endswith('.xlsx') for n in buyer.namelist())==2 and 'README.md' in buyer.namelist()
 def lines(path):return [s for s in z.read(path).decode('utf-8').splitlines() if s and not s.startswith('ETSY')]
 titles=lines('listing-copy/01-titles.txt');tags=lines('listing-copy/02-tags.txt')
 assert len(titles)==3 and all(len(s)<=140 for s in titles)
 assert len(tags)==13 and len(set(tags))==13 and all(len(s)<=20 for s in tags)
 desc=z.read('listing-copy/03-description.txt').decode('utf-8')
 for phrase in ('have not been verified','does not sync','row positions','current cumulative average','not encryption','14 lines','illustrative'):
  assert phrase in desc,phrase
 print('OK:',len(imgs),'2000×2000 JPEGs,',len(copies),'copy documents, matching buyer ZIP')
 print('Title lengths:',[len(s) for s in titles]);print('Tag lengths:',[len(s) for s in tags])
 print('Buyer SHA-256:',sha256(original).hexdigest())
