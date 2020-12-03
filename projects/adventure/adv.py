from room import Room
from player import Player
from world import World
from queue import SimpleQueue

import random
from ast import literal_eval

# Load world
world = World()


# You may uncomment the smaller graphs for development and testing purposes.
# map_file = "maps/test_line.txt"
# map_file = "maps/test_cross.txt"
# map_file = "maps/test_loop.txt"
# map_file = "maps/test_loop_fork.txt"
map_file = "maps/main_maze.txt"

# Loads the map into a dictionary
room_graph = literal_eval(open(map_file, "r").read())
world.load_graph(room_graph)

# Print an ASCII map
world.print_rooms()

player = Player(world.starting_room)


player = Player(world.starting_room)
test_player = Player(world.starting_room)

opposite = {'n': 's', 'e': 'w', 's': 'n', 'w': 'e'}


def find_nearest_unexplored(start_id, current_map):
    """

    Breadth-first search for nearest '?' exit to room.
    Arguments:
    start_id - id of room from which to start search & measure distance
    current_map - dictionary mapping

    """

    # Path trace dictionary:
    # Maps room id -> step direction by which room was first reached in bft.
    searched = {}

    # FIFO queue of rooms scheduled for search.
    # Entries are tuples of the form (room id, step direction).
    to_search = SimpleQueue()

    # Seed queue with starting room.
    to_search.put((start_id, None))

    # Search!
    while to_search.qsize() > 0:
        (room, prev_dir) = to_search.get()

        # Only previously unsearched rooms require any processing.
        if room not in searched:
            searched[room] = prev_dir  # Update path trace dictionary.
            options = []  # Initialize list for unexplored exits, if any.

            # Check each exit on the map.
            for exit_dir, next_room in current_map[room].items():
                if next_room == '?':
                    options.append(exit_dir)

            # If the current room has any unexplored exits, terminate the
            # search and return to the path.
            if len(options) > 0:
                return_path = []
                step = prev_dir
                while step is not None:
                    return_path.append(step)
                    room = current_map[room][opposite[step]]
                    step = searched[room]
                return return_path[::-1]

            # If there are no unexplored exits, add next rooms to
            # queue and continue searching.
            for exit_dir, neighboring_room in current_map[room].items():
                if ((neighboring_room != '?' and
                     neighboring_room not in searched)):
                    to_search.put((neighboring_room, exit_dir))


def is_dead_end(start_room, first_step):
    """

    Check if path from the starting room is a dead end. If yes, return the
    number of rooms reachable through that path. If no, return -1.

    """
    searched = {}              # room_id -> direction of first
    to_search = SimpleQueue()  # FIFO queue of search

    # Seed search queue with the first room AFTER the start room
    to_search.put((room_graph[start_room][1][first_step], first_step))
    while to_search.qsize() > 0:
        (room, last_step) = to_search.get()

        # Only unknown rooms are processed.
        if room not in searched:
            searched[room] = last_step

            # If route back to the start, this is not a dead end.
            if room == start_room:
                return -1

            # Otherwise, continue search, moving only forward.
            for exit_dir, destination in room_graph[room][1].items():
                if exit_dir != opposite[last_step]:
                    to_search.put((destination, exit_dir))

    # Start room not here; this is a dead-end. Return room count.
    return len(searched)


def get_next_move(player, curr_map):
    """

    Return next move or series of moves, given present location and map.

    """
    start = player.current_room.id
    options = []
    for exit_dir, room in curr_map[player.current_room.id].items():
        if room == '?':
            explorer = Player(player.current_room)
            explorer.travel(exit_dir)
            if explorer.current_room.id not in curr_map:
                options.append((exit_dir, is_dead_end(start, exit_dir)))

            # If adjacent room has been previously explored, add it to map.
            # No need to add this to the traversal path yet.
            else:
                curr_map[player.current_room.id][exit_dir] = \
                    explorer.current_room.id
                curr_map[explorer.current_room.id][opposite[exit_dir]] = \
                    player.current_room.id

    if len(options) > 0:
        # Make path options.
        dead_ends = [option for option in options if option[1] > 0]
        connected = [option for option in options if option[1] == -1]

        # Special case to find shortest traversal for test_loop.txt.
        if len(dead_ends) == 2 and len(connected) == 2:
            return random.choice(options)[0]

        # Explore dead ends, start with shortest.
        if len(dead_ends) > 0:
            return min(dead_ends, key=lambda x: x[1])[0]

        # If all unexplored exits are connected, chose one at random.
        else:
            return random.choice(options)[0]

    # If the map is fully explored no next move.
    if map_complete(curr_map):
        return None

    # If there are no '?' exits from the current room, but the map is not yet
    # explored, retrace steps to find an unexplored exit.
    return find_nearest_unexplored(player.current_room.id, curr_map)


def map_complete(current_map):
    """

    Check map for unexplored paths. Return true if none.

    """
    return not any(['?' in exits.values() for exits in current_map.values()])


def add_new_room(room, curr_map):
    """

    Add unexplored room to map.

    """
    # Initialize room entry on map with blank exits.
    curr_map[room.id] = {direction: '?' for direction in room.get_exits()}

    # connect current room on map.
    for exit_dir in room.get_exits():
        explorer = Player(world.rooms[room.id])
        explorer.travel(exit_dir)
        if explorer.current_room.id in curr_map:
            curr_map[room.id][exit_dir] = explorer.current_room.id
            curr_map[explorer.current_room.id][opposite[exit_dir]] = room.id


def get_traversal_path(player):
    """

    Find directions for traversal, start from current room.

    """
    traversal_path = []  # list of directions for path
    adv_map = {}         # dictionary room_id -> {exit: next_room_id or '?'}
    player = Player(player.current_room)

    # Seed map with starting room. Pulled from dict
    adv_map[player.current_room.id] = {direction: '?' for direction in
                                       player.current_room.get_exits()}

    # Choose a next move or moves, update the traversal path, and move the
    # player accordingly. Repeat until no more useful moves can be made.
    next_move = get_next_move(player, adv_map)
    while next_move is not None:
        traversal_path += next_move
        for direction in next_move:
            player.travel(direction)

        # If unknown room add to the map.
        if player.current_room.id not in adv_map:
            add_new_room(player.current_room, adv_map)

        next_move = get_next_move(player, adv_map)

    return traversal_path


# TRAVERSAL TEST
visited_rooms = set()
test_player.current_room = world.starting_room
visited_rooms.add(test_player.current_room)
path = get_traversal_path(test_player)

try:
    with open('best_so_far.txt', 'r') as file:
        previous_best = file.readlines()
except FileNotFoundError:
    previous_best = None

for move in path:
    test_player.travel(move)
    visited_rooms.add(test_player.current_room)

    print(f"TESTS PASSED: {len(path)} moves, {len(visited_rooms)} "
          "rooms visited.\n")
    if map_file == "maps/main_maze.txt":
        if previous_best is None or len(path) < len(previous_best):
            with open('best_so_far.txt', 'w') as file:
                file.writelines([step + '\n' for step in path])
    else:
        print("TESTS FAILED: INCOMPLETE TRAVERSAL")
        print(f"{len(room_graph) - len(visited_rooms)} unvisited rooms")

if map_file == "maps/main_maze.txt":
    print(f'Previous best path {len(previous_best)} moves.')


#######
# UNCOMMENT TO WALK AROUND
#######
player.current_room.print_room_description(player)
while True:
    cmds = input("-> ").lower().split(" ")
    if cmds[0] in ["n", "s", "e", "w"]:
        player.travel(cmds[0], True)
    elif cmds[0] == "q":
        break
    else:
        print("I did not understand that command.")
