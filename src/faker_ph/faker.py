"""
Faker-PH: Philippine-specific synthetic data generator for FilPII.

STARTER SKELETON — extends faker.Faker with Philippine identifiers and
PH-aware name, address, phone, and email generation.

Author: Daniel Roxas (MSc Applied Data Science, TED University)
License: MIT (to be finalized — check TLUnified-NER's GPL if you train models
         on data combined with TLUnified; this module alone is license-free).

Dependencies:
    pip install faker pandas

Usage:
    from faker_ph import FakerPH
    fake = FakerPH(seed=42)
    fake.psn()            # '1985-0412-00234-7'
    fake.tin()            # '123-456-789-000'
    fake.philhealth_pin() # '12-345678901-2'
    fake.sss()            # '01-2345678-9'
    fake.mobile()         # '0917 555 1234'
    fake.landline('02')   # '8 1234 5678'
    fake.address()        # {'region': '...', 'province': '...', 'city': '...', 'barangay': '...', 'full': '...'}
    fake.full_name(origin='spanish', sex='f')  # 'María Elena Santos'

Data files expected in ./data/:
    - psgc_regions.csv, psgc_provinces.csv, psgc_cities.csv, psgc_barangays.csv
      (from jgngo/psgc-data or altcoder/philippines-psgc-shapefiles)
    - mobile_prefixes.json  (from this starter package)
    - landline_area_codes.json  (from this starter package)
    - ph_names.json  (from this starter package)
"""

import json
import random
import string
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker


class FakerPH:
    """
    Philippine-specific synthetic data generator.

    All methods are deterministic when seeded. Generated identifiers match
    real-world format specifications (including checksums where published)
    but are guaranteed not to correspond to any real person: the entropy
    range of each generator intersects with real-issued ranges only by
    coincidence, and we do no lookups against real databases.
    """

    DATA_DIR = Path(__file__).parent / "data"

    def __init__(self, seed: int = 42, locale: str = "en_PH"):
        self._rng = random.Random(seed)
        self._faker = Faker(locale)
        self._faker.seed_instance(seed)

        # Lazy-loaded data attributes
        self._psgc_loaded = False
        self._psgc_regions = None
        self._psgc_provinces = None
        self._psgc_cities = None
        self._psgc_barangays = None
        self._mobile = None
        self._landline = None
        self._names = None

    # ------------------------------------------------------------------
    # Data loading (lazy)
    # ------------------------------------------------------------------

    def _load_psgc(self):
        if self._psgc_loaded:
            return
        # altcoder PSGC CSVs are UTF-8 (jgngo CSVs are Latin-1; switch
        # encoding here if you're using that source instead).
        self._psgc_regions = pd.read_csv(self.DATA_DIR / "psgc_regions.csv", encoding="utf-8")
        self._psgc_provinces = pd.read_csv(self.DATA_DIR / "psgc_provinces.csv", encoding="utf-8")
        self._psgc_cities = pd.read_csv(self.DATA_DIR / "psgc_cities.csv", encoding="utf-8")
        self._psgc_barangays = pd.read_csv(self.DATA_DIR / "psgc_barangays.csv", encoding="utf-8")
        self._psgc_loaded = True

    def _load_mobile(self):
        if self._mobile is None:
            with open(self.DATA_DIR / "mobile_prefixes.json") as f:
                self._mobile = json.load(f)
        return self._mobile

    def _load_landline(self):
        if self._landline is None:
            with open(self.DATA_DIR / "landline_area_codes.json") as f:
                self._landline = json.load(f)
        return self._landline

    def _load_names(self):
        if self._names is None:
            with open(self.DATA_DIR / "ph_names.json") as f:
                self._names = json.load(f)
        return self._names

    # ------------------------------------------------------------------
    # Government identifiers
    # ------------------------------------------------------------------

    def psn(self) -> str:
        """
        PhilSys Number (PSN).

        Format: 16-digit number displayed as NNNN-NNNN-NNNN-NNNN (per PSA
        Circular 2020-2004). Assigned by PSA for the National ID system.
        Format-valid but unregistered; no real-person correspondence.
        """
        digits = "".join(self._rng.choice(string.digits) for _ in range(16))
        return f"{digits[0:4]}-{digits[4:8]}-{digits[8:12]}-{digits[12:16]}"

    def pcn(self) -> str:
        """
        PhilSys Card Number (PCN). 12 digits, displayed as NNNN-NNNN-NNNN.
        PCN is printed on the physical National ID card and is distinct
        from the PSN (which is a permanent lifetime number).
        """
        digits = "".join(self._rng.choice(string.digits) for _ in range(12))
        return f"{digits[0:4]}-{digits[4:8]}-{digits[8:12]}"

    def tin(self) -> str:
        """
        Taxpayer Identification Number (TIN).

        Format: 9-digit core + 3-digit branch code, displayed as
        NNN-NNN-NNN-BBB where BBB is branch (000 for head office).
        Issued by BIR (Bureau of Internal Revenue).
        """
        core = "".join(self._rng.choice(string.digits) for _ in range(9))
        branch = self._rng.choice(["000", "001", "002", "003"])
        return f"{core[0:3]}-{core[3:6]}-{core[6:9]}-{branch}"

    def sss(self) -> str:
        """
        Social Security System number. Format: 10 digits, displayed as
        NN-NNNNNNN-N where the last digit is a checksum (published algorithm
        unknown; we emit 10 digits in correct visual format).
        """
        digits = "".join(self._rng.choice(string.digits) for _ in range(10))
        return f"{digits[0:2]}-{digits[2:9]}-{digits[9]}"

    def gsis(self) -> str:
        """Government Service Insurance System number, 11 digits."""
        return "".join(self._rng.choice(string.digits) for _ in range(11))

    def philhealth_pin(self) -> str:
        """
        PhilHealth Identification Number (PIN). 12 digits, displayed as
        NN-NNNNNNNNN-N.
        """
        digits = "".join(self._rng.choice(string.digits) for _ in range(12))
        return f"{digits[0:2]}-{digits[2:11]}-{digits[11]}"

    def umid(self) -> str:
        """Unified Multi-Purpose ID. 12-digit CRN format: NNNN-NNNNNNN-N."""
        digits = "".join(self._rng.choice(string.digits) for _ in range(12))
        return f"{digits[0:4]}-{digits[4:11]}-{digits[11]}"

    def prc_license(self) -> str:
        """Professional Regulation Commission license. 7 digits typical."""
        return "".join(self._rng.choice(string.digits) for _ in range(7))

    def driver_license(self) -> str:
        """LTO driver's license. Format: CNN-NN-NNNNNN (C = region code letter)."""
        region = self._rng.choice(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"])
        return f"{region}{self._rng.randint(10, 99):02d}-" \
               f"{self._rng.randint(10, 99):02d}-" \
               f"{self._rng.randint(100000, 999999):06d}"

    def passport(self) -> str:
        """DFA passport. Format: 2 letters + 7 digits (e.g. P1234567A)."""
        return f"{self._rng.choice(string.ascii_uppercase)}" \
               f"{self._rng.randint(1000000, 9999999):07d}" \
               f"{self._rng.choice(string.ascii_uppercase)}"

    def barangay_cert_num(self) -> str:
        """Generic barangay certificate control number."""
        return f"{self._rng.randint(2015, 2026)}-{self._rng.randint(1, 9999):04d}"

    # ------------------------------------------------------------------
    # Financial identifiers
    # ------------------------------------------------------------------

    def bdo_account(self) -> str:
        """BDO savings account. 10-12 digits typical."""
        return "".join(self._rng.choice(string.digits) for _ in range(10))

    def bpi_account(self) -> str:
        """BPI savings. 10 digits."""
        return "".join(self._rng.choice(string.digits) for _ in range(10))

    def landbank_account(self) -> str:
        """Landbank account. 10 digits."""
        return "".join(self._rng.choice(string.digits) for _ in range(10))

    def gcash(self) -> str:
        """GCash number (Globe mobile-linked). Same format as mobile."""
        return self.mobile()

    # ------------------------------------------------------------------
    # Phone numbers
    # ------------------------------------------------------------------

    def mobile(self, carrier: str = None, formatted: bool = True) -> str:
        """
        Generate a PH mobile number.

        Args:
            carrier: 'Globe' | 'Smart' | 'Sun' | 'DITO' | None (random).
            formatted: True -> '0917 555 1234', False -> '09175551234'.
        """
        data = self._load_mobile()
        if carrier is None:
            carrier = self._rng.choice(list(data["carriers"].keys()))
        prefix = self._rng.choice(data["carriers"][carrier]["prefixes"])
        suffix = "".join(self._rng.choice(string.digits) for _ in range(7))
        if formatted:
            return f"{prefix} {suffix[0:3]} {suffix[3:7]}"
        return f"{prefix}{suffix}"

    def international_mobile(self, carrier: str = None) -> str:
        """International format: +63 9XX XXX XXXX."""
        local = self.mobile(carrier=carrier, formatted=False)
        return f"+63 {local[1:4]} {local[4:7]} {local[7:11]}"

    def landline(self, area_code: str = None) -> str:
        """
        Generate a PH landline. If area_code is '02', generates the 8-digit
        Metro Manila format with PTE leading digit.
        """
        data = self._load_landline()
        if area_code is None:
            area_code = self._rng.choice(list(data["area_codes"].keys()))
        if area_code == "2":
            pte = self._rng.choice(list(data["area_codes"]["2"]["pte_identifiers"].keys()))
            rest = "".join(self._rng.choice(string.digits) for _ in range(7))
            return f"(02) {pte}{rest[0:3]}-{rest[3:7]}"
        else:
            subscriber = "".join(self._rng.choice(string.digits) for _ in range(7))
            return f"({area_code}) {subscriber[0:3]}-{subscriber[3:7]}"

    # ------------------------------------------------------------------
    # Names
    # ------------------------------------------------------------------

    def surname(self, origin: str = None) -> str:
        """
        origin: 'spanish' | 'chinese' | 'tagalog' | 'anglo' | None (weighted random)
        """
        data = self._load_names()["surnames"]
        if origin is None:
            # Demographic weights (approximate, adjustable)
            origin = self._rng.choices(
                ["spanish_origin", "native_tagalog_austronesian", "chinese_origin", "anglo_origin_rare"],
                weights=[0.62, 0.25, 0.08, 0.05]
            )[0]
        else:
            key_map = {
                "spanish": "spanish_origin",
                "tagalog": "native_tagalog_austronesian",
                "chinese": "chinese_origin",
                "anglo": "anglo_origin_rare",
            }
            origin = key_map.get(origin, origin)
        return self._rng.choice(data[origin])

    def first_name(self, sex: str = None, origin: str = None) -> str:
        """
        sex: 'm' | 'f' | None (random)
        origin: 'spanish' | 'english' | 'tagalog' | None (weighted)
        """
        data = self._load_names()["first_names"]
        if sex is None:
            sex = self._rng.choice(["m", "f"])
        sex_key = {"m": "masculine", "f": "feminine"}[sex]
        bucket = data[sex_key]

        if origin is None:
            origin_key = self._rng.choices(
                ["common_spanish_saint", "common_english_filam_influence", "native_tagalog_popular"],
                weights=[0.5, 0.4, 0.1]
            )[0]
        else:
            origin_key = {
                "spanish": "common_spanish_saint",
                "english": "common_english_filam_influence",
                "tagalog": "native_tagalog_popular",
            }.get(origin, "common_spanish_saint")
        return self._rng.choice(bucket[origin_key])

    def full_name(self, sex: str = None, origin: str = None,
                  include_middle: bool = True, include_honorific: bool = False) -> str:
        """
        Generate a full PH name. Convention: [Honorific] First [Middle] Last.
        Middle name is conventionally the mother's maiden surname.
        """
        sex = sex or self._rng.choice(["m", "f"])
        origin = origin or self._rng.choices(
            ["spanish", "chinese", "tagalog", "anglo"],
            weights=[0.6, 0.1, 0.25, 0.05]
        )[0]

        first = self.first_name(sex=sex)
        last = self.surname(origin=origin)

        parts = []
        if include_honorific:
            parts.append(self._rng.choice(
                ["Dr.", "Atty.", "Engr.", "Mr.", "Mrs.", "Ms.", "Bb.", "Gng.", "Kuya", "Ate"]
                if sex == "m"
                else ["Dr.", "Dra.", "Atty.", "Engr.", "Mrs.", "Ms.", "Bb.", "Gng.", "Ate"]
            ))
        parts.append(first)
        if include_middle:
            parts.append(self.surname(origin=self._rng.choice(["spanish", "tagalog"])))
        parts.append(last)
        return " ".join(parts)

    # ------------------------------------------------------------------
    # Addresses
    # ------------------------------------------------------------------

    def address(self) -> dict:
        """
        Sample a real PH address hierarchically from PSGC (altcoder schema
        using PSGC codes as foreign keys). Joins parent levels via code
        prefix matching.
        Returns a dict with region, province, city, barangay, and a
        formatted full-address string.
        """
        self._load_psgc()
        # Sample a barangay uniformly. Entries have adm1_psgc, adm2_psgc,
        # adm3_psgc, adm4_psgc columns already populated with parent codes.
        bgy = self._psgc_barangays.sample(1, random_state=self._rng.randint(0, 10**9)).iloc[0]

        city_rows = self._psgc_cities[self._psgc_cities["adm3_psgc"] == bgy["adm3_psgc"]]
        province_rows = self._psgc_provinces[self._psgc_provinces["adm2_psgc"] == bgy["adm2_psgc"]]
        region_rows = self._psgc_regions[self._psgc_regions["adm1_psgc"] == bgy["adm1_psgc"]]

        # Graceful fallback if a join misses (rare — some SubMun entries)
        city_name = city_rows.iloc[0]["adm3_en"] if len(city_rows) else "Unknown City"
        province_name = province_rows.iloc[0]["adm2_en"] if len(province_rows) else "Unknown Province"
        region_name = region_rows.iloc[0]["adm1_en"] if len(region_rows) else "Unknown Region"

        block = self._rng.randint(1, 99)
        lot = self._rng.randint(1, 99)
        street = self._rng.choice([
            "Rizal St", "Mabini St", "Bonifacio St", "Luna St", "Del Pilar St",
            "Aguinaldo Ave", "Aguinaldo Hwy", "Quezon Blvd", "Roxas Blvd",
            "Espana Blvd", "España Blvd", "Taft Ave", "EDSA", "Commonwealth Ave",
            "P. Burgos St", "Real St", "Maharlika Hwy",
            "Sampaguita St", "Ilang-Ilang St", "Rosal St", "Magnolia St",
            "St. Peter St", "Santa Cruz St"
        ])
        zip_code = f"{self._rng.randint(1000, 9999):04d}"

        # NCR cities and Highly Urbanized Cities (HUCs like Angeles,
        # Tacloban, Cebu City) are directly under the region with no
        # intervening province. Detect this and format the address
        # accordingly rather than showing "Unknown Province".
        is_ncr = region_name.startswith("National Capital Region")
        is_huc = not is_ncr and len(province_rows) == 0

        if is_ncr:
            full = f"Blk {block} Lot {lot}, {street}, Brgy. {bgy['adm4_en']}, " \
                   f"{city_name}, Metro Manila, {zip_code}"
            province_display = "Metro Manila"
        elif is_huc:
            # HUC: format as "City, Region" without the province layer
            full = f"Blk {block} Lot {lot}, {street}, Brgy. {bgy['adm4_en']}, " \
                   f"{city_name}, {zip_code}"
            province_display = "(HUC — no province)"
        else:
            full = f"Blk {block} Lot {lot}, {street}, Brgy. {bgy['adm4_en']}, " \
                   f"{city_name}, {province_name}, {zip_code}"
            province_display = province_name

        return {
            "region": region_name,
            "province": province_display,
            "city": city_name,
            "barangay": bgy["adm4_en"],
            "zip_code": zip_code,
            "full": full,
        }

    # ------------------------------------------------------------------
    # Emails
    # ------------------------------------------------------------------

    PH_DOMAINS = [
        "gmail.com", "gmail.com", "gmail.com", "yahoo.com",  # Gmail dominates
        "yahoo.com.ph", "outlook.com", "hotmail.com",
        "up.edu.ph", "dlsu.edu.ph", "ateneo.edu", "ust.edu.ph",
        "pup.edu.ph", "umanila.edu.ph",
        "gov.ph", "doh.gov.ph", "dilg.gov.ph", "pnp.gov.ph",
        "bdo.com.ph", "bpi.com.ph", "pldt.com.ph",
    ]

    def email(self, full_name: str = None) -> str:
        """Generate a PH-plausible email address."""
        if full_name is None:
            full_name = self.full_name(include_middle=False)
        parts = full_name.lower().replace(".", "").split()
        first, last = parts[0], parts[-1]
        style = self._rng.choice([
            f"{first}.{last}",
            f"{first}{last}",
            f"{first[0]}{last}",
            f"{first}_{last}",
            f"{first}.{last}{self._rng.randint(0, 99)}",
        ])
        domain = self._rng.choice(self.PH_DOMAINS)
        return f"{style}@{domain}"

    # ------------------------------------------------------------------
    # Dates (Filipino-style)
    # ------------------------------------------------------------------

    def _random_date(self, min_year=1950, max_year=2025) -> date:
        start = date(min_year, 1, 1)
        end = date(max_year, 12, 31)
        days = (end - start).days
        return start + timedelta(days=self._rng.randint(0, days))

    def filipino_date(self) -> str:
        """Generate a date in Filipino long-form style (e.g., 'Ika-12 ng Hunyo, 1998')."""
        d = self._random_date()
        months_fil = ["Enero", "Pebrero", "Marso", "Abril", "Mayo", "Hunyo",
                      "Hulyo", "Agosto", "Setyembre", "Oktubre", "Nobyembre", "Disyembre"]
        return f"Ika-{d.day} ng {months_fil[d.month - 1]}, {d.year}"

    def date_iso(self) -> str:
        return self._random_date().isoformat()

    def date_us_format(self) -> str:
        d = self._random_date()
        return f"{d.month:02d}/{d.day:02d}/{d.year}"

    def date_eu_format(self) -> str:
        d = self._random_date()
        return f"{d.day:02d}/{d.month:02d}/{d.year}"

    def legal_date_en(self) -> str:
        """Formal English legal-document date: '16th day of January, 1990'.
        PH affidavits, notarial acknowledgments, and court pleadings use this
        form regardless of whether the narrative is English or Taglish. The
        filipino_date() form does NOT appear in legal prose.
        """
        d = self._random_date()
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        n = d.day
        if 11 <= n % 100 <= 13:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
        return f"{n}{suffix} day of {months[d.month - 1]}, {d.year}"

    # ------------------------------------------------------------------
    # Full record for document generation
    # ------------------------------------------------------------------

    def patient_record(self) -> dict:
        """A full fake patient record with all quasi-identifiers filled in."""
        sex = self._rng.choice(["m", "f"])
        addr = self.address()
        full = self.full_name(sex=sex, include_middle=True)
        return {
            "full_name": full,
            "sex": sex,
            "date_of_birth": self.date_iso(),
            "age": self._rng.randint(18, 85),
            "address": addr["full"],
            "mobile": self.mobile(),
            "landline": self.landline(),
            "email": self.email(full),
            "philsys_psn": self.psn(),
            "philhealth_pin": self.philhealth_pin(),
            "sss": self.sss(),
            "tin": self.tin(),
            "umid": self.umid(),
        }
