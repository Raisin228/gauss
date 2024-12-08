from typing import List, Dict

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QMainWindow, QMenuBar, QMenu, QAction, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSpinBox, QGroupBox, QRadioButton, QPushButton, QTabWidget, QTableWidget, QTableWidgetItem, QFileDialog,
    QCheckBox, QScrollArea
)
from fractions import Fraction

from logic.io_bound_operations import IOOperations
from logic.simplex_method import SimplexMethod
from logic.storage_task import SimplexInput, SimplexResult


class OptimizationApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.open_action = None
        self.file_menu = None
        self.menu_bar = None
        self.var_label = None
        self.setWindowTitle("Симплекс метод")
        self.setMinimumSize(600, 600)

        self.basis_checkboxes = None

        self.init_ui()

    def init_ui(self):
        # Создание виджета вкладок
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Добавление вкладок
        self.add_problem_conditions_tab()
        self.add_result_tab()

        # Создание меню
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        self.file_menu = QMenu("Файл", self)
        self.menu_bar.addMenu(self.file_menu)

        self.open_action = QAction("Открыть файл", self)
        self.open_action.triggered.connect(self.open_file)
        self.file_menu.addAction(self.open_action)

    def add_problem_conditions_tab(self):
        """Добавляем вкладку 'Условия задачи'."""
        tab = QWidget()
        main_layout = QVBoxLayout(tab)

        input_layout = QHBoxLayout()
        left_panel = QVBoxLayout()

        # Лейблы и спинбоксы для ввода переменных и ограничений
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

        # Группа для выбора задачи оптимизации
        opt_group = QGroupBox("Задача оптимизации")
        opt_layout = QHBoxLayout()
        self.min_radio = QRadioButton("min")
        self.max_radio = QRadioButton("max")
        self.min_radio.setChecked(True)
        opt_layout.addWidget(self.min_radio)
        opt_layout.addWidget(self.max_radio)
        opt_group.setLayout(opt_layout)
        left_panel.addWidget(opt_group)

        # Группа для выбора базиса
        basis_group = QGroupBox("Базис")
        basis_layout = QHBoxLayout()
        self.artificial_basis_radio = QRadioButton("Искусственный")
        self.artificial_basis_radio.toggled.connect(self.__del_previous_checkboxes)
        self.given_basis_radio = QRadioButton("Заданный")
        self.artificial_basis_radio.setChecked(True)
        basis_layout.addWidget(self.artificial_basis_radio)
        basis_layout.addWidget(self.given_basis_radio)
        basis_group.setLayout(basis_layout)
        left_panel.addWidget(basis_group)

        # Группа для выбора режима решения
        mode_group = QGroupBox("Режим решения")
        mode_layout = QHBoxLayout()
        self.auto_mode_radio = QRadioButton("Автоматический")
        self.step_mode_radio = QRadioButton("Пошаговый")
        self.auto_mode_radio.setChecked(True)
        mode_layout.addWidget(self.auto_mode_radio)
        mode_layout.addWidget(self.step_mode_radio)
        mode_group.setLayout(mode_layout)
        left_panel.addWidget(mode_group)

        # Кнопка "Применить"
        self.apply_button = QPushButton("Применить")
        self.apply_button.clicked.connect(self.build_tables)
        left_panel.addWidget(self.apply_button)

        input_layout.addLayout(left_panel)

        self.table_layout = QVBoxLayout()
        input_layout.addLayout(self.table_layout)
        main_layout.addLayout(input_layout)

        # Кнопка "Решить задачу"
        self.solve_button = QPushButton("Решить задачу")
        self.solve_button.hide()
        self.solve_button.clicked.connect(self.start_calculating)
        main_layout.addWidget(self.solve_button)

        self.tab_widget.addTab(tab, "Условие задачи")

    def add_result_tab(self):
        """Добавляем вкладку 'Симплекс метод'."""
        tab = QWidget()

        # Создаем область с прокруткой
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # Автоматическая настройка содержимого

        # Контейнер внутри области прокрутки
        scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_widget)  # Макет для таблиц
        scroll_area.setWidget(scroll_widget)  # Устанавливаем контейнер в область прокрутки

        # Главный макет вкладки
        self.simplex_layout = QVBoxLayout(tab)
        self.simplex_layout.addWidget(scroll_area)  # Добавляем область прокрутки на вкладку

        # Добавляем вкладку в интерфейс
        self.tab_widget.addTab(tab, "Симплекс метод")

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
    def __fill_tables_with_data(table_widget: QTableWidget, data: list[list[Fraction]], support: tuple[int] = None,
                                down_row: List[Dict[str, Fraction]] = None) -> None:
        """Заполняем таблицу данными из файла"""
        if data:
            q_rows = table_widget.rowCount()
            if down_row:
                q_rows -= 1
            for row in range(q_rows):
                for col in range(table_widget.columnCount()):
                    cell = QTableWidgetItem(str(data[row][col]))
                    if support and row == support[0] and col == support[1]:
                        cell.setBackground(QColor('#42aaff'))
                    table_widget.setItem(row, col, cell)

            # заполнили строку коэффициентов ф-ии
            if down_row:
                for i in range(len(down_row)):
                    k, v = next(iter(down_row[i].items()))
                    table_widget.setItem(table_widget.rowCount() - 1, i, QTableWidgetItem(str(down_row[i][k])))

    def __del_previous_checkboxes(self) -> None:
        """Убираем предыдущие чекбоксы если они есть"""
        while self.basis_checkboxes and len(self.basis_checkboxes) > 0:
            widget = self.basis_checkboxes.pop(0)
            if widget:
                widget.deleteLater()
            if self.basis_label:
                self.basis_layout.removeWidget(self.basis_label)
                self.basis_label.deleteLater()
                self.basis_label = None

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

    def __init_simplex_table(self, table: List[List[Fraction]], down_row: List[Dict[str, Fraction]],
                             b_vars: List[int]) -> QTableWidget:
        """Инициализируем симплекс таблицу (размер/заголовки/нейминг)"""
        rows = len(table) + 1
        table = QTableWidget(rows, len(table[0]))

        table_width = sum(table.horizontalHeader().sectionSize(col) for col in range(table.columnCount())) + 50
        table_width += table.verticalHeader().width()

        table_height = sum(table.verticalHeader().sectionSize(row) for row in range(table.rowCount())) + 20
        table_height += table.horizontalHeader().height()
        table.setFixedSize(table_width, table_height)

        custom_headers = []
        for d in down_row:
            key, value = next(iter(d.items()))
            custom_headers.append(key)
        table.setHorizontalHeaderLabels(custom_headers)

        custom_row_naming = []
        for var in b_vars:
            custom_row_naming.append(f'x{var}')
        table.setVerticalHeaderLabels(custom_row_naming + ['f(x)'])

        self.scroll_layout.addWidget(table)
        return table

    @classmethod
    def clear_previous_steps(cls, layout):
        """Удаляем предыдущие шаги решения"""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                del item

    def display_step(self, data: SimplexInput, s_el: tuple[int]):
        """Отобразить симплекс шаг"""
        table = self.__init_simplex_table(data.table, data.down_row, data.b_vars)
        self.__fill_tables_with_data(table, data.table, s_el, down_row=data.down_row)

    def show_ans(self, result: SimplexResult | None | str):
        """Вывод ответа"""
        answer = QLabel()
        if result is None:
            answer.setText('Ответ: Нет решений')
        elif result == 'Ф-ия не ограничена. Оптимальное реш.отсутствует':
            answer.setText('Ответ: Ф-ия не ограничена. Оптимальное реш.отсутствует')
        else:
            prepare_vars = tuple(map(lambda n: str(n), result.x_vars))
            print(prepare_vars)
            answer.setText(f'Ответ: f({", ".join(prepare_vars)}) = {result.func_res}')
        self.scroll_layout.addWidget(answer)

    def start_calculating(self):
        SimplexMethod.solving(self)

#         todo сделать покраску других опорных элементов
