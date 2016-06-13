import coverage

from smother import Smother


def pytest_addoption(parser):
    """Add options to control coverage."""

    group = parser.getgroup(
        'smother', 'smother reporting')
    group.addoption('--smother', action='append', default=[], metavar='path',
                    nargs='?', const=True, dest='cov_source',
                    help='measure coverage for filesystem path '
                    '(multi-allowed)')
    group.addoption('--smother-config', action='store', default='.coveragerc',
                    metavar='path',
                    help='config file for coverage, default: .coveragerc')
    group.addoption('--smother-append', action='store_true', default=False,
                    help='append to existing smother report, '
                         'default: False')
    group.addoption('--smother-output', action='store', default='.smother',
                    metavar='path',
                    help='output file for smother report. '
                         'default: .smother')


def pytest_configure(config):
    """Activate plugin if appropriate."""
    if config.getvalue('cov_source'):
        if not config.pluginmanager.hasplugin('_smother'):
            plugin = Plugin(config.option)
            config.pluginmanager.register(plugin, '_smother')


class Plugin(object):

    def __init__(self, options):
        self.coverage = coverage.coverage(
            source=options.cov_source,
            config_file=options.smother_config,
        )
        self.coverage._init()
        self.smother = Smother(self.coverage)
        self.output = options.smother_output
        self.append = options.smother_append

    def pytest_runtest_setup(self, item):
        print("starting")
        self.smother.start()

    def pytest_runtest_teardown(self, item, nextitem):
        print("finish %s" % item.nodeid)
        self.coverage.stop()
        self.smother.save_context(item.nodeid)

    def pytest_terminal_summary(self, terminalreporter):
        print("report")
        self.smother.write(self.output, append=self.append)
