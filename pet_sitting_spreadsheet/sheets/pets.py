"""`Pets` - full pet profiles: care routine, medical, vaccinations, warnings."""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from, number_check
from .common import alert_cf, blank, id_col

NAME = "Pets"

_LAST_VISIT = ('SUMPRODUCT(MAX(([[Visit Log.pet]]={label}{r})'
               '*([[Visit Log.status]]="Completed")*[[Visit Log.date]]))')


def spec(cfg: Config) -> SheetSpec:
    columns = [
        id_col("name", "PetPrefix"),
        Col("name", "Pet name", 14, "text"),
        Col("owner", "Owner (client)", 20, "text",
            validate=list_from("ClientNames"),
            note="Pick the client from the drop down so bookings, visits "
                 "and invoices all line up."),
        Col("label", "Pet reference", 24, "text",
            formula='=IF({name}{r}="","",{name}{r}&" ("&{owner}{r}&")")',
            note="This is the value used by the Bookings, Visit Log and "
                 "Health Log drop downs."),
        Col("client_id", "Client ID", 10, "text",
            formula=blank("owner",
                          'IFERROR(INDEX([[Clients.id]],'
                          'MATCH({owner}{r},[[Clients.name]],0)),"")')),
        Col("type", "Pet type", 11, "text",
            validate=list_from("PetTypeList")),
        Col("breed", "Breed", 20, "text"),
        Col("dob", "Date of birth", 13, "date", validate=date_check()),
        Col("age", "Age (yrs)", 9, "number1",
            formula=blank("dob", 'ROUND(YEARFRAC({dob}{r},TODAY()),1)')),
        Col("gender", "Gender", 14, "text",
            validate=list_from("PetGenderList")),
        Col("weight", "Weight (kg)", 10, "number1",
            validate=number_check(0, 200)),
        Col("colour", "Colour & markings", 22, "text"),
        Col("photo", "Photo link", 18, "text",
            note="Paste a link to the photo in your cloud folder, or "
                 "insert a small picture next to the row."),
        Col("microchip", "Microchip number", 16, "text"),
        Col("temperament", "Temperament", 16, "text",
            validate=list_from("TemperamentList")),
        Col("behaviour", "Behaviour issues", 28, "wrap"),
        Col("allergies", "Allergies", 20, "wrap"),
        Col("medical", "Medical conditions / special needs", 30, "wrap"),
        Col("vet_name", "Veterinarian", 22, "text"),
        Col("vet_phone", "Vet phone", 16, "text"),
        Col("emerg_clinic", "Emergency clinic", 22, "text"),
        Col("emerg_phone", "Emergency clinic phone", 16, "text"),
        Col("vacc_date", "Vaccinated on", 13, "date", validate=date_check()),
        Col("vacc_expiry", "Vaccination expires", 13, "date",
            validate=date_check()),
        Col("vacc_status", "Vaccination status", 17, "status",
            formula=blank("vacc_expiry",
                          'IF({vacc_expiry}{r}<TODAY(),"Expired",'
                          'IF({vacc_expiry}{r}-TODAY()<=VaccAlertDays,'
                          '"Due in "&TEXT({vacc_expiry}{r}-TODAY(),"0")'
                          '&" days","Valid"))'),
            cf=[{"type": "text", "criteria": "containing",
                 "value": "Expired", "fmt": "bad"},
                {"type": "text", "criteria": "containing",
                 "value": "Due in", "fmt": "warn"},
                {"type": "text", "criteria": "containing",
                 "value": "Valid", "fmt": "good"}]),
        Col("insurer", "Pet insurance", 18, "text"),
        Col("policy", "Policy number", 14, "text"),
        Col("insurance_expiry", "Insurance renewal", 13, "date",
            validate=date_check()),
        Col("feeding", "Feeding instructions", 30, "wrap"),
        Col("food", "Food type", 18, "text"),
        Col("portion", "Portion size", 13, "text"),
        Col("feed_schedule", "Feeding schedule", 18, "text"),
        Col("medication", "Medication", 20, "text"),
        Col("dosage", "Dosage & instructions", 26, "wrap"),
        Col("med_schedule", "Medication schedule", 18, "text"),
        Col("walking", "Walking & exercise preferences", 30, "wrap"),
        Col("potty", "Potty / litter routine", 26, "wrap"),
        Col("grooming", "Grooming requirements", 24, "wrap"),
        Col("favourites", "Favourite toys, treats & games", 28, "wrap"),
        Col("risk", "Risk flag", 16, "status",
            validate=list_from("RiskFlagList"),
            cf=[{"type": "text", "criteria": "not containing",
                 "value": "None", "fmt": "warn"}]),
        Col("handling", "Handling instructions", 30, "wrap"),
        Col("warnings", "Safety warnings", 30, "wrap"),
        Col("visits", "Visits", 8, "int",
            formula=blank("label",
                          'COUNTIFS([[Visit Log.pet]],{label}{r},'
                          '[[Visit Log.status]],"Completed")')),
        Col("last_visit", "Last visit", 13, "date",
            formula=('=IF({label}{r}="","",'
                     f'IF({_LAST_VISIT}=0,"",{_LAST_VISIT}))')),
        Col("meds_logged", "Med records", 10, "int",
            formula=blank("label",
                          'COUNTIFS([[Health Log.pet]],{label}{r})')),
        Col("alert", "Alerts", 30, "status",
            formula=blank(
                "name",
                'TRIM(IF({vacc_status}{r}="Expired","VACCINATION EXPIRED. ",'
                'IF(LEFT({vacc_status}{r},6)="Due in","Vaccination due. ",""))'
                '&IF(AND({risk}{r}<>"",{risk}{r}<>"None"),{risk}{r}&". ","")'
                '&IF(AND({medication}{r}<>"",{medication}{r}<>"None",'
                '{medication}{r}<>"-"),"On medication. ","")'
                '&IF({allergies}{r}<>"",IF(OR({allergies}{r}="None",'
                '{allergies}{r}="None known"),"","Allergy: "'
                '&{allergies}{r}),""))'),
            cf=alert_cf() + [{"type": "text", "criteria": "containing",
                              "value": "EXPIRED", "fmt": "bold_bad"},
                             {"type": "text", "criteria": "containing",
                              "value": "Allergy", "fmt": "warn"},
                             {"type": "text", "criteria": "containing",
                              "value": "risk", "fmt": "warn"}]),
    ]

    return SheetSpec(
        name=NAME,
        title="Pet Profiles",
        subtitle="Everything a sitter needs before they walk through the "
                 "door: routine, medical, vet, vaccination status and "
                 "safety warnings.",
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=Palette.primary,
        freeze_cols=2,
        samples=sample(cfg).pets,
        help_text="Choose the owner from the drop down first. The grey "
                  "'Pet reference' column is what bookings and visit logs "
                  "use, so two pets with the same name never get mixed up.",
    )
