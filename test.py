import pytest
import time

def test_something_else():
    time.sleep(5)
    assert 1 == 2


@pytest.mark.parametrize('name', ['this', 'is', 'a', 'book'])
def test_lots_of_things(name):
    time.sleep(2)
