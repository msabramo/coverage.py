"""Code common to test runner plugins."""

import optparse, sys
import coverage

class CoverageTestWrapper(object):
    """A coverage test wrapper.

    1) Setup the with the parsed options
    2) Call start()
    3) Run your tests
    4) Call finish()
    5) Improve your code coverage ;)
    """

    coverPackages = None

    def __init__(self, options, _covpkg=coverage):
        # _covpkg is for dependency injection, so we can test this code.

        self.options = options
        self.covpkg = _covpkg

        self.coverage = None

        self.coverTests = options.cover_tests
        self.coverPackages = options.cover_package

    def start(self):
        self.coverage = self.covpkg.coverage(
            data_suffix = bool(self.options.cover_parallel_mode),
            cover_pylib = self.options.cover_pylib,
            timid = self.options.cover_timid,
            branch = self.options.cover_branch,
        )

        self.skipModules = sys.modules.keys()[:] #TODO: is this necessary??

        self.coverage.start()

    def finish(self, stream=None):
        self.coverage.stop()
        self.coverage.save()

        modules = [module for name, module in sys.modules.items()
                   if self._want_module(name, module)]

        # Remaining actions are reporting, with some common self.options.
        report_args = {
            'morfs': modules,
            'ignore_errors': self.options.cover_ignore_errors,
            }

        try: # try looking for an omit file
            omit_file = open(self.options.cover_omit)
            omit = [line.strip() for line in omit_file.readlines()]
            report_args['omit'] = omit
        except: # assume cover_omit is a ',' separated list if provided
            omit = self.options.cover_omit.split(',')
            report_args['omit'] = omit

        if 'report' in self.options.cover_actions:
            self.coverage.report(
                    show_missing=self.options.cover_show_missing,
                    file=stream, **report_args)
        if 'annotate' in self.options.cover_actions:
            self.coverage.annotate(
                    directory=self.options.cover_directory, **report_args)
        if 'html' in self.options.cover_actions:
            self.coverage.html_report(
                    directory=self.options.cover_directory, **report_args)
        if 'xml' in self.options.cover_actions:
            outfile = self.options.cover_outfile
            if outfile == '-':
                outfile = None
            self.coverage.xml_report(outfile=outfile, **report_args)

        return

    def _want_module(self, name, module):
        for package in self.coverPackages:
            if module is not None and name.startswith(package):
                return True

        return False


options = [
    optparse.Option('--cover-action', action='append', default=['report'],
                    dest='cover_actions', type="choice",
                    choices=['annotate', 'html', 'report', 'xml'],
                    help="""\
annotate    Annotate source files with execution information.
html        Create an HTML report.
report      Report coverage stats on modules.
xml         Create an XML report of coverage results.
                    """.strip()),

    optparse.Option('--cover-package', action='append', default=[],
                    dest="cover_package", metavar="COVER_PACKAGE",
                    help=("Restrict coverage output to selected package "
                          "- can be specified multiple times")),

    optparse.Option("--cover-tests", action="store_true", dest="cover_tests",
                    metavar="[NOSE_COVER_TESTS]", default=False,
                    help="Include test modules in coverage report "),

    optparse.Option('--cover-branch', action='store_true',
                    help="Measure branch execution. HIGHLY EXPERIMENTAL!"),

    optparse.Option('--cover-directory', action='store', metavar="DIR",
                    help="Write the output files to DIR."),

    optparse.Option('--cover-ignore-errors', action='store_true',
                    help="Ignore errors while reading source files."),

    optparse.Option('--cover-pylib', action='store_true',
                    help=("Measure coverage even inside the Python installed "
                         "library, which isn't done by default.")),

    optparse.Option('--cover-show-missing', action='store_true',
                    help=("Show line numbers of statements in each module "
                         "that weren't executed.")),

    optparse.Option('--cover-omit', action='store',
                    metavar="PRE1,PRE2,...", default='',
                    help=("Omit files when their filename path matches one "
                         "of these patterns.")),

    optparse.Option('--cover-outfile', action='store', metavar="OUTFILE",
                    help=("Write the XML report to this file. Defaults to "
                         "'coverage.xml'")),

    optparse.Option('--cover-parallel-mode', action='store_true',
                    help=("Include the machine name and process id in the "
                          ".coverage data file name.")),

    optparse.Option('--cover-timid', action='store_true',
                    help=("Use a simpler but slower trace method.  Try this "
                          "if you get seemingly impossible results!")),

    optparse.Option('--cover-append', action='store_false',
                    help=("Append coverage data to .coverage, otherwise it "
                          "is started clean with each run."))
]