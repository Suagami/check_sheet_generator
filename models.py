from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Person(BaseModel):
    id: UUID = Field(default_factory=lambda: uuid4(), title="Person ID")
    name: str = Field(..., title="Person name")


class Pair(BaseModel):
    id: UUID = Field(default_factory=lambda: uuid4(), title="Pair ID")
    first: Person = Field(..., title="First Person ID")
    second: Person = Field(..., title="Second Person ID")


class People(BaseModel):
    people: dict[UUID, Person] = Field(..., title="People DB")
    pairs: dict[UUID, Pair] = Field(..., title="Pair DB")
    pairs_by_person: dict[UUID, Pair] | None = Field(
        None, title="Pair By Person ID mapping"
    )

    def model_post_init(self, __context):
        pairs_by_person = {}
        for pair in self.pairs.values():
            pairs_by_person[pair.first.id] = pair
            pairs_by_person[pair.second.id] = pair
        self.pairs_by_person = pairs_by_person

    def get_person(self, id: UUID) -> Person:
        return self.people[id]

    def get_pair(self, id: UUID) -> Pair:
        return self.pairs[id]

    def is_person_in_pair(self, id: UUID) -> bool:
        return id in self.pairs_by_person

    def is_person_first_in_pair(self, id: UUID) -> bool:
        return self.is_person_in_pair(id) and self.pairs_by_person[id].first.id == id

    def is_person_second_in_pair(self, id: UUID) -> bool:
        return self.is_person_in_pair(id) and self.pairs_by_person[id].second.id == id

    def get_second_from_pair(self, person_id: UUID) -> Person | None:
        pair = self.pairs_by_person.get(person_id)
        if not pair:
            return None
        return (
            self.get_person(pair.first.id)
            if person_id != pair.first.id
            else self.get_person(pair.second.id)
        )

    def count(self):
        return len(self.people.keys())


def get_people_from_input(input_str: str) -> People:
    raw_people = input_str.split(",")
    people = {}
    pairs = {}
    for raw_person in raw_people:
        if "+" in raw_person:
            raw_pair = raw_person.split("+")
            first = Person(name=raw_pair[0])
            second = Person(name=raw_pair[1])
            pair = Pair(first=first, second=second)
            people[first.id] = first
            people[second.id] = second
            pairs[pair.id] = pair
        else:
            person = Person(name=raw_person)
            people[person.id] = person
    return People(people=people, pairs=pairs)
