# Bug Report

## Issues Identified

1. **Visit Record Update Issue**
    - When changing the examination, the visit record is not updating for the same patient.

2. **Data Isolation Problem**
    - When adding history to patient problems, the same history displays in doctor findings.
    - Both sections should be isolated from each other.
    - When reopening, the status updates in both dental chat sections.
    - Need to keep data isolated for both dental chat components.
    - Issue: Same database value renders in both sections - they should be separate filter based on (record_type = Column(String(20), nullable=False)  # 'patient_problem' or 'doctor_finding').

3. **Save Functionality Enhancement**
    - Update code to allow saving even when no description is provided.
    - Description should be an optional field.

4. **CSV Export Feature**
    - Merge all data into a single column and export as one CSV file.
    - Create function to flatten all data before CSV export.
    - Remove import feature from export tab.