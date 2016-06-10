import logging

from nose.plugins.cover import Coverage

from smother import Smother


log = logging.getLogger(__name__)


class SmotherNose(Coverage):
    name = "smother"

    def afterTest(self, test):
        self.coverInstance.stop()
        self.smother.save_context("%s:%s" % test.address()[1:3])

    def beforeTest(self, test):
        self.smother.start()

    def configure(self, options, conf):
        super(SmotherNose, self).configure(options, conf)
        if self.enabled:
            self.smother = Smother(self.coverInstance)
            self.coverInstance.stop() # XXX why is this needed to capture the first test?

    def options(self, parser, env):
        super(Coverage, self).options(parser, env)
        parser.add_option("--smother-package", action="append",
                          default=env.get('NOSE_COVER_PACKAGE'),
                          metavar="PACKAGE",
                          dest="cover_packages",
                          help="Restrict coverage output to selected packages "
                          "[NOSE_COVER_PACKAGE]")
        parser.add_option("--smother-erase", action="store_true",
                          default=env.get('NOSE_COVER_ERASE'),
                          dest="cover_erase",
                          help="Erase previously collected coverage "
                          "statistics before run")
        parser.add_option("--smother-tests", action="store_true",
                          dest="cover_tests",
                          default=env.get('NOSE_COVER_TESTS'),
                          help="Include test modules in coverage report "
                          "[NOSE_COVER_TESTS]")
        parser.add_option("--smother-min-percentage", action="store",
                          dest="cover_min_percentage",
                          default=env.get('NOSE_COVER_MIN_PERCENTAGE'),
                          help="Minimum percentage of coverage for tests "
                          "to pass [NOSE_COVER_MIN_PERCENTAGE]")
        parser.add_option("--smother-inclusive", action="store_true",
                          dest="cover_inclusive",
                          default=env.get('NOSE_COVER_INCLUSIVE'),
                          help="Include all python files under working "
                          "directory in coverage report.  Useful for "
                          "discovering holes in test coverage if not all "
                          "files are imported by the test suite. "
                          "[NOSE_COVER_INCLUSIVE]")
        parser.add_option("--smother-html", action="store_true",
                          default=env.get('NOSE_COVER_HTML'),
                          dest='cover_html',
                          help="Produce HTML coverage information")
        parser.add_option('--smother-html-dir', action='store',
                          default=env.get('NOSE_COVER_HTML_DIR', 'cover'),
                          dest='cover_html_dir',
                          metavar='DIR',
                          help='Produce HTML coverage information in dir')
        parser.add_option("--smother-branches", action="store_true",
                          default=env.get('NOSE_COVER_BRANCHES'),
                          dest="cover_branches",
                          help="Include branch coverage in coverage report "
                          "[NOSE_COVER_BRANCHES]")
        parser.add_option("--smother-xml", action="store_true",
                          default=env.get('NOSE_COVER_XML'),
                          dest="cover_xml",
                          help="Produce XML coverage information")
        parser.add_option("--smother-xml-file", action="store",
                          default=env.get('NOSE_COVER_XML_FILE',
                                          'coverage.xml'),
                          dest="cover_xml_file",
                          metavar="FILE",
                          help="Produce XML coverage information in file")
        parser.add_option("--smother-config-file", action="store",
                          default=env.get('NOSE_COVER_CONFIG_FILE'),
                          dest="cover_config_file",
                          help="Location of coverage config file "
                          "[NOSE_COVER_CONFIG_FILE]")
        parser.add_option("--smother-no-print", action="store_true",
                          default=env.get('NOSE_COVER_NO_PRINT'),
                          dest="cover_no_print",
                          help="Suppress printing of coverage information")

    def report(self, stream):
        with open('.smother', 'w') as outfile:
            self.smother.write(outfile)
