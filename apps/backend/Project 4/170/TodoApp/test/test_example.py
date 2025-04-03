import pytest


def test_equal_or_not_equal():
    assert 3 == 3
    assert 3 != 4
    # assert 3 != 3
    num_list = [1, 2, 3, 4, 5]
    any_list = [False, True]

    # all() returns True if all elements in the list are True
    assert all(num_list)
    # any() returns True if any element in the list is True
    assert any(any_list)


class Student:
    def __init__(self, first_name, last_name, age, major):
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.major = major


@pytest.fixture
def default_employee():
    return Student("John", "Doe", 30, "Computer Science")


def test_person_initialization(default_employee):
    assert default_employee.first_name == "John"
    assert default_employee.last_name == "Doe"
    assert default_employee.age == 30
    assert default_employee.major == "Computer Science"
