#!/usr/bin/env python3
"""Verify the Etsy kit's archive, dimensions, copy constraints and buyer package."""
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
from hashlib import sha256
from PIL import Image
root=Path(__file__).resolve().parent.parent
with ZipFile(root/'download/airbnb-rental-etsy-listing-kit.zip') as z:
 assert z.testzip() is None
 names=z.namelist();imgs=[x for x in names if x.startswith('listing-images/')];copies=[x for x in names if x.startswith('listing-copy/')]
 assert len(names)==28 and len(imgs)==18 and len(copies)==8
 for name in imgs:
  with Image.open(BytesIO(z.read(name))) as im:
   assert im.size==(2000,2000) and im.format=='JPEG';im.verify()
 original=(root/'download/airbnb-rental-management-spreadsheet.zip').read_bytes()
 assert sha256(z.read('CUSTOMER-DOWNLOAD.zip')).digest()==sha256(original).digest()
 def lines(path):return [s for s in z.read(path).decode('utf-8').splitlines() if s and not s.startswith('ETSY')]
 titles=lines('listing-copy/01-titles.txt');tags=lines('listing-copy/02-tags.txt')
 assert len(titles)==3 and all(len(x)<=140 for x in titles)
 assert len(tags)==13 and len(set(tags))==13 and all(len(x)<=20 for x in tags)
 text=z.read('listing-copy/03-description.txt').decode('utf-8')
 for required in ('not yet been verified','no Airbnb','not affiliated','first 12 properties','not encryption'):
  assert required in text,required
 print('OK:',len(imgs),'2000×2000 images,',len(copies),'copy documents, matching customer ZIP')
 print('Title lengths:',[len(x) for x in titles]);print('Tag lengths:',[len(x) for x in tags])
