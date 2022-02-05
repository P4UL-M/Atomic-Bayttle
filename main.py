from game_manager import Game as game

a = game()

if __name__=="__main__":
    try:
        a.run()
    except SystemExit:
        print("bye !")