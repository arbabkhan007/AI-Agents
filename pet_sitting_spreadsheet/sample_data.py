"""
Demo data.

Sample clients, pets, bookings, invoices, payments, expenses and trips are
written into the input (cream) cells so the dashboard, reports and reminders
show meaningful numbers the moment the workbook is opened.  Everything is
dated relative to the build date and can be switched off with
``--no-sample-data``.
"""

from __future__ import annotations

import datetime as _dt
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List

from .config import Config


def d(base: _dt.date, offset: int) -> _dt.date:
    return base + _dt.timedelta(days=offset)


def t(hour: int, minute: int = 0) -> _dt.time:
    return _dt.time(hour, minute)


@dataclass
class Sample:
    clients: List[Dict[str, Any]] = field(default_factory=list)
    pets: List[Dict[str, Any]] = field(default_factory=list)
    services: List[Dict[str, Any]] = field(default_factory=list)
    staff: List[Dict[str, Any]] = field(default_factory=list)
    bookings: List[Dict[str, Any]] = field(default_factory=list)
    visits: List[Dict[str, Any]] = field(default_factory=list)
    invoices: List[Dict[str, Any]] = field(default_factory=list)
    payments: List[Dict[str, Any]] = field(default_factory=list)
    expenses: List[Dict[str, Any]] = field(default_factory=list)
    mileage: List[Dict[str, Any]] = field(default_factory=list)
    health: List[Dict[str, Any]] = field(default_factory=list)
    incidents: List[Dict[str, Any]] = field(default_factory=list)
    messages: List[Dict[str, Any]] = field(default_factory=list)
    inventory: List[Dict[str, Any]] = field(default_factory=list)
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    drawings: List[Dict[str, Any]] = field(default_factory=list)


_CACHE: Dict[int, Sample] = {}


def get(cfg: Config) -> Sample:
    """Build (once) the demo dataset for this configuration."""
    key = id(cfg)
    if key not in _CACHE:
        _CACHE[key] = _build(cfg)
    return _CACHE[key]


# ---------------------------------------------------------------------------

def _build(cfg: Config) -> Sample:
    rnd = random.Random(20261011)
    today = cfg.today
    s = Sample()

    # ------------------------------------------------------------- services
    s.services = [
        dict(name="Dog Walk - 30 min", category="Dog walking",
             description="Solo neighbourhood walk, water top-up and paw wipe",
             unit="Per walk", duration=30, rate=25, extra_pet=10,
             staff_cost=11, active="Yes", travel="No",
             notes="Most popular weekday service"),
        dict(name="Dog Walk - 60 min", category="Dog walking",
             description="Long walk or park session with recall practice",
             unit="Per walk", duration=60, rate=40, extra_pet=15,
             staff_cost=20, active="Yes", travel="No"),
        dict(name="Puppy Visit - 30 min", category="Puppy care",
             description="Toilet break, short play, crate reset and feed",
             unit="Per visit", duration=30, rate=28, extra_pet=8,
             staff_cost=12, active="Yes", travel="No"),
        dict(name="Drop-in Visit - 30 min", category="Drop-in visit",
             description="Feed, fresh water, litter or potty break, playtime",
             unit="Per visit", duration=30, rate=26, extra_pet=8,
             staff_cost=11, active="Yes", travel="No"),
        dict(name="Cat Feeding Visit", category="Feeding visit",
             description="Feed, water, litter tray clean, cuddles, plant care",
             unit="Per visit", duration=20, rate=22, extra_pet=7,
             staff_cost=9, active="Yes", travel="No"),
        dict(name="Pet Sitting - Half Day", category="Pet sitting",
             description="Four hours of care in the client's home",
             unit="Per hour", duration=240, rate=18, extra_pet=6,
             staff_cost=9, active="Yes", travel="Yes"),
        dict(name="Overnight Pet Sitting", category="Overnight stay",
             description="Evening arrival to morning departure, in-home stay",
             unit="Per night", duration=840, rate=95, extra_pet=20,
             staff_cost=45, active="Yes", travel="Yes"),
        dict(name="House Sitting - Per Night", category="House sitting",
             description="Overnight house and pet care, mail and bins",
             unit="Per night", duration=840, rate=85, extra_pet=18,
             staff_cost=40, active="Yes", travel="Yes"),
        dict(name="Senior Pet Care Visit", category="Senior pet care",
             description="Gentle care, mobility help, medication, comfort",
             unit="Per visit", duration=45, rate=34, extra_pet=10,
             staff_cost=15, active="Yes", travel="No"),
        dict(name="Medication Administration", category="Medication visit",
             description="Scheduled medication with written administration log",
             unit="Per visit", duration=20, rate=18, extra_pet=6,
             staff_cost=8, active="Yes", travel="No"),
        dict(name="Pet Taxi / Vet Transport", category="Pet transport",
             description="Door to door transport including waiting time",
             unit="Per hour", duration=60, rate=38, extra_pet=10,
             staff_cost=17, active="Yes", travel="Yes"),
        dict(name="Extra Pet Add-on", category="Add-on",
             description="Additional pet on any visit",
             unit="Flat fee", duration=0, rate=8, extra_pet=0,
             staff_cost=3, active="Yes", travel="No"),
    ]

    # ---------------------------------------------------------------- staff
    s.staff = [
        dict(name="Alex Morgan", phone="+1 (555) 014 2200",
             email="alex@happypawspetcare.com", role="Owner",
             employment="Employee - full time", start_date=d(today, -980),
             status="Active", availability="Mon-Fri 07:00-18:00",
             days_off="Sunday", pay_type="Salary", pay_rate=26,
             certs="Pet First Aid, Canine Behaviour L3",
             cert_expiry=d(today, 160), check_date=d(today, -220),
             emergency="Jordan Morgan +1 (555) 014 2201",
             leave="None booked", notes="Handles reactive dogs"),
        dict(name="Jamie Lee", phone="+1 (555) 330 8812",
             email="jamie@happypawspetcare.com", role="Dog walker",
             employment="Employee - part time", start_date=d(today, -420),
             status="Active", availability="Mon-Sat 08:00-16:00",
             days_off="Sunday", pay_type="Hourly", pay_rate=19,
             certs="Pet First Aid", cert_expiry=d(today, 24),
             check_date=d(today, -180),
             emergency="Pat Lee +1 (555) 330 8813",
             leave="2 days in December", notes="Great with puppies"),
        dict(name="Priya Shah", phone="+1 (555) 772 6690",
             email="priya@happypawspetcare.com", role="Pet sitter",
             employment="Casual", start_date=d(today, -260),
             status="Active", availability="Tue-Sun 09:00-20:00",
             days_off="Monday", pay_type="Per visit", pay_rate=16,
             certs="Pet First Aid, Cat Care", cert_expiry=d(today, 310),
             check_date=d(today, -150),
             emergency="Ravi Shah +1 (555) 772 6691",
             leave="None booked", notes="Overnight specialist"),
        dict(name="Tom Reed", phone="+1 (555) 448 1120",
             email="tom.reed@example.com", role="Contractor",
             employment="Contractor", start_date=d(today, -120),
             status="Active", availability="Weekends only",
             days_off="Mon-Fri", pay_type="Commission %", pay_rate=55,
             certs="Pet First Aid", cert_expiry=d(today, -8),
             check_date=d(today, -110),
             emergency="Sam Reed +1 (555) 448 1121",
             leave="None booked",
             notes="Invoices monthly - certificate expired, chase renewal"),
    ]

    # -------------------------------------------------------------- clients
    client_rows = [
        ("Sarah Mitchell", "+1 (555) 201 7744", "sarah.mitchell@example.com",
         "14 Juniper Way", "Springfield", "62704", "Tom Mitchell",
         "+1 (555) 201 7745", "SMS", "Google search", -240, "Active",
         "Key held", "KEY-01", "Lockbox by side gate, code 4471",
         "Signed", "Yes", 500,
         "Bella pulls left on the lead. Treats in blue tin.",
         "Prefers evening walks. Pays by card on the 1st."),
        ("James Okafor", "+1 (555) 889 2031", "james.okafor@example.com",
         "7 Ashgrove Court", "Springfield", "62702", "Ada Okafor",
         "+1 (555) 889 2032", "Email", "Client referral", -190, "Active",
         "Key held", "KEY-02", "Front door key, alarm code 8812 then #",
         "Signed", "Yes", 400,
         "Luna hides under the bed - give her 10 minutes.",
         "Travels for work most months."),
        ("Priya Raman", "+1 (555) 663 4417", "priya.raman@example.com",
         "92 Hilltop Drive", "Riverton", "62711", "Vijay Raman",
         "+1 (555) 663 4418", "WhatsApp", "Instagram", -150, "Active",
         "Lockbox code", "KEY-03", "Lockbox on tap, code 2290",
         "Signed", "Yes", 600,
         "Cooper is in training - no treats before walks.",
         "Weekly Tuesday and Thursday walks."),
        ("Daniel Brooks", "+1 (555) 712 9034", "daniel.brooks@example.com",
         "3 Meadow Lane", "Springfield", "62703", "Erin Brooks",
         "+1 (555) 712 9035", "Phone call", "Vet clinic", -120, "Active",
         "Key held", "KEY-04", "Back door, lift handle then turn",
         "Signed", "Yes", 750,
         "Daisy needs 60 minute runs. Teddy stays home.",
         "Referred by Riverton Vet Clinic."),
        ("Megan Foster", "+1 (555) 204 5588", "megan.foster@example.com",
         "18 Willow Street", "Riverton", "62712", "Chris Foster",
         "+1 (555) 204 5589", "SMS", "Facebook", -95, "Active",
         "Smart lock code", "-", "Smart lock code 3391, auto locks",
         "Signed", "Yes", 350,
         "Two cats, feed separately. Milo is on medication.",
         "Books two weeks of holiday cover twice a year."),
        ("Luis Hernandez", "+1 (555) 556 1177", "luis.hernandez@example.com",
         "45 Oakfield Road", "Springfield", "62705", "Maria Hernandez",
         "+1 (555) 556 1178", "Phone call", "Word of mouth", -70, "Active",
         "Not held", "-", "Owner home most days - ring the bell",
         "Signed", "Yes", 300,
         "Ruby is nervous with men in hats.",
         "Pays cash at the end of each week."),
        ("Chloe Bennett", "+1 (555) 991 3320", "chloe.bennett@example.com",
         "11 Garden Terrace", "Riverton", "62713", "Paul Bennett",
         "+1 (555) 991 3321", "Email", "Flyer / poster", -45, "Active",
         "Key held", "KEY-05", "Side gate latch, key under planter",
         "Sent", "Yes", 250,
         "Poppy the rabbit needs fresh greens daily.",
         "New client - send the 6 week check-in."),
        ("Robert Nguyen", "+1 (555) 338 7742", "robert.nguyen@example.com",
         "60 Station Road", "Springfield", "62701", "Linh Nguyen",
         "+1 (555) 338 7743", "SMS", "Google search", -400, "Inactive",
         "Key returned", "-", "Key returned 10 months ago",
         "Expired", "No", 0,
         "Charlie loves the river path.",
         "Moved to a new suburb - win-back candidate."),
        ("Amelia Clarke", "+1 (555) 447 2218", "amelia.clarke@example.com",
         "2 Bridge View", "Riverton", "62714", "Noah Clarke",
         "+1 (555) 447 2219", "Email", "Instagram", -12, "Prospective",
         "Not held", "-", "Meet and greet booked",
         "Not sent", "No", 0,
         "Two rescue dogs - needs a slow introduction.",
         "Quote sent for weekday walks."),
    ]
    for (name, phone, email, addr, city, post, ename, ephone, contact,
         referral, reg_offset, status, key_status, key_tag, access,
         contract, consent, limit, prefs, notes) in client_rows:
        s.clients.append(dict(
            name=name, phone=phone, email=email, address=addr, city=city,
            postcode=post, emergency_name=ename, emergency_phone=ephone,
            contact_method=contact, referral=referral,
            reg_date=d(today, reg_offset), status=status,
            key_status=key_status, key_tag=key_tag, access_notes=access,
            access_code="See access notes",
            contract=contract, agreement_date=d(today, reg_offset + 2),
            vet_consent=consent, vet_limit=limit, preferences=prefs,
            notes=notes))

    # ----------------------------------------------------------------- pets
    pet_rows = [
        ("Bella", "Sarah Mitchell", "Dog", "Labrador Retriever", -1460,
         "Female (spayed)", 28.5, "Golden, white chest patch", "Friendly",
         "Pulls on the lead when excited", "None known",
         "Mild hip stiffness in cold weather", "Riverton Vet Clinic",
         "+1 (555) 100 2000", 40, "Pet Secure", "PS-55012",
         "2 cups dry food am and pm", "Dry kibble - salmon", "2 cups",
         "07:30 and 18:00", "Joint supplement", "1 chew with breakfast",
         "Daily with breakfast", "60 min walks, loves fetch",
         "Garden every 4 hours", "Brush twice a week",
         "Tennis ball, peanut butter kong", "None",
         "Harness on before the front door opens",
         "Do not let off lead near the main road"),
        ("Max", "Sarah Mitchell", "Dog", "Beagle", -980, "Male (neutered)",
         14.2, "Tricolour", "Energetic", "Food obsessed - counter surfs",
         "Chicken", "None", "Riverton Vet Clinic", "+1 (555) 100 2000", 70,
         "Pet Secure", "PS-55013", "1.5 cups twice daily",
         "Dry kibble - lamb", "1.5 cups", "07:30 and 18:00", "None", "-",
         "-", "30 min sniffy walks", "Garden every 4 hours",
         "Monthly nail trim", "Squeaky duck", "Escape artist",
         "Double check the side gate latch",
         "Will bolt through open gates"),
        ("Luna", "James Okafor", "Cat", "Ragdoll", -1100, "Female (spayed)",
         4.8, "Cream and grey point", "Shy", "Hides from strangers",
         "Dust mites", "None", "Springfield Animal Hospital",
         "+1 (555) 100 3000", 150, "CatCare Plus", "CC-9902",
         "Wet food am, dry topped up pm", "Wet - tuna pate", "1 pouch",
         "08:00 and 17:30", "None", "-", "-", "Indoor only - wand toy play",
         "Litter tray in laundry - scoop daily", "Brush every visit",
         "Feather wand, sunny windowsill", "None",
         "Let her come to you, never lift her", "Indoor cat - keep doors shut"),
        ("Cooper", "Priya Raman", "Dog", "Cockapoo", -620, "Male (neutered)",
         9.4, "Apricot curly coat", "Playful", "Jumps up when greeting",
         "Grain", "None", "Hilltop Veterinary", "+1 (555) 100 4000", 25,
         "Pet Secure", "PS-55120", "1 cup twice daily", "Grain free kibble",
         "1 cup", "07:00 and 18:30", "None", "-", "-",
         "45 min walks, training recall", "Garden before and after walks",
         "Groomer every 6 weeks", "Rope tug, training treats", "None",
         "Lead on in the hallway, treats for calm", "Training in progress"),
        ("Daisy", "Daniel Brooks", "Dog", "Border Collie", -1750, "Female",
         19.0, "Black and white", "Energetic", "Herds joggers",
         "None known", "None", "Riverton Vet Clinic", "+1 (555) 100 2000",
         210, "Pet Secure", "PS-55211", "2 cups am, 1 cup pm",
         "Dry kibble - chicken", "2 cups", "06:30 and 17:30", "None", "-",
         "-", "60 min off-lead run at Hill Park", "Garden every 3 hours",
         "Brush weekly", "Frisbee, flirt pole", "None",
         "Long line until recall is solid", "Keep away from cyclists"),
        ("Milo", "Megan Foster", "Cat", "Domestic Short Hair", -2200,
         "Male (neutered)", 5.6, "Black with white bib", "Calm",
         "Dislikes being picked up", "None known",
         "Hyperthyroid - daily medication", "Springfield Animal Hospital",
         "+1 (555) 100 3000", -5, "CatCare Plus", "CC-7781",
         "Half pouch three times daily", "Wet - chicken", "Half pouch",
         "07:00, 13:00, 19:00", "Felimazole 2.5mg",
         "1 tablet in food, morning only", "Daily 07:00",
         "Indoor with catio access", "Two trays - scoop every visit",
         "Brush twice weekly", "Catnip mouse", "Medical risk",
         "Medication must be given before food",
         "Vomiting or refusing food = call owner and vet"),
        ("Ruby", "Luis Hernandez", "Dog", "Staffordshire Bull Terrier",
         -1330, "Female (spayed)", 16.8, "Brindle", "Needs slow introduction",
         "Nervous of men in hats", "Beef", "None", "Oakfield Vets",
         "+1 (555) 100 5000", 95, "None", "-", "1.5 cups twice daily",
         "Dry kibble - fish", "1.5 cups", "08:00 and 18:00", "None", "-",
         "-", "30 min quiet street walks", "Garden every 4 hours",
         "Wipe down after walks", "Stuffed kong", "Not dog friendly",
         "Keep 10m from other dogs, treat scatter to pass",
         "Reactive to other dogs on lead"),
        ("Oscar", "Chloe Bennett", "Dog", "Dachshund", -700,
         "Male (neutered)", 7.2, "Smooth black and tan", "Friendly",
         "Barks at the postman", "None known", "Mild back sensitivity",
         "Hilltop Veterinary", "+1 (555) 100 4000", 300, "Pet Secure",
         "PS-55330", "0.75 cup twice daily", "Dry kibble - turkey",
         "0.75 cup", "08:00 and 18:00", "None", "-", "-",
         "20 min flat walks - no stairs", "Garden every 4 hours",
         "Ear clean weekly", "Soft bear, chew stick", "None",
         "Lift with two hands supporting the back",
         "Never let him jump off furniture"),
        ("Poppy", "Chloe Bennett", "Rabbit", "Mini Lop", -500, "Female",
         1.9, "White with grey ears", "Shy", "Startles easily",
         "None known", "None", "Hilltop Veterinary", "+1 (555) 100 4000",
         20, "None", "-", "Unlimited hay, fresh greens daily",
         "Hay and pellets", "Handful of greens", "Morning", "None", "-",
         "-", "Run time in the pen for 30 minutes",
         "Litter corner - clean daily", "Check nails monthly",
         "Parsley, cardboard tunnel", "None",
         "Scoop from underneath, support the back legs",
         "Keep away from the dogs next door"),
        ("Charlie", "Robert Nguyen", "Dog", "Golden Retriever", -2500,
         "Male (neutered)", 32.0, "Golden", "Calm", "None",
         "Pollen - seasonal", "Arthritis", "Station Road Vets",
         "+1 (555) 100 6000", -120, "None", "-", "3 cups twice daily",
         "Senior kibble", "3 cups", "07:00 and 18:00", "Metacam",
         "0.8ml with food", "Daily morning", "Gentle 30 min river walks",
         "Garden every 3 hours", "Brush every visit", "Old tennis ball",
         "None", "Help him into the car with the ramp",
         "Senior dog - watch for limping"),
        ("Simba", "Megan Foster", "Cat", "Maine Coon", -900, "Male",
         7.9, "Ginger tabby", "Playful", "Door dasher", "None known",
         "None", "Springfield Animal Hospital", "+1 (555) 100 3000", 35,
         "CatCare Plus", "CC-7782", "1 pouch twice daily", "Wet - salmon",
         "1 pouch", "07:00 and 19:00", "None", "-", "-",
         "Indoor play, laser pointer", "Two trays - scoop every visit",
         "Daily brush - knots easily", "Laser pointer", "Door dasher",
         "Shut the hallway door before opening the front door",
         "Will dash out of the front door"),
        ("Teddy", "Daniel Brooks", "Dog", "Cavoodle", -300,
         "Male (neutered)", 8.1, "Chocolate curly", "Friendly",
         "Separation anxiety - whines at first", "None known", "None",
         "Riverton Vet Clinic", "+1 (555) 100 2000", 180, "Pet Secure",
         "PS-55212", "1 cup twice daily", "Puppy kibble", "1 cup",
         "07:30 and 18:00", "None", "-", "-", "30 min walk plus garden play",
         "Garden every 3 hours", "Groomer every 8 weeks",
         "Rope toy, frozen kong", "None",
         "Leave the radio on when you go", "Anxious if left alone too long"),
    ]
    for (name, owner, ptype, breed, dob_off, gender, weight, colour,
         temperament, behaviour, allergies, medical, vet, vet_phone,
         vacc_off, insurer, policy, feeding, food, portion, schedule,
         medication, dosage, med_schedule, walking, potty, grooming,
         favourites, risk, handling, warnings) in pet_rows:
        s.pets.append(dict(
            name=name, owner=owner, type=ptype, breed=breed,
            dob=d(today, dob_off), gender=gender, weight=weight,
            colour=colour, photo="Link to photo folder",
            microchip=f"9560000{rnd.randint(100000, 999999)}",
            temperament=temperament, behaviour=behaviour,
            allergies=allergies, medical=medical, vet_name=vet,
            vet_phone=vet_phone, emerg_clinic="24/7 Springfield Pet ER",
            emerg_phone="+1 (555) 100 9111",
            vacc_date=d(today, vacc_off - 365),
            vacc_expiry=d(today, vacc_off), insurer=insurer, policy=policy,
            insurance_expiry=d(today, vacc_off + 40) if insurer != "None"
            else None,
            feeding=feeding, food=food, portion=portion,
            feed_schedule=schedule, medication=medication, dosage=dosage,
            med_schedule=med_schedule, walking=walking, potty=potty,
            grooming=grooming, favourites=favourites, risk=risk,
            handling=handling, warnings=warnings))

    pet_label = {p["name"]: f'{p["name"]} ({p["owner"]})' for p in s.pets}

    # ------------------------------------------------------------- bookings
    plan = [
        # (day offset, client, pet, service, start hour, staff, status)
        (-28, "Sarah Mitchell", "Bella", "Dog Walk - 60 min", 10, "Jamie Lee"),
        (-27, "Priya Raman", "Cooper", "Dog Walk - 30 min", 9, "Jamie Lee"),
        (-26, "Megan Foster", "Milo", "Cat Feeding Visit", 8, "Priya Shah"),
        (-24, "Daniel Brooks", "Daisy", "Dog Walk - 60 min", 7, "Alex Morgan"),
        (-23, "James Okafor", "Luna", "Drop-in Visit - 30 min", 17,
         "Priya Shah"),
        (-21, "Sarah Mitchell", "Max", "Dog Walk - 30 min", 11, "Jamie Lee"),
        (-20, "Luis Hernandez", "Ruby", "Dog Walk - 30 min", 15, "Alex Morgan"),
        (-18, "Chloe Bennett", "Oscar", "Puppy Visit - 30 min", 12,
         "Priya Shah"),
        (-17, "Megan Foster", "Simba", "Cat Feeding Visit", 8, "Priya Shah"),
        (-15, "Daniel Brooks", "Teddy", "Pet Sitting - Half Day", 9,
         "Alex Morgan"),
        (-14, "Priya Raman", "Cooper", "Dog Walk - 30 min", 9, "Jamie Lee"),
        (-12, "James Okafor", "Luna", "Overnight Pet Sitting", 19,
         "Priya Shah"),
        (-11, "Sarah Mitchell", "Bella", "Dog Walk - 60 min", 10, "Jamie Lee"),
        (-9, "Megan Foster", "Milo", "Medication Administration", 7,
         "Priya Shah"),
        (-8, "Chloe Bennett", "Poppy", "Drop-in Visit - 30 min", 16,
         "Priya Shah"),
        (-7, "Daniel Brooks", "Daisy", "Dog Walk - 60 min", 7, "Alex Morgan"),
        (-6, "Luis Hernandez", "Ruby", "Dog Walk - 30 min", 15, "Tom Reed"),
        (-5, "Priya Raman", "Cooper", "Dog Walk - 30 min", 9, "Jamie Lee"),
        (-4, "Sarah Mitchell", "Max", "Dog Walk - 30 min", 11, "Jamie Lee"),
        (-3, "Megan Foster", "Simba", "Cat Feeding Visit", 8, "Priya Shah"),
        (-2, "James Okafor", "Luna", "Drop-in Visit - 30 min", 17,
         "Priya Shah"),
        (-1, "Daniel Brooks", "Teddy", "Senior Pet Care Visit", 13,
         "Alex Morgan"),
        (0, "Sarah Mitchell", "Bella", "Dog Walk - 60 min", 10, "Jamie Lee"),
        (0, "Priya Raman", "Cooper", "Dog Walk - 30 min", 9, "Jamie Lee"),
        (1, "Chloe Bennett", "Oscar", "Puppy Visit - 30 min", 12,
         "Priya Shah"),
        (2, "Megan Foster", "Milo", "Cat Feeding Visit", 8, "Priya Shah"),
        (3, "Luis Hernandez", "Ruby", "Dog Walk - 30 min", 15, "Tom Reed"),
        (4, "Daniel Brooks", "Daisy", "Dog Walk - 60 min", 7, "Alex Morgan"),
        (6, "James Okafor", "Luna", "Overnight Pet Sitting", 19,
         "Priya Shah"),
        (8, "Sarah Mitchell", "Bella", "Pet Taxi / Vet Transport", 14,
         "Alex Morgan"),
        (10, "Priya Raman", "Cooper", "Dog Walk - 30 min", 9, "Jamie Lee"),
        (12, "Megan Foster", "Simba", "House Sitting - Per Night", 18,
         "Priya Shah"),
    ]
    svc_by_name = {s_["name"]: s_ for s_ in s.services}
    for i, (offset, client, pet, service, hour, staff) in enumerate(plan):
        svc = svc_by_name[service]
        minutes = svc["duration"] or 30
        start = t(hour, 0)
        end_minutes = (hour * 60 + minutes) % (24 * 60)
        end = t(end_minutes // 60, end_minutes % 60)
        if offset < -1:
            status = "Completed"
        elif offset <= 0:
            status = "In progress" if offset == 0 else "Completed"
        elif offset <= 4:
            status = "Confirmed"
        else:
            status = "Pending"
        if i in (7, 19):
            status = "Cancelled"
        booking = dict(
            request_date=d(today, offset - rnd.randint(2, 10)),
            client=client, pet=pet_label[pet], pet_count=1, service=service,
            date=d(today, offset), start=start, end=end, qty=1,
            distance=round(rnd.uniform(2, 14), 1), staff=staff,
            status=status,
            confirm_sent="Yes" if status not in ("Pending", "Enquiry")
            else "No",
            reminder_sent="Yes" if offset < 2 else "No",
            recurring="Weekly" if service.startswith("Dog Walk") else "None",
            discount_type="None",
            notes="")
        if status == "Cancelled":
            booking["cancel_reason"] = rnd.choice(
                ["Client away", "Pet unwell", "Weather"])
            booking["notes"] = "Cancelled by client - offered a reschedule"
        if service == "Overnight Pet Sitting":
            booking["qty"] = 2
            booking["notes"] = "Two nights - keys collected in advance"
        if service == "House Sitting - Per Night":
            booking["qty"] = 4
            booking["notes"] = "Holiday cover - bins out Tuesday"
        if service == "Pet Sitting - Half Day":
            booking["qty"] = 4
            booking["notes"] = "Four hours of in-home care"
        if client == "Sarah Mitchell" and pet == "Bella":
            booking["extra_pets"] = "Max joins the walk"
            booking["pet_count"] = 2
        s.bookings.append(booking)

    # --------------------------------------------------------------- visits
    walk_services = ("Dog Walk - 30 min", "Dog Walk - 60 min")
    visit_index = 0
    for idx, bk in enumerate(s.bookings):
        if bk["status"] not in ("Completed", "In progress"):
            continue
        visit_index += 1
        booking_id = f'BK-{idx + 1:04d}'
        start_hour = bk["start"].hour
        arrive = t(start_hour, rnd.choice([0, 2, 5, 8]))
        dur = svc_by_name[bk["service"]]["duration"] or 30
        depart_minutes = (arrive.hour * 60 + arrive.minute + dur) % (24 * 60)
        depart = t(depart_minutes // 60, depart_minutes % 60)
        is_walk = bk["service"] in walk_services
        visit = dict(
            booking=booking_id, date=bk["date"], staff=bk["staff"],
            arrive=arrive, depart=depart,
            fed="Yes" if not is_walk else "N/A",
            water="Yes",
            meds="Yes" if bk["service"] == "Medication Administration"
            else "N/A",
            potty=rnd.choice(["Both", "Pee only", "Litter cleaned"]),
            play="15 min fetch" if is_walk else "10 min wand toy play",
            grooming="Paws wiped" if is_walk else "Brushed",
            mood=rnd.choice(["Happy", "Calm", "Playful"]),
            appetite=rnd.choice(["Normal", "Normal", "Reduced"]),
            health="All normal", incident="No",
            photos="Photo sent to owner", update_sent="Yes",
            checklist="Yes", status="Completed",
            notes="Visit completed as planned")
        if is_walk:
            visit["walk_start"] = arrive
            walk_end_minutes = (arrive.hour * 60 + arrive.minute + dur - 5)
            visit["walk_end"] = t((walk_end_minutes // 60) % 24,
                                  walk_end_minutes % 60)
            visit["walk_distance"] = round(dur / 20 + rnd.uniform(0.2, 1.4), 1)
        if visit_index == 6:
            visit.update(status="Missed", notes="Client was home - no access "
                                                "needed, visit cancelled on "
                                                "arrival",
                         update_sent="Yes", mood="", appetite="")
        if visit_index == 11:
            visit.update(incident="Yes", incident_ref="IN-002",
                         health="Small cut on left front paw - cleaned",
                         notes="Owner notified immediately, vet not required")
        s.visits.append(visit)

    # ------------------------------------------------------------- invoices
    inv_plan = [
        ("Sarah Mitchell", -26, "Dog walking - 4 visits", 4, 25, "Paid"),
        ("Priya Raman", -25, "Dog walking - weekly package", 4, 25, "Paid"),
        ("Megan Foster", -24, "Cat feeding visits", 6, 22, "Paid"),
        ("Daniel Brooks", -22, "Dog walking - 60 min x 3", 3, 40, "Paid"),
        ("James Okafor", -20, "Drop-in visits x 5", 5, 26, "Paid"),
        ("Luis Hernandez", -18, "Dog walking - 30 min x 4", 4, 25, "Paid"),
        ("Chloe Bennett", -15, "Puppy visits x 3", 3, 28, "Partially paid"),
        ("Megan Foster", -12, "Cat feeding - fortnight cover", 10, 22, "Paid"),
        ("Daniel Brooks", -10, "Half day pet sitting", 4, 18, "Paid"),
        ("James Okafor", -9, "Overnight pet sitting x 2 nights", 2, 95,
         "Sent"),
        ("Sarah Mitchell", -6, "Dog walking - 60 min x 2", 2, 40, "Sent"),
        ("Megan Foster", -4, "Medication visits x 3", 3, 18, "Sent"),
        ("Priya Raman", -2, "Dog walking - 30 min x 2", 2, 25, "Draft"),
        ("Chloe Bennett", -1, "Drop-in visit - rabbit care", 1, 26, "Draft"),
        ("Luis Hernandez", -21, "Dog walking - 30 min x 6", 6, 25, "Paid"),
        ("Daniel Brooks", -16, "Senior pet care visits x 4", 4, 32, "Paid"),
        ("Sarah Mitchell", -13, "Dog walking - 60 min x 4", 4, 40, "Paid"),
        ("Chloe Bennett", -10, "Puppy visits x 5", 5, 28, "Paid"),
        ("James Okafor", -7, "Drop-in visits x 4", 4, 26, "Paid"),
        ("Megan Foster", -5, "Cat feeding - week cover", 7, 22, "Sent"),
    ]
    # A few invoices are raised straight from a booking instead of being
    # typed by hand - that is what the Booking ref column is for.  The
    # client and the wording come from the booking itself, so the two
    # records can never drift apart.  (booking number, days ago, status)
    linked_plan = [(19, -3, "Sent"), (21, -2, "Sent"), (22, -1, "Draft")]
    for i, (client, offset, desc, qty, rate, status) in enumerate(inv_plan):
        s.invoices.append(dict(
            date=d(today, offset), client=client, booking="",
            description=desc, qty=qty, rate=rate, status=status,
            fees=0, discount=0,
            deposit=0,
            sent_date=d(today, offset) if status != "Draft" else None,
            reminder_sent="Yes" if status == "Sent" and offset < -7 else "No",
            notes="Thank you for your business" if status == "Paid" else ""))
    for number, offset, status in linked_plan:
        booked = s.bookings[number - 1]
        ref = f"BK-{number:04d}"
        pet_name = booked["pet"].split(" (")[0]
        # No Qty / Rate: the amount comes from the linked booking.
        s.invoices.append(dict(
            date=d(today, offset), client=booked["client"], booking=ref,
            description=f'{booked["service"]} for {pet_name}', status=status,
            fees=0, discount=0, deposit=0,
            sent_date=d(today, offset) if status != "Draft" else None,
            reminder_sent="No",
            notes=f"Raised from booking {ref} - the amount comes straight "
                  f"from the booking"))

    # ------------------------------------------------------------- payments
    # Payments settle the invoice *including* tax, so the invoice shows as
    # Paid rather than part paid.  `share` < 1 leaves a balance on purpose.
    def _gross(index: int) -> float:
        qty, rate = inv_plan[index][3], inv_plan[index][4]
        gross = qty * rate
        if (cfg.tax_registered == "Yes"
                and cfg.prices_include_tax != "Yes"):
            gross *= 1 + cfg.tax_rate
        return round(gross, 2)

    #        invoice, day, method, share paid, tip
    pay_plan = [
        (0, -24, "Card - online", 1.0, 5.0),
        (1, -23, "Bank transfer", 1.0, 0.0),
        (2, -21, "Card - in person", 1.0, 0.0),
        (3, -19, "Bank transfer", 1.0, 10.0),
        (4, -17, "Digital wallet", 1.0, 0.0),
        (5, -14, "Cash", 1.0, 0.0),
        (6, -11, "Card - online", 0.45, 0.0),
        (7, -8, "Bank transfer", 1.0, 0.0),
        (8, -6, "Card - online", 1.0, 8.0),
        (14, -20, "Bank transfer", 1.0, 0.0),
        (15, -15, "Card - online", 1.0, 12.0),
        (16, -12, "Digital wallet", 1.0, 0.0),
        (17, -9, "Card - in person", 1.0, 0.0),
        (18, -6, "Bank transfer", 1.0, 5.0),
        (9, -3, "Card - online", 1.0, 15.0),
    ]
    for inv_index, offset, method, share, tip in pay_plan:
        client = inv_plan[inv_index][0]
        amount = round(_gross(inv_index) * share, 2)
        s.payments.append(dict(
            date=d(today, offset), client=client,
            invoice_no=f"INV-{1001 + inv_index}", amount=amount,
            method=method, reference=f"REF{rnd.randint(10000, 99999)}",
            tip=tip, late_fee=0, refund=0,
            deposit="No", confirmed="Yes",
            reconciled="Yes" if offset < -2 else "No",
            notes="Part payment - balance to follow" if share < 1 else ""))

    # ------------------------------------------------------------- expenses
    exp_plan = [
        (-29, "Fuel", "Weekly fuel - client visits", "QuickFuel", 62.40,
         "Card - online"),
        (-27, "Pet supplies", "Poop bags, wipes and treats", "PetMart",
         48.75, "Card - in person"),
        (-25, "Software & subscriptions", "Scheduling app monthly",
         "PetDesk", 29.00, "Direct debit"),
        (-24, "Marketing & advertising", "Local Facebook ads", "Meta",
         45.00, "Card - online"),
        (-22, "Insurance", "Business liability - monthly",
         "PetGuard Business Insurance", 48.00, "Direct debit"),
        (-20, "Cleaning supplies", "Enzyme cleaner and towels",
         "CleanCo", 32.10, "Cash"),
        (-18, "Equipment", "Two slip leads and a treat pouch", "PetMart",
         39.90, "Card - in person"),
        (-16, "Fuel", "Weekly fuel - client visits", "QuickFuel", 58.20,
         "Card - online"),
        (-14, "Vehicle maintenance", "Tyre rotation and oil", "AutoFix",
         86.00, "Bank transfer"),
        (-12, "Pet food & treats", "Emergency food supply", "PetMart",
         38.40, "Card - in person"),
        (-11, "Parking & tolls", "City parking - vet transport", "City Park",
         14.00, "Card - in person"),
        (-9, "Staff wages", "Jamie Lee - fortnight", "Payroll", 396.00,
         "Bank transfer"),
        (-8, "Training & certification", "Canine first aid refresher",
         "PetCare Academy", 65.00, "Card - online"),
        (-6, "Fuel", "Weekly fuel - client visits", "QuickFuel", 60.80,
         "Card - online"),
        (-5, "Phone & internet", "Mobile plan", "TelCo", 45.00,
         "Direct debit"),
        (-4, "Office & admin", "Printer paper and ink", "OfficeHub", 27.65,
         "Card - online"),
        (-3, "Contractor payments", "Tom Reed - weekend walks", "Tom Reed",
         145.00, "Bank transfer"),
        (-2, "Vet & emergency supplies", "First aid kit restock",
         "Riverton Vet Clinic", 42.30, "Card - in person"),
        (-1, "Pet supplies", "Waste bags bulk pack", "PetMart", 24.99,
         "Card - online"),
        (0, "Bank & merchant fees", "Card processing fees", "PayGate", 18.45,
         "Direct debit"),
    ]
    recurring_map = {
        "Software & subscriptions": "Monthly",
        "Insurance": "Monthly",
        "Phone & internet": "Monthly",
        "Staff wages": "Fortnightly",
    }
    for offset, category, desc, supplier, amount, method in exp_plan:
        s.expenses.append(dict(
            date=d(today, offset), category=category, description=desc,
            supplier=supplier, amount=amount, method=method, type="Business",
            deductible=1.0, receipt="Receipts folder",
            recurring=recurring_map.get(category, "No"),
            approval="Approved", notes=""))

    # Two special cases so the Business use % and Business / personal
    # columns are shown doing their job.
    s.expenses.append(dict(
        date=d(today, -7), category="Phone & internet",
        description="Home broadband - part business use", supplier="TelCo",
        amount=55.00, method="Direct debit", type="Business",
        deductible=0.6, receipt="Receipts folder", recurring="Monthly",
        approval="Approved",
        notes="Only 60% is claimable - see the Business use % column"))
    s.expenses.append(dict(
        date=d(today, -13), category="Pet supplies",
        description="Toys for my own dog", supplier="PetMart",
        amount=32.00, method="Card - in person", type="Personal",
        deductible=0.0, receipt="", recurring="No", approval="Approved",
        notes="Personal spend - left out of profit and tax figures"))

    # -------------------------------------------------------------- mileage
    for i in range(18):
        offset = -28 + i * 2
        staff = ["Alex Morgan", "Jamie Lee", "Priya Shah"][i % 3]
        client = s.clients[i % 7]["name"]
        start_odo = 48200 + i * 37
        km = round(rnd.uniform(6, 28), 1)
        s.mileage.append(dict(
            date=d(today, offset), staff=staff, client=client,
            purpose="Client visit" if i % 4 else "Supplies run",
            start_loc="Home office", end_loc=f"{client} - client home",
            start_odo=start_odo, end_odo=round(start_odo + km, 1),
            round_trip="Yes" if i % 3 else "No",
            fuel=0, parking=4.0 if i % 5 == 0 else 0,
            tolls=2.5 if i % 6 == 0 else 0,
            travel_mins=int(km * 2.2), notes=""))

    # --------------------------------------------------------------- health
    s.health = [
        dict(date=d(today, -9), time=t(7, 10), pet="Milo (Megan Foster)",
             type="Medication", item="Felimazole 2.5mg",
             dosage="1 tablet in food", sched_time=t(7, 0),
             given_time=t(7, 10), staff="Priya Shah", status="Given",
             supply=18, refill_due=d(today, 12), cost=0, notified="Yes",
             notes="Ate the full portion"),
        dict(date=d(today, -5), time=t(7, 5), pet="Milo (Megan Foster)",
             type="Medication", item="Felimazole 2.5mg",
             dosage="1 tablet in food", sched_time=t(7, 0),
             given_time=t(7, 5), staff="Priya Shah", status="Given",
             supply=16, refill_due=d(today, 12), cost=0, notified="Yes",
             notes=""),
        dict(date=d(today, -2), time=t(7, 0), pet="Milo (Megan Foster)",
             type="Medication", item="Felimazole 2.5mg",
             dosage="1 tablet in food", sched_time=t(7, 0),
             staff="Priya Shah", status="Missed", supply=16,
             refill_due=d(today, 12), cost=0, notified="Yes",
             notes="Refused food - owner called, giving it tonight"),
        dict(date=d(today, -20), time=t(10, 30), pet="Charlie (Robert Nguyen)",
             type="Vet visit", item="Arthritis review",
             dosage="Metacam 0.8ml daily", staff="Alex Morgan",
             status="Not required", vet_appt=d(today, 25), cost=110.0,
             notified="Yes", notes="Owner attended, we transported"),
        dict(date=d(today, -15), time=t(9, 0), pet="Bella (Sarah Mitchell)",
             type="Vaccination", item="Annual booster",
             dosage="-", staff="Alex Morgan", status="Not required",
             cost=86.0, notified="Yes", notes="Certificate photographed"),
        dict(date=d(today, -1), time=t(13, 20), pet="Teddy (Daniel Brooks)",
             type="Health observation", item="Loose stool",
             dosage="-", staff="Alex Morgan", status="Not required",
             cost=0, notified="Yes",
             notes="Monitor - owner changing food gradually"),
        dict(date=d(today, 3), time=t(7, 0), pet="Milo (Megan Foster)",
             type="Medication", item="Felimazole 2.5mg",
             dosage="1 tablet in food", sched_time=t(7, 0),
             staff="Priya Shah", status="Scheduled", supply=14,
             refill_due=d(today, 12), cost=0, notified="No", notes=""),
        dict(date=d(today, 10), time=t(11, 0), pet="Poppy (Chloe Bennett)",
             type="Vet visit", item="Nail trim and check",
             dosage="-", staff="Priya Shah", status="Scheduled",
             vet_appt=d(today, 10), cost=0, notified="Yes", notes=""),
    ]

    # ------------------------------------------------------------ incidents
    s.incidents = [
        dict(date=d(today, -22), time=t(10, 40), client="Luis Hernandez",
             pet="Ruby (Luis Hernandez)", staff="Alex Morgan",
             ref="BK-0007", type="Aggression", severity="Medium",
             description="Ruby lunged at an off-lead dog on Oakfield Road",
             action="Moved to a side street, treat scatter, finished the "
                    "walk on quiet streets",
             vet_contacted="No", clinic="-", owner_notified="Yes",
             notified_at="Same day 11:05", follow_up="Yes",
             follow_due=d(today, -15), status="Resolved", cost=0,
             claim="No", notes="Route changed permanently"),
        dict(date=d(today, -11), time=t(16, 15), client="Chloe Bennett",
             pet="Oscar (Chloe Bennett)", staff="Priya Shah",
             ref="BK-0015", type="Injury", severity="Low",
             description="Small cut on the left front paw from a stick",
             action="Cleaned with saline and covered, photo sent to owner",
             vet_contacted="No", clinic="-", owner_notified="Yes",
             notified_at="Same day 16:30", follow_up="Yes",
             follow_due=d(today, -4), status="Resolved", cost=0,
             claim="No", notes="Healed well, checked next visit"),
        dict(date=d(today, -3), time=t(8, 20), client="Megan Foster",
             pet="Simba (Megan Foster)", staff="Priya Shah",
             ref="BK-0020", type="Escape", severity="High",
             description="Simba dashed into the hallway when the front door "
                         "opened",
             action="Door closed immediately, Simba recovered within 2 "
                    "minutes, no injuries",
             vet_contacted="No", clinic="-", owner_notified="Yes",
             notified_at="Same day 08:35", follow_up="Yes",
             follow_due=d(today, 4), status="In progress", cost=0,
             claim="No",
             notes="Added a door-dash warning to the pet profile"),
    ]

    # ------------------------------------------------------------- messages
    msg_plan = [
        (-26, "Sarah Mitchell", "Booking confirmation", "Email", "Outgoing",
         "Confirmed 4 walks for the month", "Yes", 5, "", "No"),
        (-24, "Priya Raman", "Visit update", "WhatsApp", "Outgoing",
         "Photo and walk summary sent", "Yes", 5, "", "No"),
        (-21, "Megan Foster", "Payment reminder", "Email", "Outgoing",
         "Invoice INV-1003 reminder", "Yes", 4, "", "No"),
        (-18, "Daniel Brooks", "Follow-up", "SMS", "Outgoing",
         "Checked in after Daisy's long run", "Yes", 5,
         "Daisy slept all afternoon - very happy", "No"),
        (-16, "Chloe Bennett", "Complaint", "Phone call", "Incoming",
         "Visit ran 15 minutes late", "Yes", 3,
         "Understood the traffic, asked for earlier slots", "Yes"),
        (-14, "James Okafor", "Booking reminder", "Email", "Outgoing",
         "Overnight stay starts Friday", "Yes", 5, "", "No"),
        (-12, "Luis Hernandez", "Thank you", "SMS", "Outgoing",
         "Thanks for the referral", "No", 5, "", "No"),
        (-9, "Sarah Mitchell", "Review request", "Email", "Outgoing",
         "Asked for a Google review", "Yes", 5,
         "Left a 5 star review - mentioned Jamie", "No"),
        (-7, "Megan Foster", "Visit update", "App message", "Outgoing",
         "Milo medication log sent", "Yes", 5, "", "No"),
        (-5, "Robert Nguyen", "Win-back offer", "Email", "Outgoing",
         "20% off the first walk back", "No", "", "", "No"),
        (-3, "Amelia Clarke", "Booking confirmation", "Email", "Outgoing",
         "Meet and greet booked for next week", "Yes", "", "", "No"),
        (-1, "Chloe Bennett", "Follow-up", "SMS", "Outgoing",
         "Checked Oscar's paw is healing", "Yes", 5,
         "Paw fine, thank you for the care", "No"),
    ]
    for (offset, client, mtype, channel, direction, summary, response,
         rating, feedback, complaint) in msg_plan:
        s.messages.append(dict(
            date=d(today, offset), client=client, type=mtype,
            channel=channel, direction=direction, summary=summary,
            response=response, rating=rating or None, feedback=feedback,
            complaint=complaint,
            issue="Visit arrived late due to traffic"
            if complaint == "Yes" else "",
            resolution="Resolved" if complaint == "Yes" else "Not required",
            resolved_date=d(today, offset + 1) if complaint == "Yes"
            else None,
            follow_due=d(today, offset + 30) if mtype == "Win-back offer"
            else None,
            follow_done="No" if mtype == "Win-back offer" else "Yes",
            notes=""))

    # ------------------------------------------------------------ inventory
    inv_items = [
        ("Waste bags (roll of 300)", "Waste bags", "PetMart", "Roll", 6.50,
         12, 6, 24, -20, None, 9),
        ("Training treats 500g", "Treats", "PetMart", "Bag", 9.20, 4, 5, 10,
         -14, 180, 6),
        ("Enzyme cleaner 1L", "Cleaning", "CleanCo", "Bottle", 11.40, 3, 2, 6,
         -25, 400, 2),
        ("Slip lead", "Leads & harnesses", "PetMart", "Each", 8.75, 6, 3, 6,
         -18, None, 1),
        ("Pet first aid kit", "First aid", "PetCare Academy", "Kit", 34.00,
         2, 2, 2, -60, 500, 0),
        ("Saline wound wash", "First aid", "Riverton Vet Clinic", "Bottle",
         6.80, 1, 2, 4, -30, 120, 1),
        ("Flea treatment (spot on)", "Medication", "Riverton Vet Clinic",
         "Pack", 22.00, 2, 1, 3, -45, 60, 1),
        ("Emergency dry food 2kg", "Pet food", "PetMart", "Bag", 14.60, 2, 1,
         3, -35, 150, 1),
        ("Hand sanitiser 500ml", "Cleaning", "CleanCo", "Bottle", 5.20, 5, 3,
         6, -22, 300, 2),
        ("Reflective vest", "Equipment", "SafetyGear", "Each", 18.00, 3, 2, 2,
         -90, None, 0),
        ("Poo bag dispenser", "Equipment", "PetMart", "Each", 4.20, 8, 4, 8,
         -40, None, 2),
        ("Business cards (250)", "Office", "PrintFast", "Pack", 32.00, 1, 1,
         2, -75, None, 1),
    ]
    for (item, category, supplier, unit, cost, qty, min_qty, reorder,
         purchase_off, expiry_off, used) in inv_items:
        s.inventory.append(dict(
            item=item, category=category, supplier=supplier, unit=unit,
            unit_cost=cost, qty=qty, min_qty=min_qty, reorder=reorder,
            last_purchase=d(today, purchase_off), qty_purchased=reorder,
            expiry=d(today, expiry_off) if expiry_off else None,
            used_month=used, notes=""))

    # ---------------------------------------------------------------- tasks
    s.tasks = [
        dict(task="Send October invoices", category="Invoicing",
             due=d(today, 2), owner="Alex Morgan", priority="High",
             status="In progress", notes="14 invoices to issue"),
        dict(task="Chase Tom Reed first aid certificate",
             category="Staff", due=d(today, -2), owner="Alex Morgan",
             priority="Urgent", status="Not started",
             notes="Certificate expired"),
        dict(task="Order waste bags and treats", category="Inventory",
             due=d(today, 5), owner="Jamie Lee", priority="Medium",
             status="Not started", notes="Two items below minimum"),
        dict(task="Call Robert Nguyen - win-back", category="Marketing",
             due=d(today, 7), owner="Alex Morgan", priority="Medium",
             status="Not started", notes="Inactive 4 months"),
        dict(task="Book insurance renewal review", category="Admin",
             due=d(today, 30), owner="Alex Morgan", priority="Low",
             status="Not started", notes=""),
        dict(task="Update holiday surcharge dates", category="Admin",
             due=d(today, 45), owner="Alex Morgan", priority="Low",
             status="Not started", notes="December peak period"),
    ]

    # ---------------------------------------------------- owner withdrawals
    s.drawings = [
        dict(date=d(today, -60), amount=400, notes="Owner drawings"),
        dict(date=d(today, -30), amount=450, notes="Owner drawings"),
        dict(date=d(today, -5), amount=350, notes="Owner drawings"),
    ]

    return s
