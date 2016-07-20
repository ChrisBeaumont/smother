import logging

from nose.plugins.cover import Coverage

from smother.control import Smother


log = logging.getLogger(__name__)


class SmotherNose(Coverage):
    name = "smother"

    def afterTest(self, test):
        self.coverInstance.stop()
        self.smother.save_context("%s:%s" % test.address()[1:3])

    def beforeTest(self, test):

        # Save coverage from before first test as an unlabeled
        # context. This captures coverage during import.
        if self.first_test:
            self.coverInstance.stop()
            self.smother.save_context("")
            self.first_test = False

        self.smother.start()

    def configure(self, options, conf):
        super(SmotherNose, self).configure(options, conf)
        if self.enabled:
            self.first_test = True
            self.output = options.smother_output
            self.append = options.smother_append
            self.smother = Smother(self.coverInstance)

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
        parser.add_option("--smother-config-file", action="store",
                          default=env.get('NOSE_COVER_CONFIG_FILE'),
                          dest="cover_config_file",
                          help="Location of coverage config file "
                          "[NOSE_COVER_CONFIG_FILE]")
        parser.add_option("--smother-output", action="store",
                          default=env.get('NOSE_SMOTHER_OUTPUT', '.smother'),
                          dest="smother_output",
                          help="Location of output file")
        parser.add_option("--smother-append", action="store_true",
                          default=env.get('NOSE_SMOTHER_APPEND'),
                          dest="smother_append",
                          help="Append to existing smother file")

    def report(self, stream):
        self.smother.write(self.output, append=self.append)
