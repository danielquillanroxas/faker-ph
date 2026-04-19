"""Smoke tests for faker-ph.

These verify format invariants and determinism, not correctness of
checksums (which are format-only for several PH agencies — see README
caveats).
"""
import re

import pytest

from faker_ph import (
    ALL_TEMPLATES,
    DISCHARGE_SUMMARY,
    FakerPH,
    render,
)

# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

def test_same_seed_produces_same_output():
    a = FakerPH(seed=42)
    b = FakerPH(seed=42)
    assert a.psn() == b.psn()
    assert a.tin() == b.tin()
    assert a.full_name() == b.full_name()


def test_different_seeds_differ():
    a = FakerPH(seed=42)
    b = FakerPH(seed=43)
    assert a.psn() != b.psn()


# ---------------------------------------------------------------------------
# Identifier format invariants
# ---------------------------------------------------------------------------

@pytest.fixture
def f():
    return FakerPH(seed=42)


def test_psn_format(f):
    # 16 digits displayed as NNNN-NNNN-NNNN-NNNN
    assert re.fullmatch(r"\d{4}-\d{4}-\d{4}-\d{4}", f.psn())


def test_pcn_format(f):
    # 12 digits displayed as NNNN-NNNN-NNNN
    assert re.fullmatch(r"\d{4}-\d{4}-\d{4}", f.pcn())


def test_tin_format(f):
    assert re.fullmatch(r"\d{3}-\d{3}-\d{3}-\d{3}", f.tin())


def test_sss_format(f):
    assert re.fullmatch(r"\d{2}-\d{7}-\d", f.sss())


def test_gsis_format(f):
    assert re.fullmatch(r"\d{11}", f.gsis())


def test_philhealth_pin_format(f):
    assert re.fullmatch(r"\d{2}-\d{9}-\d", f.philhealth_pin())


def test_umid_format(f):
    assert re.fullmatch(r"\d{4}-\d{7}-\d", f.umid())


def test_passport_format(f):
    # 2 letters + 7 digits (DFA convention approximated as L + 7D + L)
    assert re.fullmatch(r"[A-Z]\d{7}[A-Z]", f.passport())


def test_driver_license_format(f):
    assert re.fullmatch(r"[A-K]\d{2}-\d{2}-\d{6}", f.driver_license())


def test_mobile_format(f):
    # '0917 555 1234' style — 4+3+4 digit groups, starts with 0
    assert re.fullmatch(r"0\d{3} \d{3} \d{4}", f.mobile())


def test_mobile_unformatted(f):
    # 11-digit sequence starting with 0
    assert re.fullmatch(r"0\d{10}", f.mobile(formatted=False))


def test_international_mobile_format(f):
    # '+63 XXX XXX XXXX' — three groups after +63
    assert re.fullmatch(r"\+63 \d{3} \d{3} \d{4}", f.international_mobile())


def test_landline_ncr_format(f):
    # NCR: '(02) PTE+XXX-XXXX' — 4 digits (1 PTE + 3), dash, 4 digits
    assert re.fullmatch(r"\(02\) \d{4}-\d{4}", f.landline(area_code="2"))


def test_landline_provincial_format(f):
    # Non-NCR: '(XX) XXX-XXXX' or similar area-code format
    # Sample several to avoid hitting NCR by chance
    seen = {f.landline() for _ in range(10)}
    for ll in seen:
        assert re.fullmatch(r"\(\d{1,3}\) \d{3,4}-\d{4}", ll), ll


# ---------------------------------------------------------------------------
# Addresses
# ---------------------------------------------------------------------------

def test_address_has_required_fields(f):
    addr = f.address()
    for key in ("region", "province", "city", "barangay", "zip_code", "full"):
        assert key in addr, f"missing key: {key}"
        assert addr[key], f"empty value for: {key}"


def test_address_zip_is_four_digits(f):
    addr = f.address()
    assert re.fullmatch(r"\d{4}", addr["zip_code"])


# ---------------------------------------------------------------------------
# Names
# ---------------------------------------------------------------------------

def test_full_name_no_honorific_by_default(f):
    # Default full_name() should not start with an honorific like Dr./Atty./Mr.
    name = f.full_name()
    first_token = name.split()[0]
    assert not first_token.endswith(".")
    assert first_token not in {"Kuya", "Ate", "Bb", "Gng"}


def test_full_name_with_honorific(f):
    # include_honorific=True should produce one of the known honorific tokens
    name = f.full_name(include_honorific=True)
    first_token = name.split()[0]
    known_honorifics = {
        "Dr.", "Dra.", "Atty.", "Engr.", "Mr.", "Mrs.", "Ms.",
        "Bb.", "Gng.", "Kuya", "Ate"
    }
    assert first_token in known_honorifics


def test_surname_origin_buckets(f):
    # All four origin buckets should return non-empty strings
    for origin in ("spanish", "tagalog", "chinese", "anglo"):
        s = f.surname(origin=origin)
        assert isinstance(s, str) and s


# ---------------------------------------------------------------------------
# Dates
# ---------------------------------------------------------------------------

def test_filipino_date_format(f):
    # 'Ika-12 ng Hunyo, 1998'
    assert re.fullmatch(
        r"Ika-\d{1,2} ng (Enero|Pebrero|Marso|Abril|Mayo|Hunyo|Hulyo|Agosto|Setyembre|Oktubre|Nobyembre|Disyembre), \d{4}",
        f.filipino_date(),
    )


def test_legal_date_en_format(f):
    # '16th day of January, 1990'
    assert re.fullmatch(
        r"\d{1,2}(st|nd|rd|th) day of "
        r"(January|February|March|April|May|June|July|August|September|October|November|December), "
        r"\d{4}",
        f.legal_date_en(),
    )


def test_date_iso_format(f):
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", f.date_iso())


# ---------------------------------------------------------------------------
# Templates and span rendering
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("template", ALL_TEMPLATES)
def test_render_produces_spans_within_text(template, f):
    text, spans = render(template, f, doc_id="test")
    assert isinstance(text, str) and text
    assert isinstance(spans, list) and spans  # every template should have ≥ 1 span

    for s in spans:
        assert s["start"] < s["end"] <= len(text)
        # The recorded value should match the actual slice of the output text
        assert text[s["start"]:s["end"]] == s["value"]


def test_render_no_placeholder_leakage(f):
    # After rendering, no `$slot_name` placeholders should remain in the text
    # (narrative_variants may embed {slot_name} patterns — those are resolved
    # internally and should not leak either)
    for template in ALL_TEMPLATES:
        text, _ = render(template, f, doc_id="test")
        # Bare $identifier should not appear in the final text
        assert not re.search(r"\$[a-zA-Z_][a-zA-Z0-9_]*", text), (
            f"unresolved placeholder in {template['doc_type']}"
        )


def test_render_deterministic(f):
    g = FakerPH(seed=42)
    t1, s1 = render(DISCHARGE_SUMMARY, f, doc_id="x")
    t2, s2 = render(DISCHARGE_SUMMARY, g, doc_id="x")
    assert t1 == t2
    assert s1 == s2
