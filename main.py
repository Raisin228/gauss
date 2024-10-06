from fractions import Fraction
from typing import Tuple, List, Union


class CustomError(Exception):
    """Что-то пошло не так. Сообщаем пользователю об этом"""


def rg_matrix(m: List[List[Fraction]]) -> int:
    """Вычисляем ранг матрицы (кол-во независимых строк т.е ненулевых)"""
    independent_row = 0
    for i in m:
        if any(map(lambda num: num != 0, i)):
            independent_row += 1
    return independent_row


def improved_print(*args, sep=' ', end='\n', file=None) -> None:
    """Стероидный print"""
    if file is None:
        print(*args, sep=sep, end=end)
    else:
        with open('output.txt', 'a') as file_obj:
            print(*args, sep=sep, end=end, file=file_obj)


def matrix_output(m: List[List[Fraction]], header: List[str], to_file: Union[bool, None] = None) -> None:
    """Вывод матрицы на консоль"""
    if to_file:
        # почистили файл от старых данных
        with open('output.txt', 'w'):
            ...

    max_el_len = 1
    for i in m:
        for j in i:
            max_el_len = max(len(str(j)), max_el_len)
    indent = max(max(map(lambda s: len(s), header)), max_el_len) + 2
    improved_print(*map(lambda num: str(num).ljust(indent), header), sep='', file=to_file)
    for row in m:
        for el in row:
            improved_print(str(el).ljust(indent), end='', file=to_file)
        improved_print(file=to_file)
    improved_print(file=to_file)


def get_data_from_file() -> Tuple[Tuple, Tuple, List, List]:
    """Получить данные из файла"""
    # file_name = input("Enter file name: ")
    file_name = 'input_data.txt'
    with open(file_name) as file:
        cut_str = map(lambda s: s.strip(), file.readlines())
        str_with_value = [row for row in cut_str if row]
        values = list(map(lambda s: s.split(), str_with_value))

        if len(values[0]) != 2:
            raise CustomError('Размерность матрицы задаётся 2-я переменными m n')
        try:
            dimension = tuple(map(int, values[0]))
            basic_variables = tuple(sorted(map(int, values[1])))
        except ValueError:
            raise CustomError('Переменные m n и индексы столбцов должны быть типа данных Int')

        if len(basic_variables) != len(set(basic_variables)):
            raise CustomError('Базисный столбец не должен повторяться')
        try:
            matrix = [list(map(lambda num: Fraction(num), values[ind])) for ind in range(2, len(values))]
            if len(matrix) != dimension[0] or any(map(lambda s: len(s) != dimension[1], matrix)):
                raise CustomError(f'Матрица неправильного размера. Ожидалась [{dimension[0]}X{dimension[1]}]')
        except ValueError:
            raise CustomError('Данные в матрице должны быть числа типа данных Int | Float')
        title = [f'x{i}"' if i in basic_variables else f'x{i}' for i in range(1, dimension[1] + 1)]

        rg_matrix(matrix)

        print('Исходная матрица')
        matrix_output(matrix, title)
        return dimension, basic_variables, matrix, title


def get_row(row: int, col: int, matrix: List[List[Fraction]]) -> Union[Exception, int]:
    """Получить индекс строки с минимальным значением"""
    ans, value = None, None
    for i in range(row, len(matrix)):
        if (tmp := abs(matrix[i][col - 1])) != 0 and (value is None or tmp < value):
            value = abs(matrix[i][col - 1])
            ans = i
    if value is None:
        raise CustomError('Базисный столбец = 0')
    return ans


def change_row(cursor: int, new_row: int, matrix: List[List[Fraction]], title: List[str]) -> None:
    """Меняет строки местами"""
    if cursor != new_row:
        print(f'Переставляю строки {cursor + 1} <-> {new_row + 1}')
        matrix[cursor], matrix[new_row] = matrix[new_row], matrix[cursor]
        matrix_output(matrix, title)


def simplify_row(row: int, col: int, matrix: List[List[Fraction]], title: List[str]) -> None:
    """Приводим элементы на гл.диагонали к 1"""
    if matrix[row][col] not in [0, 1]:
        divider = matrix[row][col]
        print(f'Разделили все элементы {row + 1} строки на {divider}')
        for k in range(len(matrix[row])):
            matrix[row][k] /= divider
        matrix_output(matrix, title)


def gauss_method(data: Tuple[Tuple, Tuple, List, List]) -> None:
    """Метод Гаусса"""
    title: List[str] = data[3]
    b_var: Tuple[int] = data[1]
    m: List[List[Fraction]] = data[2]
    for i in range(len(b_var)):
        non_zero_row = get_row(i, b_var[i], m)
        change_row(i, non_zero_row, m, title)
        simplify_row(i, b_var[i] - 1, m, title)

        for j in range(len(m)):
            if j == i:
                continue
            multiple = m[j][b_var[i] - 1] / m[i][b_var[i] - 1]
            if multiple == 0:
                continue
            for k in range(len(m[j])):
                m[j][k] -= m[i][k] * multiple
            print(f"Из {j + 1} строки - {i + 1}-юу * {multiple}")
            matrix_output(m, title)
    if rg_matrix(m) != len(b_var):
        print('ERROR (Stack above or down)')
        raise CustomError(f'Неверное кол-во базисных переменных')
    matrix_output(m, title, to_file=True)


if __name__ == "__main__":
    information = get_data_from_file()
    gauss_method(information)
