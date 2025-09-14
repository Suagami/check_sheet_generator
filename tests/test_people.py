from models import People, Pair, Person


def test_pairs_by_person(people: People, pair: Pair):
    assert people.pairs_by_person
    assert pair.first.id in people.pairs_by_person
    assert pair.second.id in people.pairs_by_person
    assert people.pairs_by_person[pair.first.id] is pair
    assert people.pairs_by_person[pair.second.id] is pair


def test_get_person(people: People, person: Person):
    assert people.get_person(person.id) == person


def test_get_pair(people: People, pair: Pair):
    assert people.get_pair(pair.id) == pair


def test_is_person_in_pair(people: People, pair: Pair, person: Person):
    assert people.is_person_in_pair(person.id) is False
    assert people.is_person_in_pair(pair.first.id) is True
    assert people.is_person_in_pair(pair.second.id) is True


def test_is_person_first_in_pair(people: People, pair: Pair, person: Person):
    assert people.is_person_first_in_pair(person.id) is False
    assert people.is_person_first_in_pair(pair.first.id) is True
    assert people.is_person_first_in_pair(pair.second.id) is False


def test_is_person_second_in_pair(people: People, pair: Pair, person: Person):
    assert people.is_person_second_in_pair(person.id) is False
    assert people.is_person_second_in_pair(pair.first.id) is False
    assert people.is_person_second_in_pair(pair.second.id) is True


def test_get_second_from_pair(people: People, pair: Pair, person: Person):
    assert people.get_second_from_pair(person.id) is None
    assert people.get_second_from_pair(pair.first.id) is pair.second
    assert people.get_second_from_pair(pair.second.id) is pair.first


def test_count(people: People):
    assert people.count() == 3
