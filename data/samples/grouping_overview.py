# ==============================================
# 1. TESTS
# Departments related to laboratory analysis and high-volume test data. 
# This group makes up the majority of the dataset and is kept separate for clarity.
# ==============================================
TESTS = [
    "LAB. ANALISI"
]


# ==============================================
# 2. RADIOLOGY
# Imaging-based diagnostic departments including radiology and neuroradiology.
# These represent a significant portion of hospital activity (≈10%) and are analyzed independently.
# ==============================================
RADIOLOGY = [
    "RADIOLOGIA",
    "U.O.S.D. NEURORADIOLOGIA"
]


# ==============================================
# 3. SPECIALTY DIAGNOSTIC / INTERVENTIONAL
# Outpatient specialty clinics (often labeled 'AMBULATORIO'). 
# These cover most of the hospital’s diagnostic and specialty services.
# ==============================================
SPECIALTY_DIAGNOSTIC = [
    "NEUROCHIRURGIA - AMBULATORIO",
    "GASTROENTEROLOGIA - AMBULATORIO",
    "ORTOPEDIA E TRAUMATOLOGIA - AMBULATORIO",
    "OTORINOLARINGOIATRIA - AMBULATORIO",
    "NEFROLOGIA - AMBULATORIO",
    "DERMATOLOGIA E MALATTIE VENEREE - AMBULATORIO",
    "MEDICINA INTERNA - AMBULATORIO",
    "NEUROLOGIA - AMBULATORIO",
    "UROLOGIA - AMBULATORIO",
    "PNEUMOLOGIA FISIOPATOLOGIA RESPIRATORIA - AMBULATORIO",
    "REPARTO AMBULATORIALE ALLERGOLOGIA",
    "CARDIOLOGIA D'EMERGENZA CON UTIC - AMBULATORIO",
    "MALATTIE INFETTIVE E TROPICALI A DIREZIONE UNIVERSITARIA - AMBULATORIO - EROGAZIONE FARMACI PER ESTERNI"
]


# ==============================================
# 4. SURGICAL / VASCULAR / ANESTESIA
# Departments responsible for surgical interventions, vascular procedures, 
# and anesthesia or resuscitation units.
# ==============================================
SURGERY = [
    "REPARTO AMBULATORIALE CHIRURGIA VASCOLARE",
    "REPARTO AMBULATORIALE CH.MAX.ODONTOST.",
    "REPARTO AMBULATORIALE ANESTESIA E RIANIMAZIONE"
]


# ==============================================
# 5. ONCOLOGY
# All oncology-related activities, including surgical, hematologic, 
# and general outpatient oncology departments.
# ==============================================
ONCOLOGY = [
    "REPARTO AMBULATORIALE ONCOLOGIA",
    "CHIRURGIA GENERALE ED ONCOLOGICA - AMBULATORIO",
    "EMATOLOGIA AD INDIRIZZO ONCOLOGICO - AMBULATORIO"
]


# ==============================================
# 6. FOLLOW-UP
# Departments focused on patient monitoring and post-acute care.
# Includes long-term management and post-surgical follow-ups.
# ==============================================
FOLLOW_UP = [
    "FOLLOW UP DEL PAZIENTE POST ACUTO - AMBULATORIO"
]
