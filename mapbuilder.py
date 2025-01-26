import leaves
import json
from pathlib import Path
import physics


class MapBuilder:
    def __init__(self, pygame_module):
        self.buildables = {'chunk': leaves.Chunk, 'player': leaves.Player, 'resource': leaves.Resource,
                           'structure': leaves.Structure, 'item': leaves.Item, 'creature': leaves.Creature}
        self.state_poppers = ['type', 'parent', 'image', 'mask', 'element', 'element_mask', 'physics', 'physic']
        self.flyweights = {}  # {flyweight_parameter: flyweight} or {key: flyweight}

        # If my flyweight system collapses, this is about what the book suggests.
        # self.flyweight_codes = {'element_water': element_water}  # {key: lambda for that key}
        # element_water = lambda sry: pygame_module.image.load('element_water_path')  # lambda input: class(input) or lambda nothing: class(static_input)

        self.map_path = 'saves/current_save/map.json'
        self.file_path = lambda chunk_grid_position: f'saves/current_save/chunk_col_{chunk_grid_position[0]}/chunk_row_{chunk_grid_position[1]}/chunk.json'
        self.shifted_file_path = lambda chunk_grid_position, directions: f'saves/current_save/chunk_col_{chunk_grid_position[0] + directions[0]}/chunk_row_{chunk_grid_position[1] + directions[1]}/chunk.json'
        self.filepath_getter = lambda is_player, child_type, chunk_grid_position, directions: {True: {'chunk': self.shifted_file_path(chunk_grid_position, directions)}.get(child_type, self.map_path)}.get(is_player, {'chunk': self.file_path(chunk_grid_position)}.get(child_type, self.map_path))

        physics.Physics.pygame = pygame_module
        a_water_physics = physics.WaterPhysics()
        an_air_physics = physics.AirPhysics()
        leaves.composite.Component.water_physics = a_water_physics
        leaves.composite.Component.air_physics = an_air_physics
        leaves.composite.Component.pygame = pygame_module
        leaves.composite.Component.mapbuilder = self

    def build_map(self, filepath):
        with open(filepath, 'r') as map_json:
            map_dictionary = json.loads(map_json.read())

        return self.recursive_build(map_dictionary)

    def recursive_build(self, json_dictionary):
        if 'children' in json_dictionary:
            current_composite = leaves.composite.Composite()
            for child in json_dictionary['children']:
                if 'path' in child:
                    if Path(child['path']).exists():
                        with open(child['path'], 'r') as child_json_file:
                            file_contents = child_json_file.read()
                            child_json_dictionary = json.loads(file_contents)
                            child_composite = self.recursive_build(child_json_dictionary)
                            current_composite.add_child(child_composite)
                    else:
                        raise Exception(f'Error in finding path {child["path"]} of a composite.')
                else:
                    current_composite.add_child(self.buildables[child['type']](child))
            return current_composite
        else:
            raise Exception('If it has no children, then you don\'t need to build recursively!')

    def get_flyweight(self, flyweight_parameter, flyweight_class):
        if self.flyweights.get(flyweight_parameter):
            return self.flyweights[flyweight_parameter]  # If multiple parameters, no idea.
        else:
            flyweight = flyweight_class(flyweight_parameter)
            self.flyweights[flyweight_parameter] = flyweight
            return flyweight

    def change_chunk(self, leaf, directions):  # Maybe parameterise a filepath. If you want.
        # Must account for falling items as well! Well, later.
        new_chunk_index = 4 + directions[0] + directions[1] * 3

        root = leaf.get_root()
        new_chunk = root.children[new_chunk_index]

        leaf.parent.remove_child(leaf)
        new_chunk.add_child(leaf)

        # Quick and Dirty.
        is_player = leaf.type == 'player'

        filepath = self.recursive_save(root, directions, is_player)['path']

        root = self.build_map(filepath)

        return root

    def recursive_save(self, current_composite, directions, is_player):
        if current_composite.children:
            file_contents = {'children': []}
            
            for child in current_composite.children:
                child_state = self.recursive_save(child, directions, is_player)
                file_contents['children'].append(child_state)

            shifted_filepath = self.save_composite(file_contents, directions, is_player)

            return {'path': shifted_filepath}
        else:
            return self.save_leaf(current_composite)
        
    def save_composite(self, file_contents, directions, is_player):
        save_contents = json.dumps(file_contents)

        filepath, shifted_filepath = self.get_save_filepath(file_contents, directions, is_player)

        with open(filepath, 'w') as file:
            file.write(save_contents)

        return shifted_filepath

    def get_save_filepath(self, file_contents, directions, is_player):  # Why did I do this to myself again? I should just have kept the conditionals.
        chunk_grid_position = file_contents.get("children", [{}])[0].get("state", {"chunk_grid_position": [0, 0]}).get("chunk_grid_position")
        child_type = file_contents.get("children", [{}])[0].get('type')

        filepath = self.filepath_getter(False, child_type, chunk_grid_position, directions)
        shifted_filepath = self.filepath_getter(is_player, child_type, chunk_grid_position, directions)

        return filepath, shifted_filepath

    def save_leaf(self, leaf):
        leaf_state = leaf.__dict__

        leaf_type = leaf_state['type']

        for state_popper in self.state_poppers:
            if leaf_state.get(state_popper):
                leaf_state.pop(state_popper)

        json_dictionary = {'type': leaf_type, 'state': leaf_state}

        return json_dictionary
