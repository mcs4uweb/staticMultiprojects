from google import genai
from google.genai import types

client = genai.Client(api_key="AIzaSyAQbhcmzdniiKIirH-V8YRH4vwSmPnS18A")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="""
Your Goal: Analyze a patient's clinical note against specific U.S. Department of Defense medical standards (DODI 6130.03, Volume 1, Section 5) to determine if the patient has medical conditions that would disqualify or potentially disqualify them from military service.
Source Documents:
1.	The Clinical Note provided below.
2.	DoD Instruction 6130.03, Volume 1: You must use the standards found only in Section 5: DISQUALIFYING CONDITIONS. (Assume you have access to this document).
Instructions (Follow these steps precisely):
Step 1: Read the Clinical Note Carefully.
•	Understand the patient's current health issues, past medical history, and any diagnoses mentioned.
Step 2: Identify Relevant Medical Information.
•	Look for any specific medical diagnoses (like "diabetes mellitus" or "ulcerative colitis").
•	Look for any history of significant medical events (like "psychotic episode" or "surgery").
•	Look for any symptoms or findings mentioned that might relate to a disqualifying condition.
Step 3: Compare with DODI Section 5 Standards.
•	For each piece of relevant medical information identified in Step 2, check if it matches any of the disqualifying conditions listed in Section 5 of DODI 6130.03, Volume 1.
Step 4: Determine the Correct Flag Type (DISQUALIFYING or POTENTIALLY DISQUALIFYING).
•	DISQUALIFYING: Assign the flag [FLAG - DISQUALIFYING] if the clinical note confirms that the patient currently has or has a history of a condition that is listed as disqualifying in DODI Section 5.
o	Example: If the note says "Patient has history of asthma after age 13" and DODI Section 5.10.e says "History of airway hyper responsiveness including asthma...after the 13th birthday," this is DISQUALIFYING. It's a confirmed history matching the standard.
•	POTENTIALLY DISQUALIFYING: Assign the flag [FLAG - POTENTIALLY DISQUALIFYING] ONLY IF the clinical note explicitly states there is uncertainty about a diagnosis (using words like "possible," "suspected," "rule out," "differential diagnosis includes") AND that specific condition, if it were confirmed, is listed as disqualifying in DODI Section 5.
o	Example: If the note says "Impression: Possible sleep apnea, requires sleep study for confirmation" and DODI Section 5.27.b lists "sleep-related breathing disorders, including but not limited to sleep apnea" as disqualifying, this is POTENTIALLY DISQUALIFYING. The diagnosis is uncertain in the note, but would be disqualifying if confirmed.
o	IMPORTANT: Do not use this flag for conditions that are confirmed in the note, even if they happened in the past or are currently managed. If a confirmed condition matches a DODI standard, it is DISQUALIFYING, not potentially disqualifying.
•	NO FLAG: If a condition mentioned in the note is not listed in DODI Section 5, or if it clearly meets an exception described within a standard in Section 5, do not create a flag for it.
Step 5: Determine the Overall Eligibility Status.
•	Look at all the flags you created in Step 4.
•	If there is at least one [FLAG - DISQUALIFYING] flag, the overall status for the patient is DISQUALIFIED.
•	If there are only [FLAG - POTENTIALLY DISQUALIFYING] flags (and zero DISQUALIFYING flags), the overall status is POTENTIALLY DISQUALIFIED.
•	If there are no flags created at all, the overall status is QUALIFIED.
•	Write this overall status at the very beginning of your response, after a placeholder name like "Doe, Jane".
Step 6: Format Your Response Using Markdown EXACTLY Like the Example Below.
•	Start with the placeholder name and the overall eligibility status (bolded).
•	Use the heading "Military Eligibility Medical Flags:".
•	For each flag you created in Step 4, use the following Markdown structure:
o	Start with the flag type (e.g., [FLAG - DISQUALIFYING] or [FLAG - QUALIFY]) on its own line.
o	Condition: [Name of the Condition]
o	Clinical Encounter Text: "[Exact quote from the clinical note related to that condition]"
o	DODI 6130.03, Vol 1 - Section [Section Number, e.g., 5.XX.y.(z)] Text: "[Exact quote of the disqualifying standard from the DODI document]"
o	Add a blank line between each complete flag entry.
Clinical Note for Mike Hubbs
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
 """,
)
print(str(response.text))