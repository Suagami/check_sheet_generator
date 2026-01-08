from pathlib import Path

from xlsxwriter.format import Format
from xlsxwriter.worksheet import Worksheet

from models import People, Person
import xlsxwriter

MAX_PERSONAL_SHEET_ROWS = 100


class BillWorkBookGenerator:
    def __init__(self, people: People, path: Path):
        self.people = people

        self.personal_sheet_width = 3 + self.people.count() + 2 + self.people.count()
        self.wb = xlsxwriter.Workbook(path)

        self.header_format = self.wb.add_format(
            {
                "bg_color": "#BDBDBD",
                "bold": True,
                "align": "center",
                "valign": "vcenter",
            }
        )
        self.header_format_blue = self.wb.add_format(
            {
                "bg_color": "#4DD0E1",
                "bold": True,
                "align": "center",
                "valign": "vcenter",
            }
        )
        self.bold_format = self.wb.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "font_size": 30,
                "border": 1,
            }
        )
        self.bold_rotated_format = self.wb.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "font_size": 30,
                "border": 1,
                "rotation": 90,
            }
        )
        self.debt_format = self.wb.add_format(
            {
                "bg_color": "#FCE8B2",
                "border": 1,
                "align": "center",
                "valign": "vcenter",
            }
        )
        self.ok_format_0 = self.wb.add_format(
            {
                "bg_color": "#FFFFFF",
                "border": 1,
                "align": "center",
                "valign": "vcenter",
            }
        )
        self.ok_format_1 = self.wb.add_format(
            {
                "bg_color": "#E0F7FA",
                "border": 1,
                "align": "center",
                "valign": "vcenter",
            }
        )
        self.default_format = self.wb.add_format(
            {
                "bg_color": "#FFFFFF",
                "border": 1,
                "align": "center",
                "valign": "vcenter",
            }
        )
        self.green_format = self.wb.add_format(
            {
                "bg_color": "#B7E1CD",
                "border": 1,
                "align": "center",
                "valign": "vcenter",
            }
        )
        self.red_format = self.wb.add_format(
            {
                "bg_color": "#F4C7C3",
                "border": 1,
                "align": "center",
                "valign": "vcenter",
            }
        )

    def generate(self) -> None:
        """Создание и заполнение книги Excel для расчета чеков"""

        ws = self.wb.add_worksheet("Свод")

        for person in self.people.people_mapping.values():
            self.generate_personal_sheet(person)
        self.generate_total_sheet(ws)

        self.wb.close()

    def get_ok_format(self, row_number: int) -> Format:
        """Получение формата для таблицы Кто/Кому для чередования цветов строк"""
        if row_number < 0:
            raise ValueError("row_number must be >= 0")
        return self.ok_format_0 if row_number % 2 == 0 else self.ok_format_1

    def generate_total_sheet(self, ws: Worksheet) -> None:
        """Заполнение листа Свод"""

        ws.set_default_row(25)

        self.fill_total_table(ws)
        self.fill_calculated_table(ws)

    def fill_total_table(self, ws: Worksheet) -> None:
        """Заполнение таблицы Кто/Кому"""

        ws.merge_range(1, 1, 1, self.people.count() + 1, "КОМУ", self.bold_format)

        ws.merge_range(
            2, 0, self.people.count() + 2, 0, "КТО", self.bold_rotated_format
        )

        for i, i_person in enumerate(self.people.people_mapping.values()):
            ws.write(2, 2 + i, i_person.name, self.header_format)
            ws.write(3 + i, 1, i_person.name, self.get_ok_format(i))

            if self.people.is_person_first_in_pair(i_person.id):
                self.fill_pair_cells(ws, i, i_person)
            elif self.people.is_person_second_in_pair(i_person.id):
                continue
            else:
                self.fill_common_cells(ws, i, i_person)

    def fill_calculated_table(self, ws: Worksheet):
        """Заполнение таблицы Чеки"""

        # фикс, что слово Поделено не влезает в колонку
        ws.set_column("C:C", width=11)

        ws.merge_range(
            2 + self.people.count() + 2,
            0,
            2 + self.people.count() + 2,
            3,
            "ЧЕКИ",
            self.bold_format,
        )
        ws.write_string(2 + self.people.count() + 3, 1, "Сумма", self.header_format)
        ws.write_string(2 + self.people.count() + 3, 2, "Поделено", self.header_format)
        ws.write_string(2 + self.people.count() + 3, 3, "Осталось", self.header_format)

        last_bill_column = self.number_to_column_name(3 + self.people.count())
        for i, i_person in enumerate(self.people.people_mapping.values()):
            row = 2 + self.people.count() + 4 + i

            ws.write_string(row, 0, i_person.name, self.default_format)

            cost_formula = f"=SUM({i_person.name}!$B$3:$B${MAX_PERSONAL_SHEET_ROWS})"
            calculated_formula = f"=SUM({i_person.name}!$D$2:${last_bill_column}$2)"
            not_calculated_formula = f"=ROUND($B{row + 1}-$C{row + 1}, 2)"

            ws.write_formula(row, 1, cost_formula, self.ok_format_0)
            ws.write_formula(row, 2, calculated_formula, self.ok_format_0)
            ws.write_formula(row, 3, not_calculated_formula, self.ok_format_0)

            self.fill_conditional_not_calculated_format(ws, row)

    def fill_conditional_debt_format(self, ws: Worksheet, row: int, col: int) -> None:
        """Условное форматирование для таблицы Кто/Кому"""

        ws.conditional_format(
            self.get_cell(col, row),
            {"type": "cell", "criteria": ">", "value": 0, "format": self.debt_format},
        )

    def fill_conditional_not_calculated_format(self, ws: Worksheet, row: int):
        """Условное форматирование для таблицы Чеки"""

        range_str = f"{self.get_cell(0, row)}:{self.get_cell(3, row)}"
        ws.conditional_format(
            range_str,
            {
                "type": "formula",
                "criteria": f"=$D${row + 1}=0",
                "format": self.green_format,
            },
        )
        ws.conditional_format(
            range_str,
            {
                "type": "formula",
                "criteria": f"=$D${row + 1}>0",
                "format": self.red_format,
            },
        )

    def fill_common_cells(self, ws: Worksheet, i: int, i_person: Person):
        """Заполнение ячеек таблицы Кто/Кому для стандартных случаев"""

        for j, j_person in enumerate(self.people.people_mapping.values()):
            if j < i:
                continue
            if i == j:
                ws.write(3 + i, 2 + i, "-", self.get_ok_format(i))
                continue
            if self.people.is_person_in_pair(j_person.id):
                continue
            i_bill_col = self.number_to_column_name(3 + i + 1)
            j_bill_col = self.number_to_column_name(3 + j + 1)

            row_subformula = (
                f"{j_person.name}!${i_bill_col}$2-{i_person.name}!{j_bill_col}$2"
            )
            ws.write_formula(
                3 + i,
                2 + j,
                f"=IF(({row_subformula})<0,0,{row_subformula})",
                self.get_ok_format(i),
            )
            self.fill_conditional_debt_format(ws, 3 + i, 2 + j)

            col_subformula = (
                f"{i_person.name}!{j_bill_col}$2-{j_person.name}!${i_bill_col}$2"
            )
            ws.write_formula(
                3 + j,
                2 + i,
                f"=IF(({col_subformula})<0,0,{col_subformula})",
                self.get_ok_format(j),
            )
            self.fill_conditional_debt_format(ws, 3 + j, 2 + i)

    def fill_pair_cells(self, ws: Worksheet, i: int, i_person: Person):
        """Заполнение ячеек таблицы Кто/Кому для пар с общим бюджетом"""

        first_bill_col = self.number_to_column_name(3 + i + 1)
        second_bill_col = self.number_to_column_name(3 + i + 1 + 1)
        second_person = self.people.get_second_from_pair(i_person.id)
        for j, j_person in enumerate(self.people.people_mapping.values()):
            if i == j:
                ws.merge_range(
                    3 + i, 2 + i, 3 + i + 1, 2 + i + 1, "-", self.get_ok_format(i)
                )
                continue
            if j == i + 1:
                continue

            j_bill_col = self.number_to_column_name(3 + j + 1)
            row_subformula = (
                f"{j_person.name}!${first_bill_col}$2+{j_person.name}!${second_bill_col}$2"
                f"-{i_person.name}!{j_bill_col}$2-{second_person.name}!{j_bill_col}$2"
            )
            ws.merge_range(
                3 + i,
                2 + j,
                3 + i + 1,
                2 + j,
                f"=IF(({row_subformula})<0,0,{row_subformula})",
                self.get_ok_format(i),
            )
            self.fill_conditional_debt_format(ws, 3 + i, 2 + j)

            col_subformula = (
                f"{i_person.name}!{j_bill_col}$2+{second_person.name}!{j_bill_col}$2"
                f"-{j_person.name}!${first_bill_col}$2-{j_person.name}!${second_bill_col}$2"
            )
            ws.merge_range(
                3 + j,
                2 + i,
                3 + j,
                2 + i + 1,
                f"=IF(({col_subformula})<0,0,{col_subformula})",
                self.get_ok_format(j),
            )
            self.fill_conditional_debt_format(ws, 3 + j, 2 + i)

    def generate_personal_sheet(self, person: Person) -> None:
        """Заполнение персонального листа"""

        ws = self.wb.add_worksheet(person.name)

        self.generate_header_for_personal_sheet(ws)
        self.fill_formulas_for_personal_sheet(ws)

    def generate_header_for_personal_sheet(self, ws: Worksheet) -> None:
        """Заполнение заголовка в таблице персонального листа"""

        for col in range(0, self.personal_sheet_width):
            ws.write(0, col, "", self.header_format)

        ws.write(0, 0, "Название", self.header_format)
        ws.set_column("A:A", width=20)
        ws.write(0, 1, "Цена", self.header_format)

        for i, i_person in enumerate(self.people.people_mapping.values()):
            ws.write(0, i + 3, i_person.name, self.header_format)
            ws.write(
                0, i + 3 + self.people.count() + 2, i_person.name, self.header_format
            )

    def fill_formulas_for_personal_sheet(self, ws: Worksheet) -> None:
        """Заполнение формул в таблице персонального листа"""

        for i, i_person in enumerate(self.people.people_mapping.values()):
            cost_column = 1
            bill_column = 3 + i
            last_bill_column = 3 + self.people.count() - 1
            bill_formula_column = 3 + self.people.count() + 2 + i

            sum_formula = (
                f"=SUM({self.number_to_column_name(bill_formula_column + 1)}3:"
                f"{self.number_to_column_name(bill_formula_column + 1)}{MAX_PERSONAL_SHEET_ROWS + 1})"
            )
            ws.write_formula(1, bill_column, sum_formula)

            for j in range(2, MAX_PERSONAL_SHEET_ROWS):
                ws.write_number(j, cost_column, 0.0)
                ws.insert_checkbox(j, bill_column, False)

                bill_formula = (
                    f"=IF({self.get_cell(bill_column, j)},$B{j + 1}/"
                    f"COUNTIF($D{j + 1}:${self.get_cell(last_bill_column, j)},TRUE),0)"
                )
                ws.write_formula(j, bill_formula_column, bill_formula)

    @staticmethod
    def number_to_column_name(n: int) -> str:
        """Преобразует номер колонки (1,2,3,..) в название (A,B,...,AA,..)."""

        result = []

        while n > 0:
            n, remainder = divmod(n - 1, 26)
            result.append(chr(65 + remainder))

        return "".join(reversed(result))

    def get_cell(self, col: int, row: int) -> str:
        """Получение названия ячейки для формул из численного представления строки и колонки"""

        if col < 0 or row < 0:
            raise ValueError("row_number and col_number must be > 0")

        return f"{self.number_to_column_name(col + 1)}{row + 1}"
