import sys
import math

# Win the water fight by controlling the most territory, or out-soak your opponent!


class Agent:
    def __init__(self, agent_id, player, shoot_cooldown, optimal_range, soaking_power, splash_bombs):
        self.agent_id = agent_id
        self.player = player
        self.shoot_cooldown = shoot_cooldown
        self.optimal_range = optimal_range
        self.soaking_power = soaking_power
        self.splash_bombs = splash_bombs
        # Attributes that change each turn:
        self.x = -1 # Initialize with a default or invalid value
        self.y = -1
        self.current_cooldown = 0
        self.current_splash_bombs = 0 # (Splash bombs reset each round, or are they persistent?)
        self.current_tile_type = 3
        self.wetness = 0
        self.is_my_agent = False # Will set this based on my_id

    def update_turn_data(self, x, y, cooldown, splash_bombs, wetness):
        self.x = x
        self.y = y
        self.current_cooldown = cooldown
        self.current_splash_bombs = splash_bombs
        self.wetness = wetness

    def __repr__(self):
        return (f"### Agentid={self.agent_id}, player={self.player}\n"
                f"  Initial: shootCD={self.shoot_cooldown}, range={self.optimal_range}, "
                f"soaking={self.soaking_power}, bombs={self.splash_bombs}\n"
                f"  Current: pos=({self.x},{self.y}), cooldown={self.current_cooldown}, "
                f"bombs_left={self.current_splash_bombs}, wetness={self.wetness} ###")
    
def printAgents(Agents_list):
    print("--- Current Agents Data (DEBUG) ---", file=sys.stderr, flush=True)
    for agent_id, agent_obj in Agents_list.items():
        print(agent_obj, file=sys.stderr, flush=True)
    print("-----------------------------------", file=sys.stderr, flush=True)

def get_cover_type(x, y, grid):
    return grid.get((x,y), 0)

def has_reach_target(agent,target):
    return agent.x == target[0] and agent.y == target[1]

def get_wettest_enemy(enemies):
    if not enemies:
        return -1
    wettest_enemy_id = -1
    max_wetness = -1
    for agent in enemies:
        if agent.wetness > max_wetness:
            wettest_enemy_id = agent.agent_id
            max_wetness = agent.wetness
    return wettest_enemy_id

def find_best_cover(agent, grid):
    directions  =  [(1, 0), (-1, 0), (0, 1), (0, -1)]
    current_type_tile = 3
    best_cover_type_tile = 0
    best_cover_pos = (agent.x, agent.y)
    for x, y in directions:
        new_x, new_y = agent.x + x, agent.y + y
        current_type_tile = get_cover_type(new_x, new_y, grid)
        if current_type_tile > best_cover_type_tile:
            best_cover_type_tile = current_type_tile
            best_cover_pos = (new_x, new_y)
    print(best_cover_type_tile, file=sys.stderr, flush=True)
    return best_cover_pos

def find_enemy_cover(agent, grid):
    max_cover = 0
    neighbors_pos = [(agent.x, agent.y-1), (agent.x, agent.y+1), (agent.x-1, agent.y), (agent.x+1, agent.y)]
    for x, y in neighbors_pos:
        cover_type = get_cover_type(x,y, grid)
        if cover_type > max_cover:
            max_cover = cover_type
    return max_cover

def get_best_target(Enemies, grid):
    best_target= None
    type_tile = 3
    for agent in Enemies:
        agent.current_cover_type = find_enemy_cover(agent, grid)
        if agent.current_cover_type < type_tile:
            best_target = agent
            type_tile = get_cover_type(agent.x,agent.y,grid)
    return best_target       


Agents_list = {}
Players = []
Enemies = []
my_id = int(input())  # Your player id (0 or 1)
agent_data_count = int(input())  # Total number of agents in the game
for i in range(agent_data_count):
    # agent_id: Unique identifier for this agent
    # player: Player id of this agent
    # shoot_cooldown: Number of turns between each of this agent's shots
    # optimal_range: Maximum manhattan distance for greatest damage output
    # soaking_power: Damage output within optimal conditions
    # splash_bombs: Number of splash bombs this can throw this game
    agent_id, player, shoot_cooldown, optimal_range, soaking_power, splash_bombs = [int(j) for j in input().split()]
        
    agent = Agent(agent_id, player, shoot_cooldown, optimal_range, soaking_power, splash_bombs)
    if player == my_id:
        agent.is_my_agent = True
        Players.append(agent)
    else:
        Enemies.append(agent)
    Agents_list[agent_id] = agent
# width: Width of the game map
# height: Height of the game map
# printAgents(Agents_list)
grid = {}
width, height = [int(i) for i in input().split()]
for i in range(height):
    inputs = input().split()
    # print(inputs, file=sys.stderr, flush=True)
    for j in range(width):
        # x: X coordinate, 0 is left edge
        # y: Y coordinate, 0 is top edge
        x = int(inputs[3*j])
        y = int(inputs[3*j+1])
        tile_type = int(inputs[3*j+2])
        grid[(x,y)] = tile_type
print("type tile ["+str(get_cover_type(4, 0, grid))+"] height_grid = " + str(height) + " width = " + str(width), file=sys.stderr, flush=True)
# game loop
# printAgents(Agents_list)
while True:
    Players.clear()
    Enemies.clear()
    agent_count = int(input())  # Total number of agents still in the game
    for i in range(agent_count):
        # cooldown: Number of turns before this agent can shoot
        # wetness: Damage (0-100) this agent has taken
        agent_id, x, y, cooldown, splash_bombs, wetness = [int(j) for j in input().split()]
        if agent_id in Agents_list:
            Agents_list[agent_id].update_turn_data(x, y, cooldown, splash_bombs, wetness)
            if Agents_list[agent_id].player == my_id:
                Players.append(Agents_list[agent_id])
            else:
                Enemies.append(Agents_list[agent_id])
    Players = [agent for agent in Players if agent.wetness < 100]
    Enemies = [agent for agent in Enemies if agent.wetness < 100]
    my_agent_count = int(input())  # Number of alive agents controlled by you
    wettest_enemy_id = get_wettest_enemy(Enemies)
    target = get_best_target(Enemies, grid)
    if target != None:
        for agent in Players:
            next_pos = find_best_cover(agent, grid)
            # print(f"{agent.agent_id};MOVE {next_pos[0]} {next_pos[1]}; SHOOT {target.agent_id}")
            print(f"{agent.agent_id};MOVE {agent.x} {agent.y+1}; SHOOT {target.agent_id}")
        # if wettest_enemy_id != -1:
        #     print(f"{agent.agent_id};SHOOT {wettest_enemy_id}")
        # else:
        #     print(f"{agent.agent_id};HUNKER_DOWN;")
    # for i in range(my_agent_count):
    #     print(f"{player_one.agent_id}THROW {player_one.x-1} {player_one.y}")
    #     print(f"{player_two.agent_id}THROW {player_two.x+1} {player_one.y}")
        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr, flush=True)
        # One line per agent: <agentId>;<action1;action2;...> actions are "MOVE x y | SHOOT id | THROW x y | HUNKER_DOWN | MESSAGE text"