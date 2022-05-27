from pydub.utils import mediainfo
from pydub.playback import play
from pydub import AudioSegment
from pydub.effects import normalize

class audio():
    def __init__(self, address) -> None:
        self.sound = AudioSegment.from_file(address)
        self.address = address

    def trim(self, from_time, to_time):
        from_sec, from_milsec = list(map(int, from_time.split(":")))
        to_sec, to_milsec = list(map(int, to_time.split(":")))
        first_cut_point = (from_milsec/100 + from_sec) * 1000
        last_cut_point = (to_milsec/100 + to_sec) * 1000
        self.sound = self.sound[first_cut_point:last_cut_point]
        
    def trim_and_attach(self, from_time1, to_time1, from_time2, to_time2):
        from1_sec, from1_milsec = list(map(int, from_time1.split(":")))
        to1_sec, to1_milsec = list(map(int, to_time1.split(":")))
        
        from2_sec, from2_milsec = list(map(int, from_time2.split(":")))
        to2_sec, to2_milsec = list(map(int, to_time2.split(":")))
        
        print(from1_sec, from1_milsec, ":", to1_sec, to1_milsec)
        print(from2_sec, from2_milsec, ":", to2_sec, to2_milsec)
        
        from_first_cut_point = (from1_milsec/100 + from1_sec) * 1000
        to_first_cut_point = (to1_milsec/100 + to1_sec) * 1000
        
        from_second_cut_point = (from2_milsec/100 + from2_sec) * 1000
        to_second_cut_point = (to2_milsec/100 + to2_sec) * 1000
        
        self.sound = self.sound[from_first_cut_point:to_first_cut_point] + self.sound[from_second_cut_point:to_second_cut_point]
        
    def increase_vol(self, vol, time=0):
        sound_clip = self.sound[:time*1000] + vol
        if(time != 0):
            self.sound = sound_clip + self.sound[time*1000:]
        else:
            self.sound = sound_clip
        
    def attach(self, sound2):
        self.sound = self.sound + sound2
        
    def add_between(self, sound2, at_time):
        sound2 = sound2.sound
        at_sec, at_milsec = list(map(int, at_time.split(":")))
        at_cut_point = (at_milsec/100 + at_sec) * 1000
        self.sound = self.sound[:at_cut_point] + sound2 + self.sound[at_cut_point:]
        
    # 1:42 - 2:42
    def change_between(self, sound2, from_time, to_time):
        sound2 = sound2.sound
        from_sec, from_milsec = list(map(int, from_time.split(":")))
        to_sec, to_milsec = list(map(int, to_time.split(":")))
        
        from_cut_point = (from_milsec/100 + from_sec) * 1000
        to_cut_point = (to_milsec/100 + to_sec) * 1000
        
        self.sound = self.sound[:from_cut_point] + sound2 + self.sound[to_cut_point:]
        
    def export(self, filename):
        print("[LOG] Exporting at:", filename)
        self.sound = normalize(self.sound)
        self.sound.export(filename, format="wav")
    
    def len(self):
        return self.sound.duration_seconds
