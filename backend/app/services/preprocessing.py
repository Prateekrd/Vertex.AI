"""Preprocessing: abbreviation expansion, unit normalization, regex extraction."""
from __future__ import annotations

import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

import spacy

# ---------------------------------------------------------------------------
# Abbreviation dictionary (industrial/procurement common terms)
# ---------------------------------------------------------------------------
ABBREVIATIONS: Dict[str, str] = {
    # Material types
    "ss": "stainless steel",
    "ss": "stainless steel",
    "cs": "carbon steel",
    "al": "aluminum",
    "brass": "brass",
    "copper": "copper",
    "pvc": "polyvinyl chloride",
    "nylon": "nylon",
    "poly": "polymer",
    "rubber": "rubber",
    "fiberglass": "fiberglass",
    "gasket": "gasket",
    "seal": "seal",
    "bolt": "bolt",
    "screw": "screw",
    "nut": "nut",
    "washer": "washer",
    "pipe": "pipe",
    "tube": "tube",
    "rod": "rod",
    "sheet": "sheet",
    "plate": "plate",
    "wire": "wire",
    "cable": "cable",
    "wire": "wire",
    "coil": "coil",
    "roll": "roll",
    "bar": "bar",
    "profile": "profile",
    "fitting": "fitting",
    "flange": "flange",
    "valve": "valve",
    "pump": "pump",
    # Units
    "mm": "millimeter",
    "cm": "centimeter",
    "m": "meter",
    "mtr": "meter",
    "mt": "meter",
    "mtrs": "meters",
    "kg": "kilogram",
    "gm": "gram",
    "g": "gram",
    "lb": "pound",
    "ft": "foot",
    "in": "inch",
    "dia": "diameter",
    "len": "length",
    "qty": "quantity",
    "dia": "diameter",
    "l": "length",
    "w": "width",
    "h": "height",
    "t": "thickness",
    "od": "outer diameter",
    "bd": "bottom diameter",
    "id": "inner diameter",
    "sch": "schedule",
    # Other common
    "qty": "quantity",
    "no": "number",
    "no.": "number",
    "part": "part",
    "asn": "asset",
    "max": "maximum",
    "min": "minimum",
    "std": "standard",
    "spec": "specification",
    "hardened": "hardened",
    "alloy": "alloy",
    "sa": "safety",
    "ptfe": "polytetrafluoroethylene",
    "ptfe": "ptfe",
    "teflon": "teflon",
    "epoxy": "epoxy",
    "paint": "paint",
    "coating": "coating",
    "powder": "powder",
    "lts": "liters",
    "ltr": "liter",
    "gal": "gallon",
    "cf": "cubic foot",
    "cu ft": "cubic foot",
    "kf": "kiloforce",
    "ns": "newton meter",
    "nm": "newton meter",
    "kn": "kilonewton",
    "psi": "pounds per square inch",
    "bar": "bar",
    "kpa": "kilopascal",
    "pa": "pascal",
    "ha": "hectare",
    "m2": "square meter",
    "sq m": "square meter",
    "cft": "cubic feet",
    "cv": "cathode",
    "eg": "electric generator",
}

# ---------------------------------------------------------------------------
# Unit mapping to canonical form
# ---------------------------------------------------------------------------
UNIT_CANONICAL: Dict[str, str] = {
    # Length
    "mm": "mm", "millimeter": "mm", "thou": "mm", "mil": "mm",
    "cm": "cm", "centimeter": "cm", "centimetre": "cm",
    "m": "m", "meter": "m", "metre": "m", "mtr": "m", "mt": "m",
    "ft": "ft", "foot": "ft",
    "in": "in", "inch": "in",
    # Weight
    "kg": "kg", "kilogram": "kg",
    "g": "g", "gram": "g",
    "lb": "lb", "pound": "lb", "lbs": "lb",
    "ton": "ton", "tonne": "ton",
    # Volume
    "l": "l", "liter": "l", "litre": "l",
    "gal": "gal", "gallon": "gal",
    "ml": "ml", "milliliter": "ml", "millilitre": "ml",
    # Others
    "pc": "pc", "piece": "pc",
    "set": "set",
    "roll": "roll",
    "kg m": "kg-m",
    "kwh": "kwh",
    "kva": "kva",
    "hp": "hp",
    "amp": "amp",
    "v": "v",
    "w": "w",
    "hz": "hz",
}

# ---------------------------------------------------------------------------
# spaCy model loading
# ---------------------------------------------------------------------------
try:
    NLP = spacy.load("en_core_web_sm")
except OSError:
    NLP = None  # Will need to download during Docker build


# ---------------------------------------------------------------------------
# Regex patterns for attribute extraction
# ---------------------------------------------------------------------------
PATTERNS = {
    "diameter": r"(\d+(?:\.\d+)?)\s*(mm|cm|in|ft|inch|dia|diameter)\b",
    "length": r"(?<![\d.])(\d+(?:\.\d+)?)\s*(meter|metre|mtr|len|m(?![a-z]))\b",
    "width": r"(\d+(?:\.\d+)?)\s*(mm|cm|m|in|width|w)\b",
    "thickness": r"(\d+(?:\.\d+)?)\s*(mm|cm|m|gauge|sch|t)\b",
    "schedule": r"sch(\d+)|schedule\s*(\d+)",
    "grade": r"(stainless\s*steel|stainless|steel\s*304|steel\s*316|alloy\s*\w+|chrome\s*steel)",
    "material": r"(stainless\s*steel|ss|carbon\s*steel|cs|aluminum|al|brass|copper|pvc|nylon|rubber|fiberglass)",
    "quantity": r"(\d+)\s*(qty|quantity|no|number|per)",
}


@dataclass
class ExtractedAttrs:
    material_type: Optional[str] = None
    diameter: Optional[float] = None
    length: Optional[float] = None
    width: Optional[float] = None
    thickness: Optional[float] = None
    schedule: Optional[str] = None
    grade: Optional[str] = None
    unit: Optional[str] = None
    raw_units: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "material_type": self.material_type,
            "diameter": self.diameter,
            "length": self.length,
            "width": self.width,
            "thickness": self.thickness,
            "schedule": self.schedule,
            "grade": self.grade,
            "unit": self.unit,
            "raw_units": self.raw_units,
        }


def expand_abbreviations(text: str) -> str:
    """Replace common abbreviations with full terms."""
    text_lower = text.lower()
    for abbr, full in ABBREVIATIONS.items():
        # Use word boundary to avoid partial replacements
        pattern = r"\b" + re.escape(abbr) + r"\b"
        text_lower = re.sub(pattern, full, text_lower, flags=re.IGNORECASE)
    return text_lower


def normalize_unit(unit: str) -> str:
    """Convert unit to canonical form."""
    if not unit:
        return ""
    unit_lower = unit.strip().lower()
    return UNIT_CANONICAL.get(unit_lower, unit_lower)


def extract_units(text: str) -> List[str]:
    """Extract all unit mentions from text."""
    units_found = set()
    text_lower = text.lower()
    for token in text_lower.replace(",", " ").replace("-", " ").split():
        if token in UNIT_CANONICAL or any(u in token for u in ["mm", "cm", "m", "in", "ft", "kg", "g", "lb"]):
            units_found.add(token)
    return sorted(list(units_found))


def extract_attributes(text: str) -> ExtractedAttrs:
    """Extract structured attributes from raw description."""
    text_lower = text.lower()
    attrs = ExtractedAttrs()

    # Extract diameter
    match = re.search(PATTERNS["diameter"], text_lower)
    if match:
        val = float(match.group(1))
        unit = match.group(2)
        if unit in ("mm", "millimeter", "centimeter"):
            attrs.diameter = val
        elif unit in ("cm", "centimeter"):
            attrs.diameter = val * 10  # convert to mm
        elif unit in ("m", "meter"):
            attrs.diameter = val * 1000
        elif unit in ("in", "inch"):
            attrs.diameter = val * 25.4
        attrs.unit = normalize_unit(unit) if unit else None

    # Extract length
    match = re.search(PATTERNS["length"], text_lower)
    if match and not attrs.length:
        val = float(match.group(1))
        unit = match.group(2)
        if unit in ("m", "meter", "metre"):
            attrs.length = val
        elif unit in ("mm", "millimeter"):
            attrs.length = val / 1000
        elif unit in ("cm", "centimeter"):
            attrs.length = val / 100
        elif unit in ("ft", "foot"):
            attrs.length = val * 0.3048
        elif unit in ("in", "inch"):
            attrs.length = val * 0.0254
        attrs.unit = normalize_unit(unit) if unit else attrs.unit

    # Extract width
    match = re.search(PATTERNS["width"], text_lower)
    if match:
        val = float(match.group(1))
        if attrs.width is None:
            attrs.width = val

    # Extract thickness
    match = re.search(PATTERNS["thickness"], text_lower)
    if match:
        attrs.thickness = float(match.group(1))

    # Extract schedule
    match = re.search(PATTERNS["schedule"], text_lower)
    if match:
        attrs.schedule = match.group(1) or match.group(2)

    # Extract grade
    match = re.search(PATTERNS["grade"], text_lower, re.IGNORECASE)
    if match:
        attrs.grade = match.group(1).upper()

    # Extract material type (prefer longer matches)
    materials = ["stainless steel", "carbon steel", "aluminum", "brass", "copper", "pvc", "nylon", "rubber", "fiberglass"]
    for mat in sorted(materials, key=len, reverse=True):
        if mat in text_lower:
            attrs.material_type = mat.replace(" ", "_")
            break

    # Fallback to regex match
    if not attrs.material_type:
        match = re.search(PATTERNS["material"], text_lower, re.IGNORECASE)
        if match:
            attrs.material_type = match.group(1).replace(" ", "_")

    attrs.raw_units = extract_units(text)

    return attrs


def clean_description(text: str) -> str:
    """Full cleaning pipeline: expand, normalize, fix spacing."""
    text = expand_abbreviations(text)
    text = text.replace(",", " ").replace("-", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def preprocess_material(record: Dict[str, Any]) -> Dict[str, Any]:
    """Preprocess a single material record."""
    raw_desc = record.get("description", "")
    cleaned = clean_description(raw_desc)
    # Extract attributes from cleaned text so abbreviations are expanded
    attrs = extract_attributes(cleaned)

    return {
        "cleaned_description": cleaned,
        "extracted_attrs": attrs.to_dict(),
        "unit": normalize_unit(record.get("unit", "")),
        "material_group": record.get("material_group", ""),
        "plant": record.get("plant", ""),
    }