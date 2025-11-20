from django.urls import include, path

from .views import *

urlpatterns = [
    path('', HomeView, name = 'home'),
    path('contact/', ContactView, name = 'contact'),
    path('contact/check/', ContactCheck, name = 'contact_check'),
    path('writeups/', WriteupView, name = 'writeups'),
    # path('dft/', DFTView, name='dft'), # sucks atm
    path('elliptic/', ECCView, name = 'ecc'),
    path('elliptic/eccencode/', ECCEncode, name = 'ecc_encode'),
    path('minimax/', MinimaxView, name = 'minimax'),
    path('minimax/calculate/', MinimaxCalculate, name = 'minimax_calculate'),
    path('mazes/', MazeView, name = 'mazes'),
    path('mazes/generate/', MazeGenerate, name = 'maze_generate'),
    path('mazes/solve/', MazeSolve, name = 'maze_solve'),
    path('tetris/', TetrisView, name = 'tetris'), 
    path('mnist/', MNISTView, name = 'mnist'), 
    path('mnist/random/', MNISTRandomImage, name = 'mnist_random'),
    path('mnist/predict/', MNISTPredict, name='mnist_predict')
]
