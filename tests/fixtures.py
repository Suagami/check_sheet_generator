import pytest

from models import Person, Pair, People


@pytest.fixture
def person() -> Person:
    return Person(name="Иван")


@pytest.fixture
def pair() -> Pair:
    person_1 = Person(name="Ромео")
    person_2 = Person(name="Джульетта")
    return Pair(first=person_1, second=person_2)


@pytest.fixture
def people(person: Person, pair: Pair) -> People:
    return People(
        people={
            person.id: person,
            pair.first.id: pair.first,
            pair.second.id: pair.second,
        },
        pairs={pair.id: pair},
    )
