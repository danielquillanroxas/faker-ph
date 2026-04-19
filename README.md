# faker-ph

**Philippine-specific synthetic PII generator.** Produces format-valid Philippine identifiers (`PSN`, `PCN`, `TIN`, `SSS`, `GSIS`, `UMID`, `PhilHealth PIN`, `PRC`, `LTO` driver's license, `DFA` passport, `Landbank`/`BPI`/`BDO` account numbers), mobile numbers (`Globe`/`Smart`/`Sun`/`DITO`), NCR and provincial landlines, `PSGC`-backed addresses across 42,036 barangays, origin-stratified Filipino names, and Filipino-style dates. Ships a small pack of document templates (`DISCHARGE_SUMMARY`, `POLICE_BLOTTER`, `AFFIDAVIT_COMPLAINT`) that render to text with character-offset gold PII spans for NLP evaluation.

Unfamiliar with the acronyms? See the [glossary](#glossary).

Licensed under `Apache-2.0`. Bundled reference data is redistributed from public upstream sources (see [`NOTICE`](NOTICE)).

> **Status:** `v0.1.0` (alpha). API is stable for identifier generators; the template pack will grow.

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

f.psn()              # '8894-1850-5612-7456'
f.tin()              # '123-456-789-000'
f.philhealth_pin()   # '12-345678901-2'
f.mobile()           # '0917 555 1234'
f.landline('2')      # '(02) 812 3456'
f.full_name(origin='spanish', sex='f')  # 'María Elena Santos-Lim'
f.filipino_date()    # 'Ika-12 ng Hunyo, 1998'
f.address()['full']  # 'Blk 12 Lot 7, Rizal St, Brgy. ..., ...'
```

All methods are deterministic when seeded (default: `seed=42`).

## Documents with gold PII spans

```python
from faker_ph import FakerPH, DISCHARGE_SUMMARY, render

f = FakerPH(seed=42)
text, spans = render(DISCHARGE_SUMMARY, f, doc_id="example_001")

for s in spans[:5]:
    print(f"  {s['type']:<16} {text[s['start']:s['end']]!r}")
```

Each span is a dict with `start`, `end`, `type`, `value`. Offsets are in the post-substitution output, not the template. See [`examples/generate_samples.py`](examples/generate_samples.py) for a deterministic script that writes 20 rendered docs to [`examples/rendered_samples.jsonl`](examples/rendered_samples.jsonl) and [`examples/gold_spans.jsonl`](examples/gold_spans.jsonl), both committed for inspection without installing.

## Why Filipino PII is distinct

Off-the-shelf multilingual PII detectors (`Presidio`, `GLiNER-Multi-PII`, `Azure PII`) don't cover Filipino as a first-class language. Key signals they miss:

- **Code-switching (Taglish).** Identifiers in English formatting inside Tagalog prose and vice versa; monolingual recognizers mis-segment at language boundaries.
- **`PSGC` geographic hierarchy.** Four levels: `region > province > city/municipality > barangay`. The 42,036 barangays (often reused across provinces) are strong quasi-identifiers that generic `LOC` taggers flatten away.
- **Origin-stratified names.** Spanish (~62%, legacy of the 1849 Clavería decree), native Tagalog (~25%), Chinese (~8%), Anglo (rare). Fairness across these buckets is measurable.
- **Filipino dates.** `Ika-12 ng Hunyo, 1998` coexists with `1998-06-12` and `06/12/1998`; no English parser recognizes `Enero`, `Pebrero`, `Marso`.
- **Honorifics fused with names.** `Kuya`, `Ate`, `Lolo`, `Lola` in social text; `Bb.`, `Gng.`, `Dr.`, `Atty.`, `Engr.` in legal/clinical text; both fuse orthographically.

### Government ID formats

| ID               | Issuer                                 | Digits | Display format        |
|------------------|----------------------------------------|--------|-----------------------|
| `PSN`            | `PSA` (national ID)                    | 16     | `NNNN-NNNN-NNNN-NNNN` |
| `PCN`            | `PSA` (card number)                    | 12     | `NNNN-NNNN-NNNN`      |
| `TIN`            | `BIR` (tax)                            | 9 + 3  | `NNN-NNN-NNN-BBB`     |
| `SSS`            | Social Security System                 | 10     | `NN-NNNNNNN-N`        |
| `GSIS`           | Gov't Service Insurance                | 11     | `NNNNNNNNNNN`         |
| `UMID`           | Unified Multi-Purpose ID               | 12     | `NNNN-NNNNNNN-N`      |
| `PhilHealth PIN` | `PhilHealth`                           | 12     | `NN-NNNNNNNNN-N`      |
| `PRC license`    | Professional Regulation Commission     | 7      | `NNNNNNN`             |
| `DFA passport`   | Department of Foreign Affairs          | 2L+7D  | `LNNNNNNNL`           |

`faker-ph` encodes these at the generator level so NLP corpora built on it reflect real Philippine linguistic and administrative reality.

## What's here / what's coming

**`v0.1.0` ships:** `FakerPH` class (25+ identifier generators plus address/name/date/email methods and a `patient_record()` builder), bundled `PSGC` data (17 regions, 117 provinces, 1,648 cities, 42,036 barangays), mobile and landline tables, origin-stratified name inventory, `render()` utility, three starter templates, and 20 deterministic example outputs.

**Roadmap:** more clinical templates (prescription, referral, lab report, PhilHealth claim), more legal templates (contract NDA, notarial acknowledgment, complaint), reverse-engineered checksum algorithms where possible, and a trained PII detection model released separately (see [Citation](#citation)).

## Glossary

**Identity and civil registry**

| Acronym    | Full name                                    | Role                                        |
|------------|----------------------------------------------|---------------------------------------------|
| `PhilSys`  | Philippine Identification System             | National ID program                         |
| `PSN`      | PhilSys Number                               | Permanent 16-digit identifier               |
| `PCN`      | PhilSys Card Number                          | 12-digit number printed on physical card    |
| `PSA`      | Philippine Statistics Authority              | Issues `PSN`/`PCN`, maintains civil registry |
| `PSGC`     | Philippine Standard Geographic Code          | Region/province/city/barangay hierarchy     |

**Tax and social insurance**

| Acronym       | Full name                          | Role                                         |
|---------------|------------------------------------|----------------------------------------------|
| `BIR`         | Bureau of Internal Revenue         | Issues `TIN`s                                |
| `TIN`         | Taxpayer Identification Number     | 12-digit tax ID                              |
| `SSS`         | Social Security System             | Private-sector contributors                  |
| `GSIS`        | Gov't Service Insurance System     | Government-sector contributors               |
| `UMID`        | Unified Multi-Purpose ID           | `SSS`/`GSIS`/`PhilHealth`/Pag-IBIG one card  |
| `PhilHealth`  | Philippine Health Insurance Corp.  | Universal health coverage                    |

**Professional and travel**

| Acronym | Full name                           | Role                                          |
|---------|-------------------------------------|-----------------------------------------------|
| `PRC`   | Professional Regulation Commission  | Licenses doctors, lawyers, engineers, teachers |
| `LTO`   | Land Transportation Office          | Driver's licenses                             |
| `DFA`   | Department of Foreign Affairs       | Passports                                     |

**Banking and telecom**

| Acronym    | Full name                           | Role                                                   |
|------------|-------------------------------------|--------------------------------------------------------|
| `BDO`      | Banco de Oro                        | Largest PH private bank                                |
| `BPI`      | Bank of the Philippine Islands      | Oldest PH bank (1851)                                  |
| `Landbank` | Land Bank of the Philippines        | State-owned bank                                       |
| `NCR`      | National Capital Region             | Metro Manila (area code `02`)                          |
| `PTE`      | Public Telecommunications Entity    | NCR 8-digit block operator (`3`=Bayan, `5`=Eastern, `6`=ABS-CBN, `7`=Globe, `8`=PLDT) |

**Other terms in the sample data**

| Acronym  | Full name                        | Role                                             |
|----------|----------------------------------|--------------------------------------------------|
| `Brgy.`  | Barangay                         | Smallest admin unit (~42K nationwide)            |
| `QC`     | Quezon City                      | Largest NCR city                                 |
| `PNP`    | Philippine National Police       | Used in `POLICE_BLOTTER` template                |
| `DOH`    | Department of Health             |                                                  |
| `BPO`    | Business Process Outsourcing     | $30B PH industry, large PII workloads            |

## Caveats

Generated identifiers are **format-valid but unregistered**; do not use them to validate real documents. Bundled name lists (~50 per origin bucket) are for synthetic generation only, not sufficient as training ground truth. `PSGC` data reflects 2023 publications; refresh from upstream for production use.

## Citation

```bibtex
@software{roxas2026fakerph,
  author  = {Roxas, Daniel Quillan},
  title   = {faker-ph: Philippine-specific synthetic PII generator},
  year    = {2026},
  url     = {https://github.com/danielquillanroxas/faker-ph},
  version = {0.1.0}
}
```

A companion paper is in preparation; this entry will be updated once published.

## Contributing

Issues and PRs welcome. Run `pytest` and `ruff check .` before submitting. For large changes (new template categories, checksum algorithms, additional name buckets), open an issue first.

## License

Code: [`Apache-2.0`](LICENSE). Bundled reference data: redistributed under original upstream licenses (see [`NOTICE`](NOTICE)).
