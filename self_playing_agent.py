from homework3 import read_input, Agent, is_game_over, is_anyone_in_camp, count_in_opponent_camp, alpha_beta_search, Agent2 
import time

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
    # player_color = 'W'
    agent1 = Agent2(player_color)

    # opp_color = 'W' if player_color == 'B' else 'B'
    # agent2 = Agent2(opp_color, positions)

    # current_color = player_color
    
    # # self play
    # current_state = positions
    # for i in range(0, 500):
    #     if(is_game_over(current_state)):
    #         print("===========GAME OVER===========")
    #         break
    #     depth = 2
    #     if(is_anyone_in_camp(current_state, current_color)):
    #         depth = 1
    #     if(count_in_opponent_camp(current_state, current_color) > 12):
    #         depth = 1
    #     print("iter: ",  i)
    #     t = time.time()
    #     if(current_color == player_color):
    #         action = alpha_beta_search(current_state, current_color, agent1.utility, max_depth=depth)
    #         agent1.opponent_camp_empty_position = None
    #     else:
    #         action = alpha_beta_search(current_state, current_color, agent2.utility, max_depth=depth)
    #         agent2.opponent_camp_empty_position = None
    #     print("CPU time", time.time()-t)
    #     print("value:", action[0])
    #     print(action[1])
    #     current_state = action[1].state
    #     current_color = 'B' if current_color == 'W' else 'W'
    # else:
    if(is_game_over(positions)):
        print("===========GAME OVER===========")
        exit()
    depth = 2
    if(is_anyone_in_camp(positions, player_color)):
        depth = 2
    if(count_in_opponent_camp(positions, player_color) > 15):
        depth = 1
    depth=7
    t = time.time()
    action = alpha_beta_search(positions, player_color, agent1.utility, max_depth=depth)
    print("CPU time", time.time()-t)
    print("value:", action[0])
    print(action[1])
    with open("input6.txt", "w") as file:
        file.write("GAME\nBLACK\n30.0\n")
        file.write(action[1].temp_out())
    # save_output(action[1])
            
