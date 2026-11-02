"""Verify listing images, copy constraints, and the embedded buyer download."""
from pathlib import Path
from zipfile import ZipFile
from hashlib import sha256
from io import BytesIO
from PIL import Image
R=Path(__file__).resolve().parent.parent
kit=R/'download/landscaping-etsy-listing-kit.zip'
buyer=R/'download/landscaping-business-manager.zip'
with ZipFile(kit) as z:
 assert z.testzip() is None
 names=z.namelist();imgs=[n for n in names if n.startswith('listing-images/') and n.endswith('.jpg')];docs=[n for n in names if n.startswith('listing-copy/') and n.endswith('.txt')]
 assert len(imgs)==18 and len(docs)==8
 for name in imgs:
  with z.open(name) as f:
   image=Image.open(f);assert image.format=='JPEG' and image.size==(2000,2000);image.verify()
 tags=[s.strip() for s in z.read('listing-copy/02-tags.txt').decode().splitlines()[2:] if s.strip()]
 titles=[s.strip() for s in z.read('listing-copy/01-titles.txt').decode().splitlines()[2:] if s.strip()]
 assert len(tags)==13 and len(set(tags))==13 and max(map(len,tags))<=20
 assert len(titles)==3 and max(map(len,titles))<=140
 payload=z.read('landscaping-business-manager.zip');assert sha256(payload).digest()==sha256(buyer.read_bytes()).digest()
 with ZipFile(BytesIO(payload)) as b:assert b.testzip() is None and len(b.namelist())==3
 print('18 JPEGs, 8 copy docs, 3 titles, 13 valid tags; embedded buyer ZIP matches:',sha256(payload).hexdigest())
