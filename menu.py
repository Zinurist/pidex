from controller import Actions as A

class Menu(object):
    def __init__(self, dex, display, audio, camera):
        self.dex = dex
        self.display = display
        self.audio = audio
        self.camera = camera
        self.previous_menu = self
        self.quit = False
    def update(self, delta_time, actions):
        raise NotImplementedError()
    def render(self):
        raise NotImplementedError()
    def enter(self): pass
    def swap_menu(self, menu):
        menu.previous_menu = self
        return menu
        
class QuitMenu(Menu):
    def __init__(self, dex, display, audio, camera):
        super().__init__(dex, display, audio, camera)
        self.quit = True
    def update(self, delta_time, actions): pass
    def render(self): pass
        
class MainMenu(Menu):
    def __init__(self, dex, display, audio, camera):
        super().__init__(dex, display, audio, camera)
        self.submenus = [
            DexScanner(dex, display, audio, camera),
            DexLister(dex, display, audio, camera),
            SettingsMenu(dex, display, audio, camera),
            QuitMenu(dex, display, audio, camera),
        ]
        
        self.menu_options = [
            'Scan', self.dex.name, 'Settings', 'Poweroff',
        ]
        self.cursor = 0
        
    def update(self, delta_time, actions):
        if A.MENU_OK in actions or A.MENU_RIGHT in actions:
            return self.swap_menu(self.submenus[self.cursor])
        elif A.MOUSE_CLICK in actions:
            pass
        elif A.MENU_UP in actions:
            self.cursor = (self.cursor-1) % len(self.menu_options)
        elif A.MENU_DOWN in actions:
            self.cursor = (self.cursor+1) % len(self.menu_options)
        
    def render(self):
        self.display.draw_text("Main", (10,10), (50,100,50))
        x,y = 30,60
        counter = 0
        for opt in self.menu_options:
            color = (250,10,100) if counter == self.cursor else (10,10,10)
            self.display.draw_text(opt, (x,y), color)
            y += 50
            counter += 1
        
        
class DexScanner(Menu):
    def __init__(self, dex, display, audio, camera):
        super().__init__(dex, display, audio, camera)
        self.entry_lister = DexEntryLister(dex, display, audio, camera, auto_speech=True)
        
    def update(self, delta_time, actions):
        if A.MENU_OK in actions or A.MENU_RIGHT in actions:
            index = self.scan()
            self.dex.set_current_entry(index)
            return self.swap_menu(self.entry_lister)
        elif A.MENU_LEFT in actions:
            return self.previous_menu
            
    def render(self):
        self.display.draw_text("Scanner", (10,10), (50,100,50))
        
    def scan(self):
        return 50
        

class DexLister(Menu):
    def __init__(self, dex, display, audio, camera):
        super().__init__(dex, display, audio, camera)
        self.entry_lister = DexEntryLister(dex, display, audio, camera, auto_cry=True)
        self.submenu_scanner = DexScanner(dex, display, audio, camera)
        self.cursor = 0
        self.cursor_submenu = 0
        self.submenus = 2
        self.view_start = 0
        self.view_len = 8
        self.prev_names_len = 0
        self.last_played_wav = -1
        self.last_img = -1
        
    def enter(self):
        self.audio.stop()
        self.names = self.dex.get_list()
        if self.cursor < 0 or self.prev_names_len != len(self.names):
            self.cursor = 0
        self.prev_names_len = len(self.names)
        
    def update(self, delta_time, actions):
        if A.MENU_OK in actions:
            if self.cursor == -1:
                if self.cursor_submenu == 0:
                    return self.previous_menu
                elif self.cursor_submenu == 1:
                    return self.swap_menu(self.submenu_scanner)
            else:
                self.dex.set_current_entry(self.cursor)
                return self.swap_menu(self.entry_lister)
        elif A.MENU_LEFT in actions:
            if self.cursor < 0:
                self.cursor_submenu = (self.cursor_submenu-1) % self.submenus
            else:
                self.cursor -= self.view_len
                self.view_start -= self.view_len
                if self.cursor < 0: self.cursor = 0
        elif A.MENU_RIGHT in actions:
            if self.cursor < 0:
                self.cursor_submenu = (self.cursor_submenu+1) % self.submenus
            else:
                self.cursor += self.view_len
                self.view_start += self.view_len
                if self.cursor >= len(self.names): self.cursor = len(self.names)-1
        elif A.MENU_UP in actions:
            if self.cursor < 0: 
                self.cursor = len(self.names)-1
            else:
                self.cursor -= 1
        elif A.MENU_DOWN in actions:
            self.cursor += 1
            if self.cursor >= len(self.names):
                self.cursor = -1
                self.view_start = 0
                
        if self.cursor < self.view_start:
            self.view_start = self.cursor
        elif self.cursor >= self.view_start+self.view_len:
            self.view_start = self.cursor - self.view_len +1
        self.view_start = max(0, min(len(self.names)-self.view_len, self.view_start))
        
        
    def render(self):
        self.display.draw_text(self.dex.name, (10,10), (50,100,50))
        self.display.draw_text("Back", (350,10), (250,10,100) if self.cursor<0 and self.cursor_submenu == 0 
                               else (10,10,10), font_id=1)
        self.display.draw_text("Scan", (400,10), (250,10,100) if self.cursor<0 and self.cursor_submenu == 1 
                               else (10,10,10), font_id=1)
        x,y = 350,60
        counter = 0
        for i in range(self.view_len):
            color = (250,10,100) if counter == self.cursor-self.view_start else (10,10,10)
            self.display.draw_text(self.names[i+self.view_start], (x,y), color, font_id=1, anchor=('left','mid'))
            self.display.draw_text(str(i+self.view_start+1), (x-25,y), color, font_id=2, anchor=('mid','mid'))
            y += 30
            counter += 1
        
        if self.cursor >= 0:
            self.last_img = self.display.load_image(self.dex.get_sprite_of(self.cursor))
        self.display.draw_image((60,60), self.last_img)
        
        if self.cursor >= 0 and self.cursor != self.last_played_wav:
            self.audio.stop()
            self.audio.play_wav(self.dex.get_sound_of(self.cursor))
            self.last_played_wav = self.cursor
        

class DexEntryLister(Menu):
    def __init__(self, dex, display, audio, camera, auto_speech=False, auto_cry=False):
        super().__init__(dex, display, audio, camera)
        self.auto_cry = auto_cry
        self.auto_speech = auto_speech
        self.auto_cry_done = False
        self.auto_speech_done = False
        self.description_page = 0
        self.last_page = 0
        self.pkmn_img = None
        
    def enter(self):
        self.data = self.dex.get_current_entry()
        self.auto_cry_done = False
        self.auto_speech_done = False
        self.pkmn_img = self.display.load_image(self.data['image'])
    
    def update(self, delta_time, actions):
        if A.MENU_OK in actions:
            self.audio.stop()
            if self.description_page == 0:
                self.audio.play_wav(data['sound'])
            elif self.description_page == 1:
                self.audio.speak(data['description'])
        elif A.MENU_LEFT in actions:
            # if show text > back
            self.description_page -= 1
            if self.description_page < 0:
                self.description_page = 0
                return self.previous_menu
        elif A.MENU_RIGHT in actions:
            self.description_page += 1
            if self.description_page >= self.last_page:
                self.description_page = self.last_page
                self.audio.stop()
                self.audio.speak(self.data['description'])
        elif A.MENU_UP in actions:
            self.dex.prev_entry()
            self.enter()
        elif A.MENU_DOWN in actions:
            self.dex.next_entry()
            self.enter()
        
    def render(self):
        self.display.draw_text(self.data['name'], (100,20), (50,100,50), anchor=('mid', 'top'))
        self.display.draw_image((10,60), self.pkmn_img)
        self.display.draw_text(self.data['type1'], (10+45,270), (50,100,50), anchor=('mid', 'top'), font_id=3)
        self.display.draw_text(self.data['type2'], (10+45+90,270), (50,100,50), anchor=('mid', 'top'), font_id=3)
        descrps = self.data['description'].split('\n')
        y = 60
        for text in descrps:
            self.display.draw_text(text, (200,y), (50,100,50), font_id=4)
            y+= 30
        
        
        if not self.auto_cry_done and self.auto_cry:
            self.audio.stop()
            self.audio.play_wav(self.data['sound'])
            self.auto_cry_done = True
        if not self.auto_speech_done and self.auto_speech:
            if not(self.auto_cry and self.audio.is_playing()): #auto cry still playing
                self.audio.stop()
                self.audio.speak(self.data['description'])
                self.auto_speech_done = True

class SettingsMenu(Menu):
    def __init__(self, dex, display, audio, camera):
        super().__init__(dex, display, audio, camera)
    
    def update(self, delta_time, actions):
        if A.MENU_OK in actions:
            pass
        elif A.MENU_LEFT in actions:
            return self.previous_menu
        elif A.MENU_RIGHT in actions:
            pass
        elif A.MENU_UP in actions:
            pass
        elif A.MENU_DOWN in actions:
            pass
       
        
    def render(self):
        self.display.draw_text("Settings", (10,10), (50,100,50))
        