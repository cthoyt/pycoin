#!/usr/bin/env python3

import pytest

from pycoin import movie
from fake_tmdbsimple import FakeTmdbsimple

@pytest.fixture
def testMovie(mocker):
    mocker.patch.dict('sys.modules', {'tmdbsimple': FakeTmdbsimple()})
    return movie.Movie('1')
    
# @pytest.fixture
# def testMovie(fake_tmdbsimple):
#     return movie.Movie('1')
#
# @pytest.fixture
# def fake_tmdbsimple(monkeypatch):
#     monkeypatch.setattr('tmdbsimple.Movies', FakeTmdbsimpleMovies)
#     monkeypatch.setattr('tmdbsimple.Find', FakeTmdbsimpleFind)
#     monkeypatch.setattr('tmdbsimple.Search', FakeTmdbsimpleSearch)
#
# class FakeTmdbsimpleMovies():
#     _example_movie_data = {
#         1: {
#             'title': 'Example Movie',
#             'vote_average': 10.0
#         }
#     }
#
#     def __init__(self, tmdb_id):
#         self.tmdb_id = tmdb_id
#
#     def info(self):
#         self.title = self._example_movie_data[self.tmdb_id]['title']
#         self.vote_average = self._example_movie_data[self.tmdb_id]['vote_average']
#
# class FakeTmdbsimpleFind():
#     def __init__(self, identifier):
#         pass
#
#     def info(self, external_source):
#         return {
#             'movie_results': [
#                 {'id': 1}
#             ]
#         }
#
# class FakeTmdbsimpleSearch():
#     def __init__(self):
#         pass
#
#     def movie(self, query):
#         return {
#             'results': [
#                 {
#                     'id': 1
#                 }
#             ]
#         }

def test_creation_of_Movie(testMovie):
    assert isinstance(testMovie, movie.Movie)

def test_properties_of_Movie(testMovie):
    assert testMovie.tmdb_id == 1
    assert testMovie.title == 'Example Movie'
    assert testMovie.vote_average == 10
    assert testMovie.watched == False
    
def test_mark_Movie_as_watched(testMovie):
    testMovie.mark_watched()
    assert testMovie.watched == True
    
