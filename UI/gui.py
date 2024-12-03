import sys

from PyQt5 import QtGui
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton, QCheckBox, QPushButton, QTableWidget,
    QSpinBox, QGroupBox
)


class OptimizationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.basis_label, self.basis_layout = None, None
        self.basis_checkboxes, self.lower_table = None, None
        self.table_layout, self.solve_button, self.upper_table = None, None, None
        self.apply_button, self.step_mode_radio = None, None
        self.auto_mode_radio, self.given_basis_radio = None, None
        self.artificial_basis_radio, self.max_radio = None, None
        self.min_radio, self.con_spinbox = None, None
        self.con_label, self.var_spinbox, self.var_label = None, None, None
        self.setWindowTitle("Симплекс метод")
        self.init_ui()
        self.setMinimumSize(600, 600)

    def init_ui(self):
        main_layout = QVBoxLayout()

        input_layout = QHBoxLayout()

        left_panel = QVBoxLayout()

        self.var_label = QLabel("Количество переменных:")
        self.var_spinbox = QSpinBox()
        self.var_spinbox.setMinimum(1)
        self.var_spinbox.setMaximum(16)
        self.var_spinbox.setValue(5)
        left_panel.addWidget(self.var_label)
        left_panel.addWidget(self.var_spinbox)

        self.con_label = QLabel("Количество ограничений:")
        self.con_spinbox = QSpinBox()
        self.con_spinbox.setMinimum(1)
        self.con_spinbox.setMaximum(16)
        self.con_spinbox.setValue(5)
        left_panel.addWidget(self.con_label)
        left_panel.addWidget(self.con_spinbox)

        opt_group = QGroupBox("Задача оптимизации")
        opt_layout = QHBoxLayout()
        self.min_radio = QRadioButton("min")
        self.max_radio = QRadioButton("max")
        self.min_radio.setChecked(True)
        opt_layout.addWidget(self.min_radio)
        opt_layout.addWidget(self.max_radio)
        opt_group.setLayout(opt_layout)
        left_panel.addWidget(opt_group)

        basis_group = QGroupBox("Базис")
        basis_layout = QHBoxLayout()
        self.artificial_basis_radio = QRadioButton("Искусственный")
        self.given_basis_radio = QRadioButton("Заданный")
        self.artificial_basis_radio.setChecked(True)
        basis_layout.addWidget(self.artificial_basis_radio)
        basis_layout.addWidget(self.given_basis_radio)
        basis_group.setLayout(basis_layout)
        left_panel.addWidget(basis_group)

        mode_group = QGroupBox("Режим решения")
        mode_layout = QHBoxLayout()
        self.auto_mode_radio = QRadioButton("Автоматический")
        self.step_mode_radio = QRadioButton("Пошаговый")
        self.auto_mode_radio.setChecked(True)
        mode_layout.addWidget(self.auto_mode_radio)
        mode_layout.addWidget(self.step_mode_radio)
        mode_group.setLayout(mode_layout)
        left_panel.addWidget(mode_group)

        self.apply_button = QPushButton("Применить")
        self.apply_button.clicked.connect(self.build_tables)
        left_panel.addWidget(self.apply_button)

        input_layout.addLayout(left_panel)

        self.table_layout = QVBoxLayout()
        input_layout.addLayout(self.table_layout)

        main_layout.addLayout(input_layout)

        self.solve_button = QPushButton("Решить задачу")
        self.solve_button.hide()
        main_layout.addWidget(self.solve_button)

        self.setLayout(main_layout)

    def build_tables(self):
        for i in reversed(range(self.table_layout.count())):
            widget = self.table_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        num_vars = self.var_spinbox.value()
        num_constraints = self.con_spinbox.value()

        self.upper_table = QTableWidget(1, num_vars + 1)
        self.upper_table.setHorizontalHeaderLabels([f"x{i + 1}" for i in range(num_vars)] + ["b"])
        self.upper_table.setVerticalHeaderLabels(["f0(x)"])
        self.table_layout.addWidget(self.upper_table)

        self.lower_table = QTableWidget(num_constraints, num_vars + 1)
        self.lower_table.setHorizontalHeaderLabels([f"x{i + 1}" for i in range(num_vars)] + ["b"])
        self.lower_table.setVerticalHeaderLabels([f"f{i + 1}(x)" for i in range(num_constraints)])
        self.table_layout.addWidget(self.lower_table)

        while self.basis_checkboxes and len(self.basis_checkboxes) > 0:
            widget = self.basis_checkboxes.pop(0)
            if widget:
                widget.deleteLater()
            if self.basis_label:
                self.basis_layout.removeWidget(self.basis_label)

        if self.given_basis_radio.isChecked():
            self.basis_layout = QVBoxLayout()
            self.basis_label = QLabel("Базисные переменные:")
            self.basis_layout.addWidget(self.basis_label)

            self.basis_checkboxes = []
            for i in range(num_vars):
                checkbox = QCheckBox(f"x{i + 1}")
                self.basis_checkboxes.append(checkbox)
                self.basis_layout.addWidget(checkbox)

            self.table_layout.addLayout(self.basis_layout)
        self.solve_button.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("icon_s.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    app.setWindowIcon(icon)

    font = QFont()
    font.setPointSize(16)
    app.setFont(font)

    window = OptimizationApp()
    window.show()
    sys.exit(app.exec_())
