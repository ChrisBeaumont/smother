import csv

import click
from diff_cover.diff_reporter import GitDiffReporter
from diff_cover.git_diff import GitDiffTool

from smother import Smother
from smother.diff import parse_intervals as diff_parse_intervals
from smother.interval import parse_intervals


"""
Implementation Goals

* [x] Give a filename:lineno, return all tests
* [x] Give a diff, return all tests
* [x] Given an import identifier, return all tests
* [x] Given a test set, run them
* Interactive browser
* Looker/tableau export (list of pairs of context names)
* [x] Collect website smother report
* [ ] Implement semantic diff
* [ ] Web dashboard
* [ ] Test suite
* [ ] fast
"""


def _get_diff_regions(branch):
    reporter = GitDiffReporter(branch, git_diff=GitDiffTool())
    for diff in reporter._get_included_diff_results():
        for rng in diff_parse_intervals(diff):
            print(rng)
            yield rng


@click.group()
@click.option('--report', '-r', default='.smother', help='Smother report file')
@click.option(
    '--semantic', '-s',
    help='Map coverage to semantic blocks (functions and classes) '
         'instead of individual line numbers.',
    is_flag=True,
)
@click.pass_context
def cli(ctx, report, semantic):
    """
    Query or manipulate smother reports
    """
    ctx.obj = {'report': report, 'semantic': semantic}


def _report_from_regions(regions, opts):
    report_file = opts['report']

    smother = Smother.load(report_file)
    result = smother.query_context(regions)
    result.report()


@cli.command()
@click.argument("path")
@click.pass_context
def lookup(ctx, path):
    """
    Determine which tests intersect a source interval.
    """
    regions = parse_intervals(path, ctx.obj['semantic'])
    _report_from_regions(regions, ctx.obj)


@cli.command()
@click.argument("branch", default="")
@click.pass_context
def diff(ctx, branch):
    """
    Determine which tests intersect a git diff.
    """
    regions = _get_diff_regions(branch)
    _report_from_regions(regions, ctx.obj)


@cli.command()
@click.argument('src', nargs=-1, type=click.Path())
@click.argument('dst', nargs=1, type=click.Path())
def combine(src, dst):
    """
    Combine several smother reports.
    """
    result = None
    for infile in src:
        sm = Smother.load(infile)
        if not result:
            result = sm
        else:
            result |= sm

    result.write(dst)


@cli.command()
@click.argument('dst', type=click.File('w'))
@click.pass_context
def flatten(ctx, dst):
    """
    Flatten a coverage file into a CSV
    of source_context, testname
    """
    sm = Smother.load(ctx.obj['report'])
    semantic = ctx.obj['semantic']
    writer = csv.writer(dst)
    dst.write("source_context, test_context\n")
    writer.writerows(sm.iter_records(semantic=semantic))


if __name__ == "__main__":
    cli()
