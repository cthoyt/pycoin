import datetime
import json
import random

import click
import py
from requests.exceptions import HTTPError
import tmdbsimple as tmdb


class PycoinError(Exception):
    """The base error from which all other errors used by this script are derived."""
    pass


class MovieCreationError(PycoinError):
    """An error raised in response to an issue in creating a Movie object."""
    pass


class Movie(dict):
    def __init__(self, identifier):
        tmdb_id = self._tmdb_id_from_identifier(identifier)
        if not tmdb_id:
            raise MovieCreationError('Unable to locate movie from identifier "{}".'.format(identifier))

        movie = tmdb.Movies(tmdb_id)
        try:
            movie.info()
        except HTTPError as e:
            if getattr(getattr(e, 'response', None), 'status_code', None) == 404:
                raise MovieCreationError('An invalid TMDB ID was used "{}"'.format(tmdb_id))

        super().__init__(
            tmdb_id=tmdb_id,
            title=movie.title,
            vote_average=movie.vote_average,
            year=datetime.datetime.strptime(movie.release_date, '%Y-%m-%d').year,
            watched=False
        )

    @staticmethod
    def _tmdb_id_from_identifier(identifier):
        try:
            if identifier.startswith('tt'):  # we have an IMDB id
                tmdb_id = tmdb.Find(identifier).info(external_source='imdb_id')['movie_results'][0]['id']
            elif not identifier.isdigit():  # we must have a title, since TMDB id's are ints
                tmdb_id = tmdb.Search().movie(query=identifier)['results'][0]['id']
            else:
                tmdb_id = identifier

            return int(tmdb_id)
        except IndexError:
            return False


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


class Config(dict):
    def __init__(self, *args, **kwargs):
        self.config = py.path.local(
            click.get_app_dir('pycoin')
        ).join('movies.json')

        super().__init__(*args, **kwargs)

    def load(self):
        try:
            self.update(json.loads(self.config.read()))
        except py.error.ENOENT:
            pass

    def save(self):
        self.config.ensure()
        with self.config.open('w') as f:
            f.write(json.dumps(self, indent=2, sort_keys=True))

pass_config = click.make_pass_decorator(Config, ensure=True)


def set_key(ctx, param, value):
    if value:
        config = ctx.ensure_object(Config)
        config.load()
        config['api_key'] = value
        config.save()
        ctx.exit('Successfully set TMDB API key "{}"'.format(value))
    else:
        return


def unset_key(ctx, param, value):
    if value:
        config = ctx.ensure_object(Config)
        config.load()
        config.pop('api_key', None)
        config.save()
        ctx.exit('Successfully unset TMDB API key')
    else:
        return


@click.group(cls=AliasedGroup)
@click.option('--set-key', callback=set_key, expose_value=False, is_eager=True, metavar='API_KEY', help='Set the TMDB API key to API_KEY and save it in the config. Required before first run.')
@click.option('--unset-key', callback=unset_key, is_flag=True, expose_value=False, is_eager=True, help='Unset the saved TMDB API key.')
@click.version_option()
@pass_config
@click.pass_context
def cli(ctx, config):
    """
    A script to semi-randomly select a movie to watch from your list.

    All commands can be accessed by their first letter (i.e. `a` for `add`, `d` for `delete`, etc.).
    """
    config.load()

    if 'api_key' not in config:
        click.echo('This application requires a TMDB API key to function.')
        click.echo('Visit "{}" to learn more about obtaining such a key.'.format('https://www.themoviedb.org/faq/api'))
        if click.confirm('Open this link in your default browser now?'):
            click.launch('https://www.themoviedb.org/faq/api')
        click.echo('To enter and save your new TMDB API key, run this script with the option `--set-key API_KEY`.')
        ctx.abort()
    tmdb.API_KEY = config.get('api_key', '11433deecaf09ef3aa3fb68d7e02a772')
    if 'movies' not in config:
        config['movies'] = {}


@cli.command()
@click.argument('identifier')
@pass_config
@click.pass_context
def add(ctx, config, identifier):
    """Add movie indicated by IDENTIFIER to your list. IDENTIFIER can be a TMDB ID, an IMDB ID, or a partial or full title."""
    try:
        new_movie = Movie(identifier)
    except MovieCreationError as e:
        ctx.fail(e)
    if new_movie in config['movies'].values():
        ctx.fail('The movie "{} ({})" is already on your list.'.format(new_movie['title'], new_movie['year']))
    config['movies'][str(new_movie['tmdb_id'])] = new_movie
    click.echo('Added "{} ({})" to your list.'.format(new_movie['title'], new_movie['year']))
    config.save()


@cli.command()
@click.argument('identifier')
@pass_config
@click.pass_context
def delete(ctx, config, identifier):
    """Remove movie indicated by IDENTIFIER from your list. IDENTIFIER can be a TMDB ID, an IMDB ID, or a partial or full title."""
    try:
        new_movie = Movie(identifier)
    except MovieCreationError as e:
        ctx.fail(e)
    if new_movie not in config['movies'].values():
        ctx.fail('The movie "{} ({})" is not on your list.'.format(new_movie['title'], new_movie['year']))
    config['movies'].pop(str(new_movie['tmdb_id']))
    click.echo('Deleted "{} ({})" from your list.'.format(new_movie['title'], new_movie['year']))
    config.save()


@cli.command()
@pass_config
@click.pass_context
def flip(ctx, config):
    """Semi-randomly select a movie from your list to watch."""
    def iter_specific_key(dictionary, key):
        for value in dictionary.values():
            yield value[key]

    unwatched_movies = {k: v for k, v in config['movies'].items() if not v['watched']}
    if not unwatched_movies:
        ctx.fail('You have no unwatched movies in your list. Try adding some!')
    total_weight = sum(iter_specific_key(unwatched_movies, 'vote_average'))
    selection = random.uniform(0, total_weight)
    for k, v in unwatched_movies.items():
        selection -= v['vote_average']
        if selection <= 0:
            break

    click.echo('Your movie is {} ({})'.format(v['title'], v['year']))
    v['watched'] = True
    config.save()


@cli.command()
@pass_config
def list_movies(config):
    """Show your list of movies."""
    def print_table(rows, sort_col):
        header = rows.pop(0)
        rows = sorted(rows, key=lambda x: x[sort_col])
        rows.insert(0, header)

        lens = []
        for col in range(len(rows[0])):
            lens.append(len(str(max([row[col] for row in rows], key=lambda x: len(str(x))))))
        pattern = '{{:>{0}}}'.format(lens[0])
        for col in range(1, len(rows[0])):
            pattern += ' | {{:<{0}}}'.format(lens[col])
        formatted = []
        for row in rows:
            formatted.append(pattern.format(*row))

        formatted.insert(1, '-+-'.join(['-'*n for n in lens]))

        for row in formatted:
            click.echo(row.rstrip())

    divided_movies = [
        ('Unwatched Movies', {k: v for k, v in config['movies'].items() if not v['watched']}),
        ('Watched Movies',  {k: v for k, v in config['movies'].items() if v['watched']})
    ]

    for movie_division in divided_movies:
        if not movie_division[1]:
            continue
        click.echo(movie_division[0])
        rows = [['TMDB ID', 'Title']]
        for movie in movie_division[1].values():
            rows.append([movie['tmdb_id'], '{} ({})'.format(movie['title'], movie['year'])])
        print_table(rows, 0)
        click.echo()


@cli.command()
@click.argument('file', type=click.File('r'))
@pass_config
@click.pass_context
def import_from_file(ctx, config, file):
    """Imports movies from FILE containing valid identifiers, one per line. Invalid entries or those already present in your list are ignored."""
    content = file.readlines()
    content = [line.strip() for line in content]
    for line in content:
        click.echo('Adding "{}".'.format(line))
        try:
            new_movie = Movie(line)
        except MovieCreationError as e:
            click.echo('WARN: {}'.format(e))
        if new_movie not in config['movies'].values():
            config['movies'][str(new_movie['tmdb_id'])] = new_movie
    config.save()


@cli.command()
@click.argument('identifier')
@pass_config
@click.pass_context
def unwatch(ctx, config, identifier):
    """Mark movie indicated by IDENTIFIER as unwatched. IDENTIFIER can be a TMDB ID, an IMDB ID, or a partial or full title."""
    try:
        new_movie = Movie(identifier)
    except MovieCreationError as e:
        ctx.fail(e)
    if new_movie not in config['movies'].values():
        ctx.fail('The movie "{} ({})" is not on your list.'.format(new_movie['title'], new_movie['year']))
    config['movies'][str(new_movie['tmdb_id'])]['watched'] = False
    click.echo('"{} ({})" marked as unwatched.'.format(new_movie['title'], new_movie['year']))
    config.save()


@cli.command()
@click.argument('identifier')
@pass_config
@click.pass_context
def watch(ctx, config, identifier):
    """Mark movie indicated by IDENTIFIER as watched. IDENTIFIER can be a TMDB ID, an IMDB ID, or a partial or full title."""
    try:
        new_movie = Movie(identifier)
    except MovieCreationError as e:
        ctx.fail(e)
    if new_movie not in config['movies'].values():
        ctx.fail('The movie "{} ({})" is not on your list.'.format(new_movie['title'], new_movie['year']))
    config['movies'][str(new_movie['tmdb_id'])]['watched'] = True
    click.echo('"{} ({})" marked as watched.'.format(new_movie['title'], new_movie['year']))
    config.save()


if __name__ == '__main__':
    cli()
