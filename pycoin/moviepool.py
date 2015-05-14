#!/usr/bin/env python3

import tmdbsimple as tmdb

class MoviePool():
    def __init__(self):
        self.pool = {}
        
    def add_movie(self, identifier):
        movie = tmdb.Movies(identifier)
        response = movie.info()
        
        self.pool[identifier] = {
            'title': movie.title,
            'vote_average': movie.vote_average,
            'watched': False
        }
