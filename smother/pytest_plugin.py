import coverage


def pytest_addoption(parser):
    """Add options to control coverage."""

    group = parser.getgroup(
        'smother', 'smother reporting')
    group.addoption('--smother', action='append', default=[], metavar='path',
                    nargs='?', const=True, dest='smother_source',
                    help='measure coverage for filesystem path '
                    '(multi-allowed)')
    group.addoption('--smother-config', action='store', default='.coveragerc',
                    help='config file for coverage, default: .coveragerc')
    group.addoption('--smother-append', action='store_true', default=False,
                    help='append to existing smother report, '
                         'default: False')
    group.addoption('--smother-output', action='store', default='.smother',
                    help='output file for smother data. '
                         'default: .smother')
    group.addoption('--smother-cover', action='store_true', default=False,
                    help='Create a vanilla coverage file in addition to '
                         'the smother output')


def pytest_configure(config):
    """Activate plugin if appropriate."""
    if config.getvalue('smother_source'):
        if not config.pluginmanager.hasplugin('_smother'):
            plugin = Plugin(config.option)
            config.pluginmanager.register(plugin, '_smother')


class Plugin(object):

    def __init__(self, options):
        self.coverage = coverage.coverage(
            source=options.smother_source,
            config_file=options.smother_config,
        )

        # The unusual import statement placement is so that
        # smother's own test suite can measure coverage of
        # smother import statements
        self.coverage.start()
        from smother.control import Smother
        self.smother = Smother(self.coverage)

        self.output = options.smother_output
        self.append = options.smother_append
        self.cover_report = options.smother_cover
        self.first_test = True

    def pytest_runtest_setup(self, item):
        if self.first_test:
            self.first_test = False
            self.coverage.stop()
            self.smother.save_context("")
        self.smother.start()

    def pytest_runtest_teardown(self, item, nextitem):
        self.coverage.stop()
        self.smother.save_context(item.nodeid)

    def pytest_terminal_summary(self):
        self.smother.write(self.output, append=self.append)
        if self.cover_report:
            self.smother.write_coverage()
