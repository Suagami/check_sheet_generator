from pathlib import Path

from generate_workbook import BillWorkBookGenerator
from models import get_people_from_input

if __name__ == "__main__":
    people_input = input(
        "Введите имена для общего чека через запятую. "
        "Тех, кого требуется считать вместе, введите вместе через знак плюс "
        "(Пример: Артем,Данчик,Тончик+Маша):"
    )
    people = get_people_from_input(people_input)
    generator = BillWorkBookGenerator(people, Path("people.xlsx"))
    generator.generate()

    print("Готово!")
