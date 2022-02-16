from multiprocessing import Process,Value,Queue
from pydub import AudioSegment
import logging

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

musique_original = None

def set_path(path):
    global musique_original
    musique_original = AudioSegment.from_file(path)

sound_factor = Value('d',1)
sound_offset = 500

Sounds_buffer = Queue(maxsize=2) # maxsize will be interfering with the update (less = more reactive but less resilient to lag)

def generator(sound_buffer:Queue,factor:Value,offset:int=500):
    # var declaration
    musique_alternate = musique_original # current study of the musique
    player_offset = offset # offset of each sample
    max_occilation = 0.01 # max modification of speed between two sample (lesser => more faded)
    local_factor = factor.value # local factor of speed

    while True:
        if not Sounds_buffer.full(): # if the Queue is not full
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
            buffer = bytearray(_sample.raw_data)
            sound_buffer.put(buffer) # buffer send to the partaged Queue

p = Process(target=generator,args=(Sounds_buffer,sound_factor,sound_offset),daemon=True)