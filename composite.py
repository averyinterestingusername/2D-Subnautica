

class Component:

    pygame = None
    mapbuilder = None
    water_physics = None
    air_physics = None

    def __init__(self):
        self.children = []
        self.parent = None

    def add_child(self, child):
        pass

    def remove_child(self, child):
        pass

    def blit(self, screen, world_position, scale):
        pass

    def move(self):
        pass

    def get_player(self):
        pass

    def get_root(self):
        pass

    def set_speed(self):
        pass

    def set_physics(self):
        pass


class Composite(Component):
    def __init__(self):
        super().__init__()

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

    def remove_child(self, child):
        self.children.remove(child)
        child.parent = None

    def blit(self, screen, world_position, scale):
        for child in self.children:
            child.blit(screen, world_position, scale)

    def move(self):
        moved_children = []
        for child in self.children:
            moved_child = child.move()

            if moved_child:
                moved_children.append(moved_child)
        
        if moved_children:
            return moved_children

    def get_player(self):
        for child in self.children:
            if child.get_player():
                return child.get_player()

    def get_root(self):
        if self.parent:
            return self.parent.get_root()
        else:
            return self

    def set_speed(self):
        for child in self.children:
            child.set_speed()

    def set_physics(self):
        for child in self.children:
            child.set_physics()
