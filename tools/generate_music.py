from multiprocessing import Process,Value,Manager,Queue
from pydub import AudioSegment

"""
A scrit that allow real time musique speed modification with calcul on another Proccess to avoid overloading the main boucle
"""

# method from https://stackoverflow.com/questions/51434897/how-to-change-audio-playback-speed-using-pydub
def speed_change(sound:AudioSegment, speed=1.0):
    # Manually override the frame_rate. This tells the computer how many
    # samples to play per second
    sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * speed)
    })

    # convert the sound with altered frame rate to a standard frame rate
    # so that regular playback programs will work right. They often only
    # know how to play audio at standard frame rate (like 44.1k)
    return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)

class generator:
    p = None

    def __init__(self,path) -> None:
        self.m = Manager()
        self.Sounds_buffer:Queue = self.m.Queue(maxsize=2)
        self.musique_original = AudioSegment.from_file(path)
        self.sound_factor = Value('d',1)
        self.sound_offset = 500

    def start(self):
        if self.p == None:
            self.p = Process(target=worker,args=(self.Sounds_buffer,self.sound_factor,self.musique_original,self.sound_offset))
            self.p.start()
        else:
            print(self.p)
    
    def reset(self):
        if self.p !=None:   
            self.p.terminate()
            self.p = None
        self.sound_factor.value = 1
        self.start()

def worker(buffer,factor,musique_original,sound_offset):
    # var declaration
    musique_alternate = musique_original # current study of the musique
    player_offset = sound_offset # offset of each sample
    max_occilation = 0.01 # max modification of speed between two sample (lesser => more faded)
    local_factor = factor.value # local factor of speed

    while True:
        if not buffer.full(): # if the Queue is not full
            # if local factor need update
            if local_factor<factor.value:
                local_factor += max_occilation
            elif local_factor>factor.value:
                local_factor -= max_occilation

            if len(musique_alternate) > player_offset*local_factor: # check if we can take a normal sample in the study
                sample, musique_alternate = musique_alternate[:player_offset*local_factor], musique_alternate[player_offset*local_factor:]
            else: # else we just play what rest and loop the study back
                sample,musique_alternate = musique_alternate,musique_original

            _sample = speed_change(sample,local_factor)
            _sample += min(5*local_factor - 15,0)
            _buffer = bytearray(_sample.raw_data)
            buffer.put(_buffer) # buffer send to the partaged Queue
