# ==============================================
# 1. TESTS
# Departments related to laboratory analysis and high-volume test data. 
# This group makes up the majority of the dataset and is kept separate for clarity.
# ==============================================
TESTS = {
    'LAB. ANALISI': 'TEST / HIGH_VOLUME_LAB',
}


# ==============================================
# 2. RADIOLOGY
# Imaging-based diagnostic departments including radiology and neuroradiology.
# These represent a significant portion of hospital activity (≈10%) and are analyzed independently.
# ==============================================
RADIOLOGY = {
    'RADIOLOGIA': 'IMAGING / RADIOLOGY_DEPT',
    'U.O.S.D. NEURORADIOLOGIA': 'NEURO_IMAGING',
    }

# ==============================================
# 3. SPECIALTY DIAGNOSTIC / INTERVENTIONAL / MEDICAL
# Outpatient specialty clinics (often labeled 'AMBULATORIO'). 
# These cover most of the hospital’s diagnostic and specialty services and also
# treatment and administration of medicines 
# ==============================================
MEDICAL = {
    'GASTROENTEROLOGIA - AMBULATORIO': 'GASTROENTEROLOGY',
    'NEFROLOGIA - AMBULATORIO':'NEPHROLOGY',
    'DERMATOLOGIA E MALATTIE VENEREE - AMBULATORIO': 'DERMATOLOGY',
    'MEDICINA INTERNA - AMBULATORIO': 'INTERNAL_MEDICINE',
    'NEUROLOGIA - AMBULATORIO': 'NEUROLOGY',
    'PNEUMOLOGIA FISIOPATOLOGIA RESPIRATORIA - AMBULATORIO': 'PULMONOLOGY',
    'REPARTO AMBULATORIALE ALLERGOLOGIA': 'ALLERGOLOGY_AMB',
    "CARDIOLOGIA D'EMERGENZA CON UTIC - AMBULATORIO": 'EMERGENCY_CARDIOLOGY_UTIC',
    'MALATTIE INFETTIVE E TROPICALI A DIREZIONE UNIVERSITARIA - AMBULATORIO - EROGAZIONE FARMACI PER ESTERNI': 'INFECTIOUS_DISEASES_PHARMACY'
    }

# ==============================================
# 4. SURGICAL / VASCULAR / ANESTESIA
# Departments responsible for surgical interventions, vascular procedures, 
# and anesthesia or resuscitation units.
# ==============================================
SURGERY = {
    'NEUROCHIRURGIA - AMBULATORIO': 'NEUROSURGERY',
    'ORTOPEDIA E TRAUMATOLOGIA - AMBULATORIO': 'ORTHOPEDICS_TRAUMA',
    'OTORINOLARINGOIATRIA - AMBULATORIO': 'ENT_OTOLARYNGOLOGY',
    'UROLOGIA - AMBULATORIO': 'UROLOGY',
    'REPARTO AMBULATORIALE CHIRURGIA VASCOLARE': 'VASCULAR_SURGERY_AMB',
    'REPARTO AMBULATORIALE CH.MAX.ODONTOST.': 'MAXILLOFACIAL_SURGERY_AMB'
}
# Note from domain expert: Given the nature of the emergency room, probably only surgical consultations, which means that our patient will most likely have this procedure linked to their
# discharge from the relevant medical department, with a small possibility of microsurgery in the ER


#5. Intensive practices 
INTENSIVE = {
    'REPARTO AMBULATORIALE ANESTESIA E RIANIMAZIONE': 'ANESTHESIA_RESUSCITATION_AMB',
}

# ==============================================
# 6. ONCOLOGY
# All oncology-related activities, including surgical, hematologic, 
# and general outpatient oncology departments.
# ==============================================
ONCOLOGY = {
    'REPARTO AMBULATORIALE ONCOLOGIA': 'ONCOLOGY_GENERAL',
    'CHIRURGIA GENERALE ED ONCOLOGICA - AMBULATORIO': 'ONCOLOGY_SURGERY',
    'EMATOLOGIA AD INDIRIZZO ONCOLOGICO - AMBULATORIO': 'ONCOLOGY_HEMATOLOGY',
    }


# ==============================================
# 7. FOLLOW-UP
# Departments focused on patient monitoring and post-acute care.
# Includes long-term management and post-surgical follow-ups.
# ==============================================
FOLLOW_UP = {
    'FOLLOW UP DEL PAZIENTE POST ACUTO - AMBULATORIO': 'POST_ACUTE_FOLLOW_UP',
}