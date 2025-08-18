def test_label_text(qtbot):
    from PySide6.QtWidgets import QLabel
    w = QLabel("hi")
    qtbot.addWidget(w)
    assert w.text() == "hi"