import psutil
import collections

import pytest
from pytest_concurrent.modes import factory


PYTEST_CONCURRENT_MODE = None


def pytest_addoption(parser):
    group = parser.getgroup('concurrent')
    group.addoption(
        '--concmode',
        action='store',
        dest='concurrent_mode',
        default=None,
        help='Set the concurrent mode (mthread, mproc, asyncnet)'
    )
    group.addoption(
        '--concworkers',
        action='store',
        dest='concurrent_workers',
        default=None,
        help='Set the concurrent worker amount (default to maximum)'
    )

    parser.addini('concurrent_mode', 'Set the concurrent mode (mthread, mproc, asyncnet)')
    parser.addini('concurrent_workers', 'Set the concurrent worker amount (default to maximum)')


def pytest_runtestloop(session):
    '''Initialize a single test session'''
    if (session.testsfailed and
            not session.config.option.continue_on_collection_errors):
        raise session.Interrupted(
            "%d errors during collection" % session.testsfailed)

    if session.config.option.collectonly:
        return True

    mode_name = session.config.option.concurrent_mode if session.config.option.concurrent_mode \
        else session.config.getini('concurrent_mode')
    if mode_name and mode_name not in ['mproc', 'mthread', 'asyncnet']:
        raise NotImplementedError('Concurrent mode %s is not supported (available: mproc, mthread, asyncnet).' % mode_name)

    try:
        workers_raw = session.config.option.concurrent_workers if session.config.option.concurrent_workers else session.config.getini('concurrent_workers')

        # set worker amount to the collected test amount
        if workers_raw == 'max':
            workers_raw = len(session.items)

        workers = int(workers_raw) if workers_raw else None

        # backport max worker: https://github.com/python/cpython/blob/3.5/Lib/concurrent/futures/thread.py#L91-L94
        if workers is None:
            cpu_counter = psutil
            workers = (cpu_counter.cpu_count() or 1) * 5
    except ValueError:
        raise ValueError('Concurrent workers can only be integer.')

    # group collected tests into different lists
    groups = collections.defaultdict(list)
    ungrouped_items = list()
    for item in session.items:
        concurrent_group_marker = item.get_closest_marker('concgroup')
        concurrent_group = None

        if concurrent_group_marker is not None:
            if 'args' in dir(concurrent_group_marker) \
                    and concurrent_group_marker.args:
                concurrent_group = concurrent_group_marker.args[0]
            if 'kwargs' in dir(concurrent_group_marker) \
                    and 'group' in concurrent_group_marker.kwargs:
                # kwargs beat args
                concurrent_group = concurrent_group_marker.kwargs['group']

        if concurrent_group:
            if not isinstance(concurrent_group, int):
                raise TypeError('Concurrent Group needs to be an integer')
            groups[concurrent_group].append(item)
        else:
            ungrouped_items.append(item)

    for group in sorted(groups):
        PYTEST_CONCURRENT_MODE.run_items(items=groups[group], session=session, workers=workers)
    if ungrouped_items:
        PYTEST_CONCURRENT_MODE.run_items(items=ungrouped_items, session=session, workers=workers)

    return True


@pytest.mark.trylast
def pytest_configure(config):
    global PYTEST_CONCURRENT_MODE
    config.addinivalue_line(
        'markers',
        'concgroup(group: int): concurrent group number to run tests in groups (smaller numbers are executed earlier)')

    mode_name = config.option.concurrent_mode if config.option.concurrent_mode \
        else config.getini('concurrent_mode')
    if mode_name and mode_name not in factory.keys():
        raise NotImplementedError('Concurrent mode "%s" is not supported (available: %s).' % (mode_name, [k for k in factory.keys()]))

    PYTEST_CONCURRENT_MODE = factory[mode_name]()
    PYTEST_CONCURRENT_MODE.set_reporter(config)
