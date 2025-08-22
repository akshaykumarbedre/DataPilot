"""
Example usage of the updated Tooth History API for frontend integration.
This shows how to work with the new JSON-based tooth history system.
"""

from app.services.tooth_history_service import tooth_history_service

class ToothHistoryAPIExample:
    """Example class showing how to use the tooth history API from frontend."""
    
    def add_patient_complaint(self, patient_id: int, tooth_number: int, complaint_status: str, complaint_description: str):
        """
        Add a new patient complaint for a tooth.
        
        Usage from frontend:
        - When patient reports a new problem with a tooth
        - Multiple complaints can be added to the same tooth over time
        """
        success = tooth_history_service.add_tooth_history_entry(
            patient_id=patient_id,
            tooth_number=tooth_number,
            record_type="patient_problem",
            status=complaint_status,
            description=complaint_description
        )
        
        return {
            "success": success,
            "message": "Patient complaint added successfully" if success else "Failed to add complaint"
        }
    
    def add_doctor_finding(self, patient_id: int, tooth_number: int, finding_status: str, finding_description: str, examination_id=None):
        """
        Add a new doctor finding for a tooth.
        
        Usage from frontend:
        - When doctor examines a tooth and records findings
        - Multiple findings can be added to track treatment progress
        """
        success = tooth_history_service.add_tooth_history_entry(
            patient_id=patient_id,
            tooth_number=tooth_number,
            record_type="doctor_finding",
            status=finding_status,
            description=finding_description,
            examination_id=examination_id
        )
        
        return {
            "success": success,
            "message": "Doctor finding added successfully" if success else "Failed to add finding"
        }
    
    def get_tooth_complete_history(self, patient_id: int, tooth_number: int):
        """
        Get complete history for a tooth to display in UI.
        
        Returns:
        - All patient complaints with their history
        - All doctor findings with their history
        - Current status of the tooth
        """
        full_history = tooth_history_service.get_tooth_full_history(patient_id, tooth_number)
        current_status = tooth_history_service.get_tooth_current_status(patient_id, tooth_number)
        
        return {
            "tooth_number": tooth_number,
            "current_status": current_status["current_status"],
            "patient_complaints": self._format_history_records(full_history["patient_problems"]),
            "doctor_findings": self._format_history_records(full_history["doctor_findings"]),
            "summary": {
                "total_complaints": len(full_history["patient_problems"]),
                "total_findings": len(full_history["doctor_findings"]),
                "latest_complaint": current_status.get("latest_patient_problem"),
                "latest_finding": current_status.get("latest_doctor_finding")
            }
        }
    
    def get_tooth_timeline_for_ui(self, patient_id: int, tooth_number: int):
        """
        Get tooth timeline formatted for UI display.
        
        Returns chronological list of all events for a tooth.
        """
        timeline = tooth_history_service.get_tooth_timeline(patient_id, tooth_number)
        
        formatted_timeline = []
        for entry in timeline:
            formatted_timeline.append({
                "date": entry["date"],
                "type": "Patient Complaint" if entry["type"] == "patient_problem" else "Doctor Finding",
                "status": entry["status"],
                "description": entry["description"],
                "icon": "👤" if entry["type"] == "patient_problem" else "👨‍⚕️"
            })
        
        return formatted_timeline
    
    def _format_history_records(self, records):
        """Helper method to format history records for UI."""
        formatted_records = []
        
        for record in records:
            # Combine the history arrays into timeline entries
            status_history = record.get("status_history", [])
            description_history = record.get("description_history", [])
            date_history = record.get("date_history", [])
            
            history_entries = []
            for i in range(len(date_history)):
                history_entries.append({
                    "date": date_history[i],
                    "status": status_history[i] if i < len(status_history) else "",
                    "description": description_history[i] if i < len(description_history) else ""
                })
            
            formatted_records.append({
                "record_id": record["id"],
                "current_status": record["current_status"],
                "current_description": record["current_description"],
                "history_entries": history_entries,
                "total_entries": len(history_entries)
            })
        
        return formatted_records

# Example usage
def example_frontend_workflow():
    """Example of how frontend would use the API."""
    
    api = ToothHistoryAPIExample()
    patient_id = 1
    tooth_number = 21
    
    # 1. Patient reports pain
    result = api.add_patient_complaint(
        patient_id=patient_id,
        tooth_number=tooth_number,
        complaint_status="pain",
        complaint_description="Sharp pain when chewing"
    )
    print("Added patient complaint:", result)
    
    # 2. Doctor examines and finds cavity
    result = api.add_doctor_finding(
        patient_id=patient_id,
        tooth_number=tooth_number,
        finding_status="caries",
        finding_description="Small cavity on occlusal surface"
    )
    print("Added doctor finding:", result)
    
    # 3. Patient reports continued pain after initial visit
    result = api.add_patient_complaint(
        patient_id=patient_id,
        tooth_number=tooth_number,
        complaint_status="pain",
        complaint_description="Pain persists, especially at night"
    )
    print("Added follow-up complaint:", result)
    
    # 4. Doctor performs treatment
    result = api.add_doctor_finding(
        patient_id=patient_id,
        tooth_number=tooth_number,
        finding_status="filled",
        finding_description="Cavity filled with composite resin"
    )
    print("Added treatment finding:", result)
    
    # 5. Get complete history for UI display
    history = api.get_tooth_complete_history(patient_id, tooth_number)
    print("\nComplete tooth history:")
    print(f"Current Status: {history['current_status']}")
    print(f"Total Complaints: {history['summary']['total_complaints']}")
    print(f"Total Findings: {history['summary']['total_findings']}")
    
    # 6. Get timeline for UI
    timeline = api.get_tooth_timeline_for_ui(patient_id, tooth_number)
    print("\nTooth Timeline:")
    for entry in timeline:
        print(f"{entry['icon']} {entry['date']} - {entry['type']}: {entry['status']} - {entry['description']}")

if __name__ == "__main__":
    example_frontend_workflow()
