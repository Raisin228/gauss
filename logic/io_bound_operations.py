from fractions import Fraction

from PyQt5.QtWidgets import QTableWidget, QMessageBox

from logic.storage_task import DataProblem


class IOOperations:

    @staticmethod
    def show_error(title_info: str, message: str) -> None:
        """Сообщение об ошибке в критической ситуации"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title_info)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    @classmethod
    def scan_data_from_file(cls, file_name: str = 'input_data1.txt') -> DataProblem:
        """
        Чтение данных задачи из файла.
        1-ая стр. q - кол-во переменных содержащихся в f и уравнениях
        2-ая стр. w - кол-во ограничений
        3-я стр. коэффициенты ф-ии f
        Дальше w - ограничений системы. Последний коэффициент в каждом уравнении считается = b.
        !Они все должны быть одинаковыми по длинне!

        Числа вида 1 2 3 - номера базисных переменных (Опционально. Может не быть)

        Выходные данные: DataProblem
        """
        with open(file_name) as file:
            rows_without_special_char = map(lambda row: row.strip(), file)
            strings_with_values = list(filter(lambda row: row, rows_without_special_char))

            b_vars = None
            try:
                q, w = int(strings_with_values[0]), int(strings_with_values[1])
                func = [list(map(lambda num: Fraction(num), strings_with_values[2].split()))]
                constr = [list(map(lambda n: Fraction(n), row.split())) for row in strings_with_values[3:w + 3]]
                if len(strings_with_values) != w + 3:
                    b_vars = list(map(int, strings_with_values[-1].split()))
                if q not in range(1, 16 + 1) or w not in range(1, 16 + 1):
                    raise ValueError(f'Кол-во переменных и ограничений должно быть в диапазоне [1, 16]')
                elif any(map(lambda c: len(c) != len(func[0]) or len(c) != q + 1, constr)):
                    raise ValueError(f'Все ограничения должны содержать одинаковое кол-во неизвестных = {q + 1}')
                elif any(map(lambda n: n > q or n < 1, b_vars)):
                    raise ValueError(f'Нет базисной переменной с таким индексом')

                return DataProblem(q, w, func, constr, b_vars)
            except BaseException as ex:
                example = """
                4 - кол-во неизвестных
                2 - кол-во ограничений
                -2 -1 -3 -1 0 - коэффициенты ф-ии f
                1 2 5 -1 -4 - ограничение 1
                1 -1 -1 2 -1 - ограничение 2
                3 4 - базисные переменные (опционально)
                """

                cls.show_error(f'Произошла ошибка при чтении данных из файла.',
                               f'Ошибка -> {ex.__class__.__name__}.\n'
                               f'Подробности: {ex}\n'
                               f'Пример файла:'
                               f'{example}')

    @classmethod
    def __data_from_selected_table(cls, table: QTableWidget) -> list[list[Fraction]] | list[Fraction]:
        """Читаем данные из конкретной таблицы и приводим в дроби"""
        ans = []
        for row in range(table.rowCount()):
            row_coeffs = []
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item is not None:
                    try:
                        value = Fraction(item.text())
                        row_coeffs.append(value)
                    except BaseException as ex:
                        row_coeffs.append(None)
                        raise ex.__class__(
                            'Не верный формат данных. Поддерживаются только числа и дроби вида 0.1, 1/10')
                else:
                    raise ValueError('Не должно быть пустых ячеек!')
            ans.append(row_coeffs)
        return ans[0] if len(ans) == 1 else ans

    @classmethod
    def scan_data_from_gui_tables(cls, wind) -> DataProblem:
        """Данные со всех таблиц складываем в класс для хранения задачи"""
        try:
            func_coef = cls.__data_from_selected_table(wind.upper_table)
            constr_coef = cls.__data_from_selected_table(wind.lower_table)
            basis = [box.property('value') for box in wind.basis_checkboxes if box.isChecked()]
            if not basis:
                basis = None
            return DataProblem(wind.var_spinbox.value(), wind.con_spinbox.value(), func_coef, constr_coef, basis)
        except BaseException as ex:
            cls.show_error(f'Произошла ошибка при вводе данных в таблицы.',
                           f'Ошибка -> {ex.__class__.__name__}.\n'
                           f'Подробности: {ex}\n'
                           f'Проверьте ввод данных!')

    @classmethod
    def improved_print(cls, *args, sep=' ', end='\n', file=None) -> None:
        """Стероидный print"""
        if file is None:
            print(*args, sep=sep, end=end)
        else:
            with open('output.txt', 'a') as file_obj:
                print(*args, sep=sep, end=end, file=file_obj)

    @classmethod
    def matrix_output(cls, m: list[list[Fraction]], header: list[str], to_file: bool | None = None) -> None:
        """Вывод матрицы на консоль"""

        max_el_len = 1
        for i in m:
            for j in i:
                max_el_len = max(len(str(j)), max_el_len)
        indent = max(max(map(lambda s: len(s), header)), max_el_len) + 2
        cls.improved_print(*map(lambda num: str(num).ljust(indent), header), sep='', file=to_file)
        for row in m:
            for el in row:
                cls.improved_print(str(el).ljust(indent), end='', file=to_file)
            cls.improved_print(file=to_file)
        cls.improved_print(file=to_file)
