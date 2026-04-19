# faker-ph

**Philippine-specific synthetic PII generator.** Produces format-valid Philippine identifiers across every major government and financial issuer: PhilSys PSN/PCN (national ID), TIN (tax), SSS and GSIS (social security), UMID (unified multi-purpose ID), PhilHealth PIN (health insurance), PRC license (professional regulation), LTO driver's license, DFA passport, and Landbank/BPI/BDO account numbers. Also generates Globe/Smart/Sun/DITO mobile numbers, NCR and provincial landline formats, PSGC-backed addresses across 42,036 barangays, origin-stratified Filipino names (Spanish/Tagalog/Chinese/Anglo buckets), and Filipino-style dates. Includes a small pack of document templates (discharge summary, police blotter, affidavit) that render to text with character-offset gold PII spans for NLP evaluation.

See the [Acronym reference](#acronym-reference) section if these abbreviations are unfamiliar.

Licensed under **Apache-2.0**. Bundled reference data is redistributed from public upstream sources; see [`NOTICE`](NOTICE).

> **Status:** v0.1.0 (alpha). API surface is stable for the identifier generators; the template pack will grow (lab report, prescription, referral letter, and additional legal forms are on the roadmap).

---

## Install

```bash
pip install faker-ph
```

From source:

```bash
git clone https://github.com/danielquillanroxas/faker-ph
cd faker-ph
pip install -e ".[dev]"
```

## Quickstart

```python
from faker_ph import FakerPH

f = FakerPH(seed=42)

f.psn()             # '8894-1850-5612-7456'   (16-digit PhilSys Number)
f.tin()             # '123-456-789-000'        (TIN + branch code)
f.philhealth_pin()  # '12-345678901-2'
f.mobile()          # '0917 555 1234'
f.landline('2')     # '(02) 812 3456'
f.full_name(origin='spanish', sex='f')  # 'María Elena Santos-Lim'
f.filipino_date()   # 'Ika-12 ng Hunyo, 1998'
f.address()['full'] # 'Blk 12 Lot 7, Rizal St, Brgy. ..., ...'
```

All methods are deterministic when seeded. Default seed is `42`.

## Generating documents with gold PII spans

```python
from faker_ph import FakerPH, DISCHARGE_SUMMARY, render

f = FakerPH(seed=42)
text, spans = render(DISCHARGE_SUMMARY, f, doc_id="example_001")

print(text[:200])
for s in spans[:5]:
    print(f"  {s['type']:<16} {text[s['start']:s['end']]!r}")
```

Each span is a dict with `start`, `end`, `type`, and `value`. Character offsets are computed in the post-substitution text, not the template. Templates ship with narrative variants to prevent prompt-memorization when used as evaluation seeds.

See [`examples/generate_samples.py`](examples/generate_samples.py) for a deterministic script that outputs 20 rendered documents with gold spans to `examples/rendered_samples.jsonl` and `examples/gold_spans.jsonl`; both files are committed to the repo so you can inspect output without installing anything.

## Why Filipino PII is distinct

Off-the-shelf multilingual PII detectors (Presidio, GLiNER-Multi-PII, Azure PII) do not cover Filipino as a first-class language, and a straight translation of English tooling misses several Philippine-specific signals:

- **Code-switching (Taglish).** Identifiers frequently appear in English formatting (phone numbers, dates, account numbers) inside otherwise-Tagalog prose, and vice versa. PII recognizers trained on monolingual corpora mis-segment at language boundaries.
- **PSGC geographic hierarchy.** The Philippine Standard Geographic Code (maintained by the Philippine Statistics Authority, PSA) organizes PH addresses in a four-level structure: `region > province > city/municipality > barangay`. Barangay names alone (42,036 unique, often reused across provinces) are strong quasi-identifiers that generic `LOC` taggers flatten away.
- **Government identifier formats with non-trivial validation.**
  - **PhilSys PSN** (Philippine Identification System Number, issued by the Philippine Statistics Authority): 16 digits, displayed `NNNN-NNNN-NNNN-NNNN` per PSA Circular 2020-2004. This is the national ID.
  - **PhilSys PCN** (PhilSys Card Number): 12 digits printed on the physical national-ID card, distinct from the permanent PSN.
  - **TIN** (Taxpayer Identification Number, issued by the Bureau of Internal Revenue, BIR): 9-digit core + 3-digit branch code, `NNN-NNN-NNN-BBB`.
  - **SSS** (Social Security System, private-sector social insurance): 10 digits, `NN-NNNNNNN-N` where the last digit is an undocumented checksum.
  - **GSIS** (Government Service Insurance System, for government employees): 11 digits.
  - **UMID** (Unified Multi-Purpose ID, combines SSS/GSIS/PhilHealth/Pag-IBIG): 12-digit CRN `NNNN-NNNNNNN-N`.
  - **PhilHealth PIN** (Philippine Health Insurance Corporation, PH's universal health insurer): 12 digits, `NN-NNNNNNNNN-N`.
  - **PRC license** (Professional Regulation Commission, issues licenses for doctors, lawyers, engineers, architects): 7 digits.
  - **DFA passport** (Department of Foreign Affairs): 2 letters + 7 digits.
- **Origin-stratified names.** Spanish-origin surnames (Santos, Cruz, Dela Cruz, ~62% of population, a legacy of the 1849 Clavería decree that assigned surnames from a state catalog), native Tagalog surnames (Lakandula, Dimakulangan, Maganda, ~25%), Chinese-origin (Tan, Lim, Sy, ~8%, dating to pre-colonial trade and 19th-century immigration), Anglo-origin (Smith, Johnson, rare). Model fairness across these buckets is measurable and worth auditing.
- **Filipino-style dates.** `Ika-12 ng Hunyo, 1998` coexists with ISO `1998-06-12` and US `06/12/1998` in the same corpus; Tagalog month names (Enero, Pebrero, Marso, etc.) don't appear in any English date parser.
- **Honorifics fused with names.** Tagalog kinship honorifics (`Kuya`, `Ate`, `Lolo`, `Lola`, `Nanay`, `Tatay`) commonly precede names in social text; formal honorifics (`Bb.`, `Gng.`, `Dr.`, `Atty.`, `Engr.`) in legal/clinical text. Both fuse orthographically in ways generic tokenizers don't respect.

faker-ph encodes these distinctions at the generator level so that NLP evaluation corpora built on top of it reflect real Philippine linguistic and administrative reality.

## What's here / what's coming

**Shipping in v0.1.0:**

- `FakerPH` class with 25+ identifier generators, address/name/date/email methods, and a `patient_record()` convenience builder
- Bundled PSGC reference data (17 regions, 117 provinces, 1,648 municipalities/cities, 42,036 barangays)
- Mobile prefix + landline area code tables (all four carriers, all NCR PTE identifiers, 80+ provincial area codes)
- Origin-stratified Filipino name inventory (Spanish/Tagalog/Chinese/Anglo buckets + honorifics)
- `render()` utility that substitutes template slots and returns `(text, gold_spans)`
- Three starter templates: `DISCHARGE_SUMMARY`, `POLICE_BLOTTER`, `AFFIDAVIT_COMPLAINT`
- 20 deterministic example outputs in [`examples/`](examples/)

**Coming in later versions:**

- Additional clinical templates: prescription, referral letter, lab report, PhilHealth claim form
- Additional legal templates: contract NDA, notarial acknowledgment, court complaint
- Published checksum algorithms where reverse-engineered (currently format-only for SSS, PhilHealth)
- A trained PII detection model and an evaluation benchmark are **forthcoming in a separate companion release.** See [Citation](#citation).

## Acronym reference

Philippine government and financial institutions use many acronyms. This section spells out every abbreviation this library encodes, grouped by issuer.

**Identity and civil registry**
- **PhilSys** - Philippine Identification System (the national ID program)
- **PSN** - PhilSys Number (permanent 16-digit lifetime identifier)
- **PCN** - PhilSys Card Number (12 digits, printed on the physical ID card)
- **PSA** - Philippine Statistics Authority (issues PSN/PCN, maintains PSGC and civil registry)
- **PSGC** - Philippine Standard Geographic Code (region/province/city/barangay hierarchy)

**Tax and social insurance**
- **BIR** - Bureau of Internal Revenue (issues TINs)
- **TIN** - Taxpayer Identification Number
- **SSS** - Social Security System (private-sector contributors)
- **GSIS** - Government Service Insurance System (government-sector contributors)
- **UMID** - Unified Multi-Purpose ID (combines SSS/GSIS/PhilHealth/Pag-IBIG on one card)
- **PhilHealth** - Philippine Health Insurance Corporation (universal health coverage)
- **PIN** - Personal Identification Number (PhilHealth's member number)

**Professional and travel**
- **PRC** - Professional Regulation Commission (licenses doctors, lawyers, engineers, teachers, etc.)
- **LTO** - Land Transportation Office (issues driver's licenses)
- **DFA** - Department of Foreign Affairs (issues passports)

**Banking and telecom**
- **BDO** - Banco de Oro (largest PH private bank)
- **BPI** - Bank of the Philippine Islands (oldest PH bank, founded 1851)
- **Landbank** - Land Bank of the Philippines (state-owned bank)
- **NCR** - National Capital Region (Metro Manila, 16 cities + 1 municipality, area code 02)
- **PTE** - Public Telecommunications Entity (the telco operating a given number block: 3=Bayan, 5=Eastern, 6=ABS-CBN, 7=Globe, 8=PLDT for the NCR 8-digit format)

**Locations frequently appearing in the sample data**
- **Brgy.** - Barangay (smallest administrative unit in the Philippines, ~42,000 nationwide)
- **QC** - Quezon City (largest NCR city by population)
- **PNP** - Philippine National Police (referenced in the police-blotter template)
- **DOH** - Department of Health
- **BPO** - Business Process Outsourcing (the $30B PH call-center/back-office industry; relevant to PII workloads)

## Caveats

- **Not a validation oracle.** Do not use generated identifiers to validate real-world documents. Some format specifications are reconstructed from public form layouts and may not match current agency-issued formats exactly.
- **Not a complete name inventory.** The bundled name lists are for synthetic-generation use (~50 names per origin bucket). They are NOT suitable as ground truth for training a name-recognition model without substantial augmentation.
- **PSA data currency.** Bundled PSGC CSVs reflect PSA publications current as of 2023. Municipalities are renamed and barangays created/dissolved periodically; refresh from upstream (see [`NOTICE`](NOTICE)) for production use.

## Citation

```bibtex
@software{roxas2026fakerph,
  author = {Roxas, Daniel Quillan},
  title  = {faker-ph: Philippine-specific synthetic PII generator},
  year   = {2026},
  url    = {https://github.com/danielquillanroxas/faker-ph},
  version = {0.1.0}
}
```

A companion paper describing a broader Filipino PII evaluation framework is in preparation. This `CITATION` entry will be updated once published.

## Contributing

Issues and PRs welcome. Please run `pytest` and `ruff check .` locally before submitting. For large changes (new template categories, checksum algorithm contributions, additional name-origin buckets), open an issue first so we can coordinate scope.

## License

- **Code**: [Apache-2.0](LICENSE)
- **Bundled reference data**: redistributed from public upstreams under their original licenses. See [`NOTICE`](NOTICE).
