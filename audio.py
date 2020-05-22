import os

try:
    import pygame
except ImportError: pass

class Audio(object):
    def preload_files(self, files):
        raise NotImplementedError()
    def stop(self):
        raise NotImplementedError()
    def speak(self, text):
        raise NotImplementedError()
    def play_wav(self, wavfile):
        raise NotImplementedError()
    def is_playing(self):
        raise NotImplementedError()
        
        
class SpeakService(object):
    def speak(self, text):
        raise NotImplementedError()
    def stop(self):
        raise NotImplementedError()
        
        
class PyTTSx3Service(SpeakService):
    def __init__(self):
        import pyttsx3, threading
        self.engine = pyttsx3.init()
        t = threading.Thread(target=self.engine.startLoop)
        t.setDaemon(True)
        t.start()
    def speak(self, text):
        self.engine.say(text)
    def stop(self):
        self.engine.stop()
        
class GoogleTTSService(SpeakService):
    def __init__(self):
        import hashlib, os, re
        from gtts import gTTS
        def h(s):
            return int(hashlib.sha256(s.encode("utf-8")).hexdigest(), 16) % 10**8
        self.gTTS = gTTS
        self.hash_func = h
        self.hash_files = {}
        files = os.listdir("tts_cache")
        regex = re.compile("(\d{8}).mp3")
        for f in files:
            m = regex.match(f)
            if m is not None:
                self.hash_files[int(m.group(1))] = 0
        
        
    def speak(self, text):
        hash_ = self.hash_func(text)
        hash_file = "tts_cache/"+str(hash_)+".mp3"
        if hash_ not in self.hash_files:
            print('New TTS file!')
            tts = self.gTTS(text, lang='en')
            tts.save(hash_file)
            self.hash_files[hash_] = 0
        pygame.mixer.music.load(hash_file)
        pygame.mixer.music.play()
        
    def stop(self):
        pygame.mixer.music.stop()
        
        
        
class PygameAudio(Audio):
    
    def __init__(self):
        pygame.mixer.init(frequency=32728)
        self._audio_cache = {}
        self.speak_service = GoogleTTSService()
        
    def preload_files(self, files):
        for filepath in files:
            if not os.path.isfile(filepath):
                filepath = 'todo replacement'
            data = pygame.mixer.Sound(filepath)
            self._audio_cache[filepath] = data
        
    def stop(self):
        pygame.mixer.stop()
        self.speak_service.stop()
    
    def speak(self, text):
        self.speak_service.speak(text)
    
    def play_wav(self, filepath):
        if filepath in self._audio_cache:
            data = self._audio_cache[filepath]
        else:
            data = pygame.mixer.Sound(filepath)
        data.play()
        
    def is_playing(self):
        return pygame.mixer.get_busy()