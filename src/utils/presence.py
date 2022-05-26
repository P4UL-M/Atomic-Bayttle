"""
Atomic Bay'ttle
Paul Mairesse, Axel Loones, Louis Le Meilleur, Joseph Bénard, Théo de Aranjo
Script to modify presence on discord, use of multiprocessing for better performance
"""
from pypresence import Presence as pyPresence
from multiprocessing import Process, Value, Manager
from ctypes import c_char_p, c_float
import time as TIME


class Presence:
    p = None

    def __init__(self, id) -> None:
        self.m = Manager()
        self.details = self.m.Value(c_char_p, "Some text Here")
        self.time = self.m.Value(c_float, 0.0)
        self.id = id

    def start(self):
        if self.p is None:
            self.p = Process(target=worker, args=(self.id, self.details, self.time))
            self.p.start()
        else:
            print(self.p)


def worker(id, details, time):
    try:
        rcp = pyPresence(client_id=id)
        rcp.connect()
    except Exception as e:
        print("Error while connecting to discord : " + str(e))
        rcp = None
    val = ""
    last_update = TIME.time()
    while rcp is not None:
        if val != details.value or TIME.time() - last_update > 30:
            val = details.value
            try:
                if time.value:
                    rcp.update(details=val, large_image="ico", start=time.value)
                else:
                    rcp.update(details=val, large_image="ico")
            except:
                rcp = None
