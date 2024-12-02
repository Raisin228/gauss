from fractions import Fraction


class IOOperations:

    @classmethod
    def scan_data_from_file(cls, file_name: str = 'input_data1.txt') -> tuple[tuple[Fraction], list[list[Fraction]]]:
        """
        Чтение данных задачи из файла.
        1-ая стр. q - кол-во переменных содержащихся в f и уравнениях
        2-ая стр. w - кол-во ограничений
        Дальше w - ограничений системы. Последний коэффициент в каждом уравнении считается = b.
        !Они все должны быть одинаковыми по длинне!

        Числа вида 1 2 3 - номера базисных переменных (опционально)

        Выходные данные: кортеж с коэффициентами ф-ии f, список со списками уравнений
        """

        with open(file_name) as file:
            rows_without_special_char = map(lambda row: row.strip(), file)
            strings_with_values = filter(lambda row: row, rows_without_special_char)
            temp = list(map(lambda r: r.split(), strings_with_values))

            try:
                data = [list(map(lambda val: Fraction(val), row)) for row in temp]
                if len(data) < 3:
                    raise ValueError('<<Слишком мало входных данных. Необходимо минимум 3 строки>>')
                elif any(map(lambda equation: len(equation) != len(data[1]), data[1:])):
                    raise ValueError('<<Все ограничения должны содержать одинаковое кол-во неизвестных>>')

                return tuple(data[0]), data[1:]
            except BaseException as ex:
                print(f'При чтении файла возникла ошибка -> {ex.__class__.__name__}.\nПояснение - {ex}.\n'
                      f'Проверьте правильность данных!')


print(Fraction('1/10'))
