# Data catalogue

The files in `synthetic/` are **synthetic, seeded demo data**, calibrated to the
scale and direction of patterns reported in Census 2011 slum tables, NFHS-5,
PMAY-U, MoHUA dashboards, SBM-U, AMRUT, Maharashtra SRA norms and SDG 6/11.
They are not observations about any named settlement and must not be used for
operational decisions. Every generated record carries a reproducible seed.

## Real data connectors to add later

| Source | Likely use | Connector status |
| --- | --- | --- |
| [data.gov.in](https://data.gov.in/) | ULB, ward, PMAY and service tables | `load_real_data()` stub |
| Census of India 2011 | Population, housing and slum baselines | `load_real_data()` stub |
| NFHS-5 | Water, sanitation and health calibration | `load_real_data()` stub |
| OpenStreetMap | Roads, transit, clinics and schools | `load_real_data()` stub |
| Sentinel-2 | Flood/water/land-cover signals | `load_real_data()` stub |
| Google Open Buildings | Built-up footprint and density | `load_real_data()` stub |
| WorldPop | Gridded population estimates | `load_real_data()` stub |
| MoHUA dashboards | PMAY-U, SBM-U and AMRUT progress | `load_real_data()` stub |
| BMC / TMC open data | Ward assets, complaints and services | `load_real_data()` stub |

The planned production pipeline is: acquire under an approved licence, map
fields to the canonical schemas, remove direct identifiers, validate geography,
then replace the synthetic files without changing the API contracts.
