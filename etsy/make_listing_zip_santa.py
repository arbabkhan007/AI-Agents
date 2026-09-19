"""
make_listing_zip_santa.py - bundle the Etsy listing kit for the Secret
Santa & White Elephant Party Tracker into ONE zip:

  LISTING_KIT_SANTA.md   title, 13+7 tags, description, alt texts,
                         pricing, publish checklist
  images_santa/          15 listing images (2400x1800 JPEG, < 1 MB each)

Run from the repo root:   python3 -m etsy.make_listing_zip_santa
"""

import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIP_NAME = "Secret_Santa_White_Elephant_Tracker_Etsy_Listing_Kit.zip"

IMAGES = [
    "01_hero", "02_dashboard", "03_whats_inside", "04_participants",
    "05_draw", "06_rules", "07_budget", "08_wishlists", "09_whiteelephant",
    "10_history_cards", "11_themes", "12_example", "13_howitworks",
    "14_files", "15_faq",
]


def main():
    src_md = os.path.join(ROOT, "etsy", "LISTING_KIT_SANTA.md")
    assert os.path.exists(src_md), "etsy/LISTING_KIT_SANTA.md missing"
    for n in IMAGES:
        p = os.path.join(ROOT, "etsy", "images_santa", n + ".jpg")
        assert os.path.exists(p), f"missing image {n}.jpg - run " \
            f"python3 -m etsy.make_listing_images_santa first"

    out = os.path.join(ROOT, ZIP_NAME)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED,
                         compresslevel=9) as z:
        z.write(src_md, "LISTING_KIT_SANTA.md")
        for n in IMAGES:
            p = os.path.join(ROOT, "etsy", "images_santa", n + ".jpg")
            z.write(p, os.path.join("images_santa", n + ".jpg"))

    with zipfile.ZipFile(out) as z:
        bad = z.testzip()
        assert bad is None, f"corrupt member: {bad}"
        names = z.namelist()
        assert len(names) == 16, names

    size = os.path.getsize(out)
    print(f"built {ZIP_NAME}")
    print(f"  members : {len(names)} (1 kit md + 15 images)")
    print(f"  size    : {size/1024/1024:.1f} MB")
    print(f"  zip ok  : integrity verified")


if __name__ == "__main__":
    main()
