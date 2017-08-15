import time


def test_multithread(testdir):
    """Make sure that pytest accepts our fixture."""

    # create a temporary pytest test module
    testdir.makepyfile("""
        import pytest
        import time

        def test_something_else():
            time.sleep(5)
            assert 1 == 2


        @pytest.mark.parametrize('name', ['this', 'is', 'a', 'book'])
        def test_lots_of_things(name):
            time.sleep(2)
    """)

    before_run = time.time()
    result = testdir.runpytest('--concmode=mthread', '--concworkers=2')
    after_run = time.time()

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*.py:*: AssertionError'
    ])

    time_diff = after_run - before_run
    assert time_diff > 4 and time_diff < 8
