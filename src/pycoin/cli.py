"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?
You might be tempted to import things from __main__ later, but that will cause
problems--the code will get executed twice:
 - When you run `python -mpycoin` python will execute
   ``__main__.py`` as a script. That means there won't be any
   ``pycoin.__main__`` in ``sys.modules``.
 - When you import __main__ it will get executed again (as a module) because
   there's no ``pycoin.__main__`` in ``sys.modules``.

Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
from itertools import chain
import os
from textwrap import TextWrapper

import click

from . import __title__ as NAME
from .media_manager import MovieManager


class AliasedGroup(click.Group):
    def get_command(self, ctx, command_name):
        rv = click.Group.get_command(self, ctx, command_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx) if x.startswith(command_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail('Too many matches: {}'.format(', '.join(sorted(matches))))


@click.group(cls=AliasedGroup, invoke_without_command=True)
@click.option('--set-key', expose_value=True, is_eager=True, metavar='API_KEY', help='Set the TMDB API key to API_KEY and save it in the config. Required before first run.')
@click.option('--unset-key', is_flag=True, expose_value=True, is_eager=True, help='Unset the saved TMDB API key.')
@click.version_option()
@click.pass_context
def main(ctx, set_key, unset_key):
    """
    A script to semi-randomly select a movie to watch from your list.

    All commands can be accessed by their first letter (i.e. `a` for `add`, `d` for `delete`, etc.).
    """
    config_path = os.path.join(click.get_app_dir(NAME), '{}.json'.format(NAME))
    ctx.obj = MovieManager(config_path=config_path)

    if unset_key:
        ctx.obj['movies_config'].pop('api_key')
        ctx.obj.write_config()
    elif set_key:
        ctx.obj['movies_config']['api_key'] = set_key
        ctx.obj.write_config()
    elif ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command()
@click.argument('identifier')
@click.pass_context
def add(ctx, identifier):
    """Add movie indicated by IDENTIFIER to your list. IDENTIFIER can be a TMDB ID, an IMDB ID, or a partial or full title."""
    ctx.obj.add(identifier)
    ctx.obj.write_config()


@main.command()
@click.argument('tmdb_id')
@click.pass_context
def delete(ctx, tmdb_id):
    """Remove movie indicated by TMDB_ID from your list."""
    ctx.obj.delete(tmdb_id)
    ctx.obj.write_config()


@main.command()
@click.pass_context
def flip(ctx):
    """Semi-randomly select a movie from your list to watch."""
    movie = ctx.obj.flip()
    click.echo('Your movie is {} ({})'.format(movie['title'], movie['year']))
    ctx.obj.write_config()


@main.command()
@click.argument('tmdb_id')
@click.pass_context
def watch(ctx, tmdb_id):
    """Mark movie indicated by TMDB_ID as watched."""
    ctx.obj.complete(tmdb_id)
    ctx.obj.write_config()


@main.command()
@click.argument('tmdb_id')
@click.pass_context
def unwatch(ctx, tmdb_id):
    """Mark movie indicated by TMDB_ID as unwatched."""
    ctx.obj.uncomplete(tmdb_id)
    ctx.obj.write_config()


@main.command(name='list')
@click.pass_context
def list_movies(ctx):
    """Show your list of movies."""
    def colorize(row):
        return (
            click.style(row[0], fg='green'),
            click.style(row[1], fg='yellow'),
            row[2]
        )

    header = [('TMDB ID', 'Title', '(Year)')]

    queued = {k: v for k, v in ctx.obj['movies'].items() if not v['completed']}
    queued_rows = sorted(
        [(str(movie['tmdb_id']), movie['title'], '({})'.format(movie['year'])) for movie in queued.values()],
        key=lambda x: int(x[0])
    )

    completed = {k: v for k, v in ctx.obj['movies'].items() if v['completed']}
    completed_rows = sorted(
        [(str(movie['tmdb_id']), movie['title'], '({})'.format(movie['year'])) for movie in completed.values()],
        key=lambda x: int(x[0])
    )

    col_widths = []
    for col in range(3):
        rows = chain(header, queued_rows, completed_rows)
        widths = [len(row[col]) for row in rows]
        col_widths.append(max(widths))
    pattern = '{{id:>{width}}} {{title}} {{year}}'.format(width=col_widths[0] + 9)

    wrapper = TextWrapper(subsequent_indent=' ' * (col_widths[0] + 1))

    colorized_header = colorize(header[0])
    click.echo(wrapper.fill(pattern.format(id=colorized_header[0], title=colorized_header[1], year=colorized_header[2])))
    click.secho('({} unwatched movies)'.format(len(queued_rows)), dim=True)

    colorized_rows = map(colorize, queued_rows)
    for row in colorized_rows:
        click.echo(wrapper.fill(pattern.format(id=row[0], title=row[1], year=row[2])))

    click.secho('\nAlready Watched:', fg='red')
    click.secho('({} watched movies)'.format(len(completed_rows)), dim=True)
    colorized_rows = map(colorize, completed_rows)
    for row in colorized_rows:
        click.echo(wrapper.fill(pattern.format(id=row[0], title=row[1], year=row[2])))

