"""
faker-ph template pack — hand-written structural sketches of common
Philippine documents (discharge summary, police blotter, legal affidavit).
Not live-scraped from any specific source; structure based on publicly
observable form layouts (DOH discharge-summary conventions, PNP blotter
format, Rule 7 legal pleadings).

Usage:
    from faker_ph import FakerPH, DISCHARGE_SUMMARY, render

    fake = FakerPH(seed=42)
    text, spans = render(DISCHARGE_SUMMARY, fake, doc_id='doc_0001')

Each template has:
    - a `$slot`-style text with placeholders
    - a slot_map defining how to fill each placeholder
    - optional narrative_variants for sampled prose sections
"""

from dataclasses import dataclass


@dataclass
class PIISpan:
    """A gold PII annotation with character offsets."""
    start: int
    end: int
    type: str
    value: str


def render(template_obj: dict, faker, doc_id: str) -> tuple[str, list[dict]]:
    """
    Fill a template with Faker-PH values, tracking exact character offsets
    of every substitution. Returns (text, list_of_pii_spans_as_dicts).
    """
    text = template_obj["text"]
    slot_map = template_obj["slot_map"]

    # Pre-generate all slot values (called once, reused across occurrences)
    filled_values = {}
    for slot_name, spec in slot_map.items():
        if isinstance(spec, tuple):
            gen_fn, pii_type = spec
        else:
            gen_fn, pii_type = spec, slot_name.upper()
        filled_values[slot_name] = (gen_fn(faker), pii_type)

    # Substitute narrative variants first. These may contain nested
    # {slot_name} placeholders that reference the same filled_values.
    for variant_slot, options in template_obj.get("narrative_variants", {}).items():
        chosen = faker._rng.choice(options)
        # Resolve {slot_name} references inside the narrative variant
        for slot_name, (value, _pii_type) in filled_values.items():
            chosen = chosen.replace("{" + slot_name + "}", value)
        text = text.replace(f"${variant_slot}", chosen)

    # Substitute each $placeholder, logging spans for every occurrence
    # (character offsets computed in the output string as we build it)
    spans = []
    output = ""
    i = 0
    while i < len(text):
        if text[i] == "$":
            # Find the slot name (alphanumeric + underscore)
            j = i + 1
            while j < len(text) and (text[j].isalnum() or text[j] == "_"):
                j += 1
            slot_name = text[i+1:j]
            if slot_name in filled_values:
                value, pii_type = filled_values[slot_name]
                start = len(output)
                output += value
                end = len(output)
                spans.append({"start": start, "end": end, "type": pii_type, "value": value})
                i = j
                continue
        output += text[i]
        i += 1

    return output, spans


# ======================================================================
# TEMPLATE 1: Discharge Summary (English header, Taglish narrative)
# ======================================================================
DISCHARGE_SUMMARY = {
    "doc_type": "discharge_summary",
    "text": """\
DISCHARGE SUMMARY
================================================================

Hospital:          $hospital_name
Patient Name:      $patient_name
Date of Birth:     $dob
Age/Sex:           $age / $sex
Address:           $address
Contact Number:    $mobile
PhilHealth PIN:    $philhealth_pin
TIN:               $tin

Admitting Physician:  Dr. $doctor_name
PRC License No:       $prc_license
Date of Admission:    $admission_date
Date of Discharge:    $discharge_date

--------------------------------------------------------------
CLINICAL SUMMARY
--------------------------------------------------------------

$narrative

Follow-up consultation: please return to $follow_up_clinic on $followup_date.
For concerns, contact $doctor_name at $hospital_landline or email $doctor_email.

Signed,
Dr. $doctor_name, MD
PRC License No. $prc_license
""",
    "slot_map": {
        "hospital_name": (lambda f: f._rng.choice([
            "Philippine General Hospital", "St. Luke's Medical Center Quezon City",
            "Makati Medical Center", "The Medical City Ortigas",
            "Asian Hospital and Medical Center", "Cardinal Santos Medical Center",
            "UERM Memorial Medical Center", "Ospital ng Maynila",
        ]), "EMPLOYER"),
        "patient_name": (lambda f: f.full_name(include_middle=True), "PERSON_NAME"),
        "dob": (lambda f: f.date_iso(), "DATE"),
        "age": (lambda f: str(f._rng.randint(18, 89)), "AGE"),
        "sex": (lambda f: f._rng.choice(["M", "F"]), "SEX"),
        "address": (lambda f: f.address()["full"], "ADDRESS_PH"),
        "mobile": (lambda f: f.mobile(), "PHONE_PH"),
        "philhealth_pin": (lambda f: f.philhealth_pin(), "PHILHEALTH_PIN"),
        "tin": (lambda f: f.tin(), "GOV_ID"),
        "doctor_name": (lambda f: f.full_name(sex="m", include_middle=False), "PERSON_NAME"),
        "prc_license": (lambda f: f.prc_license(), "GOV_ID"),
        "admission_date": (lambda f: f.date_iso(), "DATE"),
        "discharge_date": (lambda f: f.date_iso(), "DATE"),
        "follow_up_clinic": (lambda f: f._rng.choice(["OPD Clinic", "Cardiology Clinic", "Internal Medicine Clinic"]), "EMPLOYER"),
        "followup_date": (lambda f: f.date_iso(), "DATE"),
        "hospital_landline": (lambda f: f.landline("2"), "PHONE_PH"),
        "doctor_email": (lambda f: f.email(), "EMAIL"),
    },
    "narrative_variants": {
        "narrative": [
            "Ang pasyente na si {patient_name} ay na-admit last {admission_date} dahil sa matinding sakit ng tyan at lagnat. After thorough workup, nadetect na may acute appendicitis. Nagkaroon ng successful laparoscopic appendectomy. Recovery was uneventful at stable na ang pasyente bago mag-discharge. Pinag-advise ng low-fiber diet sa unang linggo at strict follow-up sa surgeon.",
            "Patient {patient_name} presented last {admission_date} with severe chest pain and shortness of breath. ECG showed signs of acute coronary syndrome. Na-manage ng conservative medical therapy including antiplatelet, statin, at beta-blocker. Clinically stable na ngayon and discharged with prescription and cardiac rehab referral. Sinabihan na ang pasyente tungkol sa importance ng dietary modification at regular exercise.",
            "Si {patient_name} ay na-admit dahil sa community-acquired pneumonia. After completing 7-day IV antibiotic course and oxygen support, improved na ang clinical condition. Follow-up chest X-ray showed resolution of infiltrates. Pinag-advise ng continued home oxygen kung may episode ng hirap sa paghinga, at strict hand hygiene."
        ]
    }
}


# ======================================================================
# TEMPLATE 2: Police Blotter Entry (PNP format)
# ======================================================================
POLICE_BLOTTER = {
    "doc_type": "police_blotter",
    "text": """\
PHILIPPINE NATIONAL POLICE
$station_name
POLICE BLOTTER ENTRY

Entry No.:          $blotter_num
Date/Time:          $incident_date at $incident_time
Place of Incident:  $incident_address

COMPLAINANT:
    Name:       $complainant_name
    Age/Sex:    $complainant_age / $complainant_sex
    Address:    $complainant_address
    Contact:    $complainant_mobile

RESPONDENT:
    Name:       $respondent_name
    Age/Sex:    $respondent_age / $respondent_sex
    Address:    $respondent_address

NATURE OF INCIDENT: $incident_type

FACTS OF THE CASE:
$narrative

Entered by:   PO2 $investigator_name
Badge No:     $badge_num
""",
    "slot_map": {
        "station_name": (lambda f: f._rng.choice([
            "Quezon City Police District Station 1 (La Loma)",
            "Manila Police District Station 1 (Raxabago)",
            "Makati Police Station, Poblacion Sub-Station",
            "Taguig City Police Station",
        ]), "EMPLOYER"),
        "blotter_num": (lambda f: f.barangay_cert_num(), "GOV_ID"),
        "incident_date": (lambda f: f.date_iso(), "DATE"),
        "incident_time": (lambda f: f"{f._rng.randint(0, 23):02d}:{f._rng.randint(0, 59):02d}H", "TIME"),
        "incident_address": (lambda f: f.address()["full"], "ADDRESS_PH"),
        "complainant_name": (lambda f: f.full_name(include_middle=True), "PERSON_NAME"),
        "complainant_age": (lambda f: str(f._rng.randint(18, 70)), "AGE"),
        "complainant_sex": (lambda f: f._rng.choice(["M", "F"]), "SEX"),
        "complainant_address": (lambda f: f.address()["full"], "ADDRESS_PH"),
        "complainant_mobile": (lambda f: f.mobile(), "PHONE_PH"),
        "respondent_name": (lambda f: f.full_name(include_middle=True), "PERSON_NAME"),
        "respondent_age": (lambda f: str(f._rng.randint(18, 70)), "AGE"),
        "respondent_sex": (lambda f: f._rng.choice(["M", "F"]), "SEX"),
        "respondent_address": (lambda f: f.address()["full"], "ADDRESS_PH"),
        "incident_type": (lambda f: f._rng.choice([
            "Physical Injuries", "Theft", "Traffic Accident",
            "Grave Threats", "Disturbance of Peace"
        ]), "OCCUPATION"),
        "investigator_name": (lambda f: f.full_name(sex="m", include_middle=False), "PERSON_NAME"),
        "badge_num": (lambda f: str(f._rng.randint(100000, 999999)), "GOV_ID"),
    },
    "narrative_variants": {
        "narrative": [
            "Nagsumbong ang complainant na noong nakasaad na petsa at oras, ang respondent ay naghagis ng bato sa kanilang bakuran na tumama sa bintana ng kanilang bahay. Dahil sa galit ng complainant, nakipagtalo siya sa respondent at halos magsuntukan kung hindi dahil sa pakikialam ng kapitbahay. Humihingi ng tulong ang complainant para sa pag-issue ng Barangay Protection Order.",
            "The complainant reports na habang naglalakad papunta sa palengke, bigla siyang nilapitan ng isang unknown male suspect na kumuha ng kanyang cellphone (brand at model sa attached inventory) at tumakbo papunta sa direksyon ng $incident_address. Tinawag ng complainant ang Mobile Patrol at nagbigay ng description ng suspect.",
            "Tumawag sa hotline ang complainant dahil sa loud music at inuman sa kalapit na bahay na hindi tumitigil despite multiple warnings. Incident occurred pasado alas-dose na ng gabi at naaabala ang tulog ng mga bata. Dumating ang responding officers at nag-issue ng warning sa respondent."
        ]
    }
}


# ======================================================================
# TEMPLATE 3: Legal Pleading — Affidavit of Complaint
# ======================================================================
AFFIDAVIT_COMPLAINT = {
    "doc_type": "affidavit",
    "text": """\
REPUBLIC OF THE PHILIPPINES )
CITY OF $city                 ) S.S.

AFFIDAVIT OF COMPLAINT

I, $affiant_name, of legal age, Filipino, $civil_status, and a resident of
$affiant_address, after having been duly sworn in accordance with law, hereby
depose and state:

1. I am the complainant in this case against $respondent_name, likewise of
   legal age, and a resident of $respondent_address;

2. On or about $incident_date, at approximately $incident_time,
   $narrative;

3. That I am executing this affidavit to attest to the truth of the foregoing
   and to support the filing of appropriate criminal charges against
   $respondent_name.

IN WITNESS WHEREOF, I have hereunto set my hand this $affidavit_date
at $notary_city, Philippines.

                                                $affiant_name
                                                Affiant
                                                TIN: $affiant_tin
                                                Mobile: $affiant_mobile

SUBSCRIBED AND SWORN TO before me this $affidavit_date at $notary_city,
Philippines, affiant exhibiting to me his/her competent proof of identity,
to wit: PhilSys ID No. $affiant_psn.

                                                Atty. $notary_name
                                                Notary Public
                                                PRC No. $notary_prc
                                                Commission No. $notary_commission
                                                Until December 31, 2026
""",
    "slot_map": {
        "city": (lambda f: f._rng.choice(["Manila", "Quezon City", "Makati", "Pasig", "Cebu"]), "ADDRESS_PH"),
        "affiant_name": (lambda f: f.full_name(include_middle=True), "PERSON_NAME"),
        "civil_status": (lambda f: f._rng.choice(["single", "married", "widowed", "separated"]), "CIVIL_STATUS"),
        "affiant_address": (lambda f: f.address()["full"], "ADDRESS_PH"),
        "respondent_name": (lambda f: f.full_name(include_middle=True), "PERSON_NAME"),
        "respondent_address": (lambda f: f.address()["full"], "ADDRESS_PH"),
        "incident_date": (lambda f: f.date_iso(), "DATE"),
        "incident_time": (lambda f: f"{f._rng.randint(1, 12)}:{f._rng.randint(0, 59):02d} {f._rng.choice(['AM', 'PM'])}", "TIME"),
        "affidavit_date": (lambda f: f.legal_date_en(), "DATE"),
        "notary_city": (lambda f: f._rng.choice(["Manila", "Quezon City", "Makati"]), "ADDRESS_PH"),
        "affiant_tin": (lambda f: f.tin(), "GOV_ID"),
        "affiant_mobile": (lambda f: f.mobile(), "PHONE_PH"),
        "affiant_psn": (lambda f: f.psn(), "PHILSYS_PSN"),
        "notary_name": (lambda f: f.full_name(include_middle=False), "PERSON_NAME"),
        "notary_prc": (lambda f: f.prc_license(), "GOV_ID"),
        "notary_commission": (lambda f: f"{f._rng.randint(100, 999)}-{f._rng.randint(2020, 2026)}", "GOV_ID"),
    },
    "narrative_variants": {
        "narrative": [
            "while I was at $incident_location, the respondent, without any justifiable cause or provocation on my part, verbally threatened me with physical harm and then proceeded to push me causing me to fall and sustain injuries to my right elbow and hip",
            "the respondent fraudulently induced me to hand over the amount of PHP 50,000.00 under the pretense of an investment opportunity in a business venture that turned out to be non-existent",
            "the respondent entered our residence without permission and took away personal belongings including my laptop, mobile phone, and cash amounting to approximately PHP 15,000.00"
        ]
    }
}


# Additional templates to build (TODO):
# - PRESCRIPTION_FORM
# - REFERRAL_LETTER
# - PHILHEALTH_CLAIM
# - EMPLOYMENT_CONTRACT_NDA
# - INSURANCE_CLAIM
# - SCHOOL_RECORD
# - BARANGAY_CLEARANCE
# - PNP_CLEARANCE

ALL_TEMPLATES = [DISCHARGE_SUMMARY, POLICE_BLOTTER, AFFIDAVIT_COMPLAINT]


if __name__ == "__main__":
    # Quick smoke test: `python -m faker_ph.templates`
    from faker_ph import FakerPH

    fake = FakerPH(seed=42)

    for template in ALL_TEMPLATES:
        filled_text, spans = render(template, fake, doc_id="demo")
        print(f"=== {template['doc_type']} ===")
        print(filled_text[:500])
        print(f"\n[{len(spans)} gold PII spans]\n")
        for span in spans[:5]:
            print(f"  {span['type']}: {span['value']} (chars {span['start']}-{span['end']})")
        print("---\n\n")
