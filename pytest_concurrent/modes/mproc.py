import os
import time
import multiprocessing
import concurrent.futures

import py
from _pytest.junitxml import LogXML
from _pytest.terminal import TerminalReporter
from _pytest.junitxml import Junit
from _pytest.junitxml import _NodeReporter
from _pytest.junitxml import bin_xml_escape
from _pytest.junitxml import mangle_test_address

from .base import BaseMode


class MultiProcessMode(BaseMode):
    NAME = 'mproc'

    # Manager for the shared variables being used by in multiprocess mode
    MANAGER = multiprocessing.Manager()

    # to override the variable self.stats from LogXML
    XMLSTATS = MANAGER.dict()
    XMLSTATS['error'] = 0
    XMLSTATS['passed'] = 0
    XMLSTATS['failure'] = 0
    XMLSTATS['skipped'] = 0

    # ensures that XMLSTATS is not being modified simultaneously
    XMLLOCK = multiprocessing.Lock()

    XMLREPORTER = MANAGER.dict()
    # XMLREPORTER_ORDERED = MANAGER.list()
    NODELOCK = multiprocessing.Lock()
    NODEREPORTS = MANAGER.list()

    # to keep track of the log for TerminalReporter
    DICTIONARY = MANAGER.dict()

    # to override the variable self.stats from TerminalReporter
    STATS = MANAGER.dict()

    # ensures that STATS is not being modified simultaneously
    LOCK = multiprocessing.Lock()

    ''' Multiprocess is not compatible with Windows !!! '''
    def run_items(self, items, session, workers=None):
        '''Using ThreadPoolExecutor as managers to control the lifecycle of processes.
        Each thread will spawn a process and terminates when the process joins.
        '''
        def run_task_in_proc(item, index):
            proc = multiprocessing.Process(target=self._run_next_item, args=(session, item, index))
            proc.start()
            proc.join()

        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            for index, item in enumerate(items):
                executor.submit(run_task_in_proc, item, index)

    def set_reporter(self, config):
        standard_reporter = config.pluginmanager.getplugin('terminalreporter')
        concurrent_reporter = ConcurrentTerminalReporter(standard_reporter)

        config.pluginmanager.unregister(standard_reporter)
        config.pluginmanager.register(concurrent_reporter, 'terminalreporter')

        if config.option.xmlpath is not None:
            xmlpath = config.option.xmlpath
            config.pluginmanager.unregister(config._xml)
            config._xml = ConcurrentLogXML(xmlpath, config.option.junitprefix, config.getini("junit_suite_name"))
            config.pluginmanager.register(config._xml)


class ConcurrentNodeReporter(_NodeReporter):
    '''to provide Node Reporting for multiprocess mode'''
    def __init__(self, nodeid, xml):

        self.id = nodeid
        self.xml = xml
        self.add_stats = self.xml.add_stats
        self.duration = 0
        self.properties = []
        self.nodes = []
        self.testcase = None
        self.attrs = {}

    def to_xml(self):  # overriden
        testcase = Junit.testcase(time=self.duration, **self.attrs)
        testcase.append(self.make_properties_node())
        for node in self.nodes:
            testcase.append(node)
        return str(testcase.unicode(indent=0))

    def record_testreport(self, testreport):
        assert not self.testcase
        names = mangle_test_address(testreport.nodeid)
        classnames = names[:-1]
        if self.xml.prefix:
            classnames.insert(0, self.xml.prefix)
        attrs = {
            "classname": ".".join(classnames),
            "name": bin_xml_escape(names[-1]),
            "file": testreport.location[0],
        }
        if testreport.location[1] is not None:
            attrs["line"] = testreport.location[1]
        if hasattr(testreport, "url"):
            attrs["url"] = testreport.url
        self.attrs = attrs

    def finalize(self):
        data = self.to_xml()  # .unicode(indent=0)
        self.__dict__.clear()
        self.to_xml = lambda: py.xml.raw(data)
        MultiProcessMode.NODEREPORTS.append(data)


class ConcurrentLogXML(LogXML):
    '''to provide XML reporting for multiprocess mode'''

    def __init__(self, logfile, prefix, suite_name="pytest"):
        logfile = logfile
        logfile = os.path.expanduser(os.path.expandvars(logfile))
        self.logfile = os.path.normpath(os.path.abspath(logfile))
        self.prefix = prefix
        self.suite_name = suite_name
        self.stats = MultiProcessMode.XMLSTATS
        self.node_reporters = {}  # XMLREPORTER  # nodeid -> _NodeReporter
        self.node_reporters_ordered = []
        self.global_properties = []
        # List of reports that failed on call but teardown is pending.
        self.open_reports = []
        self.cnt_double_fail_tests = 0

    def pytest_sessionfinish(self):
        dirname = os.path.dirname(os.path.abspath(self.logfile))
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        logfile = open(self.logfile, 'w', encoding='utf-8')
        suite_stop_time = time.time()
        suite_time_delta = suite_stop_time - self.suite_start_time

        numtests = (self.stats['passed'] + self.stats['failure'] +
                    self.stats['skipped'] + self.stats['error'] -
                    self.cnt_double_fail_tests)
        # print("NODE REPORTS: " + str(NODEREPORTS))
        logfile.write('<?xml version="1.0" encoding="utf-8"?>')
        logfile.write(Junit.testsuite(
            self._get_global_properties_node(),
            [self.concurrent_log_to_xml(x) for x in MultiProcessMode.NODEREPORTS],
            name=self.suite_name,
            errors=self.stats['error'],
            failures=self.stats['failure'],
            skips=self.stats['skipped'],
            tests=numtests,
            time="%.3f" % suite_time_delta, ).unicode(indent=0))
        logfile.close()

    def add_stats(self, key):
        MultiProcessMode.XMLLOCK.acquire()
        if key in self.stats:
            self.stats[key] += 1
        MultiProcessMode.XMLLOCK.release()

    def node_reporter(self, report):
        nodeid = getattr(report, 'nodeid', report)
        # local hack to handle xdist report order
        slavenode = getattr(report, 'node', None)

        key = nodeid, slavenode
        # NODELOCK.acquire()
        if key in self.node_reporters:
            # TODO: breasks for --dist=each
            return self.node_reporters[key]

        reporter = ConcurrentNodeReporter(nodeid, self)

        self.node_reporters[key] = reporter
        # NODEREPORTS.append(reporter.to_xml())
        return reporter

    def pytest_terminal_summary(self, terminalreporter):
        terminalreporter.write_sep("-",
                                   "generated xml file: %s" % (self.logfile))

    def concurrent_log_to_xml(self, log):
        return py.xml.raw(log)


class ConcurrentTerminalReporter(TerminalReporter):
    '''to provide terminal reporting for multiprocess mode'''

    def __init__(self, reporter):
        TerminalReporter.__init__(self, reporter.config)
        self._tw = reporter._tw
        self.stats = MultiProcessMode.STATS

    def add_stats(self, key):
        if key in self.stats:
            self.stats[key] += 1

    def pytest_runtest_logreport(self, report):
        rep = report
        res = self.config.hook.pytest_report_teststatus(report=rep)
        cat, letter, word = res

        self.append_list(self.stats, cat, rep)

        if report.when == 'call':
            MultiProcessMode.DICTIONARY[report.nodeid] = report
        self._tests_ran = True
        if not letter and not word:
            # probably passed setup/teardown
            return
        if self.verbosity <= 0:
            if not hasattr(rep, 'node') and self.showfspath:
                self.write_fspath_result(rep.nodeid, letter)
            else:
                self._tw.write(letter)
        else:
            if isinstance(word, tuple):
                word, markup = word
            else:
                if rep.passed:
                    markup = {'green': True}
                elif rep.failed:
                    markup = {'red': True}
                elif rep.skipped:
                    markup = {'yellow': True}
            line = self._locationline(rep.nodeid, *rep.location)
            if not hasattr(rep, 'node'):
                self.write_ensure_prefix(line, word, **markup)
                # self._tw.write(word, **markup)
            else:
                self.ensure_newline()
                if hasattr(rep, 'node'):
                    self._tw.write("[%s] " % rep.node.gateway.id)
                self._tw.write(word, **markup)
                self._tw.write(" " + line)
                self.currentfspath = -2

    def append_list(self, stats, cat, rep):
        MultiProcessMode.LOCK.acquire()
        cat_string = str(cat)
        if stats.get(cat_string) is None:
            stats[cat_string] = MultiProcessMode.MANAGER.list()

        mylist = stats.get(cat_string)
        mylist.append(rep)
        stats[cat] = mylist
        MultiProcessMode.LOCK.release()
