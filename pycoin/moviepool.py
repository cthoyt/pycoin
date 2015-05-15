#!/usr/bin/env python3

import tmdbsimple as tmdb
from . import private_constants

tmdb.API_KEY = private_constants.API_KEY

class MoviePoolDuplicateMovieError(Exception):
    pass

class MoviePool():
    def __init__(self):
        self.pool = {}
        
    def _tmdb_id_from_identifier(self, identifier):
        if identifier[:2] == 'tt':  # we have an IMDb id
            tmdb_id = tmdb.Find(identifier).info(external_source = 'imdb_id')['movie_results'][0]['id']
        elif not identifier.isdigit(): # we must have a title, since tmdb id's are ints
            tmdb_id = tmdb.Search().movie(query = identifier)['results'][0]['id']
        else:
            tmdb_id = int(identifier)
        
        return tmdb_id
        
    def add_movie(self, identifier):
        tmdb_id = self._tmdb_id_from_identifier(identifier)
        
        movie = tmdb.Movies(tmdb_id)
        response = movie.info()
        
        if tmdb_id not in self.pool:
            self.pool[tmdb_id] = {
                'title': movie.title,
                'vote_average': movie.vote_average,
                'watched': False
            }
        else:
            raise MoviePoolDuplicateMovieError
            
    def remove_movie(self, identifier):
        tmdb_id = self._tmdb_id_from_identifier(identifier)
        self.pool.pop(tmdb_id)
