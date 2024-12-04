from fractions import Fraction

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMenuBar, QMenu, QAction, QHBoxLayout, QLabel, QSpinBox, QGroupBox, \
    QRadioButton, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, QCheckBox

from logic.io_bound_operations import IOOperations
from logic.simplex_method import SimplexMethod


class OptimizationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.menu_bar, self.file_menu, self.open_action = None, None, None
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

        # Создание меню
        self.menu_bar = QMenuBar(self)
        self.file_menu = QMenu("Файл", self)
        self.menu_bar.addMenu(self.file_menu)

        self.open_action = QAction("Открыть файл", self)
        self.open_action.triggered.connect(self.open_file)
        self.file_menu.addAction(self.open_action)
        main_layout.setMenuBar(self.menu_bar)

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
        self.solve_button.clicked.connect(self.start_calculating)

        self.setLayout(main_layout)

    def open_file(self):
        """Диалоговое окно для выбора файла"""
        file_name, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Text Files (*.txt);;All Files (*)")

        if file_name:
            data = IOOperations.scan_data_from_file(file_name)
            self.build_tables(data.quant_vars, data.quant_constr, data.basic_vars, data.function_coefficients,
                              data.constraints)

    def __del_previous_tables(self) -> None:
        """Удаляем все таблицы с прошлых сеансов"""
        for i in reversed(range(self.table_layout.count())):
            widget = self.table_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

    def __set_fields(self, v: int, c: int) -> None:
        """Заполняем поля интерфейса данными из файла"""
        self.var_spinbox.setValue(v)
        self.con_spinbox.setValue(c)
        self.given_basis_radio.setChecked(True)

    def __table_initialization(self, v: int, c: int) -> None:
        """Объявление таблиц"""
        self.upper_table = QTableWidget(1, v + 1)
        self.upper_table.setHorizontalHeaderLabels([f"x{i + 1}" for i in range(v)] + ["b"])
        self.upper_table.setVerticalHeaderLabels(["f0(x)"])
        self.table_layout.addWidget(self.upper_table)

        self.lower_table = QTableWidget(c, v + 1)
        self.lower_table.setHorizontalHeaderLabels([f"x{i + 1}" for i in range(v)] + ["b"])
        self.lower_table.setVerticalHeaderLabels([f"f{i + 1}(x)" for i in range(c)])
        self.table_layout.addWidget(self.lower_table)

    @staticmethod
    def __fill_tables_with_data(table_widget: QTableWidget, data: list[list[Fraction]]) -> None:
        """Заполняем таблицу данными из файла"""
        if data:
            for row in range(table_widget.rowCount()):
                for col in range(table_widget.columnCount()):
                    table_widget.setItem(row, col, QTableWidgetItem(str(data[row][col])))

    def __del_previous_checkboxes(self) -> None:
        """Убираем предыдущие чекбоксы если они есть"""
        while self.basis_checkboxes and len(self.basis_checkboxes) > 0:
            widget = self.basis_checkboxes.pop(0)
            if widget:
                widget.deleteLater()
            if self.basis_label:
                self.basis_layout.removeWidget(self.basis_label)

    def __show_checkbox_for_basis(self, v: int, b: list[int]) -> None:
        """Отображаем поле для выбора базиса"""
        if self.given_basis_radio.isChecked():
            self.basis_layout = QVBoxLayout()
            self.basis_label = QLabel("Базисные переменные:")
            self.basis_layout.addWidget(self.basis_label)

            self.basis_checkboxes = []
            for i in range(v):
                checkbox = QCheckBox(f"x{i + 1}")
                checkbox.setProperty('value', i + 1)
                if b and i + 1 in b:
                    checkbox.setChecked(True)
                self.basis_checkboxes.append(checkbox)
                self.basis_layout.addWidget(checkbox)

            self.table_layout.addLayout(self.basis_layout)

    def build_tables(self, num_vars: int = None, num_constraints: int = None, basis: list[int] = None,
                     f_coff: list[list[Fraction]] = None, constr: list[list[Fraction]] = None):
        """Отображение таблиц на основе информации из файла/выберенных параметров"""
        self.__del_previous_tables()

        # если таблицы строим из файла то заполняем соответствующие поля данными
        if not num_vars and not num_constraints and not basis:
            num_vars = self.var_spinbox.value()
            num_constraints = self.con_spinbox.value()
        else:
            self.__set_fields(num_vars, num_constraints)

        self.__table_initialization(num_vars, num_constraints)

        self.__fill_tables_with_data(self.upper_table, f_coff)
        self.__fill_tables_with_data(self.lower_table, constr)

        self.__del_previous_checkboxes()

        self.__show_checkbox_for_basis(num_vars, basis)

        self.solve_button.show()

    def start_calculating(self):
        SimplexMethod.solving(self)
