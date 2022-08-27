"""
Fixtures for behavioral tests.
"""

import pytest
from .behavioral_test_fixture import BehavioralTest


@pytest.fixture
def behavioral_test_fixture():
    """
    Basic test fixture.
    """

    test = BehavioralTest()
    yield test
    test.teardown()
