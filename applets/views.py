import time

import numpy as np


from json import loads
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from digitalresume.settings import EMAIL, PHONE
from .ecc import ECC, ascii_encode
from .mazes import Maze, Solver
from .minimax import Board
from .models import Writeup




# Create your views here.

def HomeView(request):
    return render(request, 'applets/home.html', {

    })

def ContactView(request):
    return render(request, 'applets/contact.html', {

    })

def ContactCheck(request):
    try:
        msg = request.POST['msg']
        if msg.lower() in ['y', 'ya', 'yes', 'a sensible response', 'a sensible response to this question']:
            return JsonResponse({'email': EMAIL})
    except:
        return HttpResponse(status=418)
    return HttpResponse(status=418)

def WriteupView(request):
    return render(request, 'applets/writeups.html', {
        'writeups': Writeup.objects.all().order_by('order')
    })

# def DFTView(request):
#     return render(request, 'applets/dft.html', {
#         # this sucks right now so its getting hidden. need to be able to slow it down?
#     })

def MinimaxView(request):
    return render(request, 'applets/minimax.html', {

    })

def MinimaxCalculate(request):
    b = Board(board=request.POST.getlist('board[]'))
    if b.gameState != 'Game is in progress.':
        return JsonResponse({'result': b.gameState})
    t0 = time.time()
    moveinfo = Board.minimax(b.board, Board.botMark, -100, 100)
    t1 = time.time()
    nodeCount = Board.nodeCount
    nodes = (nodeCount/(1000*(t1-t0))) if t1-t0 != 0 else 0
    b.makeBotMove(moveinfo['move'])
    stats = 'Bot has selected move {} with score {} - {} nodes calculated in {:.2f} seconds ({:.2f} kn/s).'.format(moveinfo['move'], moveinfo['score'], nodeCount, t1-t0, nodes)
    Board.nodeCount = 0

    if b.checkWin('o'): # bot win
        return JsonResponse({'result': b.gameState, 'stats': stats, 'move': moveinfo['move']})
    
    return JsonResponse({
        'move': moveinfo['move'],
        'stats': stats,
        'result': b.gameState
    })

def ECCView(request):
    return render(request, 'applets/elliptic.html', {

    })

def ECCEncode(request):
    ecc = ECC(408616349, -1, 1, N=408594286, kf=1000, bound=3) # precomputed since sometimes takes a while?

    if request.method == 'POST':
        msg = request.POST['msg']
        s = ascii_encode(msg)
        blocks = ecc.ascii_blocks(s)
        encoded = ecc.encode(msg)

    cpub, cpri = ecc.generate_key_pair() # sender public + private key
    dpub, dpri = ecc.generate_key_pair() # receiver public + private key

    step1_points = ecc.encrypt(encoded, cpub) # cP_m
    step2_points = ecc.encrypt(step1_points, dpub) #dcP_m
    step3_points = ecc.encrypt(step2_points, cpri) #c'dcP_m = dP_m
    step4_points = ecc.encrypt(step3_points, dpri) #d'dP_m = P_m
    decoded = ecc.decode(step4_points)



    return JsonResponse({
        's': s,
        'bs': blocks,
        'enc': encoded, 
        'cpub': cpub,
        'cpri': cpri,
        'dpub': dpub,
        'dpri': dpri,
        'step1_points': step1_points,
        'step2_points': step2_points,
        'step3_points': step3_points,
        'step4_points': step4_points,
        'decoded': decoded
    })


def MazeView(request):
    return render(request, 'applets/mazes.html', {
    })


def MazeGenerate(request):
    height, width = (31, 31)
    m = Maze(dimensions=(height,width))
    return JsonResponse({
        'maze': m.maze,
        'padded': m.padded.tolist()
        })

def MazeSolve(request):
    try:
        params = loads(request.body)
        m = Maze(maze=params['maze'])
        s = Solver(m)
        frames = s.generateFrames(method=params['method'])
        return JsonResponse({'frames': frames})
    except Exception as e:
        print(e)
        return HttpResponse(status=500)

