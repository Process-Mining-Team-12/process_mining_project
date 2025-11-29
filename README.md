# Emergency Room Process Mining Analysis

Link to the presentation: https://1drv.ms/p/c/bb84f531edaba980/ESdKGRbvZ5BIgvmYx1JdLyUBXXqkpEbzQ1bY7DsRAy8QAA?e=4NaCXv

This project aims to analyze and discover the patient care process within an emergency room using process mining techniques. The goal is to transform raw hospital data into a structured event log for analysis, identifying bottlenecks and common patient journeys.

---

## Project Structure

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

## Target Data Schema

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

## Data Mapping: Raw Columns to Target Fields

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

## Average Activity Time Mapping

| Department (Mapped)              | Average time per patient (minutes) |
|----------------------------------|------------------------------------|
| TEST                             | 10 min                             |
| RADIOLOGY_DEPT                   | 20 min                             |
| NEURORADIOLOGY                   | 40 min                             |
| GASTROENTEROLOGY                 | 25 min                             |
| NEPHROLOGY                       | 25 min                             |
| DERMATOLOGY                      | 25 min                             |
| INTERNAL_MEDICINE                | 25 min                             |
| NEUROLOGY                        | 30 min                             |
| PULMONOLOGY                      | 25 min                             |
| ALLERGOLOGY_AMB                  | 25 min                             |
| EMERGENCY_CARDIOLOGY_UTIC        | 30 min                             |
| INFECTIOUS_DISEASES_PHARMACY     | 25 min                             |
| ELIOT_TRANSFUSION                | 60 min                             |
| NEUROSURGERY                     | 30 min                             |
| ORTHOPEDICS_TRAUMA               | 25 min                             |
| ENT_OTOLARYNGOLOGY               | 25 min                             |
| UROLOGY                          | 25 min                             |
| VASCULAR_SURGERY_AMB             | 25 min                             |
| MAXILLOFACIAL_SURGERY_AMB        | 25 min                             |
| ANESTHESIA_RESUSCITATION_AMB     | 30 min                             |
| ONCOLOGY_GENERAL                 | 30 min                             |
| ONCOLOGY_SURGERY                 | 30 min                             |
| ONCOLOGY_HEMATOLOGY              | 30 min                             |
| POST_ACUTE_FOLLOW_UP             | 30 min                             |

## Activity Groups

Due to a large number of individual activities, the data was split into 6 different groups based on the `DESCR_EROGATORE` column. This column holds the description of the department that provided the service for the patient and thus served as a strong logical basis for grouping related departments together.

The mapping below defines the six categories and lists the original DESCR_EROGATORE values that were assigned to each. The format for the mapping list is [**Former DESCR_EROGATORE Name ->  `TEST/VISIT.*_department`**]
</br> example: visit to the dermatologist (previously: `DERMATOLOGIA E MALATTIE VENEREE - AMBULATORIO`) would be grouped under value `VISIT_Specialty_Diagnostics`.

</br>

 | Group| Name                    | Example Departments                              |
| :---- | :---------------------- |:----------------------------------------------  |
| 1     | Tests        | Lab. Analisi                                   |
| 2     | Radiology     | Radiologia, Neuroradiologia                     |
| 3     | Medical   | Cardio, Oculistico, Dermatologico |
| 4     | Surgery | Chirurgia, Rianimazione, Amb. Maxillo-Odontost. |
| 5     | Intensive | Reparto ambulatoriale anestesia e rianimazione |
| 6     | Oncology                | Oncologia Medica, Amb. Oncologico               |
| 7     | Follow-Up  | Follow-up del paziente post acuto - ambulatorio           |

💡 Full group division with description is available in this [file](data/samples/grouping_overview.py).

## Italian Guidelines

### Maximum waiting time based on Severity

| Severity | Maximum waiting time |
| :--- | :--- |
| RED | - |
| ORANGE | 15 minutes |
| BLUE | 60 minutes |
| GREEN | 120 minutes |
| WHITE | 240 minutes |

### Set of Indicators and Reference Standards

| INDICATOR | TYPE OF INDICATOR | REFERENCE STANDARD |
|----------|--------------------|--------------------|
| % of code-2 urgent patients who access treatment within 15 minutes | appropriateness | 85% of patients admitted with code 2 |
| % of code-3 deferrable urgency patients who access treatment within 60 minutes | appropriateness | 80% of patients admitted with code 3 |
| % of code-4 minor urgency patients who access treatment within 120 minutes | appropriateness | 75% of patients admitted with code 4 |
| % of code-5 non-urgent patients who access treatment within 240 minutes | appropriateness | 75% of patients admitted with code 5 |

## Setup & Troubleshooting

This repository uses **Git LFS** (Large File Storage) to handle large data files. You must have the Git LFS client installed to clone and pull data correctly.

### Error Handling: `git-lfs: command not found`

If you see this error while cloning or pulling, it means the Git LFS client is not installed on your system.

```bash
git-lfs filter-process: git-lfs: command not found
fatal: the remote end hung up unexpectedly
```

#### Solution

1. Install the Git LFS client.

    - macOS: `brew install git-lfs`
    - Linux (Debian/Ubuntu): `sudo apt-get install git-lfs`
    - Windows: Download and run the installer from [git-lfs.com](https://git-lfs.com/).

2. Initialize Git LFS for your user account.

    ```bash
    git lfs install
    ```

## Environment Setup

This project uses [uv](https://docs.astral.sh/uv/).

1. Install uv:

    ```bash
    pip install uv
    ```

2. Sync dependencies:

    ```bash
    uv sync
    ```

3. Run scripts:

    ```bash
    uv run scripts/s01_data_preprocessing.py
    ```

### How to Pull Large Files

After installing Git LFS, you need to download the actual data files. If you've already cloned the repository and only see small "pointer" files, run this command from inside the repository folder:

```bash
git lfs pull
```

This command checks out the correct versions of the large files from the LFS store and replaces the pointers with the actual file content. Future `git pull` commands should now work automatically.
