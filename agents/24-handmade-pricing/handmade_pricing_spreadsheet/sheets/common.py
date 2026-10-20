"""Shared column factories and formula fragments for the handmade sheets.

Everything in here exists so that the forty tab modules stay short and, more
importantly, so that no sheet ever hard codes a column letter or a range.
Formulas are written with the tokens :mod:`..layout` understands:

    {key}{r}            same sheet, this row
    {key_first}         same sheet, top of the data block
    {key_last}          same sheet, bottom of the data block
    [[Sheet.key]]       the data block of `key` on another sheet
    [[Sheet.key#12]]    one cell of `key` on another sheet

Named ranges that point at the Settings tab (``HourlyRate``, ``ListingFee``,
``RoundingRule`` ...) are workbook scoped, so any sheet can use them.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from ..config import (CRAFT_SHEETS, PRICING_SCENARIOS, PRODUCT_CATEGORIES,
                      PRODUCT_STATUSES, ROUNDING_RULES, SALES_CHANNELS,
                      UNIT_CONVERSIONS, VOLUME_STEPS, Config, Palette)
from ..layout import Col, SheetSpec, blank_if, lookup, max_if, min_if, safe
from ..writer import (cf_bar, cf_formula, cf_text, date_check, list_from,
                      number_check, time_check, yes_no)

P = Palette

#: Rows are numbered from 5 down (1 title, 2 strapline, 3 nav, 4 headers).
FIRST_ROW = 5
#: Sentinel used wherever a MIN over a filtered set could come back empty.
NO_MATCH = 999999


# ---------------------------------------------------------------------------
# List data - written to the Lists tab and used by the drop downs
# ---------------------------------------------------------------------------

YES_NO = ["Yes", "No"]

DIFFICULTIES = ["Easy", "Medium", "Hard", "Expert"]
DIFFICULTY_FACTORS = [("Easy", 1.00), ("Medium", 1.15), ("Hard", 1.35),
                      ("Expert", 1.60)]

SIZES = ["XS", "S", "M", "L", "XL", "XXL", "One size", "Custom"]
SIZE_FACTORS = [("XS", 0.80), ("S", 0.90), ("M", 1.00), ("L", 1.10),
                ("XL", 1.25), ("XXL", 1.40), ("One size", 1.00),
                ("Custom", 1.00)]

RUSH_OPTIONS = ["No", "Yes - 1 week", "Yes - 48 hours", "Yes - 24 hours"]
RUSH_FACTORS = [("No", 1.00), ("Yes - 1 week", 1.15),
                ("Yes - 48 hours", 1.35), ("Yes - 24 hours", 1.50)]

SEASONS = ["All year", "Spring", "Summer", "Autumn", "Autumn / Winter",
           "Winter", "Holiday", "Wedding season", "Back to school"]

MATERIAL_CATEGORIES = [
    "Yarn", "Fibre", "Fabric", "Wax", "Fragrance", "Wick", "Vessel",
    "Stone", "Metal", "Findings", "Chain", "Bead", "Lumber", "Finish",
    "Hardware", "Notions", "Label", "Packaging", "Mailer", "Box", "Wrap",
    "Insert", "Clay", "Glaze", "Paper", "Ink", "Paint", "Leather", "Fill",
    "Consumable", "Other",
]

MATERIAL_STATUS = ["In stock", "Low", "Out of stock", "On order",
                   "Discontinued"]

SUPPLIER_TERMS = ["Prepaid", "Net 15", "Net 30", "Card on delivery",
                  "Deposit 50%"]

PACK_TYPES = ["Mailer", "Box", "Wrap", "Seal", "Insert", "Ribbon", "Tape",
              "Fill", "Gift box", "Envelope", "Tube", "Crate"]

CARRIER_OPTIONS = ["USPS", "UPS", "FedEx", "DHL", "Royal Mail",
                   "Local courier", "Hand delivery", "None"]

SERVICE_OPTIONS = ["First Class", "Priority Mail", "Ground", "2 Day",
                   "Overnight", "International", "Instant", "Local"]

ZONE_OPTIONS = ["Domestic", "Local", "Regional", "International", "N/A"]

CHANNEL_TYPES = ["Marketplace", "Own store", "In person", "Wholesale",
                 "Social", "Subscription", "Other"]

OVERHEAD_CATEGORIES = ["Space", "Utilities", "Insurance", "Platform",
                       "Software", "Professional", "Equipment", "Marketing",
                       "Supplies", "Training", "Vehicle", "Other"]

OVERHEAD_FREQUENCY = ["Weekly", "Monthly", "Quarterly", "Semi-annual",
                      "Annual", "One off"]

OVERHEAD_METHODS = ["Per unit", "Per hour", "Per month"]

EMPLOYMENT_TYPES = ["Owner", "Employee", "Contractor", "Volunteer",
                    "Family help"]

LABOR_TASKS = ["Cutting", "Sewing", "Crochet", "Knitting", "Assembly",
               "Pouring candles", "Wicking and labeling", "Stone setting",
               "Wire wrapping", "Sanding", "Finishing", "Woodworking",
               "Photography", "Listing and SEO", "Packing orders",
               "Customer service", "Craft fair setup", "Prototyping",
               "Quality check", "Repairs"]

SALE_STATUSES = ["Paid", "Pending", "Refunded", "Cancelled", "Part refunded"]

PAYMENT_METHODS = ["Card", "PayPal", "Etsy payments", "Bank transfer",
                   "Cash", "Cheque", "Gift card", "Other"]

ORDER_STATUSES = ["Quote", "Confirmed", "In production", "Packed",
                  "Invoiced", "Shipped", "Paid", "Overdue", "Cancelled"]

CUSTOMER_STATUSES = ["Prospect", "Approved", "On hold", "Closed",
                     "Do not supply"]

CUSTOMER_TERMS = ["Prepaid", "Net 15", "Net 30", "Net 45", "Net 60",
                  "Deposit 50%"]

PROMO_TYPES = ["Percentage", "Fixed amount", "Free shipping", "Buy one "
               "get one", "Bundle price", "Tiered"]

PRICE_REASONS = ["Launch", "Cost increase", "Repositioning", "Sale",
                 "Competitor match", "Fee change", "Seasonal",
                 "Discontinued", "Correction"]

COMPETITOR_POSITION = ["Cheaper", "Same", "Premium"]

WASTE_REASONS = ["Breakage", "Spillage", "Cutting error", "Defect",
                 "Misprint", "Shedding", "Knots", "Damaged in storage",
                 "Expired", "Wrong colour", "Sample", "Other"]

DEV_STAGES = ["Ideation", "Research", "Prototyping", "Testing",
              "Costing", "Photography", "Launch", "Done", "Shelved"]

DEV_TYPES = ["New product", "Pattern", "Process", "Price test",
             "Packaging", "Marketing", "Tooling", "Training"]

DEV_STATUSES = ["Not started", "On track", "At risk", "Overdue", "Done",
                "Shelved"]

EVENT_TYPES = ["Craft fair", "Market stall", "Pop-up shop", "Wholesale "
               "show", "Studio sale", "Festival", "Class / workshop"]

EVENT_STATUSES = ["Planned", "Booked", "Running", "Done", "Cancelled"]

CRAFT_LIST = list(CRAFT_SHEETS)

VARIATION_OPTIONS = ["Size", "Colour", "Scent", "Stone", "Finish",
                     "Material", "Length", "Personalisation", "Bundle",
                     "Gift wrap"]

FREQUENCY_UNITS = ["Per unit", "Per hour", "Per batch", "Per month"]

METAL_OPTIONS = ["Sterling silver", "14k gold filled", "18k gold filled",
                 "Brass", "Copper", "Stainless steel", "Aluminium",
                 "Niobium", "Mixed"]

YARN_WEIGHTS = ["Lace", "Fingering", "Sport", "DK", "Worsted", "Aran",
                "Bulky", "Super bulky", "Jumbo"]

WAX_TYPES = ["Soy 464", "Soy blend", "Paraffin", "Beeswax", "Coconut blend",
             "Palm", "Gel"]

WOOD_SPECIES = ["Hard maple", "Black walnut", "Cherry", "White oak",
                "Red oak", "Ash", "Birch", "Pine", "Cedar", "Mahogany",
                "Bamboo"]

FIBRE_TYPES = ["Merino", "Cotton", "Linen", "Bamboo", "Acrylic", "Alpaca",
               "Silk", "Wool blend", "Recycled"]

DIGITAL_TYPES = ["PDF pattern", "Video tutorial", "Printable art",
                 "SVG file", "Presets", "Course", "Template", "Clip art"]

DIGITAL_FORMATS = ["PDF", "PNG", "JPG", "SVG", "ZIP", "MP4", "EPUB",
                   "XLSX", "PSD"]

FEE_REVIEW_STATES = ["Current", "Check soon", "Out of date"]

FLAG_OK = "OK"
FLAG_THIN = "THIN"
FLAG_LOSS = "LOSS"
FLAG_REVIEW = "REVIEW"

#: name -> values, written to the Lists tab and turned into defined names
LISTS: Dict[str, List[str]] = {
    "YesNoList": YES_NO,
    "CategoryList": list(PRODUCT_CATEGORIES),
    "StatusList": list(PRODUCT_STATUSES),
    "ChannelList": list(SALES_CHANNELS),
    "CraftList": CRAFT_LIST,
    "DifficultyList": DIFFICULTIES,
    "SizeList": SIZES,
    "RushList": RUSH_OPTIONS,
    "SeasonList": SEASONS,
    "RoundingList": list(ROUNDING_RULES),
    "ScenarioList": list(PRICING_SCENARIOS),
    "VolumeList": [str(v) for v in VOLUME_STEPS],
    "UnitList": [u for u, _b, _f in UNIT_CONVERSIONS],
    "MaterialCategoryList": MATERIAL_CATEGORIES,
    "MaterialStatusList": MATERIAL_STATUS,
    "SupplierTermList": SUPPLIER_TERMS,
    "PackTypeList": PACK_TYPES,
    "CarrierList": CARRIER_OPTIONS,
    "ServiceList": SERVICE_OPTIONS,
    "ZoneList": ZONE_OPTIONS,
    "ChannelTypeList": CHANNEL_TYPES,
    "OverheadCategoryList": OVERHEAD_CATEGORIES,
    "OverheadFrequencyList": OVERHEAD_FREQUENCY,
    "OverheadMethodList": OVERHEAD_METHODS,
    "EmploymentTypeList": EMPLOYMENT_TYPES,
    "TaskList": LABOR_TASKS,
    "SaleStatusList": SALE_STATUSES,
    "PaymentMethodList": PAYMENT_METHODS,
    "OrderStatusList": ORDER_STATUSES,
    "CustomerStatusList": CUSTOMER_STATUSES,
    "CustomerTermList": CUSTOMER_TERMS,
    "PromoTypeList": PROMO_TYPES,
    "PriceReasonList": PRICE_REASONS,
    "PositionList": COMPETITOR_POSITION,
    "WasteReasonList": WASTE_REASONS,
    "DevStageList": DEV_STAGES,
    "DevTypeList": DEV_TYPES,
    "DevStatusList": DEV_STATUSES,
    "EventTypeList": EVENT_TYPES,
    "EventStatusList": EVENT_STATUSES,
    "VariationOptionList": VARIATION_OPTIONS,
    "FrequencyUnitList": FREQUENCY_UNITS,
    "MetalList": METAL_OPTIONS,
    "YarnWeightList": YARN_WEIGHTS,
    "WaxTypeList": WAX_TYPES,
    "WoodSpeciesList": WOOD_SPECIES,
    "FibreList": FIBRE_TYPES,
    "DigitalTypeList": DIGITAL_TYPES,
    "DigitalFormatList": DIGITAL_FORMATS,
    "FeeReviewList": FEE_REVIEW_STATES,
    "FlagList": [FLAG_OK, FLAG_THIN, FLAG_LOSS, FLAG_REVIEW],
}

#: which sheet each list is mainly used on - shown in the Lists tab help
LIST_USED_BY: Dict[str, str] = {
    "CategoryList": "Products",
    "StatusList": "Products",
    "ChannelList": "Products, Sales",
    "CraftList": "Products",
    "DifficultyList": "Products, craft tabs",
    "SizeList": "Products, Variations",
    "RushList": "Variations, Retail Calculator",
    "SeasonList": "Products",
    "RoundingList": "Settings",
    "ScenarioList": "Scenarios",
    "UnitList": "Materials, Material Usage",
    "MaterialCategoryList": "Materials",
    "MaterialStatusList": "Materials",
    "PackTypeList": "Packaging",
    "CarrierList": "Shipping",
    "ServiceList": "Shipping",
    "ZoneList": "Shipping",
    "ChannelTypeList": "Channels",
    "OverheadCategoryList": "Overhead",
    "OverheadFrequencyList": "Overhead",
    "OverheadMethodList": "Settings",
    "EmploymentTypeList": "Labor",
    "TaskList": "Labor",
    "SaleStatusList": "Sales",
    "PaymentMethodList": "Sales",
    "OrderStatusList": "Wholesale Orders",
    "CustomerStatusList": "Wholesale Customers",
    "CustomerTermList": "Wholesale Customers",
    "PromoTypeList": "Promotions",
    "PriceReasonList": "Price History",
    "PositionList": "Competitors",
    "WasteReasonList": "Waste Log",
    "DevStageList": "Development",
    "DevTypeList": "Development",
    "DevStatusList": "Development",
    "EventTypeList": "Events",
    "EventStatusList": "Events",
    "VariationOptionList": "Variations",
    "MetalList": "Jewelry",
    "YarnWeightList": "Crochet",
    "WaxTypeList": "Candles",
    "WoodSpeciesList": "Woodworking",
    "FibreList": "Crochet, Clothing",
    "DigitalTypeList": "Digital",
    "DigitalFormatList": "Digital",
}

#: defined names that must exist before the workbooks opens cleanly
REQUIRED_NAMES = ["ShopName", "TodayDate", "HourlyRate", "LaborCostHour",
                  "ListingFee", "TransactionFee", "ProcessingPercent",
                  "ProcessingFixed", "TargetRetailMargin", "RoundingRule",
                  "MarginWarning", "WholesaleDiscount", "MinimumWage",
                  "ProductIDs", "ProductNames", "MaterialIDs",
                  "MaterialNames"]


# ---------------------------------------------------------------------------
# Column factories
# ---------------------------------------------------------------------------

def tok(key: str) -> str:
    """`{key}` - a same-sheet column token."""
    return "{" + key + "}"


def row_ref(key: str) -> str:
    """`{key}{r}` - this column on the current row."""
    return "{" + key + "}{r}"


def block(key: str) -> str:
    """`{key_first}:{key_last}` - the whole column on this sheet."""
    return "{" + key + "_first}:{" + key + "_last}"


def other(sheet: str, key: str) -> str:
    """`[[Sheet.key]]` - the whole data block of a column elsewhere."""
    return "[[" + sheet + "." + key + "]]"


def other_cell(sheet: str, key: str, row: Any) -> str:
    return "[[" + sheet + "." + key + "#" + str(row) + "]]"


def same_row(sheet: str, key: str) -> str:
    """`[[Sheet.key#]]` - the cell on the same row of another sheet."""
    return "[[" + sheet + "." + key + "#]]"


def id_col(prefix: str, trigger: str = "name", width: float = 12.0,
           note: Optional[str] = None) -> Col:
    """Auto numbering column: blank until the trigger column is filled."""
    formula = (f'=IF({row_ref(trigger)}="","",'
               f'{prefix}&TEXT(ROW()-{FIRST_ROW - 1},"0000"))')
    return Col(key="id", header="ID", width=width, style="id",
               formula=formula,
               note=note or "Numbered automatically - do not type here.")


def text_col(key: str, header: str, width: float = 18.0,
             note: Optional[str] = None, group: str = "") -> Col:
    return Col(key=key, header=header, width=width, style="text",
               note=note, group=group)


def wrap_col(key: str, header: str, width: float = 34.0,
             note: Optional[str] = None, group: str = "") -> Col:
    return Col(key=key, header=header, width=width, style="wrap",
               note=note, group=group)


def list_col(key: str, header: str, list_name: str, width: float = 16.0,
             note: Optional[str] = None, group: str = "") -> Col:
    return Col(key=key, header=header, width=width, style="text",
               validate=list_from(list_name), note=note, group=group)


def yesno_col(key: str, header: str, width: float = 9.0,
              note: Optional[str] = None, group: str = "") -> Col:
    return Col(key=key, header=header, width=width, style="flag",
               validate=list_from("YesNoList"), note=note, group=group,
               cf=[cf_text("Yes", "good"), cf_text("No", "muted")])


def money_col(key: str, header: str, width: float = 12.0,
              note: Optional[str] = None, style: str = "money",
              group: str = "", maximum: float = 10000000) -> Col:
    return Col(key=key, header=header, width=width, style=style,
               validate=number_check(0, maximum), note=note, group=group)


def num_col(key: str, header: str, width: float = 11.0,
            note: Optional[str] = None, group: str = "",
            maximum: float = 1000000) -> Col:
    return Col(key=key, header=header, width=width, style="number",
               validate=number_check(0, maximum), note=note, group=group)


def int_col(key: str, header: str, width: float = 10.0,
            note: Optional[str] = None, group: str = "",
            maximum: float = 100000) -> Col:
    return Col(key=key, header=header, width=width, style="int",
               validate=number_check(0, maximum, decimal=False), note=note,
               group=group)


def pct_col(key: str, header: str, width: float = 10.0,
            note: Optional[str] = None, group: str = "") -> Col:
    return Col(key=key, header=header, width=width, style="percent",
               validate=number_check(0, 1), note=note, group=group)


def date_col(key: str, header: str, width: float = 13.0,
             note: Optional[str] = None, group: str = "") -> Col:
    return Col(key=key, header=header, width=width, style="date",
               validate=date_check(), note=note, group=group)


def time_col(key: str, header: str, width: float = 11.0,
             note: Optional[str] = None, group: str = "") -> Col:
    return Col(key=key, header=header, width=width, style="time",
               validate=time_check(), note=note, group=group)


def link_col(key: str, header: str, width: float = 14.0,
             note: Optional[str] = None, group: str = "") -> Col:
    return Col(key=key, header=header, width=width, style="link",
               note=note, group=group)


def product_col(key: str = "product", header: str = "Product ID",
                width: float = 13.0,
                note: Optional[str] = None, group: str = "") -> Col:
    """Drop down of every product ID in the catalog."""
    return Col(key=key, header=header, width=width, style="id",
               validate=list_from("ProductIDs"),
               note=note or "Pick a product from the list.", group=group)


def material_col(key: str = "material", header: str = "Material ID",
                 width: float = 13.0,
                 note: Optional[str] = None, group: str = "") -> Col:
    return Col(key=key, header=header, width=width, style="id",
               validate=list_from("MaterialIDs"),
               note=note or "Pick a material from the list.", group=group)


def inline_list(items: Sequence[str], note: str = "") -> Dict[str, Any]:
    """A short drop down that does not need a name on the Lists tab."""
    opts: Dict[str, Any] = {"validate": "list", "source": list(items)}
    if note:
        opts["input_message"] = note[:255]
    return opts


def fetch(sheet: str, match_key: str, fetch_key: str, value: str,
          fallback: str = '""') -> str:
    """INDEX/MATCH one value out of another register."""
    return lookup(value, other(sheet, match_key), other(sheet, fetch_key),
                  fallback)


def list_col_inline(key: str, header: str, items: Sequence[str],
                    width: float = 16.0, note: Optional[str] = None,
                    group: str = "") -> Col:
    return Col(key=key, header=header, width=width, style="text",
               validate=inline_list(items, note or ""), note=note,
               group=group)


def lookup_col(key: str, header: str, value: str, sheet: str,
               match_on: str, fetch: str, width: float = 20.0,
               style: str = "text", note: Optional[str] = None,
               group: str = "") -> Col:
    """INDEX/MATCH against another register."""
    formula = "=" + lookup(value, other(sheet, match_on), other(sheet, fetch),
                           '""')
    return Col(key=key, header=header, width=width, style=style,
               formula=formula, note=note, group=group)


def calc_col(key: str, header: str, body: str, width: float = 12.0,
             style: str = "money", note: Optional[str] = None,
             cf: Optional[List[Dict[str, Any]]] = None, group: str = "",
             hidden: bool = False) -> Col:
    """A locked formula column. `body` is the formula without the leading =."""
    return Col(key=key, header=header, width=width, style=style,
               formula="=" + body, note=note, cf=list(cf or []),
               group=group, hidden=hidden)


def sumifs(total_range: str, pairs: Sequence[Sequence[str]],
           fallback: str = "0") -> str:
    """SUMIFS(total_range, crit_range1, crit1, ...) as a formula body."""
    parts = [total_range]
    for crit_range, crit in pairs:
        parts.append(crit_range)
        parts.append(crit)
    return "IFERROR(SUMIFS(" + ",".join(parts) + "),0)" + (
        "" if fallback == "0" else "")


def sumifs_wild(total_range: str, crit_range: str, key: str,
                extra: Sequence[Sequence[str]] = ()) -> str:
    """SUMIFS where the criterion column holds a comma separated list."""
    pairs = [(crit_range, '"*"&' + row_ref(key) + '&"*"')]
    pairs.extend(extra)
    return "IFERROR(SUMIFS(" + ",".join(
        [total_range] + [p for pair in pairs for p in pair]) + "),0)"


def countifs(pairs: Sequence[Sequence[str]]) -> str:
    return "IFERROR(COUNTIFS(" + ",".join(
        [p for pair in pairs for p in pair]) + "),0)"


def rank_desc(value_key: str, id_key: str = "id",
              blank_sink: int = NO_MATCH) -> str:
    """Unique descending rank, ties broken by ID order, blanks last."""
    return (f'IF({row_ref(id_key)}="",{blank_sink},'
            f'COUNTIFS({block(value_key)},">"&N({row_ref(value_key)})'
            f',{block(value_key)},N({row_ref(value_key)}),'
            f'{block(id_key)},"<="&{row_ref(id_key)}))')


def rank_asc(value_key: str, id_key: str = "id",
             blank_sink: int = NO_MATCH) -> str:
    return (f'IF({row_ref(id_key)}="",{blank_sink},'
            f'COUNTIFS({block(value_key)},"<"&N({row_ref(value_key)})'
            f',{block(value_key)},N({row_ref(value_key)}),'
            f'{block(id_key)},"<="&{row_ref(id_key)}))')


def rank_flag(flag_key: str, value: str, id_key: str = "id") -> str:
    """Rank only the rows whose flag says `value`; the rest sink to the bottom.

    Used by the Dashboard to list the products that are losing money, the
    reviews that are overdue and the materials that need ordering, without an
    array formula - a plain MATCH on the hidden rank does the work.
    """
    return (f'IF({row_ref(flag_key)}<>"{value}",{NO_MATCH},'
            f'COUNTIFS({block(flag_key)},"{value}",'
            f'{block(id_key)},"<="&{row_ref(id_key)}))')


def flag_list(sheet: str, rank_key: str, name_key: str, n: int,
              value_key: str = "", value_sheet: str = "") -> str:
    """The nth entry of a flagged list, by its hidden rank column."""
    target = value_sheet or sheet
    if not value_key:
        return (f'IFERROR(INDEX({other(sheet, name_key)},'
                f'MATCH({n},{other(sheet, rank_key)},0)),"")')
    return (f'IFERROR(INDEX({other(target, value_key)},'
            f'MATCH({n},{other(sheet, rank_key)},0)),"")')


def top_by(rank_sheet: str, rank_key: str, fetch_sheet: str,
           fetch_key: str, n: int) -> str:
    """The nth best entry of `fetch_key`, by a hidden rank column."""
    return (f'IFERROR(INDEX({other(fetch_sheet, fetch_key)},'
            f'MATCH({n},{other(rank_sheet, rank_key)},0)),"")')


def top_value(rank_sheet: str, rank_key: str, value_sheet: str,
              value_key: str, n: int) -> str:
    return (f'IFERROR(INDEX({other(value_sheet, value_key)},'
            f'MATCH({n},{other(rank_sheet, rank_key)},0)),"")')


# ---------------------------------------------------------------------------
# Pricing maths
# ---------------------------------------------------------------------------

def round_price(expr: str) -> str:
    """Apply the rounding rule chosen on Settings (eight branches)."""
    branches = [
        ("None", expr),
        ("Nearest 0.99", f"ROUND({expr}+0.5,0)-0.01"),
        ("Nearest 0.95", f"ROUND({expr}+0.5,0)-0.05"),
        ("Nearest 0.50", f"ROUND({expr}*2,0)/2"),
        ("Nearest 1", f"ROUND({expr},0)"),
        ("Nearest 5", f"ROUND({expr}/5,0)*5"),
        ("Up to whole 1", f"CEILING({expr},1)"),
        ("Up to whole 5", f"CEILING({expr},5)"),
    ]
    out = branches[-1][1]
    for rule, value in reversed(branches[:-1]):
        out = f'IF(RoundingRule="{rule}",{value},{out})'
    return out


def price_from(cost: str, fixed: str, margin: str, rate: str) -> str:
    """The whole pricing model in one line.

        price = (cost + fixed fees) / (1 - target margin - fee rate)
    """
    room = f"(1-{margin}-{rate})"
    core = f"({cost}+{fixed})/{room}"
    return f'IFERROR({round_price(f"IF({room}<=0,0,{core})")},"")'


def channel_lookup(channel: str, key: str, fallback: str) -> str:
    """A fee value for one sales channel, from the Channels tab."""
    return (f"IFERROR(INDEX({other('Channels', key)},"
            f"MATCH({channel},{other('Channels', 'name')},0)),{fallback})")


def channel_fee_rate(channel: str) -> str:
    """Every percentage a channel takes, including its share of ad fees."""
    return ("(" + channel_lookup(channel, "transaction_pct", "TransactionFee")
            + "+" + channel_lookup(channel, "processing_pct",
                                   "ProcessingPercent")
            + "+" + channel_lookup(channel, "regulatory_fee", "RegulatoryFee")
            + "+" + channel_lookup(channel, "currency_fee", "CurrencyFee")
            + "+" + channel_lookup(channel, "ads_effective", "0") + ")")


def channel_fixed_fee(channel: str) -> str:
    """Fees charged once per order, whatever the price."""
    return ("(" + channel_lookup(channel, "listing_fee", "ListingFee")
            + "+" + channel_lookup(channel, "processing_fixed",
                                   "ProcessingFixed") + ")")


def labor_cost(minutes: str) -> str:
    """What an amount of time costs once payroll on-costs are added."""
    return f'IF(N({minutes})=0,0,N({minutes})/60*LaborCostHour)'


def overhead_per_unit(minutes: str = "0", units: str = "1") -> str:
    """Overhead share, following the method chosen on Settings."""
    per_hour = f'IF(N({minutes})=0,0,N({minutes})/60*OverheadPerHour)'
    per_unit = f'IF(N({units})=0,0,OverheadPerUnit/N({units}))'
    return (f'IF(OverheadMethod="Per hour",{per_hour},'
            f'IF(OverheadMethod="Per unit",{per_unit},'
            f'IF(UnitsPerMonth<=0,0,OverheadMonthly/UnitsPerMonth)))')


def hours_of(minutes: str) -> str:
    return f"(N({minutes})/60)"


def margin_flag(margin: str, profit: str, price: str) -> str:
    return (f'IF(N({price})=0,"",'
            f'IF(N({profit})<=0,"{FLAG_LOSS}",'
            f'IF(N({margin})<MarginWarning,"{FLAG_THIN}","{FLAG_OK}")))')


def margin_cf() -> List[Dict[str, Any]]:
    """Conditional formats that make a bad price obvious."""
    return [cf_text(FLAG_LOSS, "bold_bad"), cf_text(FLAG_THIN, "warn"),
            cf_text(FLAG_OK, "good"), cf_text(FLAG_REVIEW, "info")]


def hourly_flag(hourly: str, minutes: str) -> str:
    return (f'IF(N({minutes})=0,"",'
            f'IF(N({hourly})<0,"PAYING TO WORK",'
            f'IF(N({hourly})<MinimumWage,"BELOW MIN WAGE",'
            f'IF(N({hourly})<HourlyRate,"BELOW YOUR RATE","GOOD"))))')


def review_flag(next_review: str, reviewed: str) -> str:
    return (f'IF({row_ref(next_review)}="","",'
            f'IF(N({row_ref(next_review)})<TodayDate,"OVERDUE",'
            f'IF(N({row_ref(next_review)})-TodayDate<=30,"DUE SOON","OK")))')


def craft_minutes_total(product_ref: str) -> str:
    """Minutes recorded for one product across all six craft tabs.

    Every craft tab keeps its labour in a column called `minutes`, so the
    catalog can add the six up without knowing which craft a product is.
    """
    parts = [sumifs(other(sheet, "minutes"),
                    [(other(sheet, "product"), product_ref)])
             for sheet in CRAFT_SHEETS]
    return "+".join(parts)


def craft_material_total(product_ref: str) -> str:
    """Material cost recorded for one product across all six craft tabs."""
    parts = [sumifs(other(sheet, "material_total"),
                    [(other(sheet, "product"), product_ref)])
             for sheet in CRAFT_SHEETS]
    return "+".join(parts)


def craft_price_total(product_ref: str) -> str:
    parts = [sumifs(other(sheet, "unit_cost"),
                    [(other(sheet, "product"), product_ref)])
             for sheet in CRAFT_SHEETS]
    return "+".join(parts)


def spec_defaults(name: str, title: str, subtitle: str, cfg: Config,
                  help_text: str, tab_color: Optional[str] = None) -> Dict[str, Any]:
    """The SheetSpec arguments every register shares.

    `freeze_cols` is deliberately not part of this: registers pass it straight
    to :class:`SheetSpec`, and keeping it out of both would mean the keyword
    arriving twice.
    """
    return dict(name=name, title=title, subtitle=subtitle,
                rows=cfg.row_count(name), tab_color=tab_color,
                help_text=help_text)


# ---------------------------------------------------------------------------
# The six craft calculators
# ---------------------------------------------------------------------------

def craft_channel_rate() -> str:
    """Fee rate of the default channel - the craft tabs price for that."""
    return channel_fee_rate("DefaultChannel")


def craft_channel_fixed() -> str:
    return channel_fixed_fee("DefaultChannel")


def craft_packaging(product_ref: str) -> str:
    """Packaging for one item: matched components, or the default."""
    specific = sumifs_wild(other("Packaging", "cost"),
                           other("Packaging", "products"), "product")
    every_order = sumifs(other("Packaging", "cost"),
                         [(other("Packaging", "products"), '"All"')])
    return (f'IF({product_ref}="",DefaultPackaging,'
            f'IF(N({specific})+N({every_order})>0,'
            f'N({specific})+N({every_order}),DefaultPackaging))')


def craft_check(price: str, profit: str, margin: str, hourly: str,
                suggested: str, id_ref: str) -> str:
    """One line that says what is wrong with this piece, if anything."""
    return (f'IF({id_ref}="","",'
            f'IF(N({price})=0,"NO PRICE YET",'
            f'IF(N({profit})<0,"PRICED BELOW COST",'
            f'IF(N({hourly})<MinimumWage,"BELOW MINIMUM WAGE",'
            f'IF(N({margin})<MarginWarning,"MARGIN BELOW TARGET",'
            f'IF(N({price})<N({suggested})*0.9,"UNDER THE MODEL PRICE",'
            f'"OK"))))))')


def craft_tail(material_expr: str, *, has_difficulty: bool = True,
               minutes_key: str = "minutes", price_key: str = "price",
               id_key: str = "id", batch_col: Optional[Col] = None) -> List[Col]:
    """The costing columns every craft calculator ends with.

    The six craft tabs each collect their own materials and their own time;
    from `material_total` and `minutes` onwards they are identical, so they
    share this tail. `unit_cost` is the cost of ONE finished item, which is
    what the Products tab picks up.
    """
    mins = row_ref(minutes_key)
    price = row_ref(price_key)
    batch = row_ref("batch_qty")
    pid = row_ref("product")
    iid = row_ref(id_key)
    rate = craft_channel_rate()
    fixed = craft_channel_fixed()
    unit_cost = (f"N({row_ref('material_total')})+N({row_ref('labor_cost')})"
                 f"+N({row_ref('packaging_cost')})"
                 f"+N({row_ref('overhead_cost')})")
    suggested = price_from(unit_cost, fixed, "TargetRetailMargin", rate)
    profit = f"N({price})-({rate}*N({price})+{fixed})-{unit_cost}"
    margin = f'IF(N({price})=0,"",({profit})/N({price}))'
    hourly = f'IF(N({mins})=0,"",({profit})/(N({mins})/60))'

    cols: List[Col] = [
        batch_col if batch_col is not None else int_col(
            "batch_qty", "Batch qty", 10.0,
            note="How many you make at once. Blank uses the default on "
                 "Settings."),
        calc_col("material_total", "Material cost an item",
                 f'IFERROR(IF({iid}="",0,{material_expr}),0)', 13.0, "money",
                 note="Everything this piece is made of, one item."),
        calc_col("labor_cost", "Labour cost",
                 f'IF({iid}="",0,IF(N({mins})=0,0,N({mins})/60*LaborCostHour))',
                 12.0, "money"),
    ]
    if has_difficulty:
        cols.append(calc_col(
            "difficulty_factor", "Difficulty factor",
            f'IF({iid}="",1,IFERROR(INDEX(DiffFactors,'
            f'MATCH({row_ref("difficulty")},DiffNames,0)),1))', 11.0,
            "number", note="From the factor table on the Lists tab."))
    cols += [
        calc_col("packaging_cost", "Packaging cost",
                 f'IF({iid}="",DefaultPackaging,{craft_packaging(pid)})',
                 12.0, "money"),
        calc_col("overhead_cost", "Overhead share",
                 f'IF({iid}="",0,{overhead_per_unit(mins, f"N({batch})")})',
                 12.0, "money",
                 note="Spread the way the Overhead method on Settings says."),
        calc_col("unit_cost", "Cost an item",
                 f'IF({iid}="",0,{unit_cost})', 13.0, "money",
                 note="Materials + labour + packaging + overhead for one "
                      "finished item. This is what Products picks up."),
        calc_col("batch_total", "Cost a batch",
                 f'IF({iid}="",0,N({row_ref("unit_cost")})*'
                 f'IF(N({batch})=0,DefaultBatchSize,N({batch})))', 13.0,
                 "money"),
        calc_col("cost_a_minute", "Cost a minute",
                 f'IF(OR({iid}="",N({mins})=0),"",'
                 f'N({row_ref("unit_cost")})/N({mins}))', 11.0, "money4"),
        calc_col("suggested_price", "Suggested price",
                 f'IF({iid}="","",{suggested})', 13.0, "money",
                 note="(cost + fixed fees) / (1 - target margin - fee rate), "
                      "rounded the way Settings says."),
        calc_col("wholesale_price", "Wholesale price",
                 f'IF({iid}="","",'
                 f'{round_price("N(" + row_ref("suggested_price") + ")*(1-WholesaleDiscount)")})',
                 13.0, "money",
                 note="The suggested retail price less the trade discount."),
        calc_col("profit", "Profit an item",
                 f'IF({iid}="","",IF(N({price})=0,"",{profit}))', 12.0,
                 "money",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "bold_bad"},
                     {"type": "cell", "criteria": ">=", "value": 0,
                      "fmt": "good"}]),
        calc_col("margin", "Margin",
                 f'IF({iid}="","",{margin})', 10.0, "percent",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "bold_bad"}]),
        calc_col("margin_flag", "Flag",
                 margin_flag(row_ref("margin"), row_ref("profit"), price),
                 9.0, "status", cf=margin_cf()),
        calc_col("effective_hourly", "Effective hourly",
                 f'IF({iid}="","",{hourly})', 12.0, "money",
                 note="What an hour of making this earns, after fees."),
        calc_col("hourly_flag", "Wage check",
                 hourly_flag(row_ref("effective_hourly"), mins), 16.0,
                 "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "PAYING TO WORK", "fmt": "bold_bad"},
                     {"type": "text", "criteria": "containing",
                      "value": "BELOW", "fmt": "warn"},
                     {"type": "text", "criteria": "containing",
                      "value": "GOOD", "fmt": "good"}]),
        calc_col("check", "Check",
                 craft_check(price, row_ref("profit"), row_ref("margin"),
                             row_ref("effective_hourly"),
                             row_ref("suggested_price"), iid), 22.0, "status",
                 cf=margin_cf() + [{"type": "text", "criteria": "containing",
                                    "value": "NO PRICE", "fmt": "info"}]),
    ]
    return cols



def samples(cfg: Config, name: str) -> List[Dict[str, Any]]:
    """Sample rows for a register (empty when building a blank workbook)."""
    if not cfg.include_sample_data:
        return []
    from ..sample_data import build_sample_data
    return build_sample_data(cfg).get(name, [])


def banner_legend(sheet, fmts, cfg: Config, reg, row: int, last_col: int):
    """Cream = type here, warm grey = calculated. Written under a page."""
    sheet.merge(row, 0, last_col, "", fmts.chrome("rule"))
    sheet.row_height(row + 1, 16)
    sheet.write(row + 1, 0, "Type here", fmts.chrome("legend_label"))
    sheet.write(row + 1, 1, "", fmts.chrome("legend_input"))
    sheet.write(row + 1, 2, "Calculated - locked",
                fmts.chrome("legend_label"))
    sheet.write(row + 1, 3, "", fmts.chrome("legend_calc"))
    sheet.merge(row + 1, 4, last_col,
                f"Sheets are protected with the password '{cfg.password}'. "
                f"Formula cells cannot be overwritten by accident.",
                fmts.chrome("note"))
    return row + 2
