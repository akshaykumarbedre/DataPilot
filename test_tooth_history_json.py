#!/usr/bin/env python3
"""
Test script for the updated tooth history system with JSON storage.
This demonstrates how to use the new tooth history features.
"""

from app.services.tooth_history_service import tooth_history_service

def test_tooth_history_json():
    """Test the new JSON-based tooth history system."""
    
    print("Testing Tooth History JSON System")
    print("=" * 40)
    
    # Test patient and tooth
    patient_id = 1
    tooth_number = 21
    
    print(f"Testing for Patient ID: {patient_id}, Tooth: {tooth_number}")
    print()
    
    # 1. Add multiple patient problems
    print("1. Adding patient problems...")
    
    problems = [
        {"status": "pain", "description": "Sharp pain when eating"},
        {"status": "sensitivity", "description": "Cold sensitivity"},
        {"status": "pain", "description": "Increased pain at night"}
    ]
    
    for i, problem in enumerate(problems, 1):
        success = tooth_history_service.add_tooth_history_entry(
            patient_id=patient_id,
            tooth_number=tooth_number,
            record_type="patient_problem",
            status=problem["status"],
            description=problem["description"]
        )
        print(f"   Problem {i}: {'✓' if success else '✗'} {problem['status']} - {problem['description']}")
    
    print()
    
    # 2. Add multiple doctor findings
    print("2. Adding doctor findings...")
    
    findings = [
        {"status": "caries", "description": "Small cavity on mesial surface"},
        {"status": "filled", "description": "Cavity filled with composite"},
        {"status": "normal", "description": "Healing well, no issues"}
    ]
    
    for i, finding in enumerate(findings, 1):
        success = tooth_history_service.add_tooth_history_entry(
            patient_id=patient_id,
            tooth_number=tooth_number,
            record_type="doctor_finding",
            status=finding["status"],
            description=finding["description"]
        )
        print(f"   Finding {i}: {'✓' if success else '✗'} {finding['status']} - {finding['description']}")
    
    print()
    
    # 3. Get full tooth history
    print("3. Getting full tooth history...")
    full_history = tooth_history_service.get_tooth_full_history(patient_id, tooth_number)
    
    print(f"   Patient Problems Records: {len(full_history['patient_problems'])}")
    for record in full_history['patient_problems']:
        print(f"     - Current Status: {record['current_status']}")
        print(f"     - Status History: {record['status_history']}")
        print(f"     - Description History: {record['description_history']}")
        print(f"     - Date History: {record['date_history']}")
        print()
    
    print(f"   Doctor Findings Records: {len(full_history['doctor_findings'])}")
    for record in full_history['doctor_findings']:
        print(f"     - Current Status: {record['current_status']}")
        print(f"     - Status History: {record['status_history']}")
        print(f"     - Description History: {record['description_history']}")
        print(f"     - Date History: {record['date_history']}")
        print()
    
    # 4. Get tooth timeline
    print("4. Getting tooth timeline...")
    timeline = tooth_history_service.get_tooth_timeline(patient_id, tooth_number)
    
    print(f"   Total timeline entries: {len(timeline)}")
    for entry in timeline:
        print(f"     {entry['date']} | {entry['type'].upper()} | {entry['status']} | {entry['description']}")
    
    print()
    
    # 5. Get current tooth status
    print("5. Getting current tooth status...")
    current_status = tooth_history_service.get_tooth_current_status(patient_id, tooth_number)
    
    print(f"   Current Status: {current_status['current_status']}")
    print(f"   Patient Problems Count: {current_status['patient_problems_count']}")
    print(f"   Doctor Findings Count: {current_status['doctor_findings_count']}")
    
    if current_status['latest_patient_problem']:
        print(f"   Latest Patient Problem: {current_status['latest_patient_problem']['status']}")
    
    if current_status['latest_doctor_finding']:
        print(f"   Latest Doctor Finding: {current_status['latest_doctor_finding']['status']}")
    
    print()
    print("Test completed successfully!")

if __name__ == "__main__":
    test_tooth_history_json()
