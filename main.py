from tools.generate_music import p,set_path
import pathlib

PATH = pathlib.Path(__file__).parent

set_path(PATH / "assets" / "music" / "Halloween LOOP.wav")

if __name__=="__main__":
    from game import Game as game
    
    try:
        p.start()
        game.run()
    except SystemExit:
        print("bye !")