#!/usr/bin/env python3

import pytest

from pycoin import moviepool as mp

@pytest.fixture
def testPool():
    return mp.MoviePool()
    
def test_creation_of_MoviePool(testPool):
    assert isinstance(testPool, mp.MoviePool)
    
def test_new_MoviePool_has_empty_pool(testPool):
    assert testPool.pool == {}
    
def test_add_movie_by_tmdb_id_to_MoviePool(testPool):
    testPool.add_movie(603) # tmdb id for 'The Matrix'
    assert testPool.pool == {
        603: {
            'title': 'The Matrix',
            'vote_average': 7.6,
            'watched': False
        }
    }
    
