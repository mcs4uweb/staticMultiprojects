import boto3


SLACK_WEBHOOK_URL = 'REDACTED_SLACK_WEBHOOK_URL'
DISQUALIFYING_CONDITIONS = {
    "mental_health_behavioral": [
        "schizophrenia",
        "psychotic disorders",
        "bipolar disorder",
        "manic-depressive illness",
        "major depressive disorder with hospitalizations",
        "severe anxiety disorders requiring medication",
        "post-traumatic stress disorder",
        "ptsd",
        "personality disorders",
        "antisocial personality disorder",
        "borderline personality disorder",
        "autism spectrum disorders",
        "severe adhd requiring medication after age 14",
        "eating disorders",
        "anorexia",
        "bulimia",
        "history of suicide attempts",
        "self-harm",
        "psychiatric hospitalization",
        "substance abuse",
        "substance dependence",
        "alcohol dependence",
        "drug dependence",
        "chronic insomnia requiring medication",
        "panic attacks",
        "severe phobias",
        "history of violence",
        "aggressive behavior",
        "compulsive behaviors interfering with function"
    ],
    
    "cardiovascular": [
        "congenital heart disease",
        "coronary artery disease",
        "heart failure",
        "cardiomyopathy",
        "heart rhythm disorders",
        "atrial fibrillation",
        "heart valve disease requiring surgery",
        "uncontrolled hypertension",
        "history of heart attack",
        "cardiac surgery",
        "pacemaker",
        "implantable cardioverter-defibrillator",
        "chest pain with exertion",
        "shortness of breath at rest",
        "syncope of cardiac origin",
        "fainting",
        "blood pressure >140/90 despite treatment"
    ],
    
    "respiratory": [
        "severe asthma requiring frequent medication",
        "chronic obstructive pulmonary disease",
        "copd",
        "cystic fibrosis",
        "pulmonary fibrosis",
        "history of pneumothorax",
        "collapsed lung",
        "sleep apnea requiring cpap",
        "chronic bronchitis",
        "wheezing with mild exertion",
        "chronic cough with sputum",
        "exercise intolerance due to breathing"
    ],
    
    "neurological": [
        "epilepsy",
        "seizure disorders",
        "multiple sclerosis",
        "cerebral palsy",
        "traumatic brain injury with lasting effects",
        "brain tumors",
        "stroke with residual deficits",
        "parkinson's disease",
        "migraine headaches requiring frequent medication",
        "narcolepsy",
        "recurring headaches affecting daily function",
        "memory problems",
        "cognitive impairment",
        "numbness",
        "weakness",
        "paralysis",
        "balance problems",
        "coordination problems",
        "speech difficulties"
    ],
    
    "musculoskeletal": [
        "amputation of limbs",
        "amputation of digits",
        "severe scoliosis",
        "spinal deformities",
        "chronic back pain with functional limitations",
        "joint replacements",
        "hip replacement",
        "knee replacement",
        "chronic arthritis affecting function",
        "muscular dystrophy",
        "myopathies",
        "osteogenesis imperfecta",
        "brittle bone disease",
        "unable to lift 50+ pounds",
        "chronic joint pain limiting mobility",
        "recurring dislocations",
        "significant range of motion limitations"
    ],
    
    "endocrine": [
        "type 1 diabetes mellitus",
        "type 2 diabetes requiring insulin",
        "severe thyroid disorders",
        "addison's disease",
        "cushing's syndrome",
        "pituitary disorders",
        "uncontrolled blood sugar levels",
        "extreme fatigue due to hormonal imbalances",
        "significant weight fluctuations"
    ],
    
    "gastrointestinal": [
        "crohn's disease",
        "ulcerative colitis",
        "chronic liver disease",
        "cirrhosis",
        "history of bowel obstruction",
        "severe gastroesophageal reflux disease",
        "severe gerd",
        "chronic pancreatitis",
        "chronic abdominal pain",
        "frequent diarrhea",
        "chronic constipation",
        "difficulty maintaining weight",
        "chronic nausea",
        "chronic vomiting"
    ],
    
    "genitourinary": [
        "chronic kidney disease",
        "history of recurrent kidney stones",
        "chronic urinary tract infections",
        "severe menstrual disorders",
        "testicular disorders affecting function",
        "ovarian disorders affecting function",
        "chronic pelvic pain",
        "urinary incontinence",
        "persistent blood in urine"
    ],
    
    "vision_hearing": [
        "legal blindness",
        "severe vision loss",
        "color blindness",
        "severe refractive errors not correctable",
        "retinal disorders",
        "glaucoma",
        "history of retinal detachment",
        "deafness",
        "severe hearing loss",
        "chronic ear infections",
        "tinnitus affecting function",
        "balance disorders",
        "meniere's disease"
    ],
    
    "skin": [
        "severe eczema",
        "severe psoriasis",
        "chronic skin ulcers",
        "extensive scarring limiting function",
        "severe acne not responsive to treatment",
        "skin cancer"
    ],
    
    "blood_disorders": [
        "sickle cell disease",
        "hemophilia",
        "bleeding disorders",
        "severe anemia not responsive to treatment",
        "leukemia",
        "lymphoma",
        "thrombotic disorders"
    ],
    
    "infectious_diseases": [
        "hiv",
        "aids",
        "chronic hepatitis b",
        "chronic hepatitis c",
        "active tuberculosis",
        "tuberculosis with complications",
        "chronic infections not responsive to treatment"
    ]
}

SEVERITY_INDICATORS = [
    "severe",
    "chronic",
    "uncontrolled",
    "requiring hospitalization",
    "requiring frequent medication",
    "with complications",
    "not responsive to treatment",
    "affecting daily function",
    "with functional limitations",
    "requiring surgery",
    "with lasting effects",
    "recurrent",
    "persistent"
]
ALL_DISQUALIFYING_CONDITIONS = []
for category, conditions in DISQUALIFYING_CONDITIONS.items():
    ALL_DISQUALIFYING_CONDITIONS.extend(conditions)

# Commonly used medication-to-condition mappings
MEDICATION_TO_CONDITION = {
    "insulin": "diabetes",
    "metformin": "diabetes",
    "glipizide": "diabetes",
    "lisinopril": "hypertension",
    "amlodipine": "hypertension",
    "metoprolol": "heart condition",
    "albuterol": "asthma",
    "inhaler": "respiratory condition",
    "sertraline": "depression",
    "fluoxetine": "depression",
    "citalopram": "depression",
    "escitalopram": "depression",
    "lorazepam": "anxiety",
    "clonazepam": "anxiety",
    "alprazolam": "anxiety",
    "lithium": "bipolar disorder",
    "quetiapine": "psychiatric condition",
    "olanzapine": "psychiatric condition",
    "warfarin": "cardiovascular condition",
    "clopidogrel": "cardiovascular condition",
    "levothyroxine": "thyroid disorder",
    "prednisone": "inflammatory condition",
    "gabapentin": "neurological condition",
    "phenytoin": "seizure disorder",
    "carbamazepine": "seizure disorder",
    "valproic acid": "seizure disorder"
}

# Conditions that may be waiverable depending on severity/control
POTENTIALLY_WAIVERABLE = [
    "mild asthma",
    "controlled hypertension",
    "mild depression without hospitalization",
    "controlled diabetes type 2",
    "mild anxiety",
    "history of kidney stones",
    "mild scoliosis",
    "correctable vision problems",
    "mild hearing loss",
    "controlled thyroid disorder",
    "mild adhd",
    "seasonal allergies",
    "mild acne",
    "controlled gerd",
    "minor joint problems"
]

def send_slack_notification(message):
   
    if not SLACK_WEBHOOK_URL:
        print("Error: Slack webhook URL is not configured.")
        return

    # The payload for the Slack message
    payload = {
        "text": message
    }

    try:
        # Send the HTTP POST request to the Slack webhook URL
        response = requests.post(
            SLACK_WEBHOOK_URL,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status() # Raise an exception for bad status codes
        print("Successfully sent message to Slack.")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error sending to Slack: {err.response.status_code} - {err.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while sending to Slack: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def get_medical_entities(text, region='us-gov-west-1'):
    """
    Analyzes medical text using AWS Comprehend Medical
    """
    client = boto3.client(service_name='comprehendmedical', region_name=region)
    result = client.detect_entities(Text=text)
    return result['Entities']

def check_extension_if_else(filename):
    """
    Checks the file extension using an if/elif/else block.
    """
    if filename.endswith('.txt'):
        print("This is a text file.")
    elif filename.endswith('.pdf'):
        print("This is a PDF file.")
    elif filename.endswith('.xml'):
        print("This is an XML file.")
    else:
        print("Unknown file type.")

def main():
    """
    Main function to demonstrate the medical text analysis
    """
    medical_text = '''
 Chief Complaint:
 “I’ve been having trouble keeping my blood sugars in range, more asthma flare‐ups, and my stomach cramps are worse. I’ve also been feeling more down and having headaches.”
History of Present Illness:
 – Diabetes Mellitus Type 1: Diagnosed at age 8. Currently on an insulin pump. Over the past 3 months, reports increased hyperglycemic episodes (BG > 250 mg/dL) despite frequent basal adjustments. Occasional nocturnal hypoglycemia (BG < 70 mg/dL) waking him twice weekly. Diet adherence variable due to gastrointestinal symptoms.
 – Asthma (mild intermittent): Since childhood. Uses albuterol inhaler ~3–4 times/week, up from baseline twice monthly. Noted increased wheezing and chest tightness with seasonal changes (pollen). No recent corticosteroid bursts.
 – Irritable Bowel Syndrome: Crampy lower abdominal pain with alternating constipation and loose stools, 3–4 days/week. Symptoms worsen after high‐fat meals. Occasional bloating and urgency. No hematochezia.
 – Atopic Dermatitis: Chronic eczematous rash on antecubital and popliteal fossae. Pruritus intensifies with stress; currently using topical corticosteroids twice daily with modest relief.
 – Migraine Headaches: Onset at age 16. 2–3 attacks per month, throbbing unilateral pain, associated with photophobia and nausea. Responds partially to sumatriptan.
 – Major Depressive Disorder: Diagnosed at age 18. Reports low mood, anhedonia, early morning awakening, concentration difficulties. Currently on sertraline 100 mg daily; efficacy waning in past 6 weeks. Denies suicidal ideation.
 – ADHD: Diagnosed at age 12. On lisdexamfetamine 30 mg in the morning. Reports occasional rebound irritability in late afternoon.
Review of Systems:
General: Reports fatigue, no fevers or night sweats, weight stable over past 6 months.
HEENT: Occasional photophobia with migraines; no vision changes aside from background retinopathy screening normal last year.
Respiratory: Intermittent wheezing and chest tightness; uses inhaler as above. No hemoptysis.
Cardiovascular: No chest pain or palpitations.
Gastrointestinal: Crampy lower abdominal pain, bloating, variable bowel habits; denies bleeding.
Genitourinary: No dysuria or hematuria.
Musculoskeletal: No joint pains beyond occasional stiffness from eczema scratching.
Neurologic: Migraines as described; no seizures or focal deficits.
Skin: Eczematous plaques with pruritus; no new lesions.
Psychiatric: Depressed mood, poor concentration, denies SI/HI.
Objective:
 Vital Signs:
Temperature: 98.4 °F (36.9 °C)
Heart Rate: 88 bpm
Blood Pressure: 132/84 mmHg
Respiratory Rate: 16 breaths/min
SpO₂: 98% on room air
Height: 5′10″ (178 cm), Weight: 200 lb (91 kg) (BMI 28.7 kg/m²)
General:
 Alert, cooperative, appears fatigued.
HEENT:
Eyes: Conjunctiva clear; fundoscopic exam shows mild background diabetic retinopathy.
Ears/Nose/Throat: Mucosa moist, no nasal polyps or pharyngeal erythema.
Neck:
 Supple, no lymphadenopathy, no thyromegaly.
Chest/Lungs:
 Bilateral expiratory wheezes, no crackles. Good air entry.
Cardiovascular:
 Regular rate and rhythm, S1/S2 normal, no murmurs/rubs/gallops.
Abdomen:
 Soft, non‐distended, mild tenderness in left lower quadrant, no rebound or guarding, bowel sounds present.
Skin:
 Eczematous, lichenified plaques in antecubital and popliteal fossae; excoriations noted.
Neurologic:
 Cranial nerves II–XII intact, normal strength and sensation in all extremities, reflexes 2+ and symmetric.
Psychiatric:
 Affect mildly constricted, mood “a bit down,” thought processes logical, oriented ×3, good insight, no psychosis.
Laboratory Data (most recent):
HbA1c: 8.7% (goal < 7%)
Fasting Blood Glucose (avg): 160–220 mg/dL
Lipid Panel: LDL 150 mg/dL, HDL 38 mg/dL, Triglycerides 200 mg/dL
TSH: 2.1 µIU/mL (normal)
Urine Microalbumin: 45 µg/mg creatinine (elevated)
Pulmonary Function (6 months ago):
FEV₁: 78% predicted
FEV₁/FVC: 0.75
Imaging:
No recent imaging studies on file.
Other Data:
Insulin pump logs show frequent missed boluses and variable basal adjustments.
DSM‐5 checklist confirms persistent ADHD and moderate depressive symptoms per PHQ-9 score of 13.
'''
    entities = get_medical_entities(medical_text)
    
    print(f"Analysis of text: '{medical_text}'\n")
    for entity in entities:
        print('Entity:', entity)

    is_fit_for_duty = True
    #disqualifying_conditions = ["asthma", "diabetes", "epilepsy"]
    mental_health_conditions = DISQUALIFYING_CONDITIONS["mental_health_behavioral"]

    print(mental_health_conditions[0])

    for entity in entities:
        # Check for disqualifying medical conditions
        if entity['Category'] == 'MEDICAL_CONDITION':
            for condition in DISQUALIFYING_CONDITIONS["mental_health_behavioral"]:
                if condition in entity['Text'].lower():
                    is_fit_for_duty = False
                    print(f"Disqualifying condition found: {entity['Text']}")
                    break # Exit inner loop once a match is found
            for condition in DISQUALIFYING_CONDITIONS["cardiovascular"]:
                if condition in entity['Text'].lower():
                    is_fit_for_duty = False
                    print(f"Disqualifying condition found: {entity['Text']}")
                    break # Exit inner loop once a match is found
            for condition in DISQUALIFYING_CONDITIONS["respiratory"]:
                if condition in entity['Text'].lower():
                    is_fit_for_duty = False
                    print(f"Disqualifying condition found: {entity['Text']}")
                    break
            for condition in DISQUALIFYING_CONDITIONS["neurological"]:
                if condition in entity['Text'].lower():
                    is_fit_for_duty = False
                    print(f"Disqualifying condition found: {entity['Text']}")
                    break
            for condition in DISQUALIFYING_CONDITIONS["musculoskeletal"]:
                if condition in entity['Text'].lower():
                    is_fit_for_duty = False
                    print(f"Disqualifying condition found: {entity['Text']}")
                    break
            for condition in DISQUALIFYING_CONDITIONS["genitourinary"]:
                if condition in entity['Text'].lower():
                    is_fit_for_duty = False
                    print(f"Disqualifying condition found: {entity['Text']}")
                    break
            for condition in DISQUALIFYING_CONDITIONS["gastrointestinal"]:
                if condition in entity['Text'].lower():
                    is_fit_for_duty = False
                    print(f"Disqualifying condition found: {entity['Text']}")
                    break
            for condition in DISQUALIFYING_CONDITIONS["vision_hearing"]:
                if condition in entity['Text'].lower():
                    is_fit_for_duty = False
                    print(f"Disqualifying condition found: {entity['Text']}")
                    break
            for condition in DISQUALIFYING_CONDITIONS["skin"]:
                if condition in entity['Text'].lower():
                    is_fit_for_duty = False
                    print(f"Disqualifying condition found: {entity['Text']}")
                    break
            for condition in DISQUALIFYING_CONDITIONS["endocrine"]:
                if condition in entity['Text'].lower():
                    is_fit_for_duty = False
                    print(f"Disqualifying condition found: {entity['Text']}")
                    break
            for condition in DISQUALIFYING_CONDITIONS["blood_disorders"]:
                if condition in entity['Text'].lower():
                    is_fit_for_duty = False
                    print(f"Disqualifying condition found: {entity['Text']}")
                    break
            for condition in DISQUALIFYING_CONDITIONS["infectious_diseases"]:
                if condition in entity['Text'].lower():
                    is_fit_for_duty = False
                    print(f"Disqualifying condition found: {entity['Text']}")
                    break
            if not is_fit_for_duty:
                break # Exit outer loop if disqualified
    
    if is_fit_for_duty:
        print("No disqualifying conditions found. Candidate may be fit for duty.")
    else:
        print("Disqualifying conditions found. Candidate is not fit for duty.")

if __name__ == '__main__':
    main()
