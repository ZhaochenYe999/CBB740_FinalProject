# conda create -n mimic python=3.10
# conda activate mimic
# pip install pandas

import pandas as pd
import json

df = pd.read_csv("edstays.csv.gz")

# Patient resources
def make_patient(subject_id):
    return {
        "resourceType": "Patient",
        "id": f"pat-{subject_id}",  
        "identifier": [{
            "system": "http://mimic.physionet.org/fhir/subject-id",
            "value": str(subject_id)
        }],
        "active": True
    }

unique_patient_ids = df["subject_id"].unique()
patients = {sid: make_patient(sid) for sid in unique_patient_ids}

# Encounter resources
def make_encounter(row):
    return {
        "resourceType": "Encounter",
        "id": f"enc-{row['stay_id']}",  
        "status": "finished",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": "EMER"
        },
        "subject": {
            "reference": f"Patient/pat-{row['subject_id']}" 
        },
        "period": {
            "start": row["intime"].replace(" ", "T"),
            "end": row["outtime"].replace(" ", "T")
        },
        "extension": [
            {
                "url": "http://mimic.physionet.org/fhir/StructureDefinition/arrival-transport",
                "valueString": row["arrival_transport"]
            }
        ],
        "hospitalization": {
            "dischargeDisposition": {"text": row["disposition"]}
        }
    }

encounters = [make_encounter(row) for _, row in df.iterrows()]

# create bundle
entries = []

# Adding patients
for sid, patient in patients.items():
    entries.append({
        "fullUrl": f"Patient/pat-{sid}",
        "resource": patient,
        "request": {
            "method": "PUT",
            "url": f"Patient/pat-{sid}"
        }
    })

# Adding encounters
for enc in encounters:
    entries.append({
        "fullUrl": f"Encounter/{enc['id']}",
        "resource": enc,
        "request": {
            "method": "PUT",
            "url": f"Encounter/{enc['id']}"
        }
    })

bundle = {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": entries
}

with open("mimic_ed_patient_encounter_stay.json", "w") as f:
    json.dump(bundle, f, indent=2)
