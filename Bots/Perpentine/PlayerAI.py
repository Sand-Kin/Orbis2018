'''if __name__ == '__main__':
    from os import path
    import sys
    #sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))) + '/Libraries')'''

from PythonClientAPI.game.PointUtils import *
from PythonClientAPI.game.Entities import FriendlyUnit, EnemyUnit, Tile
from PythonClientAPI.game.Enums import Team
from PythonClientAPI.game.World import World
from PythonClientAPI.game.TileUtils import TileUtils

class PlayerAI:

    def __init__(self):
        ''' Initialize! '''
        self.turn_count = 0             # game turn count
        self.target = None              # target to send unit to!
        self.outbound = True            # is the unit leaving, or returning?


    def evaluatePoint(self, testPoint, world, friendly_unit, enemy_units):

        #weights
        PT = 1 #points
        DD = 1 #deathdistance
        BL = 1 #bodyLength
        SD = 1 #safeDistance
        CD = 1 #captureDistance



        deathDist = float('inf') #change to none?
        bodyLength = 0
        for bodyPoint in friendly_unit.snake:
            bodyLength += 1
            newPoint = world.util.get_closest_enemy_head_from(bodyPoint, None).position
            newDist = world.path.get_shortest_path_distance(newPoint, bodyPoint)
            if (newDist < deathDist):
                deathDist = newDist


        ##NONE NEEDS TO BE REPLACED WITH AVOID LIST OF WALLS
        ##channging friendly unit positions to testPoint
        hypoMove = world.util.get_closest_friendly_territory_from(testPoint, friendly_unit.body).position
        hypoPath = world.path.get_shortest_path(testPoint, hypoMove, friendly_unit.body)
        hypoBody = friendly_unit.snake
        hypoBody.union(set(hypoPath[:-1]))
        hypoBody.union(set(testPoint))

        points = 0

        if len(hypoPath) == 1:
            lastStep = testPoint
        else:
            lastStep = hypoPath[-2]

        for filled in world.fill.flood_fill(hypoBody, friendly_unit.territory, lastStep, hypoMove):
            rfilled = world.position_to_tile_map[filled]
            if rfilled.is_neutral:
                points += 1

            if rfilled.is_enemy:
                points += 2  ##possibly change to 1.33

        capturePoint = world.util.get_closest_capturable_territory_from(testPoint, None).position
        captureDist = world.path.get_shortest_path_distance(testPoint, capturePoint)

        #distance to safety
        safeDist = world.path.get_shortest_path_distance(testPoint, hypoMove)
        if (testPoint in friendly_unit.territory) and (friendly_unit.position not in friendly_unit.territory) and (bodyLength > 4):
            safeDist = 0.1

        safeBonus = 0
        if (deathDist <= safeDist + 2):
            safePoint = world.util.get_closest_friendly_territory_from(friendly_unit.position, friendly_unit.body).position
            safePath = world.path.get_shortest_path(friendly_unit.position, safePoint, friendly_unit.body)

            if testPoint in safePath:
                safeBonus += 100

        headPoint = world.util.get_closest_enemy_head_from(testPoint, None).position
        headDist = world.path.get_shortest_path_distance(testPoint, headPoint)
        if headDist < 3:
            safeBonus -= 100


        if safeDist < 5 and self.turns_outside < 10:
            H = PT * points + CD / captureDist + safeBonus + safeDist
        else:
            H = PT * points + SD / safeDist + CD / captureDist + safeBonus

        return H



    def do_move(self, world, friendly_unit, enemy_units):


        if friendly_unit.position in friendly_unit.territory:
            self.turns_outside = 0
        else:
            self.turns_outside += 1
        '''
        This method is called every turn by the game engine.
        Make sure you call friendly_unit.move(target) somewhere here!

        Below, you'll find a very rudimentary strategy to get you started.
        Feel free to use, or delete any part of the provided code - Good luck!

        :param world: world object (more information on the documentation)
            - world: contains information about the game map.
            - world.path: contains various pathfinding helper methods.
            - world.util: contains various tile-finding helper methods.
            - world.fill: contains various flood-filling helper methods.

        :param friendly_unit: FriendlyUnit object
        :param enemy_units: list of EnemyUnit objects
        '''

        '''# increment turn count
        self.turn_count += 1

        # if unit is dead, stop making moves.
        if friendly_unit.status == 'DISABLED':
            print("Turn {0}: Disabled - skipping move.".format(str(self.turn_count)))
            self.target = None
            self.outbound = True
            return

        # if unit reaches the target point, reverse outbound boolean and set target back to None
        if self.target is not None and friendly_unit.position == self.target.position:
            self.outbound = not self.outbound
            self.target = None

        # if outbound and no target set, set target as the closest capturable tile at least 1 tile away from your territory's edge.
        #if self.outbound and self.target is None:

        edges = [tile for tile in world.util.get_friendly_territory_edges()]
        avoid = []
        for edge in edges:
            avoid += [pos for pos in world.get_neighbours(edge.position).values()]

        if self.outbound:

            self.target = world.util.get_closest_capturable_territory_from(friendly_unit.position, avoid)

            n = world.util.get_closest_friendly_territory_from(friendly_unit.position, None).position
            safeDist = world.path.get_shortest_path_distance(friendly_unit.position, n)

            deathDist = 100000
            for bodyPoint in friendly_unit.snake:
                newPoint = world.util.get_closest_enemy_head_from(bodyPoint, None).position
                newDist = world.path.get_shortest_path_distance(newPoint, bodyPoint)
                if (newDist < deathDist) or (deathDist == None):
                    deathDist = newDist

            if (deathDist <= (safeDist + 1)):
                self.outbound = not self.outbound
                self.target = world.util.get_closest_friendly_territory_from(friendly_unit.position, avoid)

            else:
                edges = [tile for tile in world.util.get_friendly_territory_edges()]
                avoid = []
                for edge in edges:
                    avoid += [pos for pos in world.get_neighbours(edge.position).values()]
                self.target = world.util.get_closest_capturable_territory_from(friendly_unit.position, avoid)

        else:
            self.target = world.util.get_closest_friendly_territory_from(friendly_unit.position, avoid)


        if self.target == None:
            self.target = world.util.get_closest_friendly_territory_from(friendly_unit.position, avoid)
        # set next move as the next point in the path to target'''






        #construct array of ajacent points:

        testPoints = []
        testPoints.append((friendly_unit.position[0], friendly_unit.position[1] + 1))
        testPoints.append((friendly_unit.position[0], friendly_unit.position[1] - 1))
        testPoints.append((friendly_unit.position[0] + 1, friendly_unit.position[1]))
        testPoints.append((friendly_unit.position[0] - 1, friendly_unit.position[1]))

        #determining best target
        print('your position')
        print(friendly_unit.position)

        maxVal = -10000000   #change to none?
        for testPoint in testPoints:

            if world.is_edge(testPoint):
                continue
            if world.is_wall(testPoint):
                continue
            if testPoint in friendly_unit.body:
                continue

            print(testPoint)
            val = self.evaluatePoint(testPoint, world, friendly_unit, enemy_units)
            if val > maxVal:
                maxVal = val
                next_move = testPoint
        print('next move is')
        print(next_move)

        #move!
        friendly_unit.move(next_move)






        # move!
        #next_move = world.path.get_shortest_path(friendly_unit.position, self.target.position, friendly_unit.snake)[0]
        
        '''print("Turn {0}: currently at {1}, making {2} move to {3}.".format(
            str(self.turn_count),
            str(friendly_unit.position),
            'outbound' if self.outbound else 'inbound',
            str(self.target.position)
        ))'''

'''if __name__ == '__main__':
    import numpy as np
    mock = np.load('/home/comicsands/ORBIS/Serpentine/Bots/Perpentine/mock.npz')
    actor = PlayerAI()
    actor.do_move(*(mock['arr_0']))'''