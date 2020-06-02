

def get_display():
    from display import PygameDisplay as Display
    return Display()

def get_audio():
    from audio import PygameAudio as Audio
    return Audio()

def get_controller():
    from controller import PygameController as Controller
    return Controller()

def get_camera():
    from camera import OpenCVCamera as Camera
    return Camera()

def get_dex():
    from dex import VeekunPokedex as Dex
    return Dex()

def get_menu(dex, display, audio, camera):
    from menu import MainMenu as Menu
    return Menu(dex, display, audio, camera)



def main():
    print('Starting PokeDex')
    
    #output interfaces
    display = get_display()
    audio = get_audio()
    
    #input interfaces
    controller = get_controller()
    camera = get_camera()
    
    #data
    dex = get_dex()
    
    #connect everything
    menu = get_menu(dex, display, audio, camera)
    
    #preload
    #display.preload_images(dex.get_image_files())
    #audio.preload_files(dex.get_sound_files())
    
    import time
    from controller import Actions as A
    start_time = time.time()
    while True:
        time.sleep(0.001)
        end_time = time.time()
        delta_time = end_time - start_time
        start_time = end_time
        
        actions = controller.get_actions()
        next_menu = menu.update(delta_time, actions)
        if next_menu is not None: 
            menu = next_menu
            menu.enter()
        if menu.quit or A.QUIT in actions: break
        menu.render()
        display.display()
        
        


if __name__ == '__main__':
    if len(sys.argv) == 1:
        import os
        os.putenv('SDL_VIDEODRIVER', 'fbcon')
        os.putenv('SDL_FBDEV', '/dev/fb1')
    main()





