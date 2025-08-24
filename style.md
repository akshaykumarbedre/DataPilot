# PySide Dental Clinic Style Guide

## Color Palette
```python
COLORS = {
    'primary': '#3b82f6',
    'primary_dark': '#2563eb', 
    'primary_light': '#eff6ff',
    'background': '#f8fafc',
    'surface': '#ffffff',
    'text_primary': '#1e293b',
    'text_secondary': '#64748b',
    'text_muted': '#94a3b8',
    'border': '#e2e8f0',
    'border_light': '#f1f5f9',
    'success': '#16a34a',
    'success_bg': '#f0fdf4',
    'warning': '#f59e0b',
    'warning_bg': '#fffbeb',
    'error': '#dc2626',
    'error_bg': '#fef2f2',
    'dark': '#0f172a'
}
```

## Main Window
```python
setStyleSheet("""
QMainWindow {
    background-color: #f8fafc;
    color: #1e293b;
}
""")
```

## Buttons
```python
# Primary Button
QPushButton {
    background-color: #3b82f6;
    color: white;
    border: 2px solid #3b82f6;
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: 500;
    font-size: 14px;
}
QPushButton:hover {
    background-color: #2563eb;
    border-color: #2563eb;
}
QPushButton:pressed {
    background-color: #1d4ed8;
}

# Secondary Button
QPushButton[class="secondary"] {
    background-color: transparent;
    color: #3b82f6;
    border: 2px solid #3b82f6;
}
QPushButton[class="secondary"]:hover {
    background-color: #eff6ff;
}
```

## Input Fields
```python
QLineEdit, QTextEdit, QComboBox {
    background-color: #ffffff;
    border: 2px solid #d1d5db;
    padding: 12px;
    border-radius: 6px;
    color: #1f2937;
    font-size: 16px;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border-color: #3b82f6;
    background-color: #eff6ff;
}
```

## Labels
```python
QLabel {
    color: #374151;
    font-weight: 500;
    margin-bottom: 8px;
}
QLabel[class="title"] {
    font-size: 28px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 8px;
}
QLabel[class="subtitle"] {
    color: #64748b;
    font-size: 16px;
}
```

## Tables
```python
QTableWidget {
    background-color: #ffffff;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    gridline-color: #e5e7eb;
}
QTableWidget::item {
    padding: 12px;
    border-bottom: 1px solid #e5e7eb;
}
QHeaderView::section {
    background-color: #f9fafb;
    color: #374151;
    font-weight: 600;
    border: none;
    border-bottom: 2px solid #d1d5db;
    padding: 12px;
}
QTableWidget::item:selected {
    background-color: #eff6ff;
    color: #1d4ed8;
}
```

## Cards/Frames
```python
QFrame[class="card"] {
    background-color: #ffffff;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    padding: 24px;
    margin: 12px;
}
QFrame[class="stat-card"] {
    background-color: #ffffff;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    padding: 24px;
    margin: 12px;
    min-width: 250px;
}
```

## Sidebar/Navigation
```python
QListWidget {
    background-color: #ffffff;
    border-right: 2px solid #e2e8f0;
    border-radius: 0px;
    padding: 24px 0px;
}
QListWidget::item {
    padding: 12px 24px;
    color: #475569;
    border-left: 4px solid transparent;
    margin-bottom: 4px;
}
QListWidget::item:hover {
    background-color: #f1f5f9;
    color: #3b82f6;
    border-left-color: #3b82f6;
}
QListWidget::item:selected {
    background-color: #eff6ff;
    color: #1d4ed8;
    border-left-color: #1d4ed8;
    font-weight: 600;
}
```

## Status Indicators
```python
QLabel[class="status-completed"] {
    background-color: #dcfce7;
    color: #166534;
    border: 1px solid #16a34a;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
}
QLabel[class="status-pending"] {
    background-color: #fef3c7;
    color: #92400e;
    border: 1px solid #f59e0b;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
}
QLabel[class="status-cancelled"] {
    background-color: #fee2e2;
    color: #991b1b;
    border: 1px solid #dc2626;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
}
```

## Dental Chart Teeth
```python
QPushButton[class="tooth-healthy"] {
    background-color: #f0fdf4;
    border: 2px solid #16a34a;
    color: #166534;
    font-weight: 600;
    min-width: 40px;
    min-height: 40px;
    border-radius: 4px;
}
QPushButton[class="tooth-cavity"] {
    background-color: #fef2f2;
    border: 2px solid #dc2626;
    color: #991b1b;
    font-weight: 600;
    min-width: 40px;
    min-height: 40px;
    border-radius: 4px;
}
QPushButton[class="tooth-filled"] {
    background-color: #fefce8;
    border: 2px solid #ca8a04;
    color: #92400e;
    font-weight: 600;
    min-width: 40px;
    min-height: 40px;
    border-radius: 4px;
}
QPushButton[class="tooth-missing"] {
    background-color: #f1f5f9;
    border: 2px solid #64748b;
    color: #475569;
    font-weight: 600;
    min-width: 40px;
    min-height: 40px;
    border-radius: 4px;
}
```

## Alerts/Messages
```python
QFrame[class="alert-info"] {
    background-color: #eff6ff;
    color: #1e40af;
    border: 2px solid #3b82f6;
    padding: 16px;
    border-radius: 6px;
    margin-bottom: 20px;
}
QFrame[class="alert-success"] {
    background-color: #f0fdf4;
    color: #15803d;
    border: 2px solid #22c55e;
    padding: 16px;
    border-radius: 6px;
    margin-bottom: 20px;
}
QFrame[class="alert-warning"] {
    background-color: #fffbeb;
    color: #92400e;
    border: 2px solid #f59e0b;
    padding: 16px;
    border-radius: 6px;
    margin-bottom: 20px;
}
QFrame[class="alert-error"] {
    background-color: #fef2f2;
    color: #991b1b;
    border: 2px solid #ef4444;
    padding: 16px;
    border-radius: 6px;
    margin-bottom: 20px;
}
```

## Usage Tips
1. Apply custom classes using `widget.setProperty("class", "card")`
2. Use consistent padding: 8px (small), 12px (medium), 16px (large), 24px (xlarge)
3. Standard margins: 4px, 8px, 12px, 16px, 20px, 24px, 32px
4. Border radius: 4px (small), 6px (medium), 8px (large)
5. Font weights: 400 (normal), 500 (medium), 600 (semibold), 700 (bold)

## Layout Guidelines
- Use QVBoxLayout/QHBoxLayout with consistent spacing
- Standard spacing: 8, 12, 16, 20, 24px
- Card margins: 12px between cards
- Form spacing: 20px between form groups
- Grid spacing: 24px for stat cards