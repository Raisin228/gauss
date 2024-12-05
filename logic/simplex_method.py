from copy import deepcopy
from fractions import Fraction

from logic.io_bound_operations import IOOperations
from logic.storage_task import DataProblem, SimplexInput, SimplexResult


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
                              b_vars: list[int], is_max_task: bool) -> dict:
        """Выражает ф-ию только через свободные переменные (после метода Гаусса)"""
        if is_max_task:
            func_cof = [-k for k in func_cof]

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
    def one_step(cls, info: SimplexInput):
        m = info.table
        old_down_row = deepcopy(info.down_row)
        down_row = info.down_row
        base_vars = info.b_vars
        ans = [[None for _ in range(len(m[0]))] for _ in range(len(m))]

        for i in range(len(down_row)):
            k, value = next(iter(down_row[i].items()))
            if k != 'coeff' and value < 0:

                col = i
                row = cls.__find_support_el(m, col)

                # меняем свободные и базисные переменные местами
                key_b_var = next(iter(down_row[col].keys()))
                b_var_val = down_row[col][key_b_var]
                buf = base_vars[row]
                base_vars[row] = int(key_b_var.split('x')[-1])
                down_row[col].pop(key_b_var)
                down_row[col] = {f'x{buf}': b_var_val}

                # новый опорный элемент
                ans[row][col] = 1 / m[row][col]

                # заполняем строку
                for element_ind in range(len(m[row])):
                    if element_ind != col:
                        ans[row][element_ind] = m[row][element_ind] / m[row][col]

                # заполняю колонку где опорный элемент
                for element_row_ind in range(len(m)):
                    if element_row_ind != row:
                        ans[element_row_ind][col] = (-1 / m[row][col]) * m[element_row_ind][col]

                ke, v = next(iter(down_row[col].items()))
                down_row[col][ke] = -1 / m[row][col] * v

                # считаем строки оставшиеся
                for i in range(len(ans)):
                    for j in range(len(ans[0])):
                        if ans[i][j] is None:
                            ans[i][j] = m[i][j] - m[i][col] * ans[row][j]

                # пересчёт коэффициентов ф-ии
                for d in range(len(down_row)):
                    if d == col:
                        continue
                    ke, v = next(iter(down_row[d].items()))
                    down_row[d][ke] = v - next(iter(old_down_row[col].values())) * ans[row][d]

                return SimplexInput(ans, down_row, base_vars)

    @classmethod
    def __need_to_continue(cls, f_coeff: list[dict]) -> bool:
        """Нужно ли продолжать крутить метод автоматически?"""
        for d in f_coeff:
            key, value = next(iter(d.items()))
            if value < 0:
                return True
        return False

    @classmethod
    def __get_ans(cls, result: list[list[Fraction]], coeffs: list[dict], base: list[int],
                  is_maximiz: bool) -> SimplexResult | None:
        """Из полученной симплекс таблицы выражаем вектор x(...) и значение ф-ии"""
        x_vals = [None for _ in range(len(coeffs) - 1 + len(base))]
        for i in range(len(base)):
            x_vals[base[i] - 1] = result[i][-1]
        x_vals = [0 if val is None else val for val in x_vals]
        if any(map(lambda n: n < 0, x_vals)):
            print('Нет решений')
            return None

        buf = [-d['coeff'] for d in coeffs if 'coeff' in d]
        if is_maximiz:
            return SimplexResult(x_vals, -buf[0])
        return SimplexResult(x_vals, buf[0])

    @classmethod
    def __check_not_limited(cls, m: list[list[Fraction]], coeff: list[dict]) -> bool:
        for j in range(len(coeff)):
            key, value = next(iter(coeff[j].items()))
            if value < 0:
                for row in m:
                    if row[j] > 0:
                        return False
        return True

    @classmethod
    def simplex(cls, info: SimplexInput, is_max: bool):
        while True:
            res = cls.one_step(info)

            if res is None:
                print(cls.__get_ans(info.table, info.down_row, info.b_vars, is_max))
                break
            elif not cls.__need_to_continue(res.down_row):
                print(cls.__get_ans(res.table, res.down_row, res.b_vars, is_max))
                break
            elif cls.__check_not_limited(res.table, res.down_row):
                print('Ф-ия не ограничена. Оптимальное реш.отсутствует')
                break
            info = res


    @classmethod
    def __compress_data(cls, m: list[list[Fraction]], b_vars_index: list[int], func_coff: dict) -> SimplexInput:
        """Чистим таблицу от базисных столбцов. (Привели задачу к симплекс таблице)"""
        without_b_vars = []

        for row in m:
            temp = []
            for col in range(len(row)):
                if col + 1 not in b_vars_index:
                    temp.append(row[col])
            without_b_vars.append(temp)

        buf = []
        for key in sorted(func_coff):
            if key != 'coeff':
                buf.append({key: func_coff[key]})
        buf.append({'coeff': -func_coff['coeff']})

        return SimplexInput(without_b_vars, buf, b_vars_index)

    @classmethod
    def solving(cls, wind):
        with open('output.txt', 'w'):
            ...

        try:
            data = IOOperations.scan_data_from_gui_tables(wind)
            title = [f'x{i}"' if i in data.basic_vars else f'x{i}' for i in range(1, data.quant_vars + 1)]
            temp = cls.__gauss_method(title, data)

            expressed = cls.express_fun_free_vars(data.function_coefficients, temp[0], data.basic_vars,
                                                  wind.max_radio.isChecked())
            prep_data = cls.__compress_data(temp[0], data.basic_vars, expressed)
            cls.simplex(prep_data, is_max=wind.max_radio.isChecked())
        except Exception as ex:
            print(ex)
