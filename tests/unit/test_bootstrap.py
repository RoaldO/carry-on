import abc

import allure
import pytest

from carry_on import bootstrap


@allure.feature("Dependency injection")
@allure.story("Fetching")
def test_that_requesting_a_not_existing_item_raises_an_error():
    class UnfulfilledInterface(abc.ABC):
        pass

    with pytest.raises(
        LookupError, match="No `UnfulfilledInterface` implementation found"
    ):
        bootstrap.get(UnfulfilledInterface)


@allure.feature("Dependency injection")
@allure.story("Registration")
def test_that_interface_must_be_a_class():
    class MyInterface(abc.ABC):
        pass

    class MyImplementation(MyInterface):
        pass

    with pytest.raises(
        TypeError, match="Class reference expected and not and instance"
    ):
        bootstrap.register(MyInterface, MyImplementation())  # type: ignore


@allure.feature("Dependency injection")
@allure.story("Registration")
def test_that_implementation_must_be_a_class():
    class MyInterface(abc.ABC):
        pass

    class MyImplementation(MyInterface):
        pass

    with pytest.raises(
        TypeError, match="Class reference expected and not and instance"
    ):
        bootstrap.register(MyInterface(), MyImplementation)  # type: ignore


@allure.feature("Dependency injection")
@allure.story("Registration")
def test_that_implementation_must_be_a_sub_class_if_interface():
    class MyInterface(abc.ABC):
        pass

    class NotAnImplementation:
        pass

    with pytest.raises(
        TypeError, match="Implementation is not a subclass of interface"
    ):
        bootstrap.register(MyInterface, NotAnImplementation)  # type: ignore


@allure.feature("Dependency injection")
@allure.story("Registration")
def test_that_implementation_must_not_be_the_interface():
    class MyInterface(abc.ABC):
        pass

    with pytest.raises(
        TypeError, match="Implementation is not a subclass of interface"
    ):
        bootstrap.register(MyInterface, MyInterface)  # type: ignore


@allure.feature("Dependency injection")
@allure.story("Registration")
def test_that_a_class_can_be_registered():
    class MyInterface(abc.ABC):
        pass

    class MyImplementation(MyInterface):
        pass

    bootstrap.register(MyInterface, MyImplementation)


@allure.feature("Dependency injection")
@allure.story("Fetching")
def test_that_a_registered_implementation_can_be_fetched():
    class MyInterface(abc.ABC):
        pass

    class MyImplementation(MyInterface):
        pass

    bootstrap.register(MyInterface, MyImplementation)
    response = bootstrap.get(MyInterface)
    assert isinstance(response, MyImplementation)
