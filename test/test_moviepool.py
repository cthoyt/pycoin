#!/usr/bin/env python3

import pytest

from pycoin import moviepool as mp

@pytest.fixture
def testPool():
    return mp.MoviePool()
    
@pytest.fixture
def fake_tmdbsimple(monkeypatch):
    monkeypatch.setattr('tmdbsimple.Movies', FakeTmdbsimpleMovies)

class FakeTmdbsimpleMovies():
    def __init__(self, identifier):
        self.title = 'Example Movie'
        self.vote_average = 10.0
    
    def info(self):
        pass
    
    
    
def test_creation_of_MoviePool(testPool):
    assert isinstance(testPool, mp.MoviePool)
    
def test_new_MoviePool_has_empty_pool(testPool):
    assert testPool.pool == {}
    
def test_add_movie_by_tmdb_id_to_MoviePool(testPool, fake_tmdbsimple):
    testPool.add_movie(1)
    assert testPool.pool == {
        1: {
            'title': 'Example Movie',
            'vote_average': 10.0,
            'watched': False
        }
    }
    
