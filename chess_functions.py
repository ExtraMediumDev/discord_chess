from lib import standard_ref, white_board, black_board, Image, moves

inbounds = lambda x, y : 0 <= x < 8 and 0 <= y < 8 

#renders both white and black boards and returns a tuple of image objects
def render(array, color):
    if color == 'w': board = white_board.copy()
    if color == 'b': board = black_board.copy()

    for y in range(8):
        for x in range(8):
            if color == 'w': piece = standard_ref[array[-(y+1)][-(x+1)]]
            if color == 'b': piece = standard_ref[array[y][x]]
            if piece != 'none': board.paste(piece,(x*125,y*125 + 200),piece)

    return board

num = {'a':0,'b':1,'c':2,'d':3,'e':4,'f':5,'g':6,'h':7}
#returns (x,y) depending on notation
def coords(ntn):
    x,y = 7 - num[ntn[0]], int(ntn[1]) - 1
    return (x,y)



#1. Find same color pieces attacking piece that is about to move. Moves only need to be recalculted for those pieces
#2. Find all possible moves for the piece that is about to move and the recalculated pieces
#3. If no pins and the move is valid, make the move, then check if the king is in danger. 
# If king is in danger, revoke move, else you keep the move.
#4. Check opponent king. If danger, check if attacking piece is killable, 
# otherwise check if the king can runaway, then check if the king is blockable
#5. If king not in danger and king not checkmated, check move list for stalemate
#Move repitition draw will be calculated throug move history






#checks a square if an opposing pieces are attacking it. Returns True or False.
def check_square(board, x,y, check_for):
    dirs = [(1,1),(-1,1),(-1,-1),(1,-1),(0,1),(1,0),(0,-1),(-1,0),(1,2),(2,1),(-1,2),(-2,1),(-1,-2),(-2,-1),(1,-2),(2,-1)]
    attacked = False
    attackers = []
    pins = []
    for i in range(8):
        #offset x and y
        off_x, off_y = dirs[i]
        allies, pinned = 0, None
        
        l_attacked = False
        for j in range(1,8):
            new_x = x + off_x * j
            new_y = y + off_y * j

            if not inbounds(new_x,new_y): break

            piece = board[new_y][new_x]
            if piece != 'none':
                color = piece[0]
                piece_type = piece[2:]
                if check_for == color:
                    if piece_type == 'queen':
                        attackers.append((new_x,new_y))
                        l_attacked = True
                    if i < 4 and piece_type == 'bishop':
                        attackers.append((new_x,new_y))
                        l_attacked = True
                    if i > 3 and piece_type == 'rook':
                        attackers.append((new_x,new_y))
                        l_attacked = True
                    if j == 1 and piece_type == 'king':
                        attackers.append((new_x,new_y))
                        l_attacked = True
                    if j == 1 and i < 2 and piece_type == 'pawn' and color == 'w':
                        attackers.append((new_x,new_y))
                        l_attacked = True
                    if j == 1 and 1 < i < 4 and piece_type == 'pawn' and color == 'b':
                        attackers.append((new_x,new_y))
                        l_attacked = True
                    
                    if l_attacked == True and allies == 1: pins.append(pinned)
                    if l_attacked == True and allies > 0:
                      l_attacked = False
                      if len(attackers) > 0: attackers.pop()

                    break

                elif check_for != color and color != 'n' and allies == 0: allies, pinned = allies + 1, (new_x,new_y)

        if l_attacked: attacked = True



    for k in range(8):
        #offset x and y
        off_x, off_y = dirs[i+8]
        new_x = x + off_x
        new_y = y + off_y

        if inbounds(new_x,new_y):
            piece = board[new_y][new_x]
            if piece != 'none':
                color = piece[0]
                piece_type = piece[2:]
                if color == check_for and piece_type == 'knight':
                    attackers.append((new_x,new_y))
                    attacked = True

    return attacked, attackers, pins

#check if file or diagonal is empty exluding (between) the marked squares
def empty(board,x1,y1,x2,y2):
    #assuming the path is diagonal with 1:1 ratio or horizontal/vertical
    k = True
    x_off, y_off, xc, yc = x2 - x1, y2 - y1, int((x2-x1)/(abs(x2-x1) or not abs(x2-x1))), int((y2-y1)/(abs(y2-y1) or not abs(y2-y1)))
    if x2-x1 == 0: off_x, off_y, l = 0, yc, abs(y_off)-1
    elif y2-y1 == 0: off_x, off_y, l = xc, 0, abs(x_off)-1
    else: off_x, off_y, l = xc, yc, abs(x_off)-1
    for i in range(l):
        new_x, new_y = x1 + off_x*(i+1), y1 + off_y*(i+1)
        if not inbounds(new_x,new_y): break
        piece = board[new_y][new_x]
        if piece != 'none':
            k = False
            break
    return k

    

#checks if piece move corresponds to the moves a piece can do
def type_check(board, name, initials, kings, x1, y1, x2, y2):
    t, k, x_off, y_off, past_square, future_square = name[2:], False, x2 - x1, y2 - y1, board[y1][x1], board[y2][x2]
    castle = False
    new_r = None
    if past_square[0] == 'w': opposing = 'b'
    if past_square[0] == 'b': opposing = 'w'

    if t == 'bishop':
        if x2-x1 != 0:
            if abs((y2-y1)/(x2-x1)) == 1:
                if future_square[0] != name[0]:
                    if empty(board,x1,y1,x2,y2):
                        k = True

    if t == 'queen':
        if future_square[0] != name[0]:
            if x_off == 0 or y_off == 0:
                if empty(board,x1,y1,x2,y2):
                    k = True
            elif abs((y2-y1)/(x2-x1)) == 1:
                if empty(board,x1,y1,x2,y2):
                    k = True

    if t == 'rook':
        if x_off == 0 or y_off == 0: 
            if future_square[0] != name[0]:
                if empty(board,x1,y1,x2,y2):
                    k = True

    if t == 'king':
        if abs(x_off) > 1 and y_off == 0 and (x1,y1) in initials:
            if initials[(x1,y1)] == name:
                for i in range(4):
                    off_c = int(x_off/abs(x_off))
                    new_x = x1 + off_c * (i + 1)
                    if not(inbounds(new_x,y1)): break

                    piece = board[y1][new_x]
                    #check if empty squares are attacked
                    if piece == 'none':
                      if check_square(board, new_x, y1, opposing)[0]: break
    
                    if name[0] == piece[0] and (new_x,y1) in initials and piece[2:] == 'rook':
                        if empty(board, x1,y1,new_x,y2):
                            if name[0] == 'w':
                                del initials[(0,0)]
                                del initials[(3,0)]
                                del initials[(7,0)]
                            elif name[0] == 'b':
                                del initials[(0,7)]
                                del initials[(3,7)]
                                del initials[(7,7)]
                            k = True
                            x2 = x1 + off_c * 2
                            board[y1][new_x] = 'none'
                            board[y1][x1 + off_c] = piece
                            new_r = ((new_x,y1),(x1+off_c,y1))

                            kings[name[0]] = (x2,y2)
                            castle = True
                            break  
        else:
            if (abs(x_off) == 1 or abs(y_off) == 1) and future_square[0] != name[0]:
                kings[name[0]] = (x2,y2)
                k = True

    if t == 'knight':
        if (abs(x_off),abs(y_off)) == (1,2) or (abs(x_off),abs(y_off)) == (2,1):
            if future_square[0] != name[0]: k = True

    if t == 'pawn':
        if abs(y_off) == 2:
            if (x1,y1) in initials:
                if initials[(x1,y1)] == name:
                    if name[0] == 'w':
                        if y_off == 2 and x_off == 0 and future_square == 'none': 
                            k = True
                            del initials[(x1,y1)]
                    if name[0] == 'b':
                        if y_off == -2 and x_off == 0 and future_square == 'none': 
                            k = True
                            del initials[(x1,y1)]
        else:
            if name[0] == 'w':
                if y_off == 1 and x_off == 0 and future_square == 'none': k = True
                if y_off == 1 and abs(x_off) == 1 and future_square[0] == 'b': k = True
            if name[0] == 'b':
                if y_off == -1 and x_off == 0 and future_square == 'none': k = True
                if y_off == -1 and abs(x_off) == 1 and future_square[0] == 'w': k = True

    return k, x1, y1, x2, y2, board, kings, castle, new_r

#lambda function that checks whether two squares are on the same diagonal, file, or column
aligned = lambda x1, y1, x2, y2 : x1 == x2 or y1 == y2 or abs((y2-y1)/(x2-x1 or not x2-x1)) == 1
#lambda function that returns the vectors based on a starting square and an ending square
def slope(x1,y1,x2,y2):
  if x1-x2 == 0: return 'undefined'
  else: return (y2-y1)/(x2-x1)

#get legal moves of a piece
def get_moves(board, x, y, pinned, kings):
    piece = board[y][x]
    color, name = piece[0], piece[2:]
    possibles = []
    if piece != 'none':
      if color == 'w': opposing = 'b'
      elif color == 'b': opposing = 'w'
      ally_king, opposing_king = kings[color], kings[opposing]
      dirs = moves.standard[name]
    #if piece is pinned, get the direction in which the king is pinned in accordance to the piece

    if name == 'queen' or name == 'bishop' or name == 'knight':
      for direction in dirs:

        new_x, new_y = x, y
        off_x, off_y = direction
        #continues if not pinned.
        if not(pinned) or (pinned and slope(ally_king[0], ally_king[1], x, y) == slope(ally_king[0], ally_king[1], x + off_x, y + off_y)):

          for i in range(1,8):
            new_x, new_y = x + off_x * i, y + off_y * i

            if inbounds(new_x,new_y):
              square = board[new_y][new_x]

              #will stop checking if square is ally piece, and if its an enemy piece it will break but count the enemy piece position
              if square[0] == 'w': break
              elif square[0] == 'b':
                possibles.append((new_x,new_y))
                break
              

              possibles.append((new_x,new_y))

            else: break

    if name == 'king' or name == 'knight' or name == 'pawn':
      for direction in dirs:
        off_x, off_y = direction
        new_x, new_y = x+off_x, y+off_y
        if inbounds(new_x,new_y):
          square = board[new_y][new_x]

          if name == 'king':
            if not(check_square(board,x,y,opposing)[0]) and color != square[0]: possibles.append((new_x,new_y))

          elif not(pinned) or (pinned and slope(ally_king[0], ally_king[1], x, y) == slope(ally_king[0], ally_king[1], x + off_x, y + off_y)):
            if name == 'knight' and color != square[0]: possibles.append((new_x,new_y))
            
            if name == 'pawn':
              if color == 'w': off_y = 1
              elif color == 'b': off_y = -1
              
              new_y = y + off_y * direction[1]
              if inbounds(new_x,new_y):
                square = board[new_y][new_x]
                if direction == (0,1) and square == 'empty': possibles.append((new_x,new_y))
                elif square[0] != color and square[0] != 'empty': possibles.append((new_x,new_y))

    return possibles
        
        
          


#move validation
def validate(board, color, initials, kings, onboard, x1, y1, x2, y2):
    valid = False
    if inbounds(x1,y1) and inbounds(x2,y2):
        past = board[y1][x1]
        future = board[y2][x2]
        if past[0] == color:
            valid, x1, y1, x2, y2, board, kings, castle, new_r = type_check(board,past,initials,kings,x1,y1,x2,y2)

            if castle:
              onboard[color][new_r[1]] = onboard[color].pop(new_r[0])

            if valid:
                if color == 'w': opposing = 'b'
                elif color == 'b': opposing = 'w'

                board[y1][x1] = 'none'
                if past[2:] == 'pawn' and y2 == 0 or y2 == 7:
                  if color == 'w': board[y2][x2] = 'w_queen'
                  if color == 'b': board[y2][x2] = 'b_queen'
                else: board[y2][x2] = past

                danger, attackers, pins = check_square(board, kings[color][0], kings[color][1], opposing)
                
                
                if danger == True: valid = 'danger'
                if valid == True:
                    opp_king_x, opp_king_y =  kings[opposing]
                    potential_checkmate, attackers, pins = check_square(board, opp_king_x, opp_king_y, color)
                    
                    #check if opposing king has squares to escape to, if not, it will check for stalemate.
                    runaway = False
                    for dir in moves.standard['king']:
                      new_x,new_y = opp_king_x + dir[0], opp_king_y + dir[1]
                      if inbounds(new_x,new_y):
                        if not(check_square(board, new_x, new_y, color)[0]) and opposing != board[new_y][new_x][0]:
                          runaway = True

                    #generates legal moves
                    if runaway == False:
                      legal_moves = []
                      for piece in onboard[color]:
                        if piece in pins: pinned = True
                        else: pinned = False
                        legal_moves.extend(get_moves(board, piece[0], piece[1], pinned, kings))
                    
                    
                    print(potential_checkmate)
                    if potential_checkmate == True:
                        attack_x, attack_y = attackers[0][0], attackers[0][1]
                        if len(attackers) == 1: counterattack = not(check_square(board, attack_x, attack_y, color)[0]) and check_square(board, attack_x, attack_y, opposing)[0]
                        elif runaway == False: valid = 'checkmate'
                        else: counterattack = False

                        print(runaway, counterattack)
                        if runaway == False and counterattack == False:
                          piece = board[attack_y][attack_x]
                          name = piece[2:]
                          color = piece[0]
                          if name == 'knight' or name == 'pawn': valid = 'checkmate'
                          elif legal_moves != []:
                            blockable = False
                            if not(abs(attack_x - opp_king_x) <= 1 and abs(attack_y - opp_king_y) <= 1):
                              for move in legal_moves:
                                #if moves(x,y) between king(k1,k2) and attacker(a1,a2) then it is blockable and break the loop
                                within_x = abs(attack_x - opp_king_x) == abs(attack_x - move[0]) + abs(opp_king_x - move[0])
                                within_y = abs(attack_y - opp_king_y) == abs(attack_y - move[1]) + abs(opp_king_y - move[1])
                                if attack_x - opp_king_x == 0: slope1 = 'infinity'
                                else: slope1 = (attack_y - opp_king_y)/(attack_x - opp_king_x)
                                if attack_x - move[0] == 0: slope2 = 'infinity'
                                else: slope2 = (attack_y - move[1])/(attack_x - move[0])
                                if within_x and within_y and slope1 == slope2:
                                  blockable = True
                                  break
                      
                            if blockable == False: valid = 'checkmate'
                        
                    elif runaway == False and legal_moves == []: valid = 'stalemate'
                      

                              


                        

                       


    #revoke move if the move is not valid, else it will update the piece position.
    if valid != True and valid != 'checkmate' and valid != 'stalemate': board[y1][x1], board[y2][x2] = past, future
    else: onboard[color][(x2,y2)] = onboard[color].pop((x1,y1))

    return valid, x1, y1, x2, y2, kings