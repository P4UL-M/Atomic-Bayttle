# only library that the new process need
from tools.generate_music import p,set_path
import pathlib

PATH = pathlib.Path(__file__).parent

set_path(PATH / "assets" / "music" / "Halloween LOOP.wav")

if __name__=="__main__":
    # start the process
    p.start()

    # import the game
    import pygame_edit
    from game import Game as game

    try:
        game.run()
    except SystemExit:
        p.kill()
        print("bye !")