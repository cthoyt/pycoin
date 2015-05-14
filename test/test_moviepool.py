#!/usr/bin/env python3

import pytest

from pycoin import moviepool as mp
from pycoin.moviepool import MoviePoolDuplicateMovieError

@pytest.fixture
def testPool():
    return mp.MoviePool()
    
@pytest.fixture
def fake_tmdbsimple(monkeypatch):
    monkeypatch.setattr('tmdbsimple.Movies', FakeTmdbsimpleMovies)
    monkeypatch.setattr('tmdbsimple.Find', FakeTmdbsimpleFind)
    monkeypatch.setattr('tmdbsimple.Search', FakeTmdbsimpleSearch)

class FakeTmdbsimpleMovies():
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
    
class FakeTmdbsimpleFind():
    def __init__(self, identifier):
        pass
        
    def info(self, external_source):
        return {
            'movie_results': [
                {'id': 1}
            ]
        }
        
class FakeTmdbsimpleSearch():
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
    
def test_creation_of_MoviePool(testPool):
    assert isinstance(testPool, mp.MoviePool)
    
def test_new_MoviePool_has_empty_pool(testPool):
    assert testPool.pool == {}
    
def test_add_movie_by_tmdb_id_to_MoviePool(testPool, fake_tmdbsimple):
    testPool.add_movie('1')
    assert testPool.pool == {
        1: {
            'title': 'Example Movie',
            'vote_average': 10.0,
            'watched': False
        }
    }
    
def test_add_movie_by_imdb_id_to_MoviePool(testPool, fake_tmdbsimple):
    testPool.add_movie('tt1')
    assert testPool.pool == {
        1: {
            'title': 'Example Movie',
            'vote_average': 10.0,
            'watched': False
        }
    }
    
def test_add_movie_by_title_to_MoviePool(testPool, fake_tmdbsimple):
    testPool.add_movie('Example Movie')
    assert testPool.pool == {
        1: {
            'title': 'Example Movie',
            'vote_average': 10.0,
            'watched': False
        }
    }
    
def test_cannot_add_movie_twice_to_MoviePool(testPool, fake_tmdbsimple):
    testPool.add_movie('1')
    with pytest.raises(MoviePoolDuplicateMovieError):
        testPool.add_movie('1')
    
