import random
import os

#Debug Vars
debug = False

#Game Vars
game = 1
turn = 1
game_over = False

#Board Vars
grid_size = 10
blank = "[ ]"
hit = "[X]"
sunk = "[X]"
hidden = "[*]"
mine = "[O]"
detected = "[!]"
miss = "[-]"
nums = ["   "]
A=["A "]
B=["B "]
C=["C "]
D=["D "]
E=["E "]
F=["F "]
G=["G "]
H=["H "]
I=["I "]
J=["J "]
num_rows = [A, B, C, D, E, F, G, H, I, J]
hits = []
misses = []
hide = []
sunken = []
bloops = []
mine_list = []

#Ship Vars
patrol_boat = [2, "Patrol Boat"]
destroyer = [3, "Destroyer"]
submarine = [3, "Submarine", [0,0], [0,0], [0,0]]
battleship = [4, "Battleship"]
aircraft_carrier = [5, "Aircraft Carrier"]
battleship2 = [4, "Battleship 2", [0,0], [0,0], [0,0]]
ships = [patrol_boat, destroyer, submarine, battleship, aircraft_carrier, battleship2]
cooldowns = [0, 3, 0, 0, 5, 0]#PB, Destroyer, Sub, Battleship, AC, Battleship2

#Player Vars
player_wins = 0
player_ships_alive = 5
player_board =[]
player_guesses = []
player_ships = ["player"]
player_mines = []
player_pb_radar = []
player_sub_radar = []
player_cooldowns = [0, 0, 0, 0, 0, 0]#PB, Destroyer, Sub, Battleship, AC, Battleship2
player_promoted = False

#Enemy Vars
enemy_wins = 0
enemy_ships_alive = 5
enemy_board = []
enemy_guesses = []
enemy_ships = ["enemy"]
enemy_mines = []
enemy_pb_radar = []
enemy_sub_radar = []
enemy_cooldowns = [0, 0, 0, 0, 0, 0]#PB, Destroyer, Sub, Battleship, AC, Battleship2
enemy_promoted = False

def cheat(current_player):
    promoted = False
    list_len = 0
    if current_player[0] == "player":
        print("Player Ship Locations: ")
        promoted = player_promoted
    else:
        print("Enemy Ship Locations: ")
        promoted = enemy_promoted
    if promoted == True:
        list_len = len(current_player)
    else:
        list_len = len(current_player) - 1
    #Player ships
    ship = ""
    for a in range(1, list_len): #For each ship
        ship = current_player[a][1]
        ship += ": "
        for b in range(2, len(current_player[a])): #For each ship point
            ship += (str(convert_y_axis(current_player[a][b][0])) + str(current_player[a][b][1]) + "(" + current_player[a][b][2] + ")")
            if b < len(current_player[a]) - 1:
                ship += ", "
        print(ship)

def set_up():
    global num_rows
    global grid_size
    global player_board
    global enemy_board
    global ships
    global player_ships
    global enemy_ships
    global game
    global player_wins
    global enemy_wins
    #Set up number of columns
    print("-----------------------------------------------------------------------------------------------------------------------")
    print("  Game: " + str(game) + "                                                                                       Wins:   P: " + str(player_wins) + "   E: " + str(enemy_wins))
    print("-----------------------------------------------------------------------------------------------------------------------")
    for i in range(0, grid_size):
        #Only needed if grid size goes over 10
        space = "  "
        if i >= 9:
            space = " "
        #--------------------------------------
        nums.append(str(i + 1) + space)
    player_board.append(nums)
    enemy_board.append(nums)
    #Set up number of rows
    for j in range(0, grid_size):
        player_board.append(num_rows[j])
        enemy_board.append(num_rows[j])
    player_board.append("Player's Board")
    enemy_board.append("Enemy's Board ")
    #Randomly place ships
    for i in range(0, len(ships)):
        deploy_ship(ships[i], player_ships)
        deploy_ship(ships[i], enemy_ships)
    set_point_status(player_ships)
    set_point_status(enemy_ships)
    take_turn()

#ships = [patrol_boat, destroyer, submarine, battleship, aircraft_carrier]
def deploy_ship(ship, current_player): #Ship in ships list order and player ships list
    global grid_size
    global submarine
    ymax = 0
    xmax = 0
    orientation = random.randint(1, 2) #Horizontal, Vertical
    ship_range = ship[0] - 1
    if orientation == 1: #Horizontal
        xmax = grid_size - ship_range
        ymax = grid_size
    else: #Vertical
        xmax = grid_size
        ymax = grid_size - ship_range
    #For non-submarines ships only!!!!:
    if ship[1] != "Submarine" and ship[1] != "Battleship 2":
        loop = True
        while loop == True:
            potential_placement = []
            X = random.randint(1,xmax)
            Y = random.randint(1,ymax)
            anchor = [Y, X]
            potential_placement.append(anchor) #first point of placement
            for points in range(1, ship[0]):
                next_point = []
                if orientation == 1: #Horizontal
                    X += 1
                    next_point = [Y, X]
                else: #Vertical
                    Y += 1
                    next_point = [Y, X]
                potential_placement.append(next_point)
            occupied = False
            for a in range(1, len(current_player)): #For each Ship (except battleship 2)
                for b in range(2, len(current_player[a])): #For each ship's point
                    for c in range(0, len(potential_placement)): #For each potential placement point
                        if current_player[a][b] == potential_placement[c]:
                            occupied = True
            if occupied != True:
                loop = False
        counter = 0
        placement = [ship[0], ship[1]]
        for point in range(0, ship[0]):
            placement.append(potential_placement[counter])
            counter += 1
        current_player.append(placement)
    elif ship[1] == "Submarine":
        placement = [ship[0], ship[1], [0,0], [0,0], [0,0]]
        current_player.append(placement)
        draw_blank_grid()
        deploy_sub(current_player)
    else:
        placement = [ship[0], ship[1], [0,0], [0,0], [0,0], [0,0]]
        current_player.append(placement)

def radar(ship, current_player, current_radar, enemy, report): 
          #Ship num, player ship list, player radar, enemy ship list, report bloop locations?
    bloops = []
    #Add spaces to ship radar depending on the ship
    if ship == 1: #Patrol Boat
        for point in range(2, len(current_player[1])): #For each point the patrol boat has
            next_point = [current_player[1][point][0], current_player[1][point][1]]
            bloops.append(next_point)
#Using point 1 as anchor [1][2][0], [1][2][1]
        if current_player[1][2][0] - 1 >= 1 and current_player[1][2][1] - 1 >=1: #North West
            next_point = [current_player[1][2][0] - 1, current_player[1][2][1] - 1]
            bloops.append(next_point)
        if current_player[1][2][0] - 1 >= 1: #North
            next_point = [current_player[1][2][0] - 1, current_player[1][2][1]]
            bloops.append(next_point)
        if current_player[1][2][0] - 1 >= 1 and current_player[1][2][1] + 1 <= grid_size: #North East
            next_point = [current_player[1][2][0] - 1, current_player[1][2][1] +1]
            bloops.append(next_point)
        if current_player[1][2][1] - 1 >= 1: #West
            next_point = [current_player[1][2][0], current_player[1][2][1] -1]
            bloops.append(next_point)
        if current_player[1][2][0] +1 <= grid_size and current_player[1][2][1] - 1 >= 1: #South West
            next_point = [current_player[1][2][0] +1, current_player[1][2][1] - 1]
            bloops.append(next_point)
 #Using point 2 as anchor [1][3][0], [1][3][1]
        if current_player[1][3][0] - 1 >= 1 and current_player[1][3][1] +1 <= grid_size: #Nort East from point 2
            next_point = [current_player[1][3][0] - 1, current_player[1][3][1] +1]
            bloops.append(next_point)
        if current_player [1][3][1] + 1 <= grid_size: #East
            next_point = [current_player[1][3][0], current_player[1][3][1] + 1]
            bloops.append(next_point)
        if current_player[1][3][0] +1 <= grid_size and current_player[1][3][1] - 1 >= 1: #South West
            next_point = [current_player[1][3][0] +1, current_player[1][3][1] - 1]
            bloops.append(next_point)
        if current_player[1][3][0] +1 <= grid_size: #South
            next_point = [current_player[1][3][0] +1, current_player[1][3][1]]
            bloops.append(next_point)
        if current_player[1][3][0] +1 <= grid_size and current_player[1][3][1] +1 <= grid_size: #South East
            next_point = [current_player[1][3][0] +1, current_player[1][3][1] +1]
            bloops.append(next_point)
    else: #Submarine
        #Use[3][3][x]
        center = [current_player[3][3][0], current_player[3][3][1]]
        bloops.append(center)
        if current_player[3][3][0] - 1 >= 1 and current_player[3][3][1] - 1 >= 1: #North West
            next_point = [current_player[3][3][0] - 1, current_player[3][3][1] - 1]
            bloops.append(next_point)
        if current_player[3][3][0] - 1 >= 1: #North
            next_point = [current_player[3][3][0] - 1, current_player[3][3][1]]
            bloops.append(next_point)
        if current_player[3][3][0] - 1 >= 1 and current_player[3][3][1] + 1 <= grid_size: #North East
            next_point = [current_player[3][3][0] - 1, current_player[3][3][1] + 1]
            bloops.append(next_point)
        if current_player[3][3][1] - 1 >= 1: #West
            next_point = [current_player[3][3][0], current_player[3][3][1] - 1]
            bloops.append(next_point)
        if current_player[3][3][1] + 1 <= grid_size: #East
            next_point = [current_player[3][3][0], current_player[3][3][1] + 1]
            bloops.append(next_point)
        if current_player[3][3][0] + 1 <= grid_size and current_player[3][3][1] - 1 >= 1: #South West
            next_point = [current_player[3][3][0] + 1, current_player[3][3][1] - 1]
            bloops.append(next_point)
        if current_player[3][3][0] + 1 <= grid_size: #South
            next_point = [current_player[3][3][0] + 1, current_player[3][3][1]]
            bloops.append(next_point)
        if current_player[3][3][0] + 1 <= grid_size and current_player[3][3][1] + 1 <= grid_size: #South East
            next_point = [current_player[3][3][0] + 1, current_player[3][3][1] + 1]
            bloops.append(next_point)
    #Clear the previous radar list
    current_radar.clear()
    #Add the new spaces to the radar
    for a in range(0, len(bloops)):
        current_radar.append(bloops[a])
    #Check for enemy ships within radar
    sub_found_at = []
    ships_found_at = []
    if ship == 1: #Patrol Boat
        detected = False
        for b in range(0, len(current_radar)): #for each radar bloop
            for c in range(2, len(enemy[3])): #for each submarine point
                enemy_location = [enemy[3][c][0], enemy[3][c][1]]
                if enemy_location == current_radar[b] and enemy[3][c][-1] != "sunk" and enemy[3][c][-1] != "hit":
                    detected = True
                    current_radar[b].append("detected")
                    sub_found_at.append(enemy_location)
        if detected == True:
            locations = ""
            for d in range(0, len(sub_found_at)):
                location = (str(convert_y_axis(sub_found_at[d][0])) + str(sub_found_at[d][1]))
                if d < len(sub_found_at) - 1:
                    location += ", "
                locations += location
            if report == True:
                print("Enemy Submarine detected at: " + locations)
    else: #Submarine code
        list_len = 0
        promoted = False
        if current_player[0] != "player":
            if player_promoted == True:
                list_len = len(enemy)
                promoted = True
            else:
                list_len = len(enemy) -1
        else:
            if enemy_promoted == True:
                list_len = len(enemy)
                promoted = True
            else:
                list_len = len(enemy) -1
        detected = False
        for b in range(0, len(current_radar)): #for each radar bloop
            for c in range(1, list_len): #for each enemy ship
                if promoted == True and c == 1:
                    continue
                else:
                    if c != 3: #don't check enemy sub location
                        for d in range(2, len(enemy[c])): #For each ship's point
                            enemy_location = [enemy[c][d][0], enemy[c][d][1]]
                            if enemy_location == current_radar[b] and enemy[c][d][-1] != "sunk" and enemy[c][d][-1] != "hit":
                                detected = True
                                current_radar[b].append("detected")
                                ships_found_at.append(enemy_location)
        if detected == True:
            locations = ""
            for e in range(0, len(ships_found_at)):
                location = (str(convert_y_axis(ships_found_at[e][0])) + str(ships_found_at[e][1]))
                if e < len(ships_found_at) - 1:
                    location += ", "
                locations += location
            if report == True:
                print("Enemy ships detected at: " + locations)

def deploy_sub(current_player): #Player ships
    global player_mines
    global enemy_mines
    if current_player[0] == "player":
        loop1 = True
        while loop1 == True:
            response = input("Pick a central point to deploy your Submarine in enemy waters: ")
            if len(response) > 3:
                print("Invalid response")
            else:
                check_row = response[0].upper()
                check_column = ""
                for i in range(1, len(response)):
                    check_column += response[i]
                placement = []
                if check_row.isalpha() and int(convert_y_axis(check_row)) <= grid_size and check_column.isdigit() and (int(check_column) <= grid_size):
                    placement.append(convert_y_axis(check_row))
                    placement.append(int(check_column))
                    loop1 = False
                else:
                    print("Invalid response")
        loop2 = True
        while loop2 == True:
            response = input("Set orientation: (Horizontal or Vertical) ")
            new_location = []
            if response.lower() == "horizontal":
                #Check min and max - Shift X placement if necessary
                if placement[1] - 1 < 1:
                    placement[1] += 1
                if placement[1] + 1 > grid_size:
                    placement[1] -= 1
                first_point = [placement[0], placement[1] - 1]
                last_point = [placement[0], placement[1] + 1]
                new_location.append(first_point)
                new_location.append(placement)
                new_location.append(last_point)
                loop2 = False
            elif response.lower() == "vertical":
                #Check min and max - Shift Y placement if necessary
                if placement[0] -1 < 1:
                    placement[0] += 1
                if placement[0] + 1 > grid_size:
                    placement[0] -= 1
                first_point = [placement[0] - 1, placement[1]]
                last_point = [placement[0] + 1, placement[1]]
                new_location.append(first_point)
                new_location.append(placement)
                new_location.append(last_point)
                loop2 = False
            else:
                print("Invalid response")
    else: #Enemy sub placement is randomized
        #Pick a random point
        xmax = grid_size - 1
        ymax = grid_size - 1
        X = random.randint(2,xmax)
        Y = random.randint(2,ymax)
        anchor = [Y, X]
        new_location = []
        orientation = random.randint(1, 2) #Horizontal, Vertical
        if orientation == 1: #Horizontal
            first_point = [Y, X -1]
            last_point = [Y, X +1]
            new_location.append(first_point)
            new_location.append(anchor)
            new_location.append(last_point)
        else: #Vertical
            first_point = [Y-1, X]
            last_point = [Y+1, X]
            new_location.append(first_point)
            new_location.append(anchor)
            new_location.append(last_point)
    for i in range(2, len(current_player[3])): #Change previous coordinates with newly chosen coordinates
        current_player[3][i][0] = new_location[i-2][0]
        current_player[3][i][1] = new_location[i-2][1]
    if current_player[0] == "player":
        check_mine_collision(current_player, enemy_mines)
    else:
        check_mine_collision(current_player, player_mines)

def drop_mine(current_player, mine_list): #current player's ship list, current player's mine list
    if current_player[0] == "player":
        radar(1, player_ships, player_pb_radar, enemy_ships, False)
        loop1 = True
        while loop1 == True:
            loop2 = True
            while loop2 == True:
                print("Mines can be placed in any square surrounding the Patrol Boat")
                valid_placements = []
                #Check if mines exist in radar
                for spot in range(0, len(player_pb_radar)): #For each radar point
                    invalid = False
                    for mine in range(0, len(player_mines)): #For each mine
                        radar_check = [player_pb_radar[spot][0], player_pb_radar[spot][1]]
                        if radar_check == player_mines[mine]:
                            invalid = True
                    if invalid == False:
                        radar_check = [player_pb_radar[spot][0], player_pb_radar[spot][1]]
                        valid_placements.append(radar_check)
                locations = ""
                for i in range(0, len(valid_placements)):
                    location = (str(convert_y_axis(valid_placements[i][0])) + str(valid_placements[i][1]))
                    if i < len(valid_placements) - 1:
                        location += ", "
                    locations += location
                print("Available mine locations: " + locations)
                response = input("Where will you drop the mine? ")
                if len(response) > 3:
                    print("Invalid response")
                else:
                    check_row = response[0].upper()
                    check_column = ""
                    for i in range(1, len(response)):
                        check_column += response[i]
                    placement = []
                    if check_row.isalpha() and int(convert_y_axis(check_row)) <= grid_size and check_column.isdigit() and (int(check_column) <= grid_size):
                        placement.append(convert_y_axis(check_row))
                        placement.append(int(check_column))
                        loop2 = False
                    else:
                        print("Invalid response")
            #Check placement against mines already placed and if within drop bounds
            within_bounds = False
            for a in range(0, len(player_pb_radar)):
                spot = [player_pb_radar[a][0], player_pb_radar[a][1]]
                if placement == spot:
                    within_bounds = True
            if within_bounds == True:
                dupe = False
                for b in range(0, len(mine_list)):
                    if placement == mine_list[b]:
                        print("Mine already placed in location. Choose another location")
                        dupe = True
                if dupe == False:
                    mine_list.append(placement)
                    print("Mine placed")
                    loop1 = False
            else:
                print("Invalid location")
                loop2 = True
    else: #Not Player
        radar(1, enemy_ships, enemy_pb_radar, player_ships, False)
        detected = False
        detected_areas = []
        for a in range(0, len(enemy_pb_radar)):
            if enemy_pb_radar[a][-1] == "detected":
                detected = True
                potential_placement = [enemy_pb_radar[a][0], enemy_pb_radar[a][1]]
                detected_areas.append(potential_placement)
        if detected == True: #place mine in detected area
            randomizer = random.randint(0, len(detected_areas)-1) #Horizontal, Vertical
            enemy_mines.append(detected_areas[randomizer])
        else: #randomly place mine in radar
            loop = True
            while loop == True:
                dupe = False
                radar_point = []
                randomizer = random.randint(0, len(enemy_pb_radar) -1)
                for b in range(0, len(enemy_mines)):
                    radar_point = [enemy_pb_radar[randomizer][0], enemy_pb_radar[randomizer][1]]
                    if radar_point == enemy_mines[b]:
                        dupe = True
                if dupe == False:
                    enemy_mines.append(radar_point)
                    loop = False
                else: #check for valid placements
                    counter = 0
                    for c in range(0, len(enemy_pb_radar)):
                        for d in range(0, len(enemy_mines)):
                            radar_point = [enemy_pb_radar[c][0], enemy_pb_radar[c][1]]
                            if radar_point == enemy_mines[d]:
                                counter += 1
                    if counter == len(enemy_pb_radar):
                        loop = False #all areas occupied by mines
    if current_player[0] == "player":
        check_mine_collision(enemy_ships, player_mines)
    else:
        check_mine_collision(player_ships, enemy_mines)

def check_mine_collision(current_player, enemy_mine_list):
    collision = False
    booms = 0
    blow_up = []
    booms_at = []
    for a in range(2, len(current_player[3])): #For each submarine point
        point = [current_player[3][a][0], current_player[3][a][1]]
        for b in range(0, len(enemy_mine_list)):
            if enemy_mine_list[b] == point and current_player[3][a][-1] != "sunk":
                booms_at.append(point)
                collision = True
                booms += 1
                blow_up.append(b)
    if len(blow_up) > 0: #Remove mines that were blown up
        for c in range(0, len(blow_up)):
            enemy_mine_list.pop(blow_up[c])
    if collision == True:
        while booms > 0:
            if current_player[3][2][-1] != "hit":
                current_player[3][2][-1] = "hit"
                booms -= 1
            elif current_player[3][3][-1] != "hit":
                current_player[3][3][-1] = "hit"
                booms -= 1
            elif current_player[3][4][-1] != "hit":
                current_player[3][4][-1] = "hit"
                booms -= 1
            else:
                booms = 0
        location = ""
        for d in range(0, len(booms_at)):
            location += (str(convert_y_axis(booms_at[d][0])) + str(booms_at[d][1]))
            if d < len(booms_at) - 1:
                location += ", "
        if current_player[0] == "player":
            print("Player's submarine hits enemy mine at: " + location)
            check_ship_status(3, player_ships, enemy_ships, player_guesses)
        else:
            print("Enemy's submarine hits player's mine at: " + location)
            check_ship_status(3, enemy_ships, player_ships, enemy_guesses)

def deploy_patrol_boat(current_player): #Current player's ship list
    global enemy_mines
    global player_mines
    #Need to test use for enemy
    loop1 = True
    while loop1 == True:
        if current_player[0] == "player":
            #Check if the response is a valid point within bounds
            loop2 = True
            while loop2 == True:
                response = input("Pick a point to deploy your Patrol Boat: ")
                if len(response) > 3:
                    print("Invalid response")
                else:
                    check_row = response[0].upper()
                    check_column = ""
                    for i in range(1, len(response)):
                        check_column += response[i]
                    placement = []
                    if check_row.isalpha() and int(convert_y_axis(check_row)) <= grid_size and check_column.isdigit() and (int(check_column) <= grid_size):
                        placement.append(convert_y_axis(check_row))
                        placement.append(int(check_column))
                        loop2 = False
                    else:
                        print("Invalid response")
        else: #Not player - Randomize point
            xmax = grid_size
            ymax = grid_size
            X = random.randint(1,xmax)
            Y = random.randint(1,ymax)
            placement = [Y, X]
        #Check if point is valid
        occupied = False
        for a in range(1, len(current_player)): #For each ship
            if a == 1 or a == 3: #Ignore self or submarine
                continue
            else:
                for b in range(2, len(current_player[a])): # For each ship's point
                    checking_point = [current_player[a][b][0], current_player[a][b][1]]
                    if checking_point == placement:
                        occupied = True
        if occupied == True:
            if current_player[0] == "player":
                print("Location occupied")
        else:
            if current_player[0] == "player":
                response = input("Select orientation: (Horizontal/Vertical) ")
                if response.lower() == "horizontal":
                    #Check horizontal neighbors
                    horizontal_neighbor = [placement[0], placement[1] + 1]
                    east_occupied = False
                    west_occupied = False
                    if horizontal_neighbor[1] > grid_size:
                        east_occupied = True
                    if east_occupied == False:
                        for c in range(1, len(current_player)): #for each ship
                            if c == 1 or c == 3:
                                continue
                            else:
                                for d in range(2, len(current_player[c])):#for each ship's point
                                    checking_point = [current_player[c][d][0], current_player[c][d][1]]
                                    if checking_point == horizontal_neighbor:
                                        east_occupied = True
                    if east_occupied == True:
                        horizontal_neighbor = [placement[0], placement[1] - 1]
                        if horizontal_neighbor[1] < 1:
                            west_occupied = True
                        if west_occupied == False:
                            for e in range(1, len(current_player)): #for each ship
                                if e == 1 or e == 3:
                                    continue
                                else:
                                    for f in range(2, len(current_player[e])):#for each ship's point
                                        chceking_point = [current_player[e][f][0], current_player[e][f][1]]
                                        if checking_point == horizontal_neighbor:
                                            west_occupied = True
                    if east_occupied == False or west_occupied == False:
                        if east_occupied == True:
                            new_location = [horizontal_neighbor, placement]
                        else:
                            new_location = [placement, horizontal_neighbor]
                        loop1 = False
                    else:
                        print("Location occupied")
                elif response.lower() == "vertical":
                    #Check vertical neighbors
                    vertical_neighbor = [placement[0] +1, placement[1]]
                    south_occupied = False
                    north_occupied = False
                    if vertical_neighbor[0] > grid_size:
                        south_occupied = True
                    if south_occupied == False:
                        for c in range(1, len(current_player)): #for each ship
                            if c == 1 or c == 3:
                                continue
                            else:
                                for d in range(2, len(current_player[c])):#for each ship's point
                                    checking_point = [current_player[c][d][0], current_player[c][d][1]]
                                    if checking_point == vertical_neighbor:
                                        south_occupied = True
                    if south_occupied == True:
                        vertical_neighbor =[placement[0] -1, placement[1]]
                        if vertical_neighbor[0] < 1:
                            north_occupied = True
                        if north_occupied == False:
                            for e in range(1, len(current_player)): #for each ship
                                if e == 1 or e == 3:
                                    continue
                                else:
                                    for f in range(2, len(current_player[e])):#for each ship's point
                                        checking_point = [current_player[e][f][0], current_player[e][f][1]]
                                        if checking_point == vertical_neighbor:
                                            north_occupied = True
                    if south_occupied == False or north_occupied == False:
                        if south_occupied == True:
                            new_location = [vertical_neighbor, placement]
                        else:
                            new_location = [placement, vertical_neighbor]
                        loop1 = False
                    else:
                        print("Location occupied")
                else: # player didn't write vertical or horizontal:
                    print("Invalid response")
            else: #Enemy randomly selects an orientation
                orientation = random.randint(1, 2) #Horizontal, Vertical
                if orientation == 1:
                    #Check horizontal neighbors
                    horizontal_neighbor = [placement[0], placement[1] + 1]
                    east_occupied = False
                    west_occupied = False
                    if horizontal_neighbor[1] > grid_size:
                        east_occupied = True
                    if east_occupied == False:
                        for c in range(1, len(current_player)): #for each ship
                            if c == 1 or c == 3:
                                continue
                            else:
                                for d in range(2, len(current_player[c])):#for each ship's point
                                    checking_point = [current_player[c][d][0], current_player[c][d][1]]
                                    if checking_point == horizontal_neighbor:
                                        east_occupied = True
                    if east_occupied == True:
                        horizontal_neighbor =[placement[0], placement[1] - 1]
                        if horizontal_neighbor[1] < 1:
                            west_occupied = True
                        if west_occupied == False:
                            for e in range(1, len(current_player)): #for each ship
                                if e == 1 or e == 3:
                                    continue
                                else:
                                    for f in range(2, len(current_player[e])):#for each ship's point
                                        checking_point = [current_player[e][f][0], current_player[e][f][1]]
                                        if checking_point == horizontal_neighbor:
                                            west_occupied = True
                    if east_occupied == False or west_occupied == False:
                        if east_occupied == True:
                            new_location = [horizontal_neighbor, placement]
                        else:
                            new_location = [placement, horizontal_neighbor]
                        loop1 = False
                else:
                    #Check vertical neighbors
                    vertical_neighbor = [placement[0] +1, placement[1]]
                    south_occupied = False
                    north_occupied = False
                    if vertical_neighbor[0] > grid_size:
                        south_occupied = True
                    if south_occupied == False:
                        for c in range(1, len(current_player)): #for each ship
                            if c == 1 or c == 3:
                                continue
                            else:
                                for d in range(2, len(current_player[c])):#for each ship's point
                                    checking_point = [current_player[c][d][0], current_player[c][d][1]]
                                    if checking_point == vertical_neighbor:
                                        south_occupied = True
                    if south_occupied == True:
                        vertical_neighbor =[placement[0] -1, placement[1]]
                        if vertical_neighbor[0] < 1:
                            north_occupied = True
                        if north_occupied == False:
                            for e in range(1, len(current_player)): #for each ship
                                if e == 1 or e == 3:
                                    continue
                                else:
                                    for f in range(2, len(current_player[e])):#for each ship's point
                                        checking_point = [current_player[e][f][0], current_player[e][f][1]]
                                        if checking_point == vertical_neighbor:
                                            north_occupied = True
                    if south_occupied == False or north_occupied == False:
                        if south_occupied == True:
                            new_location = [vertical_neighbor, placement]
                        else:
                            new_location = [placement, vertical_neighbor]
                        loop1 = False
    for g in range(2, len(current_player[1])): #for each of the patrol_boat's points
        for h in range(0, 2): #For each individual Y, X
            current_player[1][g][h] = new_location[g-2][h]
    if current_player[0] == "player":
        check_mine_collision(current_player, enemy_mines)
    else:
        check_mine_collision(current_player, player_mines)

def set_point_status(current_player): #Current player's ships list
    for i in range(1, len(current_player) -1): #For each ship 
        for j in range(2, len(current_player[i])): #For each ship's point
            if current_player[0] == "player" or debug == True:
                current_player[i][j].append("hidden")
            else:
                current_player[i][j].append("blank")

def convert_y_axis(letter):
    if letter == "A":
        return 1
    elif letter == "B":
        return 2
    elif letter == "C":
        return 3
    elif letter == "D":
        return 4
    elif letter == "E":
        return 5
    elif letter == "F":
        return 6
    elif letter == "G":
        return 7
    elif letter == "H":
        return 8
    elif letter == "I":
        return 9
    elif letter == "J":
        return 10
    elif letter == 1:
        return "A"
    elif letter == 2:
        return "B"
    elif letter == 3:
        return "C"
    elif letter == 4:
        return "D"
    elif letter == 5:
        return "E"
    elif letter == 6:
        return "F"
    elif letter == 7:
        return "G"
    elif letter == 8:
        return "H"
    elif letter == 9:
        return "I"
    elif letter == 10:
        return "J"
    else:
        return "Invalid input"

#ships = [current_player, patrol_boat, destroyer, submarine, battleship, aircraft_carrier, battleship2]
def player_attack(ship): #ship num, player ship list, player cooldowns, enemy ship list
    global player_ships
    global player_cooldowns
    global enemy_ships
    global player_guesses
    #Battleship
    if ship == 4 or ship == 6:
        loop = True
        while loop == True:
            response = input("Where do you want to attack? ")
            if len(response) > 3:
                print("Invalid response")
            else:
                check_row = response[0].upper()
                check_column = ""
                for i in range(1, len(response)):
                    check_column += response[i]
                placement = []
                if check_row.isalpha() and int(convert_y_axis(check_row)) <= grid_size and check_column.isdigit() and (int(check_column) <= grid_size):
                    placement.append(convert_y_axis(check_row))
                    placement.append(int(check_column))
                    loop = False
                    attack = [placement]
                    print("Attack launched!")
                    check_guess(ship, attack, player_ships, player_guesses, enemy_ships)
                else:
                    print("Invalid response")
    elif ship == 2: #Destroyer
        loop = True
        while loop == True:
            response = input("Where do you want to launch missiles? ")
            if len(response) > 3:
                print("Invalid response")
            else:
                check_row = response[0].upper()
                check_column = ""
                for i in range(1, len(response)):
                    check_column += response[i]
                placement = []
                if check_row.isalpha() and int(convert_y_axis(check_row)) <= grid_size and check_column.isdigit() and (int(check_column) <= grid_size):
                    placement.append(convert_y_axis(check_row))
                    placement.append(int(check_column))
                    #Build AOE
                    AOE = [placement]
                    if placement[0] - 1 >= 1 and placement[1] - 1 >= 1: #North West
                        next_point = [placement[0] - 1, placement[1] - 1]
                        AOE.append(next_point)
                    if placement[0] - 1 >= 1: #North
                        next_point = [placement[0] -1, placement[1]]
                        AOE.append(next_point)
                    if placement[0] - 1 >= 1 and placement[1] +1 <= grid_size: #North East
                        next_point = [placement[0] - 1, placement[1] + 1]
                        AOE.append(next_point)
                    if placement[1] - 1 >= 1: #West
                        next_point = [placement[0], placement[1] - 1]
                        AOE.append(next_point)
                    if placement[1] + 1 <= grid_size: #East
                        next_point = [placement[0], placement[1] + 1]
                        AOE.append(next_point)
                    if placement[0] + 1 <= grid_size and placement[1] - 1 >= 1: #South West
                        next_point = [placement[0] + 1, placement[1] - 1]
                        AOE.append(next_point)
                    if placement[0] + 1 <= grid_size: #South
                        next_point = [placement[0] + 1, placement[1]]
                        AOE.append(next_point)
                    if placement[0] + 1 <= grid_size and placement[1] + 1 <= grid_size: #South East
                        next_point = [placement[0] + 1, placement[1] + 1]
                        AOE.append(next_point)
                    loop = False
                    print("Missiles launched!")
                    check_guess(ship, AOE, player_ships, player_guesses, enemy_ships)
                else:
                    print("Invalid response")
    else: #Aircraft Carrier
        barrage = []
        loop = True
        attack_num = 1
        print("Callout five airstrike locations")
        while loop == True:
            response = input("Where do you want to strike? (" + str(attack_num) + "/5) ")
            if len(response) > 3:
                print("Invalid response")
            else:
                check_row = response[0].upper()
                check_column = ""
                for i in range(1, len(response)):
                    check_column += response[i]
                placement = []
                if check_row.isalpha() and int(convert_y_axis(check_row)) <= grid_size and check_column.isdigit() and (int(check_column) <= grid_size):
                    placement.append(convert_y_axis(check_row))
                    placement.append(int(check_column))
                    barrage.append(placement)
                    attack_num += 1
                    if attack_num == 6:
                        loop = False
                        print("Airstrike deployed")
                        check_guess(ship, barrage, player_ships, player_guesses, enemy_ships)
                else:
                    print("Invalid response")
    if cooldowns[ship - 1] > 0:
        player_cooldowns[ship - 1] = cooldowns[ship - 1]

def enemy_attack(): #Num, ship list, cooldown list, player ships, enemy guesses
    global enemy_ships
    global enemy_cooldowns
    global player_ships
    global enemy_guesses
    #Check cooldown list and add available ships to randomizer list
    available_ships = []
    #PB, Destroyer, Sub, Battleship, AC, Battleship2
    if enemy_cooldowns[1] <= 0 and enemy_ships[2][2][-1] != "sunk":
        available_ships.append("destroyer")
    if enemy_cooldowns[3] <= 0 and enemy_ships[4][2][-1] != "sunk":
        available_ships.append("battleship1")
    if enemy_cooldowns[4] <= 0 and enemy_ships[5][2][-1] != "sunk":
        available_ships.append("aircraft carrier")
    if enemy_cooldowns[5] <= 0 and enemy_promoted == True and enemy_ships[6][2][-1] != "sunk":
        available_ships.append("battleship2")
    #Set enemy radar
    radar(3, enemy_ships, enemy_sub_radar, player_ships, False)
    #Get list of known hits/detections
    unsunken_ship = False
    known_hits = []
    fire_at = []
    for a in range(0, len(enemy_guesses)):
        if enemy_guesses[a][-1] == "hit":
            known_hit = [enemy_guesses[a][0], enemy_guesses[a][1]]
            known_hits.append(known_hit)
            unsunken_ship = True
    for b in range(0, len(enemy_sub_radar)):
        if enemy_sub_radar[b][-1] == "detected":
            known_location = [enemy_sub_radar[b][0], enemy_sub_radar[b][1]]
            known_hits.append(known_location)
            unsunken_ship = True
    #Randomly pick a location from the list to shoot at
    if unsunken_ship == True:
        randomizer = random.randint(0, len(known_hits)-1)
        aim_at = [known_hits[randomizer][0], known_hits[randomizer][1]]
        detected_ship = False
        for c in range(0, len(enemy_sub_radar)):
            check_status = [enemy_sub_radar[c][0], enemy_sub_radar[c][1]]
            if aim_at == check_status:
                if enemy_sub_radar[c][-1] == "detected":
                    fire_at = aim_at
                    detected_ship = True
        if detected_ship == False:
            compass = random.randint(0, 3)
            if compass == 0 and aim_at[0] +1 <= grid_size: #North Y+1
                fire_at = [aim_at[0] +1, aim_at[1]]
            elif compass == 1 and aim_at[0] -1 >= 1: #South
                fire_at = [aim_at[0] -1, aim_at[1]]
            elif compass == 2 and aim_at[1] -1 >= 1: #West
                fire_at = [aim_at[0], aim_at[1] -1]
            elif compass == 3 and aim_at[1] +1 <= grid_size: #east
                fire_at = [aim_at[0], aim_at[1] +1]
            else:
                fire_at = known_hits[0]
    else:
        X = random.randint(1,grid_size)
        Y = random.randint(1,grid_size)
        fire_at = [Y, X]
    #Randomize the attacking ship
    ship = 0
    attack_with = 0
    if len(available_ships) > 1:
        attack_with = random.randint(0, len(available_ships)-1)
    else:
        attack_with == 0
    #Attack and call check on guess
    if len(available_ships) > 0:
        if available_ships[attack_with] == "destroyer":
            ship = 2
            #Build AOE
            AOE = [fire_at]
            if fire_at[0] - 1 >= 1 and fire_at[1] - 1 >= 1: #North West
                next_point = [fire_at[0] - 1, fire_at[1] - 1]
                AOE.append(next_point)
            if fire_at[0] - 1 >= 1: #North
                next_point = [fire_at[0] -1, fire_at[1]]
                AOE.append(next_point)
            if fire_at[0] - 1 >= 1 and fire_at[1] +1 <= grid_size: #North East
                next_point = [fire_at[0] - 1, fire_at[1] + 1]
                AOE.append(next_point)
            if fire_at[1] - 1 >= 1: #West
                next_point = [fire_at[0], fire_at[1] - 1]
                AOE.append(next_point)
            if fire_at[1] + 1 <= grid_size: #East
                next_point = [fire_at[0], fire_at[1] + 1]
                AOE.append(next_point)
            if fire_at[0] + 1 <= grid_size and fire_at[1] - 1 >= 1: #South West
                next_point = [fire_at[0] + 1, fire_at[1] - 1]
                AOE.append(next_point)
            if fire_at[0] + 1 <= grid_size: #South
                next_point = [fire_at[0] + 1, fire_at[1]]
                AOE.append(next_point)
            if fire_at[0] + 1 <= grid_size and fire_at[1] + 1 <= grid_size: #South East
                next_point = [fire_at[0] + 1, fire_at[1] + 1]
                AOE.append(next_point)
            attack_location = ""
            for d in range(0, len(AOE)):
                attack_location += (str(convert_y_axis(AOE[d][0])) + str(AOE[d][1]))
                if d < len(AOE) - 1:
                    attack_location += (", ")
            print("Incoming enemy missiles at locations: " + attack_location)
            check_guess(2, AOE, enemy_ships, enemy_guesses, player_ships)
        elif available_ships[attack_with] == "battleship1":
            ship = 4
            attack = [fire_at]
            print("Incoming enemy attack at " + str(convert_y_axis(fire_at[0])) + str(fire_at[1]))
            check_guess(4, attack, enemy_ships, enemy_guesses, player_ships)
        elif available_ships[attack_with] == "aircraft carrier":
            ship = 5
            barrage = []
            shots_left = 5
            while shots_left > 0:
                X = random.randint(1,grid_size)
                Y = random.randint(1,grid_size)
                location = [Y, X]
                if location not in barrage:
                    barrage.append(location)
                    shots_left -= 1
            attack_location = ""
            for e in range(0, len(barrage)):
                attack_location += (str(convert_y_axis(barrage[e][0])) + str(barrage[e][1]))
                if e < len(barrage) -1:
                    attack_location += (", ")
            print("Incoming enemy airstrike at locations: " + attack_location)
            check_guess(5, barrage, enemy_ships, enemy_guesses, player_ships)
        elif available_ships[attack_with] == "battleship2":
            ship = 6
            attack = [fire_at]
            print("Incoming enemy attack at " + str(convert_y_axis(fire_at[0])) + str(fire_at[1]))
            check_guess(6, attack, enemy_ships, enemy_guesses, player_ships)
    else:
        print("The enemy is unable to attack!")
    #Set cooldowns
    if cooldowns[ship - 1] > 0 and ship > 0:
        enemy_cooldowns[ship - 1] = cooldowns[ship - 1]

def check_guess(ship, coordinates, current_player, guesses, enemy): #ship num, guess list, current player ship list, current player guesses, enemy ship list
    ships_hit = []
    list_len = 0
    promoted = False
    if enemy[0] == "player":
        if player_promoted == True:
            list_len = len(enemy)
            promoted = True
        else:
            list_len = len(enemy) -1
    else:
        if enemy_promoted == True:
            list_len = len(enemy)
            promoted = True
        else:
            list_len = len(enemy) -1
    for c in range(0, len(coordinates)): #For each coordinate being attacked
        successful_attack = False
        dupe = False
        for a in range(1, list_len): #For each enemy ship
            if a == 3: #Don't check the enemy sub
                continue
            elif promoted == True and a == 1:
                continue
            else:
                for b in range(2, len(enemy[a])): #For each point the ship has
                    ship_point = [enemy[a][b][0], enemy[a][b][1]]
                    if coordinates[c] == ship_point and enemy[a][b][-1] != "sunk" and enemy[a][b][-1] != "promoted":
                        if enemy[a][b][-1] == "hit" and a != 1:
                            translator = (str(convert_y_axis(coordinates[c][0])) + str(coordinates[c][1]))
                            print(translator + ": Target already hit!")
                            dupe = True
                        elif enemy[a][b][-1] == "hit" and a == 1: #The patrol boat has already been hit
                            successful_attack = True
                            translator = (str(convert_y_axis(coordinates[c][0])) + str(coordinates[c][1]))
                            print(translator + ": hit!")
                            for d in range(2, len(enemy[a])):
                                if enemy[a][d][-1] != "hit":
                                    enemy[a][d][2] = "hit"
                                    new_point = [enemy[a][d][0], enemy[a][d][1]]
                                    #Check Guesses
                                    set_guess_status(guesses, new_point, "hit")
                        else:
                            successful_attack = True
                            enemy[a][b][2] = "hit"
                            translator = (str(convert_y_axis(coordinates[c][0])) + str(coordinates[c][1]))
                            print(translator + ": hit!")
                            set_guess_status(guesses, ship_point, "hit")
            if successful_attack == True:
                ships_hit.append(a)
        if successful_attack == False and dupe == False:
            translator = (str(convert_y_axis(coordinates[c][0])) + str(coordinates[c][1]))
            print(translator + ": miss!")
            set_guess_status(guesses, coordinates[c], "miss")
    for i in range(1, list_len): #check ship status
        if i == 3:
            continue
        elif promoted == True and i == 1:
            continue
        else:
            if ships_hit.count(i) > 0:
                check_ship_status(i, enemy, current_player, guesses)

def set_guess_status(guess_list, coordinates, status):
    already_guessed = False
    for a in range(0, len(guess_list)):
        guessed_point = [guess_list[a][0], guess_list[a][1]]
        if guessed_point == coordinates:
            guess_list[a][2] = status
            already_guessed = True
    if already_guessed == False:
        coordinates.append(status)
        guess_list.append(coordinates)

def check_ship_status(ship, ship_owner, attacker, guesses): #Number, owner ship list, attacker ship list, attacker guess list
    global game_over
    global player_wins
    global enemy_wins
    global player_ships_alive
    global enemy_ships_alive
    current_player = ""
    enemy = ""
    hits = 0
    promotion = False
    for a in range(2, len(ship_owner[ship])): #For each of the ship's points
        if ship_owner[ship][a][-1] == "hit":
            hits += 1
    if hits == ship_owner[ship][0]:
        for b in range(2, len(ship_owner[ship])):
            ship_owner[ship][b][-1] = "sunk"
            if ship != 3: #If not submarine, update guess list to sunk status
                for c in range(0, len(guesses)):
                    ship_point = [ship_owner[ship][b][0], ship_owner[ship][b][1]]
                    guessed_point = [guesses[c][0], guesses[c][1]]
                    if ship_point == guessed_point:
                        guesses[c][-1] = "sunk"
            else: #if sub is sunk, promote patrol boat
                promotion = True
        if attacker[0] == "player":
            current_player = "Player"
            enemy = "the Enemy's"
            enemy_ships_alive -= 1
            if enemy_ships_alive == 1 and enemy_ships[3][2][-1] != "sunk":
                game_over = True
            if enemy_ships_alive == 0:
                game_over = True
        else:
            current_player = "The Enemy"
            enemy = "the Player's"
            player_ships_alive -= 1
            if player_ships_alive == 1 and player_ships[3][2][-1] != "sunk":
                game_over = True
            if player_ships_alive == 0:
                game_over = True
        print(str(current_player) + " sunk " + str(enemy)+ " " + str(ship_owner[ship][1]) + "!")
        if game_over == False and promotion == True:
            promote(attacker)
        if game_over == True:
            print("Game Over! " + current_player + " wins!")
            if current_player == "Player":
                player_wins += 1
            else:
                enemy_wins += 1

def draw_grid(current_player, board, pb_radar, mines, sub_radar, enemys_guesses, enemys_ships): #current player's ship list, board, pb radar, and mines, enemy sub radar enemy guesses, enemy ships
    global grid_size
    global blank
    global hit
    global miss
    global sunk
    global hidden
    global mine
    global detected
    global nums
    global hits
    global misses
    global hide
    global sunken
    global bloops
    global mine_list
    #debug
    global player_guesses
    global enemy_guesses
    global player_promoted
    global enemy_promoted
    #Initialize non-blank lists
    hits.clear()
    misses.clear()
    hide.clear()
    sunken.clear()
    bloops.clear()
    mine_list.clear()
    #Draw Board Header
    player = board[-1]
    print("----------------------")
    print(" " + player + "     /")
    print("--------------------")
    #Check current player's ships
    list_len = 0
    promoted = False
    if current_player[0] == "player":
        if player_promoted == True:
            list_len = len(current_player)
            promoted = True
        else:
            list_len = len(current_player) -1
    else:
        if enemy_promoted == True:
            list_len = len(current_player)
            promoted = True
        else:
            list_len = len(current_player) -1
    for ship in range(1, list_len): #For each ship
        if ship == 3:
            if current_player[0] == "enemy" and enemys_ships[3][4][-1] != "sunk":
                location1 = [enemys_ships[3][2][0], enemys_ships[3][2][1]]
                location2 = [enemys_ships[3][3][0], enemys_ships[3][3][1]]
                location3 = [enemys_ships[3][4][0], enemys_ships[3][4][1]]
                hide.append(location1)
                hide.append(location2)
                hide.append(location3)
        elif promoted == True and ship == 1:
            continue
        else:
            for point in range(2, len(current_player[ship])): #For each ship's point
                if current_player[ship][point][-1] != "blank":
                    location = []
                    if current_player[ship][point][-1] == "hit":
                        location.append(current_player[ship][point][0])
                        location.append(current_player[ship][point][1])
                        hits.append(location)
                    elif current_player[ship][point][-1] == "sunk":
                        location.append(current_player[ship][point][0])
                        location.append(current_player[ship][point][1])
                        sunken.append(location)
                    else: #hidden
                        location.append(current_player[ship][point][0])
                        location.append(current_player[ship][point][1])
                        hide.append(location)
    #Check radar
    if current_player[0] == "player":
        if current_player[1][3][-1] != "sunk" and current_player[1][3][-1] != "promoted": #If patrol boat is not sunk
            for a in range(0, len(pb_radar)):
                if pb_radar[a][-1] == "detected":
                    bloop = [pb_radar[a][0], pb_radar[a][1]]
                    bloops.append(bloop)
    else:
        if player_ships[3][4][-1] != "sunk": #If submarine is not sunk
            for a in range(0, len(sub_radar)):
                if sub_radar[a][-1] == "detected":
                    bloop = [sub_radar[a][0], sub_radar[a][1]]
                    bloops.append(bloop)
    #Add mines
    if current_player[0] == "player":
        for i in range(0, len(mines)):
            mine_list.append(mines[i])
    #Add misses
    for b in range(0, len(enemys_guesses)):
        if enemys_guesses[b][-1] == "miss":
            missed = [enemys_guesses[b][0], enemys_guesses[b][1]]
            misses.append(missed)
    #Draw Grid
    header = ""
    for num in range(0, grid_size +1):
        row = nums[num]
        header = header + row
    Asquares = ""
    Bsquares = ""
    Csquares = ""
    Dsquares = ""
    Esquares = ""
    Fsquares = ""
    Gsquares = ""
    Hsquares = ""
    Isquares = ""
    Jsquares = ""
    gridrows =[header, Asquares, Bsquares, Csquares, Dsquares, Esquares, Fsquares, Gsquares, Hsquares, Isquares, Jsquares]
    remove_grid_dupes(current_player)
    hits.append("hit")
    misses.append("miss")
    hide.append("hidden")
    sunken.append("sunk")
    bloops.append("detected")
    mine_list.append("mine")
    not_blanks = [hits, misses, hide, sunken, bloops, mine_list]
    counter = 0
    for a in range (1, grid_size +1): #Rows
        row = str(board[a][0])
        for b in range(1, grid_size +1): #Columns
            not_blank_detected = False
        #Check non-blanks
            for c in range(0, len(not_blanks)): #For each not blank
                for d in range(0, len(not_blanks[c])): #For each point in each set of not-blanks
                    point_check = [a, b]
                    if point_check == not_blanks[c][d]: #If not-blank detected
                        not_blank_detected = True
                        if not_blanks[c][-1] == "hit":
                            row = row + hit
                        elif not_blanks[c][-1] == "miss":
                            row = row + miss
                        elif not_blanks[c][-1] == "sunk":
                            row = row + sunk
                        elif not_blanks[c][-1] == "detected":
                            row = row + detected
                        elif not_blanks[c][-1] == "mine":
                            row = row + mine
                        else:
                            row = row + hidden
            if not_blank_detected == False:
                row = row + blank
        gridrows[a] = gridrows[a] + row
    for rows in range(0, grid_size +1):
        print(gridrows[rows])

def draw_blank_grid():
    row = "    "
    for c in range(1, grid_size + 1):
        space = "  "
        if c >= 10:
            space = " "
        row += str(c) + space
    print(row)
    for a in range(1, grid_size + 1):
        row = " " + convert_y_axis(a) + " "
        for b in range(1, grid_size + 1):
            row += "[ ]"
        print(row)

def remove_grid_dupes(current_player):
    global hits
    global misses
    global hide
    global sunken
    global bloops
    global mine_list
    #Check for duplicate points in non-blanks and adjust according to priority
    #If looking at player board: detected, hits, hidden, mine, sunken, miss
    #If looking at enemy board: hits, detected, hidden, sunken, miss
    remove_from_hits = []
    remove_from_miss = []
    remove_from_hidden = []
    remove_from_detected = []
    remove_from_mine = []
    remove_from_sunken = []
    remover = [remove_from_hits, remove_from_miss, remove_from_hidden, remove_from_detected, remove_from_mine, remove_from_sunken]
    if current_player[0] == "player":
        for a in range(0, len(bloops)): #Check Against Bloops: Priority 1
            for b in range(0, len(hits)): #Hits
                if bloops[a] == hits[b]:
                    remove_from_hits.append(hits[b])
            for c in range(0, len(hide)): #Hide
                if bloops[a] == hide[c]:
                    remove_from_hidden.append(hide[c])
            for d in range(0, len(mine_list)): #Mine_list
                if bloops[a] == mine_list[d]:
                    remove_from_mine.append(mine_list[d])
            for e in range(0, len(sunken)):
                if bloops[a] == sunken[e]: #sunken
                    remove_from_sunken.append(sunken[e])
            for f in range(0, len(misses)): #misses
                if bloops[a] == misses[f]:
                    remove_from_miss.append(misses[f])
        for dupes in range(0, len(remover)): #Remove Bloop Dupes
            if len(remover[dupes]) > 0:
                for doubledupes in range(0, len(remover[dupes])):
                    if dupes == 0: #hits
                        hits.remove(remover[dupes][doubledupes])
                    elif dupes == 1: #miss
                        misses.remove(remover[dupes][doubledupes])
                    elif dupes == 2: #hidden
                        hide.remove(remover[dupes][doubledupes])
                    elif dupes == 3: #detected
                        bloops.remove(remover[dupes][doubledupes])
                    elif dupes == 4: #mine
                        mine_list.remove(remover[dupes][doubledupes])
                    else:
                        sunken.remove(remover[dupes][doubledupes])
        remove_from_hits.clear()
        remove_from_miss.clear()
        remove_from_hidden.clear()
        remove_from_detected.clear()
        remove_from_mine.clear()
        remove_from_sunken.clear()
        for h in range(0, len(hits)): #Check Against Hits: Priority 2
            for j in range(0, len(hide)): #Hide
                if hits[h] == hide[j]:
                    remove_from_hidden.append(hide[j])
            for k in range(0, len(mine_list)): #Mine List
                if hits[h] == mine_list[k]:
                    remove_from_mine.append(mine_list[k])
            for m in range(0, len(sunken)):
                if hits[h] == sunken[m]: #sunken
                    remove_from_sunken.append(sunken[m])
            for l in range(0, len(misses)): #Misses
                if hits[h] == misses[l]:
                    remove_from_miss.append(misses[l])
        for abra in range(0, len(remover)):
            if len(remover[abra]) > 0:
                for cadabra in range(0, len(remover[abra])):
                    if abra == 0: #hits
                        hits.remove(remover[abra][cadabra])
                    elif abra == 1: #miss
                        misses.remove(remover[abra][cadabra])
                    elif abra == 2: #hidden
                        hide.remove(remover[abra][cadabra])
                    elif abra == 3: #detected
                        bloops.remove(remover[abra][cadabra])
                    elif abra == 4: #mine
                        mine_list.remove(remover[abra][cadabra])
                    else: #sunk
                        sunken.remove(remover[abra][cadabra])
        remove_from_hits.clear()
        remove_from_miss.clear()
        remove_from_hidden.clear()
        remove_from_detected.clear()
        remove_from_mine.clear()
        remove_from_sunken.clear()
        for m in range(0, len(hide)): #Check Against Hidden: Priority 3
            for n in range(0, len(mine_list)): #Mine_list
                if hide[m] == mine_list[n]:
                    remove_from_mine.append(mine_list[n])
            for p in range(0, len(sunken)): #sunk
                if hide[m] == sunken[p]:
                    remove_from_sunken.append(sunken[p])
            for o in range(0, len(misses)): #misses
                if hide[m] == misses[o]:
                    remove_from_miss.append(misses[o])
        for ban in range(0, len(remover)):
            if len(remover[ban]) > 0:
                for ana in range(0, len(remover[ban])):
                    if ban == 0: #hits
                        hits.remove(remover[ban][ana])
                    elif ban == 1: #miss
                        misses.remove(remover[ban][ana])
                    elif ban == 2: #hidden
                        hide.remove(remover[ban][ana])
                    elif ban == 3: #detected
                        bloops.remove(remover[ban][ana])
                    elif ban == 4: #mine
                        mine_list.remove(remover[ban][ana])
                    else: #sunk
                        sunken.remove(remover[ban][ana])
        remove_from_hits.clear()
        remove_from_miss.clear()
        remove_from_hidden.clear()
        remove_from_detected.clear()
        remove_from_mine.clear()
        remove_from_sunken.clear()
        for p in range(0, len(mine_list)): #Check Against Mine List: Priority 4
            for r in range(0, len(sunken)):
                if mine_list[p] == sunken[r]:
                    remove_from_sunken.append(sunken[r])
            for q in range(0, len(misses)):
                if mine_list[p] == misses[q]:
                    remove_from_miss.append(misses[q])
        for thisis in range(0, len(remover)):
            if len(remover[thisis]) > 0:
                for toolong in range(0, len(remover[thisis])):
                    if thisis == 0: #hits
                        hits.remove(remover[thisis][toolong])
                    elif thisis == 1: #miss
                        misses.remove(remover[thisis][toolong])
                    elif thisis == 2: #hidden
                        hide.remove(remover[thisis][toolong])
                    elif thisis == 3: #detected
                        bloops.remove(remover[thisis][toolong])
                    elif thisis == 4: #mine
                        mine_list.remove(remover[thisis][toolong])
                    else: #sunk
                        sunken.remove(remover[thisis][toolong])
        remove_from_hits.clear()
        remove_from_miss.clear()
        remove_from_hidden.clear()
        remove_from_detected.clear()
        remove_from_mine.clear()
        remove_from_sunken.clear()
        for s in range(0, len(sunken)):
            for t in range(0, len(misses)):
                if sunken[s] == misses[t]:
                    remove_from_miss.append(misses[t])
        for thisis in range(0, len(remover)):
            if len(remover[thisis]) > 0:
                for toolong in range(0, len(remover[thisis])):
                    if thisis == 0: #hits
                        hits.remove(remover[thisis][toolong])
                    elif thisis == 1: #miss
                        misses.remove(remover[thisis][toolong])
                    elif thisis == 2: #hidden
                        hide.remove(remover[thisis][toolong])
                    elif thisis == 3: #detected
                        bloops.remove(remover[thisis][toolong])
                    elif thisis == 4: #mine
                        mine_list.remove(remover[thisis][toolong])
                    else: #sunk
                        sunken.remove(remover[thisis][toolong])
        remove_from_hits.clear()
        remove_from_miss.clear()
        remove_from_hidden.clear()
        remove_from_detected.clear()
        remove_from_mine.clear()
        remove_from_sunken.clear()
    else: #Not player's board
    #hits
    #detected
    #hidden
    #sunk
    #miss
        for a in range(0, len(hits)):
            for b in range(0, len(bloops)):
                if hits[a] == bloops[b]:
                    remove_from_detected.append(bloops[b])
            for c in range(0, len(hide)):
                if hits[a] == hide[c]:
                    remove_from_hidden.append(hide[c])
            for e in range(0, len(sunken)):
                if hits[a] == sunken[e]:
                    remove_from_sunken.append(sunken[e])
            for d in range(0, len(misses)):
                if hits[a] == misses[d]:
                    remove_from_miss.append(misses[d])
        for dupes in range(0, len(remover)): #Remove Dupes
            if len(remover[dupes]) > 0:
                for doubledupes in range(0, len(remover[dupes])):
                    if dupes == 0: #hits
                        hits.remove(remover[dupes][doubledupes])
                    elif dupes == 1: #miss
                        misses.remove(remover[dupes][doubledupes])
                    elif dupes == 2: #hidden
                        hide.remove(remover[dupes][doubledupes])
                    elif dupes == 3: #detected
                        bloops.remove(remover[dupes][doubledupes])
                    elif dupes == 4: #mine
                        mine_list.remove(remover[abra][cadabra])
                    else: #Sunk
                        sunken.remove(remover[abra][cadabra])
        remove_from_hits.clear()
        remove_from_miss.clear()
        remove_from_hidden.clear()
        remove_from_detected.clear()
        remove_from_mine.clear()
        remove_from_sunken.clear()
        for e in range(0, len(bloops)):
            for f in range(0, len(hide)):
                if bloops[e] == hide[f]:
                    remove_from_hidden.append(hide[f])
            for h in range(0, len(sunken)):
                if bloops[e] == sunken[h]:
                    remove_from_sunken.append(sunken[h])
            for g in range(0, len(misses)):
                if bloops[e] == misses[g]:
                    remove_from_misses.append(misses[g])
        for abra in range(0, len(remover)):
            if len(remover[abra]) > 0:
                for cadabra in range(0, len(remover[abra])):
                    if abra == 0: #hits
                        hits.remove(remover[abra][cadabra])
                    elif abra == 1: #miss
                        misses.remove(remover[abra][cadabra])
                    elif abra == 2: #hidden
                        hide.remove(remover[abra][cadabra])
                    elif abra == 3: #detected
                        bloops.remove(remover[abra][cadabra])
                    elif abra == 4: #mine
                        mine_list.remove(remover[abra][cadabra])
                    else: #Sunk
                        sunken.remove(remover[abra][cadabra])
        remove_from_hits.clear()
        remove_from_miss.clear()
        remove_from_hidden.clear()
        remove_from_detected.clear()
        remove_from_mine.clear()
        remove_from_sunken.clear()
        for h in range(0, len(hide)):
            for j in range(0, len(sunken)):
                if hide[h] == sunken[j]:
                    remove_from_sunken.append(sunken[j])
            for i in range(0, len(misses)):
                if hide[h] == misses[i]:
                    remove_from_miss.append(misses[i])
        for thisis in range(0, len(remover)):
            if len(remover[thisis]) > 0:
                for toolong in range(0, len(remover[thisis])):
                    if thisis == 0: #hits
                        hits.remove(remover[thisis][toolong])
                    elif thisis == 1: #miss
                        misses.remove(remover[thisis][toolong])
                    elif thisis == 2: #hidden
                        hide.remove(remover[thisis][toolong])
                    elif thisis == 3: #detected
                        bloops.remove(remover[thisis][toolong])
                    elif thisis == 4: #mine
                        mine_list.remove(remover[thisis][toolong])
                    else: #sunk
                        sunken.remove(remover[thisis][toolong])
        remove_from_hits.clear()
        remove_from_miss.clear()
        remove_from_hidden.clear()
        remove_from_detected.clear()
        remove_from_mine.clear()
        remove_from_sunken.clear()
        for k in range(0, len(sunken)):
            for l in range(0, len(misses)):
                if sunken[k] == misses[l]:
                    remove_from_miss.append(misses[l])
        for thisis in range(0, len(remover)):
            if len(remover[thisis]) > 0:
                for toolong in range(0, len(remover[thisis])):
                    if thisis == 0: #hits
                        hits.remove(remover[thisis][toolong])
                    elif thisis == 1: #miss
                        misses.remove(remover[thisis][toolong])
                    elif thisis == 2: #hidden
                        hide.remove(remover[thisis][toolong])
                    elif thisis == 3: #detected
                        bloops.remove(remover[thisis][toolong])
                    elif thisis == 4: #mine
                        mine_list.remove(remover[thisis][toolong])
                    else: #sunk
                        sunken.remove(remover[thisis][toolong])
        remove_from_hits.clear()
        remove_from_miss.clear()
        remove_from_hidden.clear()
        remove_from_detected.clear()
        remove_from_mine.clear()
        remove_from_sunken.clear()

def choose_attacker():
    global player_cooldowns
    global player_ships
    available_ships = []
    #PB, Destroyer, Sub, Battleship, AC, Battleship2
    if player_cooldowns[1] <= 0 and player_ships[2][2][-1] != "sunk":
        available_ships.append("Destroyer")
    if player_cooldowns[3] <= 0 and player_ships[4][2][-1] != "sunk":
        available_ships.append("Battleship")
    if player_cooldowns[4] <= 0 and player_ships[5][2][-1] != "sunk":
        available_ships.append("Aircraft Carrier")
    if player_cooldowns[5] <= 1 and player_promoted == True and player_ships[6][2][-1] != "sunk":
        available_ships.append("Battleship 2")
    ships = ""
    for a in range(0, len(available_ships)):
        ships += (str(available_ships[a]))
        if a < len(available_ships) -1:
            ships += (", ")
    if len(available_ships) > 0:
        loop = True
        while loop == True:
            print("Available Ships: " + ships)
            response = input("Choose a ship to attack with: ")
            check = response.lower()
            if check == "battleship":
                if player_cooldowns[3] <= 0:
                    if player_ships[4][2][-1] != "sunk":
                        player_attack(4)
                        loop = False
                    else:
                        print("Ship is destroyed. Choose another ship")
                else:
                    print("Ship reloading. Choose another ship")
            elif check == "destroyer":
                if player_cooldowns[1] <= 0:
                    if player_ships[2][2][-1] != "sunk":
                        player_attack(2)
                        loop = False
                    else:
                        print("Ship is destroyed. Choose another ship")
                else:
                    print("Ship reloading. Choose another ship")
            elif check == "aircraft carrier":
                if player_cooldowns[4] <= 0:
                    if player_ships[5][2][-1] != "sunk":
                        player_attack(5)
                        loop = False
                    else:
                        print("Ship is destroyed. Choose another ship")
            elif check == "battleship 2" and player_promoted == True:
                if player_cooldowns[5] <= 0:
                    if player_ships[6][2][-1] != "sunk":
                        player_attack(6)
                        loop = False
                    else:
                        print("Ship is destroyed. Choose another ship")
                else:
                    print("Ship reloading. Choose another ship")
            else:
                print("Invalid response")
    else:
        print("No ships available to attack")

def drop_or_deploy(current_player):
    global player_mines
    global enemy_mines
    global enemy_pb_radar
    global player_ships
    if current_player[0] == "player":
        loop = True
        while loop == True:
            if current_player[1][2][-1] != "sunk" and current_player[1][2][-1] != "promoted": #Check if patrol boat is alive
                response = input("Will you move a ship or drop a mine? (move/drop) ")
                if response.lower() == "move": #Move a ship
                    if current_player[3][2][-1] != "sunk":
                        response2 = input("Which ship will you move? (Patrol Boat/Submarine) ")
                        if response2.lower() == "patrol boat" or response2.lower() == "pb":
                            deploy_patrol_boat(current_player)
                            loop = False
                        elif response2.lower() == "submarine" or response2.lower() == "sub":
                            deploy_sub(current_player)
                            loop = False
                        else:
                            print("Invalid response")
                    else:
                        deploy_patrol_boat(current_player)
                elif response.lower() == "drop" or response.lower() == "mine":
                    drop_mine(current_player, player_mines)
                    loop = False
                else:
                    print("Invalid response")
            else: #Patrol Boat is sunk
                if current_player[3][2][-1] != "sunk":
                    deploy_sub(current_player)
                    loop = False
                else: #Both ships are sunk
                    loop = False
    else: #Not player
        pb_unavailable = False
        if current_player[1][2][-1] == "sunk" or current_player[1][2][-1] == "promoted":
            pb_unavailable = True
        if pb_unavailable == False:
            radar(1, current_player, enemy_pb_radar, player_ships, False) #Check if player sub is in radar
            detected = False
            for a in range(0, len(enemy_pb_radar)):
                if enemy_pb_radar[a][-1] == "detected":
                    detected = True
            if detected == True:
                drop_mine(current_player, enemy_mines)
            else: #Randomly choose between dropping a mine and moving a ship
                randomizer = random.randint(1, 2)
                if randomizer == 1:
                    drop_mine(current_player, enemy_mines)
                else:
                    #Randomly choose a ship to move
                    random_ship = random.randint(1, 2)
                    if random_ship == 1:
                        deploy_patrol_boat(current_player)
                    else:
                        deploy_sub(current_player)
        elif current_player[3][2][-1] != "sunk" and pb_unavailable == True:
            deploy_sub(current_player)

def promote(current_player):
    global player_promoted
    global enemy_promoted
    if current_player[1][2][-1] != "sunk":
        if current_player[0] == "player":
            player_promoted = True
        else:
            enemy_promoted = True
        for a in range(2, len(current_player[1])):
            current_player[1][a][-1] = "promoted"
    #Deploy the battleship somewhere
    if current_player[0] == "player":
        print("Patrol Boat promoted to Battleship!")
        locations = []
        placement = []
        loop1 = True
        while loop1 == True:
            loop2 = True
            while loop2 == True:
                locations.clear()
                placement.clear()
                print("Choose a location to deploy your new battleship. This cannot be moved once placed.")
                response = input("Where do you want to deploy? ")
                if len(response) > 3:
                    print("Invalid response")
                else:
                    check_row = response[0].upper()
                    check_column = ""
                    for i in range(1, len(response)):
                        check_column += response[i]
                    if check_row.isalpha() and int(convert_y_axis(check_row)) <= grid_size and check_column.isdigit() and (int(check_column) <= grid_size):
                        placement.append(convert_y_axis(check_row))
                        placement.append(int(check_column))
                        loop2 = False
                        locations.append(placement)
                    else:
                        print("Invalid response")
            occupied = False
            for a in range(2, len(current_player)-1): #For each ship except PB and BS2
                if a == 3:
                    continue
                else:
                    for b in range(2, len(current_player[a])): #For each ship's point
                        check_point = [current_player[a][b][0], current_player[a][b][1]]
                        if check_point == placement:
                            occupied = True
            if occupied == False:
                loop3 = True
                acceptable = True
                while loop3 == True:
                    response = input("Choose orientation: (Horizontal/Vertical) ")
                    if response.lower() == "horizontal":
                        new_X = placement[1]
                        for c in range(0, 3):
                            location = [placement[0], new_X +1]
                            locations.append(location)
                            new_X += 1
                            loop3 = False
                    elif response.lower() == "vertical":
                        new_Y = placement[0]
                        for c in range(0, 3):
                            location = [new_Y + 1, placement[1]]
                            locations.append(location)
                            new_Y += 1
                            loop3 = False
                    else:
                        print("Invalid response")
                        acceptable = False
                    for z in range(0, len(locations)):
                        for y in range(0, len(locations[z])):
                            if locations[z][y] > grid_size:
                                acceptable = False
                    if acceptable == True:
                        occupied = False
                        for f in range(0, len(locations)):
                            len_of_list = len(current_player) -1
                            for d in range(2, len_of_list): #For each ship excluding PB and BS2
                                if d == 3:
                                    continue
                                else:
                                    for e in range(2, len(current_player[d])): #For each ship's point
                                        check_point = [current_player[d][e][0], current_player[d][e][1]]
                                        if check_point == locations[f]:
                                            occupied = True
                        if occupied == False:
                            for g in range(2, len(current_player[6])):
                                current_player[6][g][0] = locations[g-2][0]
                                current_player[6][g][1] = locations[g-2][1]
                                current_player[6][g].append("hidden")
                                loop1 = False
                        else:
                            print("Location occupied. Choose another location")
                            loop3 = False
                            loop2 = True
                    else:
                        print("Ship out of bounds. Choose another location")
                        loop2 = True
    else:
        locations = []
        loop = True
        while loop == True:
            locations.clear()
            orientation = random.randint(1, 2) #Horizontal, Vertical
            ship_range = current_player[6][0] - 3
            if orientation == 1: #Horizontal
                xmax = grid_size - ship_range
                ymax = grid_size
            else: #Vertical
                xmax = grid_size
                ymax = grid_size - ship_range
            X = random.randint(1, xmax)
            Y = random.randint(1, ymax)
            location = [Y, X] #First point
            locations.append(location)
            if orientation == 1: #Horizontal:
                new_X = X
                for a in range(0, 3):
                    location = [Y, new_X + 1]
                    locations.append(location)
                    new_X += 1
            else:
                new_Y = Y
                for a in range(0, 3):
                    location = [new_Y + 1, X]
                    locations.append(location)
                    new_Y += 1
            occupied = False
            for b in range(0, len(locations)): #For each potential location 
                for c in range(2, len(current_player)-1): #For each ship starting from destroyer to AC
                    if c == 3: #skip sub
                        continue
                    else:
                        for d in range(2, len(current_player[c])): #For each ship point
                            check_point = [current_player[c][d][0], current_player[c][d][1]]
                            if check_point == locations[b]:
                                occupied = True
            if occupied == False:
                for e in range(2, len(current_player[6])):
                    current_player[6][e][0] = locations[e-2][0]
                    current_player[6][e][1] = locations[e-2][1]
                    current_player[6][e].append("blank")
                loop = False
    #Debug
    print(str(current_player))

def take_turn():
    global player_ships
    global enemy_ships
    global player_cooldowns
    global enemy_cooldowns
    global player_guesses
    global enemy_guesses
    global turn
    global game_over
    global debug
    loop = True
    while loop == True:
        print("----------------------------------------------------")
        print(" Turn: " + str(turn) + "      Ships Remaining: P:" + str(player_ships_alive) + "  E:" + str(enemy_ships_alive) + "           /")
        print("--------------------------------------------------")
        if debug == True:
            cheat(enemy_ships)
        #Draw Enemy Board
        if enemy_ships[3][2][-1] != "sunk":
            radar(3, player_ships, player_sub_radar, enemy_ships, True)
        draw_grid(enemy_ships, enemy_board, enemy_pb_radar, enemy_mines, player_sub_radar, player_guesses, player_ships)
        #Draw Player Board
        if player_ships[3][2][-1] != "sunk" or player_ships[3][2][-1] != "promoted":
            radar(1, player_ships, player_pb_radar, enemy_ships, True)
        draw_grid(player_ships, player_board, player_pb_radar, player_mines, player_sub_radar, enemy_guesses, enemy_ships)
        #Player Attack
        choose_attacker()
        if game_over != True:
            #Enemy Attack
            enemy_attack()
        else:
            loop = False
#Redraw boards
        if game_over != True:
            #Draw Enemy Board
            if enemy_ships[3][2][-1] != "sunk":
                radar(3, player_ships, player_sub_radar, enemy_ships, True)
            draw_grid(enemy_ships, enemy_board, enemy_pb_radar, enemy_mines, player_sub_radar, player_guesses, player_ships)
            #Draw Player Board
            if player_ships[3][2][-1] != "sunk":
                radar(1, player_ships, player_pb_radar, enemy_ships, True)
            draw_grid(player_ships, player_board, player_pb_radar, player_mines, player_sub_radar, enemy_guesses, enemy_ships)
            #Player move or drop mine
            drop_or_deploy(player_ships)
            #Enemy move or drop mine
            drop_or_deploy(enemy_ships)
            #Subtract from cooldowns
            for a in range(0, len(player_cooldowns)):
                if player_cooldowns[a] > 0:
                    player_cooldowns[a] -= 1
                    if debug == True:
                        player_cooldowns[a] = 0
                if enemy_cooldowns[a] > 0:
                    enemy_cooldowns[a] -= 1
            turn += 1
        else:
            play_again()

def rules():
    global cooldowns
    global hit
    global miss
    global hidden
    global detected
    global mine
    global debug
    print("-------------------------")
    print("   Rules               /")
    print("-----------------------")
    print(" Be the first to sink all of the Enemy's ships!")
    print(" Each player has 5 ships: Patrol Boat, Submarine, Destroyer, Battleship, Aircraft Carrier")
    print(" Each ship has a unique ability")
    print(" * Patrol Boat: Can detect Enemy Submarines when directly over them and can drop mines to attack")
    print(" * Submarine: Is deployed in Enemy waters and can detect when directly below Enemy ships")
    print(" * Destroyer: Attacks a 3x3 area when attacking. Must take " + str(cooldowns[1]) + " turns to reload after attacking")
    print(" * Battleship: Can attack a single location once per turn")
    print(" * Aircraft Carrier: Can attack 5 designated areas via airstrike. Must take " + str(cooldowns[4]) + " turns to refuel after attacking")
    print(" Each turn, players picks 1 attacking ship. Then players chooses to move their Submarine or Patrol Boat, or drop a mine")
    print(" You do not need to sink the enemy Submarine to win. You only need to sink each other enemy ship")
    print(" If you DO sink the enemy Submarine, your Patrol Boat will be promoted to a second Battleship")
    print(" Hits will appear as " + hit)
    print(" Misses will appear as " + miss)
    print(" Mines will appear as " + mine)
    print(" Detected enemy ships will appear as " + detected)
    print(" Your hidden ships will appear as " + hidden)
    print(" Remember: Ships can move, so you may want to consider targeting areas that were previously misses")
    print("")
    response = input(" *** Press Enter to Start *** ")
    if response.lower() == "pumpkineater":
        if debug == True:
            debug = False
        else:
            debug = True

def version():
    print("-----------------------------------------------------------------------------------------------------------------------")
    print("                                        Battleship 2 - Code by Daniel Navarro                                 ver: 1.10")
    print("-----------------------------------------------------------------------------------------------------------------------")

def reset_game():
    #Game Vars
    global game_over
    global game
    global turn
    #Player Vars
    global player_ships_alive
    global player_board
    global player_guesses
    global player_ships
    global player_mines
    global player_cooldowns
    global player_pb_radar
    global player_sub_radar
    global player_promoted
    #Enemy Vars
    global enemy_ships_alive
    global enemy_board
    global enemy_guesses
    global enemy_ships
    global enemy_mines
    global enemy_cooldowns
    global enemy_pb_radar
    global enemy_sub_radar
    global enemy_promoted
    #Grid Vars
    global nums
    global A
    global B
    global C
    global D
    global E
    global F
    global G
    global H
    global I
    global J
    global num_rows

    game_over = False
    game += 1
    turn = 1

    nums = ["   "]
    A=["A "]
    B=["B "]
    C=["C "]
    D=["D "]
    E=["E "]
    F=["F "]
    G=["G "]
    H=["H "]
    I=["I "]
    J=["J "]
    num_rows = [A, B, C, D, E, F, G, H, I, J]
    hits = []
    misses = []
    hide = []
    sunken = []
    bloops = []
    mine_list = []

    player_ships_alive = 5
    player_board =[]
    player_guesses = []
    player_ships = ["player"]
    player_mines = []
    player_pb_radar = []
    player_sub_radar = []
    player_cooldowns = [0, 0, 0, 0, 0, 0]#PB, Destroyer, Sub, Battleship, AC, Battleship2
    player_promoted = False

    enemy_ships_alive = 5
    enemy_board = []
    enemy_guesses = []
    enemy_ships = ["enemy"]
    enemy_mines = []
    enemy_pb_radar = []
    enemy_sub_radar = []
    enemy_cooldowns = [0, 0, 0, 0, 0, 0]#PB, Destroyer, Sub, Battleship, AC, Battleship2
    enemy_promoted = False

    set_up()

def play_again():
    loop = True
    while loop == True:
        response = input("Play again? (Yes/No) ")
        if (response.lower()) == "yes":
            loop2 = True
            while loop2 == True:
                response = input("Review rules? (Yes/No) ")
                if response.lower() == "yes":
                    rules()
                    reset_game()
                    loop2 = False
                elif response.lower() == "no":
                    reset_game()
                    loop2 = False
                else:
                    print("Invalid response")
            loop = False
        elif (response.lower()) == "no":
            print("Thanks for playing!")
            loop = False
        else:
            print("Invalid response")

version()
rules()
set_up()
