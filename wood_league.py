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

def find_best_cover_position(agent, grid):
    best_cover_type = -1
    player_pos = (agent.x, agent.y)

Agents_list = {}
Players = []
Enemies = []
my_id = int(input())  # Your player id (0 or 1)
agent_data_count = int(input())  # Total number of agents in the game
# print(agent_data_count, file=sys.stderr, flush=True)
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
target1 = (6, 1)
target2 = (6, 3)
# game loop
printAgents(Agents_list)
while True:
    Players = []
    Enemies = []
    agent_count = int(input())  # Total number of agents still in the game
    print(agent_count,file=sys.stderr, flush=True)
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
    print(wettest_enemy_id, file=sys.stderr, flush=True)

    for agent in Players:
        if wettest_enemy_id != -1:
            print(f"{agent.agent_id};SHOOT {wettest_enemy_id}")
        else:
            print(f"{agent.agent_id};HUNKER_DOWN;")
    # for i in range(my_agent_count):
    #     print(f"{player_one.agent_id}THROW {player_one.x-1} {player_one.y}")
    #     print(f"{player_two.agent_id}THROW {player_two.x+1} {player_one.y}")
        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr, flush=True)
        # One line per agent: <agentId>;<action1;action2;...> actions are "MOVE x y | SHOOT id | THROW x y | HUNKER_DOWN | MESSAGE text"
