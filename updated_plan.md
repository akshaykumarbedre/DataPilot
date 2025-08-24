# Plan to Implement Multi-Status Selection for Teeth

This document outlines the plan to add a feature that allows selecting multiple statuses for a single tooth and storing this information in the patient's history.

## 1. Database Schema

No changes are required to the database schema. The existing `ToothHistory` table has a `status_history` column of type `TEXT`, which is already used to store a JSON-encoded list of historical statuses. We will adapt our use of this column to store a list of lists, where each inner list contains the multiple statuses for a single historical entry.

## 2. Service Layer (`app/services/tooth_history_service.py`)

The following functions in `tooth_history_service.py` will be modified to handle a list of statuses instead of a single status string:

-   **`add_tooth_history_entry(self, patient_id: int, tooth_number: int, record_type: str, statuses: List[str], description: str = "", examination_id: Optional[int] = None) -> bool`**:
    -   The `status: str` parameter will be changed to `statuses: List[str]`.
    -   The `status_history` column will be updated by appending the new list of `statuses`. This will make `status_history` a list of lists.
    -   The `status` column will be updated with a comma-separated string of the `statuses` list for backward compatibility.

-   **`update_tooth_status(self, patient_id: int, tooth_number: int, new_statuses: List[str], record_type: str, description: str = '', examination_id: Optional[int] = None) -> bool`**:
    -   The `new_status: str` parameter will be changed to `new_statuses: List[str]`.
    -   This function will call the modified `add_tooth_history_entry`.

-   **`add_tooth_history(self, patient_id: int, tooth_data: Dict[str, Any]) -> Optional[Dict[str, Any]]`**:
    -   The `tooth_data` dictionary will now expect a `statuses` key with a list of strings.

## 3. UI Layer

The UI will be updated to allow users to select multiple statuses for a tooth.

-   **New `MultiSelectComboBox` Widget**:
    -   A new custom widget, `MultiSelectComboBox`, will be created to provide a dropdown with checkboxes for multiple selections.

-   **`app/ui/components/enhanced_tooth_widget.py`**:
    -   The existing `QComboBox` for status selection will be replaced with the new `MultiSelectComboBox`.
    -   A new `statuses_selected` signal will be added to emit a list of selected status strings.
    -   The `update_tooth_appearance` function will be enhanced to visually represent multiple statuses on a tooth (e.g., using gradients or other indicators).

-   **`app/ui/components/dental_chart_panel.py`**:
    -   The `on_tooth_status_changed` slot will be updated to accept a list of statuses.
    -   It will call the updated `tooth_history_service.add_tooth_history_entry` with the list of statuses.
    -   The `load_tooth_history` function will be modified to correctly parse and display the history of multiple statuses.

-   **`app/ui/dental_chart.py`**:
    -   The `on_tooth_status_changed` slot will be updated to handle the list of statuses from the `DentalChartPanel`.

## 4. Implementation Steps

The implementation will be done in the following order:

1.  Create the `MultiSelectComboBox` widget.
2.  Modify `app/ui/components/enhanced_tooth_widget.py` to use the new widget.
3.  Modify `app/services/tooth_history_service.py`.
4.  Modify `app/ui/components/dental_chart_panel.py`.
5.  Modify `app/ui/dental_chart.py`.
6.  Thoroughly test the new feature.