from models import get_people_from_input


def test_get_people_from_input():
    input_str = "1,2,3,4,5,6,7,8,9,10"

    people = get_people_from_input(input_str)

    assert len(people.people.keys()) == 10
    assert not people.pairs


def test_get_people_from_input_with_pairs():
    input_str = "1,2,3,4,5,6,7,8,9,10+11"

    people = get_people_from_input(input_str)

    assert len(people.people.keys()) == 11
    assert len(people.pairs.keys()) == 1
    assert list(people.pairs.values())[0].first.name == "10"
    assert list(people.pairs.values())[0].second.name == "11"
