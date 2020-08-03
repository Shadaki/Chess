board = [["r", "n", "b", "q", "k", "b", "n", "r"],
         ["p", "p", "p", "p", "p", "p", "p", "p"],
         [".", ".", ".", ".", ".", ".", ".", "."],
         [".", ".", ".", ".", ".", ".", ".", "."],
         [".", ".", ".", ".", ".", ".", ".", "."],
         [".", ".", ".", ".", ".", ".", ".", "."],
         ["P", "P", "P", "P", "P", "P", "P", "P"],
         ["R", "N", "B", "Q", "K", ".", ".", "R"]]
turn = "white"
end = False
possibleMoves = {"k": [["notTeammate", x, y] for x in range(-1, 2) for y in range(-1, 2) if [x, y] != [0, 0]] + [["canCastle/kingside", 0, 2], ["canCastle/queenside", 0, -2]],
                 "q": [["notTeammate+noPieceBetween", x, y] for x in range(-7, 8) for y in range(-7, 8) if (x == y or x == 0 or y == 0) and [x, y] != [0, 0]],
                 "r": [["notTeammate+noPieceBetween", x, y] for x in range(-7, 8) for y in range(-7, 8) if (x == 0 or y == 0) and [x, y] != [0, 0]],
                 "b": [["notTeammate+noPieceBetween", x, y] for x in range(-7, 8) for y in range(-7, 8) if abs(x) == abs(y) != 0],
                 "n": [["notTeammate", x, y] for [x, y] in [[-2, -1], [-2, 1], [-1, 2], [1, 2], [2, 1], [2, -1], [1, -2], [-1, -2]]],
                 "p": [["notTeammate+isWhite", -1, 0], ["notTeammate+noPieceBetween+onRow/2+isWhite", -2, 0], ["enemyOrEnPassant+isWhite", -1, -1], ["enemyOrEnPassant+isWhite", -1, 1],
                       ["notTeammate+isBlack", 1, 0], ["notTeammate+noPieceBetween+onRow/7+isBlack", 2, 0], ["enemyOrEnPassant+isBlack", 1, -1], ["enemyOrEnPassant+isBlack", 1, 1]]}

whiteKing = [7, 4]
blackKing = [0, 4]
whiteKingCheck, blackKingCheck = True, False
alreadyMoved = {"a1":False, "e1":False, "h1":False, "a8":False, "e8":False, "h8":False}

def chessToList(coord):
    x = 8 - int(coord[1])
    y = ord(coord[0]) - 97
    return x, y


def isCheck(xSquare, ySquare, color):
    global board, possibleMoves
    check = False
    piece = board[xSquare][ySquare]
    for x in range(8):
        for y in range(8):
            square = board[x][y]
            if (color == "black" and square.isupper()) or (color == "white" and square.islower()):
                if moveAllowed(x, y, xSquare, ySquare, square, piece):
                    return True
    return False

def notTeammate(_, __, xFinish, yFinish):
    global board, turn
    square = board[xFinish][yFinish]
    if (square.isupper() and turn == "white") or (square.islower() and turn == "black"):
        return False
    return True

def noPieceBetween(xStart, yStart, xFinish, yFinish):
    global board
    if xStart == xFinish:  # horizontal
        if yStart < yFinish and board[xStart][yStart + 1:yFinish] == ["."] * (yFinish - yStart - 1):
            return True
        elif yFinish < yStart and board[xStart][yFinish + 1:yStart] == ["."] * (yStart - yFinish - 1):
            return True
        return False
    
    elif yStart == yFinish:  # vertical
        if xStart < xFinish:
            squareStripe = range(xStart + 1, xFinish)
        else:
            squareStripe = range(xFinish + 1, xStart)
        for x in squareStripe:
            if board[x][yStart] != ".":
                return False
        return True
    
    else:
        xSmallest = min(xStart, xFinish)
        ySmallest = min(yStart, yFinish)
        for diff in range(1, abs(xStart - xFinish)):
            if board[xSmallest + diff][ySmallest + diff] != ".":
                return False
        return True

def enemyOrEnPassant(_, __, xFinish, yFinish):
    global board, turn
    square = board[xFinish][yFinish]
    if (square.isupper() and turn == "black") or (square.islower() and turn == "white"):
        return True
    return False

def onRow(xStart, yStart, _, __, nRow):
    if 8 - xStart == int(nRow):
        return True
    return False

def isWhite(xStart, yStart, _, __):
    global board
    if board[xStart][yStart].isupper():
        return True
    return False

def isBlack(xStart, yStart, _, __):
    global board
    if board[xStart][yStart].islower():
        return True
    return False

def canCastle(xStart, yStart, _, __, side):
    global board, alreadyMoved
    if board[xStart][yStart] == "K" and not alreadyMoved["e1"] and not isCheck(7,4,"white"):
        if side == "kingside" and not alreadyMoved["h1"] and not (isCheck(7,5,"white") or isCheck(7,6,"white")):
            return True
        if side == "queenside" and not alreadyMoved["a1"] and True not in [isCheck(7,y,"white") for y in range(1,4)]:
            return True
    elif board[xStart][yStart] == "k" and not alreadyMoved["e8"] and not isCheck(0,4,"black"):
        if side == "kingside" and not alreadyMoved["h8"] and not (isCheck(0,5,"white") or isCheck(0,6,"white")):
            return True
        if side == "queenside" and not alreadyMoved["a8"] and True not in [isCheck(0,y,"white") for y in range(1,4)]:
            return True
    return False


def moveAllowed(xStart, yStart, xFinish, yFinish, pieceMoving, pieceEaten):
    global turn, whiteKing, blackKing, whiteKingCheck, blackKingCheck
    if pieceMoving == "." or (pieceMoving.isupper() and turn == "black") or (pieceMoving.islower() and turn == "white"):
        return False
    for coord in [xStart, yStart, xFinish, yFinish]:
        if coord < 0 or coord > 7:
            return False
    
    xDiff, yDiff = xFinish - xStart, yFinish - yStart
    foundMove = False
    for moveTest in possibleMoves[pieceMoving.lower()]:
        if moveTest[1] == xDiff and moveTest[2] == yDiff:
            move = moveTest
            foundMove = True
            break
    if not foundMove:
        return False
    
    functionAnswers = []
    for condition in move[0].split("+"):
        condition = condition.split("/")
        toExec = "" + condition[0] + "(xStart,yStart,xFinish,yFinish"
        try:
            toExec += ",\"" + condition[1] + "\")"
        except:
            toExec += ")"
        functionAnswers.append(eval(toExec))
    if False in functionAnswers:
        return False
    
    if (isCheck(whiteKing[0], whiteKing[1], "white") and turn == "white") or \
    (isCheck(blackKing[0], blackKing[1], "black") and turn == "black"):
        return False
    
    makeMove(xStart, yStart, xFinish, yFinish, pieceMoving)
    if isCheck(whiteKing[0], whiteKing[1], "white") and turn == "black" or \
    isCheck(blackKing[0], blackKing[1], "black") and turn == "black":
        undoMove(xStart, yStart, xFinish, yFinish, pieceMoving, pieceEaten)
        return False
    undoMove(xStart, yStart, xFinish, yFinish, pieceMoving, pieceEaten)
    
    return True

def makeMove(xStart, yStart, xFinish, yFinish, pieceMoving):
    global whiteKing, blackKing
    board[xStart][yStart] = "."
    board[xFinish][yFinish] = pieceMoving
    if pieceMoving == "K":
        whiteKing = [xFinish, yFinish]
    elif pieceMoving == "k":
        blackKing = [xFinish, yFinish]
    if abs(yStart - yFinish) == 2 and pieceMoving.lower() == "k":
        if [xFinish, yFinish] == [7, 2]: makeMove(7, 0, 7, 3, "R")
        elif [xFinish, yFinish] == [7, 6]: makeMove(7, 7, 7, 5, "R")
        elif [xFinish, yFinish] == [0, 2]: makeMove(0, 0, 0, 3, "R")
        elif [xFinish, yFinish] == [0, 6]: makeMove(0, 7, 0, 5, "R")
    changeTurn()

def undoMove(xStart, yStart, xFinish, yFinish, pieceMoving, pieceEaten):
    global whiteKing, blackKing
    board[xStart][yStart] = pieceMoving
    board[xFinish][yFinish] = pieceEaten
    if pieceMoving == "K":
        whiteKing = [xStart, yStart]
    elif pieceMoving == "k":
        blackKing = [xStart, yStart]
    changeTurn()

def changeTurn():
    global turn
    if turn == "white":
        turn = "black"
    else:
        turn = "white"


while True:
    print()
    for row in board:
        print("".join(row))
    print()
    move = input("Move : ")
    start, finish = move[:2], move[2:]
    xStart, yStart = chessToList(start)
    xFinish, yFinish = chessToList(finish)
    pieceMoving = board[xStart][yStart]
    pieceEaten = board[xFinish][yFinish]
    if moveAllowed(xStart, yStart, xFinish, yFinish, pieceMoving, pieceEaten):
        makeMove(xStart, yStart, xFinish, yFinish, pieceMoving)
        if start in alreadyMoved:
            alreadyMoved[start] = True
        changeTurn()
    else:
        print("Your move isn't correct!")
