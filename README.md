# Emergency Room Process Mining Analysis

This project aims to analyze and discover the patient care process within an emergency room using process mining techniques. The goal is to transform raw hospital data into a structured event log for analysis, identifying bottlenecks and common patient journeys.

---

## 📂 Project Structure

The repository is organized to separate data, analysis scripts, and outputs:

```plain
.
├── data/
│   ├── raw/          # Original, unmodified source data files
│   └── processed/    # Cleaned and structured event logs (e.g., CSV, XES)
├── scripts/
│   └── ...           # Python scripts for data cleaning and analysis
├── outputs/
│   ├── figures/      # Saved process maps and charts
│   └── reports/      # Generated analysis reports
├── .gitattributes    # Git LFS configuration file
└── README.md         # Project documentation
```

---

## 🎯 Target Data Schema

The raw data will be processed into a structured event log. Each case will follow the `JSON` schema below, which is designed to be easily converted to the `XES` format.

```json
[
    {
        "name": "Case 1 [ID]",
        "emergency_room": "PS SOMETHING",
        "file": "XXXXXXXXXXX",
        "sex": "F",
        "birthday": "AAAA-MM-DD",
        "residence_city": "Milano",
        "residence_region": "Lombardia",
        "arrival_method": "CAR",
        "department": "XXXX", // check if it can change
        "age": "XX",
        "age_group": "XX-XX",
        "activities": [
            {
                "name": "ARRIVAL",
                "timestamp": "timestamp_arrival",
            },
            {
                "name": "TRIAGE_ENTRY", // or "TRIAGE_ENTRY_GREEN"
                "timestamp": "timestamp_arrival + 1 millis",
                "severity": "GREEN",
            },
            {
                "name": "ACCEPTANCY",
                "timestamp": "timestamp_acceptancy",
            },
            {
                "name": "TESTS_123",
                "timestamp": "timestamp_tests",
                "code": "AAAAXXXXXXXXX",
                "description": "GLUCOSIO,UREA (AZOTEMIA),CREATININA,...",
                "department": "",
            },
            // [more tests]
            {
                "name": "VISIT_456",
                "timestamp": "timestamp_visit",
                "code": "AAAAXXXXXXXXX",
                "description": "",
                "department": "",
            },
            // [more visits / tests]
            {
                "name": "OUTCOME_HOME",
                "timestamp": "timestamp_discharge",
            },
            {
                "name": "TRIAGE_EXIT", // or "TRIAGE_EXIT_RED"
                "timestamp": "timestamp_discharge + 1 millis",
                "severity": "RED",
            },
            {
                "name": "DISCHARGE",
                "timestamp": "timestamp_discharge + 2 millis",
                "diagnosy": {
                    "description": "",
                    "class": "",
                    "code": "",
                },
            },
        ]
    }
]
```

---

## 🗺️ Data Mapping: Raw Columns to Target Fields

The following table details how the raw data columns are mapped to the final, clean event log structure.

| Original Field | Keep? | Target Field / Activity | Notes |
|---|---|---|---|
| ID | ✅ Yes | `case_id` | Unique identifier for the patient journey. |
| PS | ✅ Yes | `emergency_room` | Filtered to keep only "PS GENERALE". |
| Scheda_PS | ✅ Yes | `file_id` | To be checked for uniqueness per case_id. |
| Sesso | ✅ Yes | `sex`| M / F. |
| Data_Nascita | ✅ Yes | `birthday` | |
| Comune_Res | ✅ Yes | `residence_city` | |
| Regione_Res | ✅ Yes | `residence_region` | |
| Mod_Arrivo | ✅ Yes | `arrival_method` | |
| Reparto | ✅ Yes | `department` | |
| eta_paziente | ✅ Yes | `age` | |
| etapaziente_ric | ✅ Yes | `age_group` | |
| data_arrivo_tot | ✅ Yes | `ARRIVAL` (Activity) | Timestamp for the "ARRIVAL" event. |
| Triage_Ingr | ✅ Yes | `TRIAGE_ENTRY` (Activity) | Timestamp for the "TRIAGE_ENTRY" event. |
| Presa_In_Carico | ✅ Yes | ACCEPTANCY (Activity) | Timestamp for the "ACCEPTANCY" event. |
| Esito | ✅ Yes | `OUTCOME_*` (Activity) | The value becomes part of the activity name (e.g. `OUTCOME_HOME`). |
| Triage_OUT | ✅ Yes | `TRIAGE_EXIT` (Activity) | Timestamp for the "TRIAGE_EXIT" event. |
| data_dimissione_tot | ✅ Yes | `DISCHARGE` (Activity) | Timestamp for the "DISCHARGE" event. |
| Medico_Dimissione | ✅ Yes | `DISCHARGE.doctor` | Attribute of the "DISCHARGE" event. |
| Diag_TXT | ✅ Yes | `DISCHARGE.diagnosis_description` | Attribute of the "DISCHARGE" event. |
| Diagnosi_Classe | ✅ Yes | `DISCHARGE.diagnosis_class` | Attribute of the "DISCHARGE" event. |
| Diagnosi_Codice | ✅ Yes | `DISCHARGE.diagnosis_code` | Attribute of the "DISCHARGE" event. |
| CODICE_RICHIESTA | ✅ Yes | `TEST/VISIT.*_code` | Used to group rows for "TEST" or "VISIT" events. |
| DESCR_PRESTAZIONE | ✅ Yes | `TEST/VISIT.*_description` | Concatenated descriptions for "TEST" or "VISIT" events. Concatenation hashed for the event. |
| DESCR_EROGATORE | ✅ Yes | `TEST/VISIT.*_department` | If this value is "LAB. ANALISI" then the activity is "TEST"; "VISIT" otherwise |
| DATA_PREVISTA_EROGAZIONE | ✅ Yes | `TEST/VISIT` (Timestamp) | Timestamp for "TEST" or "VISIT" events. |
| OBI / Data_OBI | ❓ | To be determined | Under consideration. |
| Other columns | ❌ No | (Discarded) | Not required for the analysis. |

## 🛠️ Setup & Troubleshooting

This repository uses **Git LFS** (Large File Storage) to handle large data files. You must have the Git LFS client installed to clone and pull data correctly.

### Error Handling: `git-lfs: command not found`

If you see this error while cloning or pulling, it means the Git LFS client is not installed on your system.

```bash
git-lfs filter-process: git-lfs: command not found
fatal: the remote end hung up unexpectedly
```

#### Solution

**1. Install the Git LFS client.**

- macOS: `brew install git-lfs`
- Linux (Debian/Ubuntu): `sudo apt-get install git-lfs`
- Windows: Download and run the installer from [git-lfs.com](https://git-lfs.com/).

**2. Initialize Git LFS for your user account.**

```bash
git lfs install
```

### How to Pull Large Files

After installing Git LFS, you need to download the actual data files. If you've already cloned the repository and only see small "pointer" files, run this command from inside the repository folder:

```bash
git lfs pull
```

This command checks out the correct versions of the large files from the LFS store and replaces the pointers with the actual file content. Future `git pull` commands should now work automatically.
