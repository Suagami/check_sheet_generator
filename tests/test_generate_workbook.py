from pathlib import Path

import pytest
from xlsxwriter.worksheet import Worksheet

from generate_workbook import BillWorkBookGenerator
from models import People


@pytest.fixture
def path(tmp_path) -> Path:
    return tmp_path / "test.xlsx"


@pytest.fixture
def generator(people: People, path: Path) -> BillWorkBookGenerator:
    return BillWorkBookGenerator(people, path)


@pytest.fixture
def ws(generator: BillWorkBookGenerator) -> Worksheet:
    return generator.wb.add_worksheet("Test")


def test_bill_workbook_generator(generator: BillWorkBookGenerator, path: Path):
    generator.generate()

    assert path.is_file()


@pytest.mark.parametrize("row, format_color", ((0, "FFFFFF"), (1, "E0F7FA")))
def test_get_ok_format_success(
    generator: BillWorkBookGenerator, row: int, format_color: str
):
    ok_format = generator.get_ok_format(row)

    assert format_color in str(ok_format.bg_color)


def test_get_ok_format_fails(generator: BillWorkBookGenerator):
    with pytest.raises(ValueError):
        generator.get_ok_format(-1)


@pytest.mark.parametrize(
    "row, col, expected",
    ((0, 0, "A1"), (50, 50, "AY51"), (327, 500, "SG328")),
)
def test_get_cell(generator: BillWorkBookGenerator, row: int, col: int, expected: str):
    cell = generator.get_cell(col, row)

    assert cell == expected


def test_get_cell_fails(generator: BillWorkBookGenerator):
    with pytest.raises(ValueError):
        generator.get_cell(-1, -1)
