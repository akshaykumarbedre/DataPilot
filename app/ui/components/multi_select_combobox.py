"""
Custom multi-select combo box widget.
"""
from PySide6.QtWidgets import QComboBox, QListWidget, QListWidgetItem
from PySide6.QtCore import Signal, Qt, QEvent

class MultiSelectComboBox(QComboBox):
    """A combo box that allows multiple selections."""
    itemsSelected = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._list_widget = QListWidget(self)
        self._list_widget.setStyleSheet("QListWidget::item { padding: 5px; }")
        self.setModel(self._list_widget.model())
        self.setView(self._list_widget)
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.lineEdit().installEventFilter(self)
        self._list_widget.itemChanged.connect(self._on_item_selection_changed)
        self._list_widget.itemClicked.connect(self._on_item_clicked)

    def eventFilter(self, obj, event):
        if obj == self.lineEdit() and event.type() == QEvent.MouseButtonRelease:
            self.showPopup()
            return True
        return super().eventFilter(obj, event)

    def _on_item_clicked(self, item):
        item.setCheckState(Qt.Checked if item.checkState() == Qt.Unchecked else Qt.Unchecked)

    def addItem(self, text, data=None):
        item = QListWidgetItem(text)
        item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        item.setCheckState(Qt.Unchecked)
        if data is not None:
            item.setData(Qt.UserRole, data)
        self._list_widget.addItem(item)

    def addItems(self, items):
        for text, data in items:
            self.addItem(text, data)

    def selected_items(self):
        """Returns a list of the selected items' data."""
        selected = []
        for i in range(self._list_widget.count()):
            item = self._list_widget.item(i)
            if item.checkState() == Qt.Checked:
                selected.append(item.data(Qt.UserRole))
        return selected

    def _on_item_selection_changed(self, item):
        self._update_line_edit()
        self.itemsSelected.emit(self.selected_items())

    def _update_line_edit(self):
        selected_texts = []
        for i in range(self._list_widget.count()):
            item = self._list_widget.item(i)
            if item.checkState() == Qt.Checked:
                selected_texts.append(item.text())
        self.lineEdit().setText(", ".join(selected_texts))

    def clear(self):
        self._list_widget.clear()