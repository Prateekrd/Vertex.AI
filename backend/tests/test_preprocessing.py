"""Tests for preprocessing module."""
import pytest
from app.services.preprocessing import (
    expand_abbreviations,
    clean_description,
    extract_attributes,
    normalize_unit,
    preprocess_material,
)


class TestExpandAbbreviations:
    def test_simple_abbreviation(self):
        assert "stainless steel" in expand_abbreviations("SS pipe")

    def test_multiple_abbreviations(self):
        result = expand_abbreviations("SS Pipe 10mm x 5mtr")
        assert "stainless steel" in result
        assert "millimeter" in result
        assert "meter" in result

    def test_case_insensitive(self):
        assert "stainless steel" in expand_abbreviations("ss")
        assert "stainless steel" in expand_abbreviations("SS")
        assert "stainless steel" in expand_abbreviations("Ss")

    def test_word_boundary(self):
        # Should not replace substring of larger word
        result = expand_abbreviations("acronyms of SS")
        assert "stainless steel" in result

    def test_no_replacement(self):
        # Words that aren't abbreviations pass through
        result = expand_abbreviations("Lorem ipsum dolor")
        assert "lorem" in result


class TestNormalizeUnit:
    def test_length_units(self):
        assert normalize_unit("mm") == "mm"
        assert normalize_unit("millimeter") == "mm"
        assert normalize_unit("MTR") == "m"
        assert normalize_unit("meters") == "m"

    def test_weight_units(self):
        assert normalize_unit("KG") == "kg"
        assert normalize_unit("gm") == "g"
        assert normalize_unit("pounds") == "lb"

    def test_unknown_unit(self):
        assert normalize_unit("xyz") == "xyz"

    def test_empty_unit(self):
        assert normalize_unit("") == ""


class TestExtractAttributes:
    def test_diameter_extraction(self):
        attrs = extract_attributes("SS pipe 10mm dia")
        assert attrs.diameter == 10
        assert attrs.material_type == "stainless_steel"

    def test_length_extraction(self):
        attrs = extract_attributes("pipe 5m length")
        assert attrs.length == 5

    def test_steel_grade_extraction(self):
        attrs = extract_attributes("Stainless Steel 304 pipe")
        assert attrs.grade and "304" in attrs.grade

    def test_carbon_steel(self):
        attrs = extract_attributes("Carbon steel plate 10mm")
        assert attrs.material_type == "carbon_steel"

    def test_pvc_pipe(self):
        attrs = extract_attributes("PVC pipe 50mm")
        assert attrs.material_type == "pvc"

    def test_schedule_extraction(self):
        attrs = extract_attributes("SS pipe Sch40")
        assert attrs.schedule in ("40", None)

    def test_no_attributes(self):
        attrs = extract_attributes("Just some text")
        # No specific attributes to extract
        assert attrs.diameter is None
        assert attrs.length is None


class TestCleanDescription:
    def test_basic_cleaning(self):
        result = clean_description("SS Pipe, 10MM DIA, 5MTR LEN")
        assert "," not in result
        assert "stainless steel" in result
        assert result == result.lower() or "stainless" in result

    def test_whitespace_normalization(self):
        result = clean_description("Pipe   10mm    x   5m")
        assert "  " not in result

    def test_hyphen_to_space(self):
        result = clean_description("SS-Pipe-10mm")
        assert "stainless steel pipe" in result


class TestPreprocessMaterial:
    def test_full_pipeline(self):
        record = {
            "description": "SS Pipe 10mm x 5m",
            "unit": "pc",
            "material_group": "Pipes",
            "plant": "Plant_01",
        }
        result = preprocess_material(record)
        assert result["cleaned_description"] != ""
        assert result["extracted_attrs"]["material_type"] == "stainless_steel"
        assert result["extracted_attrs"]["diameter"] == 10
        assert result["extracted_attrs"]["length"] == 5
        assert result["unit"] == "pc"
        assert result["material_group"] == "Pipes"
        assert result["plant"] == "Plant_01"
