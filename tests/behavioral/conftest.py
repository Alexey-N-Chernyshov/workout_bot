import pytest
from .behavioral_test_fixture import BehavioralTest


@pytest.fixture
def behavioral_test_fixture():
    test = BehavioralTest()
    yield test
    test.teardown()
