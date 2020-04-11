from __future__ import print_function, division
from collections import deque
import math
import sys
import time
import pickle
BOARD_SIZE = 16
INPUT_FILE = './input6.txt'
INFINITY = sys.maxsize
NEGATIVE_INFINITY = -1*sys.maxsize
DIRECTIONS = [(1, 1), (1, -1), (1, 0), (0, 1), (0, -1), (-1, 0), (-1, 1), (-1, -1)]

CAMP = {}
CAMP['W'] = {
        (15, 15): "W",
        (15, 14): "W",
        (14, 15): "W",
        (15, 13): "W",
        (14, 14): "W",
        (13, 15): "W",
        (15, 12): "W",
        (14, 13): "W",
        (13, 14): "W",
        (12, 15): "W",  
        (15, 11): "W",
        (14, 12): "W",
        (13, 13): "W", 
        (12, 14): "W", 
        (11, 15): "W", 
        (14, 11): "W",
        (13, 12): "W", 
        (12, 13): "W",
        (11, 14): "W"
        }
CAMP['B'] = {
            (0, 0): "B", 
            (0, 1): "B", 
            (1, 0): "B",
            (0, 2): "B", 
            (1, 1): "B",
            (2, 0): "B",  
            (0, 3): "B", 
            (1, 2): "B", 
            (2, 1): "B",
            (3, 0): "B",  
            (0, 4): "B", 
            (1, 3): "B", 
            (2, 2): "B", 
            (3, 1): "B", 
            (4, 0): "B", 
            (1, 4): "B", 
            (2, 3): "B", 
            (3, 2): "B", 
            (4, 1): "B"
            }
CAMP_CORNER = {}
CAMP_CORNER['W'] = (15, 15)
CAMP_CORNER['B'] = (0, 0)


PRECOMPUTED_DISTANCES = None
with open("distances.pkl", "rb") as f:
    PRECOMPUTED_DISTANCES = pickle.load(f)

def read_input():
    # reading input.txt
    with open(INPUT_FILE, 'r') as file:
        line = file.readline()
        mode = line.strip()
        line = file.readline()
        player_color = line.strip()
        line = file.readline()
        total_play_time = float(line.strip())
        
        board = []
        for i in range(BOARD_SIZE):
            line = file.readline()
            board.append(line.strip())
        return mode, player_color, total_play_time, board

def save_output(x):
    path = x.get_path_for_output()
    with open('./output.txt', 'w') as file:
        file.write(path)
    return path

class Agent:
    def __init__(self, player_color):
        self.MY_COLOR = player_color
        self.opponent_color = 'W' if player_color == 'B' else 'B'
        self.opponent_camp_empty_position = None

    def utility(self, state):
        
        if(self.opponent_camp_empty_position == None):
            for position in CAMP[self.opponent_color].keys():
                if(not position in state):
                    self.opponent_camp_empty_position = position
                    break
            if(self.opponent_camp_empty_position == None):
                self.opponent_camp_empty_position = CAMP_CORNER[self.opponent_color]

        sum_dist = 0
        max_dist = NEGATIVE_INFINITY
        occupied_positions = 0
        for position, color in state.items():
            if(color == self.MY_COLOR):
                if(position in CAMP[self.opponent_color]):
                    occupied_positions += 20
                    continue
                dist = SLD(position, self.opponent_camp_empty_position)
                if(dist > max_dist): 
                    max_dist = dist
                sum_dist += dist
                

        return (-1*sum_dist) + (-5*max_dist) + occupied_positions

class Agent2:
    def __init__(self, player_color):
        self.MY_COLOR = player_color
        self.opponent_color = 'W' if player_color == 'B' else 'B'
        self.opponent_camp_empty_position = None
        self.my_camp_empty_position = None

    def utility(self, state):
        if(count_in_opponent_camp(state, self.MY_COLOR) > 10):
            #all spaces utility
            empty_spaces_in_opponent_camp = []
            for opp_position in CAMP[self.opponent_color].keys():
                if(not opp_position in state):
                    empty_spaces_in_opponent_camp.append(opp_position)
            
            sum_dist = 0
            max_dist = NEGATIVE_INFINITY
            for position, color in state.items():
                if(color == self.MY_COLOR and not position in CAMP[self.opponent_color]):
                    dist = [SLD(position, opp_position) for opp_position in empty_spaces_in_opponent_camp]
                    if(len(dist) == 0):
                        return INFINITY
                    dist = max(dist)
                    if(dist > max_dist): 
                        max_dist = dist
                    sum_dist -= dist
            return sum_dist

        else:
            sum_dist = 0
            opponent_sum_dist = 0

            opponent_empty = None
            # for position in CAMP[self.opponent_color].keys():
            #     if(not position in state):
            #         opponent_empty = position
            #         break
            if(opponent_empty == None):
                opponent_empty = CAMP_CORNER[self.opponent_color]

            # max_dist = NEGATIVE_INFINITY
            for position, color in state.items():
                if(color == self.MY_COLOR):
                    dist = SLD(position, opponent_empty)
                    sum_dist -= dist
                    # if(dist > max_dist): 
                    #     max_dist = dist
                else:
                    dist = SLD(position, CAMP_CORNER[self.MY_COLOR])
                    opponent_sum_dist += dist
            return 1.5*sum_dist + opponent_sum_dist



def jump_or_move(x, y):
    d = SLD(x, y)
    if(d > SLD((0, 0), (1,1))):
        return 'J'
    else:
        return 'E'

class Node:
    def __init__(self, pawn_positions, current_pawn, parent=None):
        self.state = pawn_positions
        self.current_pawn = current_pawn
        self.parent = parent

    def get_single_jump_options(self):
        options = []
        for direction in DIRECTIONS:
            neighbor = (self.current_pawn[0] + direction[0], self.current_pawn[1] + direction[1])
            neighbors_neighbor = (neighbor[0] + direction[0], neighbor[1] + direction[1])
            if(neighbors_neighbor[0] < 0 or neighbors_neighbor[0] >= BOARD_SIZE or neighbors_neighbor[1] >= BOARD_SIZE or neighbors_neighbor[1] < 0):
                continue
            if(neighbor in self.state and not neighbors_neighbor in self.state):#and self.parent != None and neighbors_neighbor != self.parent.pawn_position 
                pawn_color = self.state[self.current_pawn]
                temp = self.state.copy()
                del temp[self.current_pawn]
                temp[neighbors_neighbor] = pawn_color
                options.append((temp, neighbors_neighbor))

        return options


    def get_path_for_output(self):
        
        x = self
        path = []
        while x != None:
            if(x.parent != None):
                move_type = jump_or_move(x.current_pawn, x.parent.current_pawn)
                path = [move_type+" " + str(x.parent.current_pawn[1]) + "," + str(x.parent.current_pawn[0]) +" " + str(x.current_pawn[1]) + "," + str(x.current_pawn[0])]+path

            x = x.parent
            
        return '\n'.join(path)
    
    def print_path(self):
        x = self
        path = ""
        while x != None:
            path = "(" + str(x.current_pawn[0]) + "," + str(x.current_pawn[1]) + ")" + path
            x = x.parent
            
        return str(self.state[self.current_pawn])+" "+path

    def start_position(self):
        x = self
        position = self.current_pawn
        while x != None:
            position = self.current_pawn
            x = x.parent
        return position
    
    def temp_out(self):
        board = ['................']*16
        for position, color in self.state.items():
            temp = list(board[position[0]])
            temp[position[1]] = color
            board[position[0]] = "".join(temp)
            
        return "\n".join(board)

    
    def __repr__(self):
        board = ['................']*16
        for position, color in self.state.items():
            temp = list(board[position[0]])
            temp[position[1]] = color
            board[position[0]] = "".join(temp)
            
        return "*0123456789012345\n"+"\n".join([str(i%10)+e for i, e in enumerate(board)]) + "\n" + self.print_path()

def GM(nums):
    if(len(nums) == 0):
        return 0
    prod = 1
    for n in nums:
        prod *= n
    return math.pow(prod, 1/len(nums)) 


# def utility(state):
#     opponent_color = 'W' if MY_COLOR == 'B' else 'B'
#     # my_positions = {}
#     opponent_camp_empty_position = None
#     # for position, color in state.items():
#     #     if(color == MY_COLOR):
#     #         my_positions[position] = color

    
#     for position in CAMP[opponent_color]:
#         if(not position in state):
#             opponent_camp_empty_position = position
#             break
        
#     # if(opponent_camp_empty_position == None and game_over_for(state, MY_COLOR)):
#     #     # opponent_camp_empty_position = CAMP_CORNER[opponent_color]
#     #     return INFINITY

#     if(opponent_camp_empty_position == None):
#         opponent_camp_empty_position = CAMP_CORNER[opponent_color]

    
#     max_dist= NEGATIVE_INFINITY
#     sum_dist = 0
#     len_dist = 0
#     for position in state.keys():
#         # d = list(map(lambda target: SLD(position, target), my_positions.keys()))
#         # d = max(d)/BOARD_SIZE
#         if(state[position] != MY_COLOR):
#             continue
#         if(position in CAMP[opponent_color]):
#             continue
#         dist = SLD(position, opponent_camp_empty_position)
#         if(dist > max_dist):
#             max_dist = dist
#         sum_dist += dist
#         len_dist += 1

#     avg_dist = sum_dist/len_dist if len_dist != 0 else 0
#     metric = (avg_dist/BOARD_SIZE)+(max_dist/BOARD_SIZE)
#     metric = -1*metric
#     # sum_dist = sum(distances)/len(distances) if len(distances) != 0 else 0
#     # sum_dist = (sum_dist))/(BOARD_SIZE-1)
#     for position in CAMP[opponent_color]:
#         if(position in state and state[position] == MY_COLOR):
#             metric += 1
#     return metric




def DFS(start_state, current_pawn):
    q = deque()
    start_state = Node(start_state, current_pawn, None)
    q.append(start_state)
    visited = []
    possible_moves = []
    while len(q) != 0:
        currnode = q.pop()
        options = currnode.get_single_jump_options()
        visited.append(currnode.state)
        # temp = []
        # for option in options:
        #     if(option[0] in visited):
        #         continue
        #     temp.append(option)
        if(currnode.parent != None):#and len(temp) == 0
            possible_moves.append(currnode)
        for option in options:
            if(option[0] in visited):
                continue
            n = Node(option[0], option[1], currnode)
            q.append(n)
    
    return possible_moves

def get_action_for_single_pawn(state, position):
    # adding moves
    node = Node(state, position, parent=None)
    moves = []
    for direction in DIRECTIONS:
        neighbor = (position[0] + direction[0], position[1] + direction[1])
        if(neighbor[0] < 0 or neighbor[0] >= BOARD_SIZE or neighbor[1] >= BOARD_SIZE or neighbor[1] < 0):
            continue
        if(not neighbor in state):
            pawn_color = state[position]
            temp = state.copy()
            del temp[position]
            temp[neighbor] = pawn_color
            moves.append(Node(temp, neighbor, parent=node))
            
    
    
    jump_moves = DFS(state, position)
    # print("jump moves", len(jump_moves), "adj moves", len(moves))
    moves = jump_moves+moves
    # moves = sorted(moves, key=lambda x: utility(x.state), reverse=True)
    # moves = moves[:math.ceil(len(moves)/2)] 
    return moves

def SLD(curr, goal):
    # straight line distance
    # x = math.pow(goal[0] - curr[0], 2)
    # y = math.pow(goal[1] - curr[1], 2)
    
    # return math.sqrt(x + y)
    return PRECOMPUTED_DISTANCES[curr][goal]

def L1(curr, goal):
    x = goal[0] - curr[0]
    y = goal[1] - curr[1]
    return abs(x) + abs(y)

def actions(state, player_color):
    moves = []
    # if something in camp move it out first
    for position in CAMP[player_color].keys():
        if(position in state and state[position] == player_color):
            proposed_moves = get_action_for_single_pawn(state, position)
            moves_out_of_camp = []
            moves_away_from_corner = []
            for move in proposed_moves:
                if(not move.current_pawn in CAMP[player_color]): #moves out of camp
                    moves_out_of_camp.append(move)
                elif(SLD(position, CAMP_CORNER[player_color]) < SLD(move.current_pawn, CAMP_CORNER[player_color]) and SLD(position, move.current_pawn) < SLD((0, 0), (1, 1))): #moves away from the camp corner
                    moves_away_from_corner.append(move)
            if(len(moves_out_of_camp) == 0 and len(moves) == 0):
                moves = moves+moves_away_from_corner
            else:
                moves = moves+moves_out_of_camp
    
    if(len(moves) != 0):
        return moves

    opponent_color = 'W' if player_color == 'B' else 'B'
    for position, color in state.items():
        if(color == player_color):
            proposed_moves = get_action_for_single_pawn(state, position)
            
            for move in proposed_moves:
                if(not move.current_pawn in CAMP[player_color] and not (move.start_position() in CAMP[opponent_color] and not move.current_pawn in CAMP[opponent_color])):
                    #does not return to camp and if in opposite camp does not get out
                    moves.append(move)

    return moves


def terminate(depth, max_depth):
    if(depth >= max_depth):
        return True
    else:
        return False

def alpha_beta_search(state, player_color, utility, max_depth=2):
    v, move = max_value(state, NEGATIVE_INFINITY, INFINITY, player_color, max_depth, utility, depth=0)
    return v, move

def max_value(state, alpha, beta, player_color, max_depth, utility, depth=0):
    if(terminate(depth, max_depth) or is_game_over(state)):
        return utility(state), None

    v = NEGATIVE_INFINITY
    v_move = None
    a = actions(state, player_color)
    # if(depth == 0):
    #     print("moves", len(a))
    for move in a:
        next_player = 'W' if player_color == 'B' else 'B'
        min_v, _ = min_value(move.state, alpha, beta, next_player, max_depth, utility, depth=depth+1)
        if(min_v > v):
            v = min_v
            v_move = move
        if(v >= beta):
            return v, v_move

        alpha = max(alpha, v)

    return v, v_move

def min_value(state, alpha, beta, player_color, max_depth, utility, depth=0):
    if(terminate(depth, max_depth) or is_game_over(state)):
        return utility(state), None

    v = INFINITY
    v_move = None
    for move in actions(state, player_color):
        next_player = 'W' if player_color == 'B' else 'B'
        max_v, _ = max_value(move.state, alpha, beta, next_player, max_depth, utility, depth=depth+1)
        if(max_v < v):
            v = max_v
            v_move = move
        if(v <= alpha):
            return v, v_move

        beta = min(beta, v)
        

    return v, v_move

def game_over_for(state, player_color):
    opponent_color = 'W' if player_color == 'B' else 'B'
    for position in CAMP[opponent_color].keys():
        if(not position in state):
            return False

    for position in CAMP[opponent_color].keys():
        if(state[position] == player_color):
            return True

    return False



def is_game_over(state):
    if(game_over_for(state, 'W')):
        return True

    elif(game_over_for(state, 'B')):
        return True

    else:
        return False

def is_anyone_in_camp(state, player_color):
    for position in CAMP[player_color].keys():
        if(position in state and state[position] == player_color):            
            return True
    return False

def count_in_opponent_camp(state, player_color):
    opponent_color = 'W' if player_color == 'B' else 'B'
    count = 0
    for position in CAMP[opponent_color].keys():
        if(position in state and state[position] == player_color):
            count += 1
    return count


if __name__ == "__main__":
    mode, player_color, total_play_time, board = read_input()
    positions = {}

    for i in range(0, len(board)):
        for j in range(0, len(board[0])):
            if(board[i][j] != '.'):
                positions[(i, j)] = board[i][j]

    if(player_color == 'WHITE'):
        player_color = 'W'
    else:
        player_color = 'B'

    agent = Agent2(player_color)

    if(mode == 'SINGLE'):
        # single mode
        # t = time.time()
        action = alpha_beta_search(positions, player_color, agent.utility, max_depth=1)
        # print("CPU time", time.time()-t)
        # print("value:", action[0])
        # print(action[1])
        save_output(action[1])
    elif(mode == 'GAME'):
        # game mode
        depth = 2
        if(is_anyone_in_camp(positions, player_color)):
            depth = 2
        if(count_in_opponent_camp(positions, player_color) > 16):
            depth = 1
        # else:
        #     base_time = None
        #     with open("calibrate.txt", "r") as f:
        #         base_time = float(f.readline())
        #     depth = 2
        # t = time.time()
        action = alpha_beta_search(positions, player_color, agent.utility, max_depth=depth)
        # print("CPU time", time.time()-t)
        # print("value:", action[0])
        # print(action[1])
        save_output(action[1])
        # if no player in camp
        # calculate depth for this move given the configuration and sample data from calibrate