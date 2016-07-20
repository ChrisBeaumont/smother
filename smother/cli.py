import csv as _csv
import os

import click
import coverage

from smother.control import Smother
from smother.git import GitDiffReporter
from smother.interval import parse_intervals


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


def _report_from_regions(regions, opts, **kwargs):
    report_file = opts['report']
    smother = Smother.load(report_file)
    result = smother.query_context(regions, **kwargs)
    result.report()


@cli.command()
@click.argument("path")
@click.pass_context
def lookup(ctx, path):
    """
    Determine which tests intersect a source interval.
    """
    regions = parse_intervals(path, as_context=ctx.obj['semantic'])
    _report_from_regions(regions, ctx.obj)


@cli.command()
@click.argument("branch", default="")
@click.pass_context
def diff(ctx, branch):
    """
    Determine which tests intersect a git diff.
    """
    diff = GitDiffReporter(branch)
    regions = diff.changed_intervals()
    _report_from_regions(regions, ctx.obj, file_factory=diff.old_file)


@cli.command()
@click.argument('src', nargs=-1, type=click.File())
@click.argument('dst', nargs=1, type=click.Path())
def combine(src, dst):
    """
    Combine several smother reports.
    """
    result = Smother()

    for infile in src:
        result |= Smother.load(infile)

    result.write(dst)


@cli.command()
@click.argument('dst', type=click.File('w'))
@click.pass_context
def csv(ctx, dst):
    """
    Flatten a coverage file into a CSV
    of source_context, testname
    """
    sm = Smother.load(ctx.obj['report'])
    semantic = ctx.obj['semantic']
    writer = _csv.writer(dst, lineterminator='\n')
    dst.write("source_context, test_context\n")
    writer.writerows(sm.iter_records(semantic=semantic))


@cli.command()
@click.pass_context
def erase(ctx):
    """
    Erase the existing smother report.
    """
    if os.path.exists(ctx.obj['report']):
        os.remove(ctx.obj['report'])


@cli.command()
@click.pass_context
def to_coverage(ctx):
    """
    Produce a .coverage file from a smother file
    """
    sm = Smother.load(ctx.obj['report'])
    sm.coverage = coverage.coverage()
    sm.write_coverage()
