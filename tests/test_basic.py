# -*- coding: utf-8 -*-
import sys
import pytest


def test_help_message(testdir):
    result = testdir.runpytest(
        '--help',
    )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        'concurrent:',
        '*--concmode=CONCURRENT_MODE',
        '*--concworkers=CONCURRENT_WORKERS',
    ])


@pytest.mark.skipif(sys.platform == 'win32',
                    reason="does not run on windows")
def test_ini_setting(testdir):
    '''notice that this is not tested for windows'''
    concurrent_mode = 'mproc'
    concurrent_workers = 100

    testdir.makeini("""
        [pytest]
        concurrent_mode = %s
        concurrent_workers = %d
    """ % (concurrent_mode, concurrent_workers))

    testdir.makepyfile("""
        import pytest

        @pytest.fixture
        def concurrent_mode(request):
            return request.config.getini('concurrent_mode')

        @pytest.fixture
        def concurrent_workers(request):
            return request.config.getini('concurrent_workers')

        def test_concurrent_mode(concurrent_mode):
            assert concurrent_mode == '%s'

        def test_concurrent_workers(concurrent_workers):
            assert concurrent_workers == '%d'
    """ % (concurrent_mode, concurrent_workers))

    result = testdir.runpytest('-v')

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*= 2 passed in *s =*'
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0
