#!/usr/bin/env python3

import tmdbsimple as tmdb
from . import private_constants

tmdb.API_KEY = private_constants.API_KEY

class Movie():
    def __init__(self, identifier):
        tmdb_id = self._tmdb_id_from_identifier(identifier)
        
        movie = tmdb.Movies(tmdb_id)
        response = movie.info()
        
        self.tmdb_id = tmdb_id
        self.title = movie.title
        self.vote_average = movie.vote_average
        self.watched = False
        
    def __repr__(self):
        return str(self.tmdb_id)
        
    def __str__(self):
        return '({}) {} - Vote Average {} {}Watched'.format(self.tmdb_id, self.title, self.vote_average, '' if self.watched else 'Not ')
        
    def __hash__(self):
        return hash(self.__repr__())
        
    def __eq__(self, other):
        return isinstance(other, Movie) and self.__hash__() == other.__hash__()
        
    def __ne__(self, other):
        return not self.__eq__(other)
        
    def _tmdb_id_from_identifier(self, identifier):
        if identifier[:2] == 'tt':  # we have an IMDb id
            tmdb_id = tmdb.Find(identifier).info(external_source = 'imdb_id')['movie_results'][0]['id']
        elif not identifier.isdigit(): # we must have a title, since tmdb id's are ints
            tmdb_id = tmdb.Search().movie(query = identifier)['results'][0]['id']
        else:
            tmdb_id = int(identifier)
        
        return tmdb_id
        
    def mark_watched(self):
        self.watched = True
