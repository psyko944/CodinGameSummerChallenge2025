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
                f"bombs_left={self.current_splash_bombs}, wetness={self.wetness}\n" 
                f"cover_type={self.current_tile_type} ###")
    
def printAgents(Agents_list):
    print("--- Current Agents Data (DEBUG) ---", file=sys.stderr, flush=True)
    for x in Agents_list:
        print(x, file=sys.stderr, flush=True)
    print("-----------------------------------", file=sys.stderr, flush=True)

def get_cover_type(x, y, grid):
    return grid.get((x,y), 0)

def has_reach_target(agent,target):
    return agent.x == target[0] and agent.y == target[1]

def move_to_the_target(agent, target):
    dx = abs(target[0] - agent.x)
    dy = abs(target[1] - agent.y)
    new_x, new_y = agent.x, agent.y
    if dx >0 or dy > 0:
        if dx >= dy:
            new_x = agent.x + (1 if target[0] > agent.x else -1)
        else:
            new_y = agent.y + (1 if target[1] > agent.y else -1)
    return new_x, new_y

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

def calculate_score(agent_id, new_x, new_y, Enemies, grid):
    score = 0
    adjacent_cover_tiles = []
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for dx, dy in directions:
        next_x, next_y = new_x + dx, new_y + dy
        cover_type = get_cover_type(next_x, next_y, grid)
        if cover_type > 0:
            adjacent_cover_tiles.append(((next_x, next_y), cover_type, (dx, dy)))
        for enemy_agent in Enemies:
            best_cover_enemy = 0
            for (cover_x, cover_y), cover_type, (dx_player, dy_player) in adjacent_cover_tiles:
                # if next_x == 11 and new_y == 1:
                    # print(cover_type, dx_player,  file=sys.stderr, flush=True)     
                is_protected = False
                if dx_player == -1 and enemy_agent.x < next_x:
                    is_protected = True
                elif dx_player == 1 and enemy_agent.x > next_x:
                    is_protected = True
                elif dy_player == -1 and enemy_agent.y < next_y:
                    is_protected = True
                elif dy_player == 1 and enemy_agent.y > next_y:
                    is_protected = True
                if is_protected:
                    best_cover_enemy = max(best_cover_enemy, cover_type)
                if best_cover_enemy == 2: score +=2
                elif best_cover_enemy == 1: score +=1
    return score


def find_best_cover(agent, grid):
    directions  =  [(0,0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    current_score = -1
    best_score = -1
    best_cover_pos = (agent.x, agent.y)
    for x, y in directions:
        new_x, new_y = agent.x + x, agent.y + y
        if not(0 <=  new_x <  width and 0 <= new_y < height) or get_cover_type(new_x, new_y, grid) != 0:
            continue
        current_score = calculate_score(agent.agent_id, new_x, new_y, Enemies, grid)
        if agent.agent_id == 2 and new_x == 12 and new_y == 1:
            print(current_score, file=sys.stderr, flush=True)
        if current_score > best_score:
            best_score = current_score
            best_cover_pos = (new_x, new_y)
    return best_cover_pos

def find_enemy_cover(agent, enemy_agent, grid):
    max_cover = 0
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for x, y in directions:
        new_x, new_y = enemy_agent.x + x, enemy_agent.y + y
        cover_type = get_cover_type(new_x,new_y, grid)
        is_protected = False
        if x == -1 and agent.x < new_x:
            is_protected = True
        elif x == 1 and agent.x > new_x:
            is_protected = True
        elif y == -1 and agent.y == new_y:
            is_protected = True
        elif y == 1 and agent.y == new_y:
            is_protected = True
        if is_protected:
            if cover_type > max_cover:
                max_cover = cover_type
    if agent.agent_id == 2:
        print(agent, file=sys.stderr, flush=True)
        print("id enemy = " + str(enemy_agent.agent_id), max_cover, file=sys.stderr, flush=True)
    return max_cover

def get_best_target(agent, Enemies, grid):
    if not Enemies:
        return None
    best_target= None
    type_tile = 3
    for enemy_agent in Enemies:
        enemy_agent.current_cover_type = find_enemy_cover(agent, enemy_agent, grid)
        d = abs(agent.x - enemy_agent.x) + abs(agent.y - enemy_agent.y)
        if enemy_agent.current_cover_type < type_tile and d <= agent.optimal_range:
            best_target = enemy_agent
            type_tile = enemy_agent.current_cover_type
    return best_target       

def targetable_area(area, Enemies, players):
    enemy_counted_in_area = 0
    for agent in Players:
        if (agent,x, agent.y) in area:
            return False
    for enemy_agent in Enemies:
        if (enemy_agent,x, enemy_agent.y) in area:
            enemy_counted_in_area += 1
    if enemy_counted_in_area >= 3:
        return True
    else:
        return False

def select_area_to_target()
def can_throw_a_bomb(player, Enemies):
    if player.current_splash_bomb == 0:
        return None
    min_throw_range = 2
    max_throw_range = 4
    ennemis_hit = 0
    aoe = [
        (-1, -1), (0, -1), (1, -1), 
        (-1,  0), (0,  0), (1,  0), 
        (-1,  1), (0,  1), (1,  1)  
    ]
    range_player_topside = [
        (-1, -2), (0, -2), (1, -2),
        (-1, -3), (0, -3), (1, -3),
        (0, -4)
    ]
    # Range pour le côté gauche

    range_player_leftside = [

    (-2, -1), (-2, 0), (-2, 1),

    (-3, -1), (-3, 0), (-3, 1),

    (-4, 0)
    ]# Range pour le côté droit

    range_player_rightside = [

    (2, -1), (2, 0), (2, 1),

    (3, -1), (3, 0), (3, 1),

    (4, 0)
    ]# Range pour le côté inférieur (botside)

    range_player_botside = [

    (-1, 2), (0, 2), (1, 2),

    (-1, 3), (0, 3), (1, 3),

    (0, 4)
    ] 
    enemy_in_map = {(e.x,e.y): e for e in Enemies} 

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

# game loop
# printAgents(Agents_list)
my_a = None
left_area = [
    (1, 1), (2, 1), (3, 1),
    (1, 2), (2, 2), (3, 2),
    (1, 3), (2, 3), (3, 3)
]

right_area = [
    (11, 1), (12, 1), (13, 1),
    (11, 2), (12, 2), (13, 2),
    (11, 3), (12, 3), (13, 3)
]

so_area = [
    (1, 8), (2, 8), (3, 8),
    (1, 9), (2, 9), (3, 9),
    (1, 10), (2, 10), (3, 10)
]

se_area = [
    (11, 8), (12, 8), (13, 8),
    (11, 9), (12, 9), (13, 9),
    (11, 10), (12, 10), (13, 10)
]
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
    left = (6, 2)
    right = (8, 2)
    bot_left = (6, 9)
    bot_right = (8, 9)
    if Enemies != None:
        for agent in Players:
            if agent.x == 7 and agent.y == 6:
                my_a = agent.agent_id
            if my_a == agent.agent_id:
                area_to_target = 
                if not has_reach_target(agent, left):
                    new_x, new_y = move_to_the_target(agent, left)
                    print(f"{agent.agent_id};MOVE {new_x} {new_y}")
                else:
                    print(f"{agent.agent_id};THROW {agent.x - 4} {agent.y}")
            else:
                print(f"{agent.agent_id};HUNKER_DOWN")

        #     actions = []
        #     if (agent.x, agent.y) != next_pos:
        #         agent.x = next_pos[0]
        #         agent.y = next_pos[1]
        #         actions.append(f"MOVE {next_pos[0]} {next_pos[1]}")
        #     target = get_best_target(agent, Enemies, grid)
        #     if target and agent.current_cooldown == 0:
        #         actions.append(f"SHOOT {target.agent_id}")
        #     print(f"{agent.agent_id};" + ";".join(actions))
        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr, flush=True)
        # One line per agent: <agentId>;<action1;action2;...> actions are "MOVE x y | SHOOT id | THROW x y | HUNKER_DOWN | MESSAGE text"
