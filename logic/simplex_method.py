from fractions import Fraction

from logic.io_bound_operations import IOOperations
from logic.storage_task import DataProblem


class CustomError(Exception):
    """Что-то пошло не так. Сообщаем пользователю об этом"""


class SimplexMethod:

    @classmethod
    def __rg_matrix(cls, m: list[list[Fraction]]) -> int:
        """Вычисляем ранг матрицы (кол-во независимых строк т.е ненулевых)"""
        independent_row = 0
        for i in m:
            if any(map(lambda num: num != 0, i)):
                independent_row += 1
        return independent_row

    @classmethod
    def __get_row(cls, row: int, col: int, matrix: list[list[Fraction]]) -> Exception | int:
        """Получить индекс строки с минимальным значением"""
        ans, value = None, None
        for i in range(row, len(matrix)):
            if (tmp := abs(matrix[i][col - 1])) != 0 and (value is None or tmp < value):
                value = tmp
                ans = i
        if value is None:
            raise CustomError('Базисный столбец = 0 или тек. кол-во базисных переменных недопустимо')
        return ans

    @classmethod
    def __change_row(cls, cursor: int, new_row: int, matrix: list[list[Fraction]], title: list[str]) -> None:
        """Меняет строки местами"""
        if cursor != new_row:
            IOOperations.improved_print(f"Setting the lines {cursor + 1} <-> {new_row + 1}")
            IOOperations.improved_print(f"Setting the lines {cursor + 1} <-> {new_row + 1}", file=True)
            matrix[cursor], matrix[new_row] = matrix[new_row], matrix[cursor]
            IOOperations.matrix_output(matrix, title)
            IOOperations.matrix_output(matrix, title, to_file=True)

    @classmethod
    def __simplify_row(cls, row: int, col: int, matrix: list[list[Fraction]], title: list[str]) -> None:
        """Приводим элементы на гл.диагонали к 1"""
        if matrix[row][col] not in [0, 1]:
            divider = matrix[row][col]
            IOOperations.improved_print(f'Divided all the elements of the {row + 1} row into {divider}')
            IOOperations.improved_print(f'Divided all the elements of the {row + 1} row into {divider}', file=True)
            for k in range(len(matrix[row])):
                matrix[row][k] /= divider
            IOOperations.matrix_output(matrix, title)
            IOOperations.matrix_output(matrix, title, to_file=True)

    @classmethod
    def __gauss_method(cls, title: list[str], data: DataProblem) -> tuple[list[list[Fraction]], list[str]] | None:
        """Метод Гаусса"""
        b_var: list[int] = data.basic_vars
        m: list[list[Fraction]] = data.constraints
        IOOperations.improved_print("----------The Gauss method for checking basic variables and expressions of "
                                    "freedom. through the basic----------")
        IOOperations.improved_print("----------The Gauss method for checking basic variables and expressions of "
                                    "freedom. through the basic----------",
                                    file=True)
        for i in range(len(b_var)):
            try:
                non_zero_row = cls.__get_row(i, b_var[i], m)
            except CustomError as ex:
                IOOperations.show_error('Неверное кол-во базисных переменных', str(ex))
                return

            cls.__change_row(i, non_zero_row, m, title)
            cls.__simplify_row(i, b_var[i] - 1, m, title)

            for j in range(len(m)):
                if j == i:
                    continue
                multiple = m[j][b_var[i] - 1] / m[i][b_var[i] - 1]
                if multiple == 0:
                    continue
                for k in range(len(m[j])):
                    m[j][k] -= m[i][k] * multiple
                IOOperations.improved_print(f"From the {j + 1}th line - {i + 1}th * {multiple}")
                IOOperations.improved_print(f"From the {j + 1}th line - {i + 1}th * {multiple}", file=True)
                IOOperations.matrix_output(m, title)
                IOOperations.matrix_output(m, title, to_file=True)
        if cls.__rg_matrix(m) != len(b_var):
            raise CustomError(f'Неверное кол-во базисных переменных')
        IOOperations.matrix_output(m, title)
        IOOperations.matrix_output(m, title, to_file=True)
        return m, title

    @classmethod
    def express_fun_free_vars(cls, func_cof: list[Fraction], expressed_through_basis: list[list[Fraction]],
                              b_vars: list[int]) -> dict:
        """Выражает ф-ию только через свободные переменные (после метода Гаусса)"""

        accumulator = {}
        for i in range(len(func_cof)):
            if i == len(func_cof) - 1:
                accumulator[f'coeff'] = accumulator.setdefault('coeff', 0) + func_cof[i]
            elif i + 1 not in b_vars:
                accumulator[f'x{i + 1}'] = accumulator.setdefault(f'x{i + 1}', 0) + func_cof[i]
            elif i + 1 in b_vars:
                for row in expressed_through_basis:
                    if row[i] == 1:
                        for j in range(len(row)):
                            if j + 1 in b_vars:
                                continue
                            if j < len(func_cof) - 1:
                                accumulator[f'x{j + 1}'] = accumulator.setdefault(f'x{j + 1}', 0) - row[j] * func_cof[i]
                            else:
                                accumulator[f'coeff'] = accumulator.setdefault('coeff', 0) + row[j] * func_cof[i]

        return accumulator

    @classmethod
    def __find_support_el(cls, m: list[list[Fraction]], col: int) -> int:
        min_row, min_val = 0, None
        for row in range(len(m)):
            if 0 < m[row][col]:
                if min_val is None or m[row][-1] / m[row][col] < min_val:
                    min_row = row
                    min_val = m[row][-1] / m[row][col]
        return min_row

    @classmethod
    def simplex(cls, down_row: dict[str, Fraction], m: list[list[Fraction]]):
        ans = [[None for _ in range(len(m[0]))] for _ in range(len(m))]
        while any(map(lambda item: item[0] != 'coeff' and item[1] < 0, down_row.items())):
            for k, v in down_row.items():
                if k != 'coeff' and v < 0:
                    col = int(k.split('x')[-1]) - 1
                    row = cls.__find_support_el(m, col)

                    # новый опорный элемент
                    ans[row][col] = 1 / m[row][col]

                    # заполняем строку
                    for element_ind in range(len(m[row])):
                        if element_ind != col:
                            ans[row][element_ind] = m[row][element_ind] / m[row][col]
                    # TODO размерность ans нужно изменить т.е исключив переменные базисные
                    # заполняю колонку где опорный элемент
                    for element_row_ind in range(len(m)):
                        if element_row_ind != row:
                            ans[element_row_ind][col] = (-1/m[row][col]) * m[element_row_ind][col]

                    # считаем строки оставшиеся
                    for i in range(len(ans)):
                        for j in range(len(ans[0])):
                            if ans[i][j] is None:
                                ans[i][j] = m[i][j] - m[i][col] * ans[row][j]

                    IOOperations.improved_print(ans)
                    input()
                    break

    @classmethod
    def solving(cls, wind):
        with open('output.txt', 'w'):
            ...

        data = IOOperations.scan_data_from_gui_tables(wind)
        title = [f'x{i}"' if i in data.basic_vars else f'x{i}' for i in range(1, data.quant_vars + 1)]
        temp = cls.__gauss_method(title, data)

        expressed = cls.express_fun_free_vars(data.function_coefficients, temp[0], data.basic_vars)
        cls.simplex(expressed, temp[0])
