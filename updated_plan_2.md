# Plan to Modify Tooth History Update Behavior

This document outlines the plan to change the tooth history update behavior from automatic to manual (on button click).

## 1. UI Layer

### `app/ui/components/dental_chart_panel.py`

-   In the `create_dental_chart_area` method, the connection between the `statuses_selected` signal of the `EnhancedToothWidget` and the `on_tooth_statuses_changed` method will be removed.
-   The `on_tooth_statuses_changed` method will be removed or commented out.
-   The `update_tooth_record` method will be modified to be the single source of truth for updating the tooth history. It will get the currently selected statuses from the `EnhancedToothWidget`'s `status_dropdown` and use them to update the history.

### `app/ui/dental_chart.py`

-   The `on_tooth_statuses_changed` method will be removed or commented out.
-   In the `connect_signals` method, the connection for the `tooth_statuses_changed` signal from the `DentalChartPanel` will be removed.

## 2. Implementation Steps

1.  Modify `app/ui/components/dental_chart_panel.py`.
2.  Modify `app/ui/dental_chart.py`.
3.  Test the application to ensure the new behavior is working as expected.
