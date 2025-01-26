import mapbuilder
import pygame as pygame_module
import shutil

pygame_module.init()


def save(a_map):
    save_name = input('Name your save: ')
    overwrite = 'y'

    if mapbuilder.Path(f'saves/{save_name}').exists():
        overwrite = input('Save already exists. Overwrite? (y): ')

    if overwrite.lower() == 'y':
        a_mapbuilder.recursive_save(a_map, [0, 0], False)

        if mapbuilder.Path(f'saves/{save_name}').exists():
            shutil.rmtree(f'saves/{save_name}')
        shutil.copytree('saves/current_save', f'saves/{save_name}')

        return a_mapbuilder.build_map('saves/current_save/map.json')

def load():
    save_name = input('Load your save: ')

    if mapbuilder.Path(f'saves/{save_name}').exists():
        shutil.rmtree('saves/current_save')
        shutil.copytree(f'saves/{save_name}', 'saves/current_save')
        
        a_map = a_mapbuilder.build_map('saves/current_save/map.json')
    else:
        print('That save doesn\'t exist.')

    return a_map

def delete():
    # It's a pain, but I should be able to get input with event.unicode better... still have to blit it, annoyingly.
    save_name = input('Delete a save: ')

    if mapbuilder.Path(f'saves/{save_name}').exists():
        if save_name != ('current_save' or 'fresh_install'):
            shutil.rmtree(f'saves/{save_name}')
        else:
            print('Those files are crucial to the game. Please don\' delete them')
    else:
        print('That save doesn\'t exist.')

def toggle_fullscreen(fullscreen):
    # Pygame fullscreen EXTREMELY laggy.
    fullscreen = not fullscreen
    if fullscreen:
        screen = pygame_module.display.set_mode((0, 0), pygame_module.FULLSCREEN)
    else:
        screen = pygame_module.display.set_mode(screen_size)

    return screen, fullscreen

def event_loop(running, menu, fullscreen, screen, a_map):
    for event in pygame_module.event.get():
        if event.type == pygame_module.QUIT:
            running = False
            menu = False
            a_mapbuilder.recursive_save(a_map, [0, 0], False)
            pygame_module.quit()

        elif event.type == pygame_module.KEYUP:
            modifier_keys = pygame_module.key.get_mods()
            if event.key == pygame_module.K_RETURN:
                if modifier_keys & pygame_module.KMOD_ALT:
                    # Pygame fullscreen EXTREMELY laggy.
                    screen, fullscreen = toggle_fullscreen(fullscreen)

            if event.key == pygame_module.K_s:
                if modifier_keys & pygame_module.KMOD_CTRL:
                    a_map = save(a_map)

            if event.key == pygame_module.K_l:
                if modifier_keys & pygame_module.KMOD_CTRL:
                    a_map = load()

            if event.key == pygame_module.K_d:
                if modifier_keys & pygame_module.KMOD_CTRL:
                    delete()

            if event.key == pygame_module.K_p:
                menu = not menu

    return running, menu, fullscreen, screen, a_map

def fontify(text):
    return pygame_module.font.Font(None, 32).render(text, True, (200, 100, 0))


# Variable initialisation
screen_size = [480, 270]
scale_dictionary = {False: 2, True: 16 / 3}
running = True
menu = True
fullscreen = False
screen = pygame_module.display.set_mode(screen_size)
clock = pygame_module.time.Clock()

a_mapbuilder = mapbuilder.MapBuilder(pygame_module)
a_map = a_mapbuilder.build_map('saves/current_save/map.json')

pause = a_mapbuilder.get_flyweight('resources/templates/water.png', pygame_module.image.load)
pause.set_alpha(80)


while running:
    # Physics
    a_map.set_physics() 
    a_map.set_speed()
    a_map.get_player().breathe()
    moved_leaves = a_map.move()

    if moved_leaves:
        for moved_leaves_in_one_chunk in moved_leaves:
            for moved_leaf in moved_leaves_in_one_chunk:
                leaf, directions = moved_leaf
                a_map = a_mapbuilder.change_chunk(leaf, directions)

    # Graphics
    screen.fill('#FFFFFF')
    a_map.blit(screen, a_map.get_player(), scale_dictionary[fullscreen])
    screen.blit(fontify(str(a_map.get_player().oxygen)), (50, 200))
    pygame_module.display.update()

    # Event loop
    running, menu, fullscreen, screen, a_map = event_loop(running, menu, fullscreen, screen, a_map)
    clock.tick(100)

    # Menu
    if running:
        screen.blit(pygame_module.transform.scale_by(pause, scale_dictionary[fullscreen]), (0, 0))
    
    while menu:
        screen.blit(fontify('Paused'), (50, 30))
        screen.blit(fontify('Press \'p\' to unpause'), (50, 60))
        pygame_module.display.update()

        running, menu, fullscreen, screen, a_map = event_loop(running, menu, fullscreen, screen, a_map)

