from django.shortcuts import render
from django.http import HttpResponse

sample_movies = [
    {
        'title': 'Movie 1',
        'year': 1999,
        'genre': 'Action',
        'description': 'A movie',
        'rating': 2.0,
        'mature': True
    },
{
        'title': 'Movie 2',
        'year': 2015,
        'genre': 'Comedy',
        'description': 'Another movie',
        'rating': 2.2,
        'mature': False
    }
]

def inventory(request):
    context = {
        'movies': sample_movies
    }
    return render(request, 'home.html', context)