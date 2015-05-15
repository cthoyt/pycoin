#!/usr/bin/env python3

class FakeTmdbsimple():
    def __init__(self):
        pass
    
    class Movies():
        _example_movie_data = {
            1: {
                'title': 'Example Movie',
                'vote_average': 10.0
            }
        }
    
        def __init__(self, tmdb_id):
            self.tmdb_id = tmdb_id
    
        def info(self):
            self.title = self._example_movie_data[self.tmdb_id]['title']
            self.vote_average = self._example_movie_data[self.tmdb_id]['vote_average']
            
    class Find():
        def __init__(self, identifier):
            pass
        
        def info(self, external_source):
            return {
                'movie_results': [
                    {'id': 1}
                ]
            }
            
    class Search():
        def __init__(self):
            pass
        
        def movie(self, query):
            return {
                'results': [
                    {
                        'id': 1
                    }
                ]
            }
