import composite


class Leaf(composite.Component):
    def __init__(self, save):
        super().__init__()

        self.type = save['type']

        self.image_path = save['state'].get('image_path')
        self.image = self.mapbuilder.get_flyweight(self.image_path, self.pygame.image.load)
        self.mask = self.mapbuilder.get_flyweight(self.image, self.pygame.mask.from_surface)

        self.world_position = save['state'].get('world_position')
        self.speeds = save['state'].get('speeds')
        self.physics = None
        self.physic = {True: self.water_physics, False: self.air_physics}

    def blit(self, screen, player, scale):
        # Calculating the offset is still a pain.
        offset = (self.world_position[0] - player.world_position[0] - player.image.get_size()[0] / 2) * scale + self.pygame.display.get_window_size()[0] / 2, \
                 (self.world_position[1] - player.world_position[1] - player.image.get_size()[1] / 2) * scale + self.pygame.display.get_window_size()[1] / 2
        
        screen.blit(self.pygame.transform.scale_by(self.image, scale), offset)

        return offset

    def set_physics(self):
        # Checking collision with water_physics, in order to set physics. Not optimal.
        collision = self.water_physics.check_collision(self, self.parent.children[0], self.parent.children[0].element_mask)
        self.physics = self.physic[type(collision) == tuple]

    def set_speed(self):
        self.physics.set_leaf_speed(self)

    def move(self):         
        return self.physics.move(self)
    
    def get_root(self):
        return self.parent.get_root()


class Chunk(Leaf):
    def __init__(self, save):
        super().__init__(save)

        self.chunk_grid_position = save['state'].get('chunk_grid_position')
        self.element_path = save['state'].get('element_path')
        self.element = self.mapbuilder.get_flyweight(self.element_path, self.pygame.image.load)
        self.element_mask = self.mapbuilder.get_flyweight(self.element, self.pygame.mask.from_surface)

    def blit(self, screen, player, scale):
        # Minor issue about the blitting order: when player leaves the water, element is partially blitted over him.
        offset = super().blit(screen, player, scale)
        screen.blit(self.pygame.transform.scale_by(self.element, scale), offset)

    def set_physics(self):
        pass        

    def set_speed(self):
        pass

    def move(self):
        pass


class Player(Leaf):
    def __init__(self, save):
        super().__init__(save)
        
        self.oxygen = save['state'].get('oxygen')
        self.oxygen_limit = 50

    def set_speed(self):
        # I really want the player to be able to hover at the surface of the water, so that he can breathe.
        self.physics.set_player_speed(self)

    def get_player(self):
        return self
    
    def breathe(self):
        self.physics.breathe(self)


class Structure(Leaf):
    def __init__(self, save):
        super().__init__(save)


class Resource(Leaf):
    def __init__(self, save):
        super().__init__(save)


class Item(Leaf):
    def __init__(self, save):
        super().__init__(save)

        self.speeds = save['state'].get('speeds')


class Creature(Leaf):
    def __init__(self, save):
        super().__init__(save)

        self.speeds = save['state'].get('speeds')

# # # 
