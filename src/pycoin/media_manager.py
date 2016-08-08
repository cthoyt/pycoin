from abc import ABCMeta, abstractmethod
import datetime
import json
import random

import py
import tmdbsimple as tmdb


class MediaManager(dict, metaclass=ABCMeta):
    def __init__(self, media_type, *args, config_path=None, **kwargs):
        self.media_type = media_type
        self.config_path = config_path

        if config_path:
            config_path = py.path.local(config_path)
            with config_path.ensure().open('r') as f:
                try:
                    config = json.load(f)
                except ValueError:
                    config = {}
        else:
            config = {}

        super().__init__(*args, **kwargs)
        self[media_type] = config.get(media_type, {})
        self['{}_config'.format(media_type)] = config.get('{}_config'.format(media_type), {})

    def write_config(self):
        config_path = py.path.local(self.config_path)
        with config_path.ensure().open('w') as f:
            json.dump(self, f, indent=2, sort_keys=True)

    @staticmethod
    def _iter_specific_key(dictionary, key):
        for value in dictionary.values():
            yield value.get(key)

    @abstractmethod
    def add(self, identifier, data):
        if identifier not in self:
            self[self.media_type][identifier] = data
        else:
            raise KeyError('{} already in list'.format(identifier), identifier, data)

    def delete(self, identifier):
        self[self.media_type].pop(identifier)

    def flip(self):
        queued = {k: v for k, v in self[self.media_type].items() if not v['completed']}
        if not queued:
            raise ValueError('No queued media in list')

        total_weights = sum(self._iter_specific_key(queued, 'weight'))
        selection = random.uniform(0, total_weights)

        item = None
        for item in queued.values():
            selection -= item['weight']
            if selection <= 0:
                break

        item['completed'] = True
        return item

    def complete(self, identifier):
        self[self.media_type][identifier]['completed'] = True

    def uncomplete(self, identifier):
        self[self.media_type][identifier]['completed'] = False


class MovieManager(MediaManager):
    def __init__(self, *args, config_path=None, **kwargs):
        super().__init__('movies', *args, config_path=config_path, **kwargs)
        tmdb.API_KEY = self['{}_config'.format(self.media_type)].get('api_key', None)

    def add(self, identifier):
        tmdb_id = self._tmdb_id_from_identifier(identifier)
        if not tmdb_id:
            raise ValueError('Unable to locate movie from identifier `{}`'.format(identifier))

        movie = tmdb.Movies(tmdb_id)
        try:
            movie.info()
        except IOError as e:
            if getattr(getattr(e, 'response', None), 'status_code', None) == 404:
                raise ValueError('An invalid TMDB ID was used `{}`'.format(tmdb_id))

        data = {
            'tmdb_id': tmdb_id,
            'title': movie.title,
            'weight': movie.vote_average,
            'year': datetime.datetime.strptime(movie.release_date, '%Y-%m-%d').year,
            'completed': False
        }
        try:
            super().add(identifier, data)
        except KeyError as e:
            raise KeyError('The movie "{} ({})" is already on your list'.format(e.args[2]['title'], e.args[2]['year']))
        return data

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
