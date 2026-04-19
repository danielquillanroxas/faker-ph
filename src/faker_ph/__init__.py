"""faker-ph — Philippine-specific synthetic PII generator.

Produces format-valid (and where published, checksum-valid) Philippine
identifiers: PhilSys PSN/PCN, TIN, SSS, GSIS, UMID, PhilHealth PIN, PRC,
LTO driver's license, DFA passport, Landbank/BPI/BDO account numbers,
Globe/Smart/Sun/DITO mobile numbers, PH landline formats, PSGC-backed
addresses, origin-stratified names, and Filipino-style dates.

Quickstart:

    >>> from faker_ph import FakerPH
    >>> f = FakerPH(seed=42)
    >>> f.psn()
    '8894-1850-5612-7456'
    >>> f.address()["full"]
    'Blk 23 Lot 7, Rizal St, Brgy. ..., ...'
"""
from faker_ph.faker import FakerPH
from faker_ph.templates import (
    AFFIDAVIT_COMPLAINT,
    ALL_TEMPLATES,
    DISCHARGE_SUMMARY,
    POLICE_BLOTTER,
    render,
)

__version__ = "0.1.0"
__all__ = [
    "FakerPH",
    "render",
    "ALL_TEMPLATES",
    "DISCHARGE_SUMMARY",
    "POLICE_BLOTTER",
    "AFFIDAVIT_COMPLAINT",
]
