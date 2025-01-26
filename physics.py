import math


class Physics:

    pygame = None

    def __init__(self):
        self.keys = {}

        # Essentially just checks if the key is being pressed and returns the dictionary values. & Checks if the player is allowed to jump.
        self.speed_getter = lambda key, keys_pressed: {True: self.keys[key]}.get(keys_pressed[key])
        self.speed_checker = lambda key, keys_pressed, player: {self.pygame.K_SPACE: {player.speeds[1]: self.speed_getter(key, keys_pressed)}.get(0)}  # Issue: The player can still jump when touching underside of something.
        self.speed_sorter = lambda key, keys_pressed, player: self.speed_checker(key, keys_pressed, player).get(key, self.speed_getter(key, keys_pressed))

        # I cannot seem to find decent values.
        self.gravity = 0.05
        self.resistance = []

    def set_leaf_speed(self, leaf):
        leaf.speeds[1] += self.gravity

    def set_player_speed(self, player):
        keys_pressed = self.pygame.key.get_pressed()

        # Lol you can fly on the roof.
        speed_setters = [self.speed_sorter(key, keys_pressed, player) for key in self.keys]

        for speed_setter in speed_setters:
            if speed_setter:
                player.speeds[speed_setter['axis']] += speed_setter['speed']

    def set_creature_speed(self):
        pass

    def move(self, leaf):
        directions = [0, 0]

        for axis in range(2):
            self.actually_move(leaf, axis)
                
            leaf.speeds[axis] *= self.resistance[axis]

            directions[axis] = self.chunk_change_direction(axis, leaf)

        if directions != [0, 0]:
            return leaf, directions
        
    def actually_move(self, leaf, axis):
        steps = math.ceil(abs(leaf.speeds[axis]))

        for step in range(steps):
                leaf.world_position[axis] += leaf.speeds[axis] / steps

                for chunk in leaf.get_root().children:
                    collision = self.check_collision(leaf, chunk.children[0], chunk.children[0].mask)

                    if collision:
                        leaf.world_position[axis] -= leaf.speeds[axis] / steps
                        leaf.speeds[axis] = 0
        
    def chunk_change_direction(self, axis, leaf):
        return int(leaf.world_position[axis] // leaf.parent.children[0].image.get_size()[axis] - leaf.parent.children[0].chunk_grid_position[axis])
    
    def check_collision(self, leaf0, leaf1, leaf1_mask):
        return leaf1_mask.overlap(leaf0.mask, self.collision_offset(leaf0.world_position, leaf1.world_position))  
                
    def collision_offset(self, leaf0_world_pos, leaf1_world_pos):
        return leaf0_world_pos[0] - leaf1_world_pos[0], leaf0_world_pos[1] - leaf1_world_pos[1]
    
    def breathe(self, player):
        pass


class WaterPhysics(Physics):
    def __init__(self):
        super().__init__()

        self.resistance = [0.01, 0.01]
        self.keys = {
            self.pygame.K_w: {'axis': 1, 'speed': -2},
            self.pygame.K_s: {'axis': 1, 'speed': 2},
            self.pygame.K_d: {'axis': 0, 'speed': 2},
            self.pygame.K_a: {'axis': 0, 'speed': -2},
        }
        
    def breathe(self, player):
        if player.oxygen > 0:
            player.oxygen -= 0.02
            player.oxygen = round(player.oxygen, 2)
        else:
            # I mean... Hurry up and implement this.
            print('You died.')


class AirPhysics(Physics):
    def __init__(self):
        super().__init__()

        self.resistance = [0.1, 0.999]
        self.keys = {
            self.pygame.K_d: {'axis': 0, 'speed': 2},
            self.pygame.K_a: {'axis': 0, 'speed': -2},
            self.pygame.K_SPACE: {'axis': 1, 'speed': -2},
        }

    def set_player_speed(self, player):
        super().set_player_speed(player)
        self.set_leaf_speed(player)
        
    def breathe(self, player):
        if player.oxygen_limit > player.oxygen:
            player.oxygen += 0.05
            player.oxygen = round(player.oxygen, 2)
