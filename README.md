# CBB740_FinalProject

This project is about predicting Emergency Department Disposition and Length of Stay with the MIMIC-IV-ED dataset. We worked with edstays.csv.gz and triage.csv.gz files.

Project Workflow:

1. Preprocessing
- FHIR standardization

  edstays.csv.gz → processed by MIMIC-IV-ED_to_FHIR.py → produces mimic_ed_patient_encounter_stay.json

  triage.csv.gz → processed by MIMIC-IV-ED_to_FHIR_triage.py → produces mimic_ed_triage_bundle.json
- NLP feature extraction

  CBB7400_ChiefComplaint.ipynb
- JSON file extraction for modeling

  json_extraction.ipynb → produces mimic_ed_clean_combined.csv

- All preprocessed files are stored in the `data/` directory.

2. Disposition Prediction

   prediction_disposition_with_cc.ipynb

   prediction_disposition_without_cc.ipynb

3. Length of Stay (LOS) Prediction

   LOS_prediction.ipynb
