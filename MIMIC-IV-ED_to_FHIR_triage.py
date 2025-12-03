import pandas as pd
import json
import math

df = pd.read_csv("triage.csv.gz")

# data cleaning
def is_number_clean(x):
    if pd.isna(x):   # filters NaN, None
        return False
    try:
        float_x = float(x)
        if math.isnan(float_x):
            return False
        return True
    except:
        return False

def make_obs(code, display, value, unit, sid, stay_id):
    return {
        "resourceType": "Observation",
        "id": f"tri-{code}-{stay_id}",
        "status": "final",
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": code,
                "display": display
            }]
        },
        "subject": {"reference": f"Patient/pat-{sid}"},
        "encounter": {"reference": f"Encounter/enc-{stay_id}"},
        "valueQuantity": {
            "value": float(value),
            "unit": unit
        }
    }

def make_chief_complaint(text, sid, stay_id):
    return {
        "resourceType": "Condition",
        "id": f"cc-{stay_id}",
        "clinicalStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active"}]},
        "verificationStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-ver-status", "code": "confirmed"}]},
        "category": [{"coding": [{"system": "http://loinc.org", "code": "75310-3", "display": "Chief complaint"}]}],
        "subject": {"reference": f"Patient/pat-{sid}"},
        "encounter": {"reference": f"Encounter/enc-{stay_id}"},
        "code": {"text": text}
    }

entries = []

for _, row in df.iterrows():
    sid = row["subject_id"]
    stay = row["stay_id"]

    vitals = [
        ("8310-5", "Temperature",   row["temperature"], "C"),
        ("8867-4", "Heart rate",    row["heartrate"],   "beats/min"),
        ("9279-1", "Resp rate",     row["resprate"],    "breaths/min"),
        ("59408-5","O2 sat",        row["o2sat"],       "%"),
        ("8480-6", "Systolic BP",   row["sbp"],         "mmHg"),
        ("8462-4", "Diastolic BP",  row["dbp"],         "mmHg"),
        ("72514-3","Pain score",    row["pain"],        "1-10"),
        ("LA30139-1","ED Acuity",   row["acuity"],      "")
    ]

    # use only valid numeric observations
    for loinc, disp, value, unit in vitals:
        if is_number_clean(value):
            obs = make_obs(loinc, disp, value, unit, sid, stay)
            entries.append({
                "resource": obs,
                "request": {"method": "PUT", "url": f"Observation/{obs['id']}"}
            })

    # chief complaint
    if isinstance(row["chiefcomplaint"], str) and len(row["chiefcomplaint"].strip()) > 0:
        cc = make_chief_complaint(row["chiefcomplaint"], sid, stay)
        entries.append({
            "resource": cc,
            "request": {"method": "PUT", "url": f"Condition/{cc['id']}"}
        })

bundle = {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": entries
}

with open("mimic_ed_triage_bundle.json", "w") as f:
    json.dump(bundle, f, indent=2)
