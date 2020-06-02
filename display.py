import os

try:
    import pygame
except ImportError: pass



class Display(object):
    def display(self, menu):
        raise NotImplementedError()
    def preload_images(self, files):
        raise NotImplementedError()
    def load_image(self, imgpath):
        raise NotImplementedError()
    def get_mouse_pos(self):
        raise NotImplementedError()
    def draw_text(self, text, pos, color, font_id=0, centered=False):
        raise NotImplementedError()
    def draw_rect(self, rect, color):
        raise NotImplementedError()
    def draw_image(self, pos, image):
        raise NotImplementedError()


class PygameDisplay(Display):
        
    def __init__(self, size):
        pygame.display.init()
        pygame.font.init()
        pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))
        self.screen = pygame.display.set_mode(size)
        self.fonts = [
            pygame.font.SysFont('Impact', 30, bold=False),
            pygame.font.SysFont('Impact', 15, bold=False),
            pygame.font.SysFont('Arial Black', 20, bold=True, italic=True),
            pygame.font.SysFont('Arial Black', 20, bold=False, italic=False),
            pygame.font.SysFont('Arial', 15, bold=True, italic=False),
        ]
        self._text_cache = {}
        self._img_cache = {}
        
    
    def display(self):
        pygame.display.flip()
        self.screen.fill((255,255,255))
        
    def preload_images(self, files):
        for filepath in files:
            if not os.path.isfile(filepath):
                filepath = 'unknown.png'
            img = pygame.image.load(filepath).convert()
            self._img_cache[filepath] = pygame.transform.scale(img, (180,180))
        
    def load_image(self, imgpath):
        if imgpath in self._img_cache:
            return self._img_cache[imgpath]
        return pygame.transform.scale(pygame.image.load(imgpath), (180,180)).convert()
    
    def get_mouse_pos(self):
        return pygame.mouse.get_pos()
    
    
    def draw_text(self, text, pos, color, font_id=0, anchor=None):
        #if text not in self._text_cache:
        #    self._text_cache[text] = self.font.render(text, False, color)
        #self.screen.blit(self._text_cache[text], pos)
        text_surface = self.fonts[font_id].render(text, False, color)
        if anchor is not None:
            pos = [pos[0],pos[1]]
            if anchor[0] == 'mid':
                pos[0] = pos[0]-text_surface.get_width()//2
            elif anchor[0] == 'right':
                pos[0] = pos[0]-text_surface.get_width()
            if anchor[1] == 'mid':
                pos[1] = pos[1]-text_surface.get_height()//2
            elif anchor[1] == 'bottom':
                pos[1] = pos[1]-text_surface.get_height()
        self.screen.blit(text_surface, pos)
    
    def draw_rect(self, rect, color):
        pygame.draw.rect(self.screen, color, pygame.Rect(rect[0],rect[1],rect[2],rect[3]))
    
    def draw_image(self, pos, image):
        if not isinstance(image, pygame.Surface):
            image = pygame.surfarray.make_surface(image)
        self.screen.blit(image, pos)
    