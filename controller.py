from enum import Enum

try:
    import pygame
except ImportError: pass


class Actions(Enum):
    MENU_LEFT=1
    MENU_RIGHT=2
    MENU_UP=3
    MENU_DOWN=4
    MENU_OK=5
    MOUSE_CLICK=6
    QUIT=7
    
    
    
class Controller(object):
    def get_actions(self):
        raise NotImplementedError()
        
class DummyController(Controller):
    def get_actions(self):
        return [],(0,0)
        
        
class PygameController(Controller):
    
    def __init__(self):
        self.key_bindings = {
            pygame.K_LEFT : Actions.MENU_LEFT,
            pygame.K_RIGHT : Actions.MENU_RIGHT,
            pygame.K_UP : Actions.MENU_UP,
            pygame.K_DOWN : Actions.MENU_DOWN,
            pygame.K_RETURN : Actions.MENU_OK,
        }
        
    def get_actions(self):
        actions = []
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key in self.key_bindings:
                actions.append(self.key_bindings[event.key])
                    
            if event.type == pygame.QUIT:
                actions.append(Actions.QUIT)
                
            if event.type == pygame.MOUSEBUTTONUP:
                actions.append(Actions.MOUSE_CLICK)
        return actions