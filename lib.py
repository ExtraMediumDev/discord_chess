import sys
import random
import discord
import traceback
import os
from discord.ext import tasks, commands
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from copy import deepcopy


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=['c$'],intents=intents,help_command=None)

main_folder = os.getcwd().split('\\')[-1]
main_path = os.getcwd()

board_size = (1000,1000)

#background images
wb = Image.open('Images/WHITE_BOARD.png','r').resize(board_size)
bb = Image.open('Images/BLACK_BOARD.png','r').resize(board_size)
white_board = Image.open('Images/SURFACE.png','r').convert('RGB').resize((1000,1200))
black_board = Image.open('Images/SURFACE.png','r').convert('RGB').resize((1000,1200))
white_board.paste(wb, (0,200))
black_board.paste(bb, (0,200))

#pieces
piece_size = (125,125)

#white
w_pawn = Image.open('Images/WHITE_PAWN.png','r').resize(piece_size)
w_rook = Image.open('Images/WHITE_ROOK.png','r').resize(piece_size)
w_knight = Image.open('Images/WHITE_KNIGHT.png','r').resize(piece_size)
w_bishop = Image.open('Images/WHITE_BISHOP.png','r').resize(piece_size)
w_queen = Image.open('Images/WHITE_QUEEN.png','r').resize(piece_size)
w_king = Image.open('Images/WHITE_KING.png','r').resize(piece_size)

#black
b_pawn = Image.open('Images/BLACK_PAWN.png','r').resize(piece_size)
b_rook = Image.open('Images/BLACK_ROOK.png','r').resize(piece_size)
b_knight = Image.open('Images/BLACK_KNIGHT.png','r').resize(piece_size)
b_bishop = Image.open('Images/BLACK_BISHOP.png','r').resize(piece_size)
b_queen = Image.open('Images/BLACK_QUEEN.png','r').resize(piece_size)
b_king = Image.open('Images/BLACK_KING.png','r').resize(piece_size)

#piece reference
standard_ref = {'w_pawn':w_pawn,
    'w_rook':w_rook,
    'w_knight':w_knight,
    'w_bishop':w_bishop,
    'w_queen':w_queen,
    'w_king':w_king,
    'b_pawn':b_pawn,
    'b_rook':b_rook,
    'b_knight':b_knight,
    'b_bishop':b_bishop,
    'b_queen':b_queen,
    'b_king':b_king,
    'none':'none'
}

#outgoing seeks {message id: member id}, {member id: message id}, and {member id : channel id, message id}
seeks1 = {}
seeks2 = {}
seeks3 = {}
#ongoing games {game_id : game_array}
games = {}
#color {player id : 'w' or 'b'}
color = {}
#move history {game_id : move history array}
move_history = {}
#piece history {game_id : piece array}
piece_history = {}
#playing players {member id : game_id}
playing = {}
#pairs {player id : opponent id}
pairs = {}
#initial move pieces {game_id : pieces array}
first_moves = {}
#location of kings {game_id : {'w' : location, 'b' : location}}
kings = {}
#pieces {game_id : pieces.standard or something}
board_pieces = {}

letters = {'a','b','c','d','e','f','g','h'}
numbers = {'1','2','3','4','5','6','7','8'}

class boards():
    standard = [
        ['w_rook','w_knight','w_bishop','w_king','w_queen','w_bishop','w_knight','w_rook'],
        ['w_pawn','w_pawn','w_pawn','w_pawn','w_pawn','w_pawn','w_pawn','w_pawn'],
        ['none','none','none','none','none','none','none','none'],
        ['none','none','none','none','none','none','none','none'],
        ['none','none','none','none','none','none','none','none'],
        ['none','none','none','none','none','none','none','none'],
        ['b_pawn','b_pawn','b_pawn','b_pawn','b_pawn','b_pawn','b_pawn','b_pawn'],
        ['b_rook','b_knight','b_bishop','b_king','b_queen','b_bishop','b_knight','b_rook']
    ]

class moves():
    standard = {
        'king':[(1,1),(1,-1),(-1,1),(-1,-1),(0,1),(0,-1),(1,0),(-1,0)],
        'queen':[(1,1),(1,-1),(-1,1),(-1,-1),(0,1),(0,-1),(1,0),(-1,0)],
        'rook':[(1,0),(-1,0),(0,1),(0,-1)],
        'bishop':[(1,1),(1,-1),(-1,1),(-1,-1)],
        'knight':[(1,2),(2,1),(-1,2),(2,-1),(-1,-2),(-2,-1),(-1,2),(-2,1)],
        'pawn':[(0,1),(1,1),(-1,1)]
    }

class pieces():
    standard = {
        'w':{
            (0,0):'w_rook',
            (1,0):'w_knight',
            (2,0):'w_bishop',
            (3,0):'w_king',
            (4,0):'w_queen',
            (5,0):'w_bishop',
            (6,0):'w_knight',
            (7,0):'w_rook',
            (0,1):'w_pawn',
            (1,1):'w_pawn',
            (2,1):'w_pawn',
            (3,1):'w_pawn',
            (4,1):'w_pawn',
            (5,1):'w_pawn',
            (6,1):'w_pawn',
            (7,1):'w_pawn',
        },
        'b':{
            (0,7):'b_rook',
            (1,7):'b_knight',
            (2,7):'b_bishop',
            (3,7):'b_king',
            (4,7):'b_queen',
            (5,7):'b_bishop',
            (6,7):'b_knight',
            (7,7):'b_rook',
            (0,6):'b_pawn',
            (1,6):'b_pawn',
            (2,6):'b_pawn',
            (3,6):'b_pawn',
            (4,6):'b_pawn',
            (5,6):'b_pawn',
            (6,6):'b_pawn',
            (7,6):'b_pawn',
        }
    }

#first move specials (like castle or pawn moves)
class initials():
    standard = {
        (0,0):'w_rook',
        (3,0):'w_king',
        (7,0):'w_rook',
        (0,1):'w_pawn',
        (1,1):'w_pawn',
        (2,1):'w_pawn',
        (3,1):'w_pawn',
        (4,1):'w_pawn',
        (5,1):'w_pawn',
        (6,1):'w_pawn',
        (7,1):'w_pawn',
        (0,7):'b_rook',
        (3,7):'b_king',
        (7,7):'b_rook',
        (0,6):'b_pawn',
        (1,6):'b_pawn',
        (2,6):'b_pawn',
        (3,6):'b_pawn',
        (4,6):'b_pawn',
        (5,6):'b_pawn',
        (6,6):'b_pawn',
        (7,6):'b_pawn'
    }

#List of files to load.
files = open('file_names.txt').read().split('\n')
def setup():
    pass