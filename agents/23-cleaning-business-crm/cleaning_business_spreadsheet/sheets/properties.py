"""The Properties register - the places you actually clean."""

from __future__ import annotations

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Col, SheetSpec


def build_register(cfg: Config, fmts: FormatBook) -> SheetSpec:
    from .. import sample_data as sd

    rows = cfg.row_count("Properties")
    samples = sd.PROPERTIES if cfg.include_sample_data else []
    unit = cfg.area_unit
    dist = cfg.distance_unit

    columns = [
        Col("id", "Property ID", 12, "text",
            formula='IF({property_name}{r}="","",' +
                    f'"PR-"&TEXT(ROW()-{4},"0000"))'),
        Col("property_name", "Property Name", 24, "text",
            note="Short label used in drop-downs, e.g. "
                 "'Whitfield - Family Home'."),
        Col("client", "Client", 24, "text",
            validate={"type": "list", "source": "=Clients_Names",
                      "ignore_blank": True}),
        Col("type", "Type", 14, "center",
            validate={"type": "list", "source": [
                "House", "Apartment", "Condo", "Office", "Retail",
                "Restaurant", "Warehouse", "School", "Medical",
                "Airbnb / Rental", "Other"]}),
        Col("address", "Address", 30, "text"),
        Col("city", "City / Area", 14, "text"),
        Col("postcode", "Postcode / ZIP", 11, "text"),
        Col("size", f"Size ({unit})", 12, "decimal",
            validate={"type": "decimal", "criteria": "between",
                      "minimum": 0, "maximum": 500000},
            note="Floor area - the quote calculator prices from this."),
        Col("bedrooms", "Bedrooms", 10, "int",
            validate={"type": "whole", "criteria": "between",
                      "minimum": 0, "maximum": 30}),
        Col("bathrooms", "Bathrooms", 10, "int",
            validate={"type": "whole", "criteria": "between",
                      "minimum": 0, "maximum": 30}),
        Col("rooms", "Other Rooms", 10, "int",
            validate={"type": "whole", "criteria": "between",
                      "minimum": 0, "maximum": 50}),
        Col("floors", "Floors", 8, "int",
            validate={"type": "whole", "criteria": "between",
                      "minimum": 1, "maximum": 60}),
        Col("travel", f"Travel ({dist})", 11, "decimal",
            validate={"type": "decimal", "criteria": "between",
                      "minimum": 0, "maximum": 500}),
        Col("access", "Access / Keys", 18, "text",
            note="Key safe code, lockbox, doorman..."),
        Col("parking", "Parking", 12, "center",
            validate={"type": "list", "source": [
                "On site", "Street", "Permit", "Paid", "Difficult"]}),
        Col("pets", "Pets", 10, "center",
            validate={"type": "list",
                      "source": ["None", "Dog", "Cat", "Both", "Other"]}),
        Col("alarm", "Alarm / Codes", 14, "text"),
        Col("hazards", "Hazards", 18, "text",
            note="Pets, alarms, fragile items, steep stairs, chemicals."),
        Col("notes", "Notes", 26, "text"),
        Col("job_count", "Jobs", 9, "int_locked",
            formula='IF({property_name}{r}="","",'
                    'COUNTIF([[Jobs.property]],{property_name}{r}))'),
        Col("revenue", "Revenue", 13, "money_locked",
            formula='IF({property_name}{r}="","",'
                    'SUMIFS([[Jobs.price]],[[Jobs.property]],'
                    '{property_name}{r}))'),
    ]

    return SheetSpec(
        name="Properties",
        title="Property Register",
        subtitle="Every address you clean, with the size and layout the "
                 "quote calculator needs and the access details the crew "
                 "needs.",
        columns=columns,
        rows=rows,
        samples=samples,
        tab_color=Palette.primary,
    )
