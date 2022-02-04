from game import Game as game

if __name__=="__main__":
    try:
        game.run()
    except SystemExit:
        print("bye !")