# only library that the new process need
import sys
import os
import multiprocessing
import pathlib

from src.tools.generate_music import generator

PATH = pathlib.Path(__file__).parent

# region windows build support
# Module multiprocessing is organized differently in Python 3.4+
try:
    # Python 3.4+
    if sys.platform.startswith('win'):
        import multiprocessing.popen_spawn_win32 as forking
    else:
        import multiprocessing.popen_fork as forking
except ImportError:
    import multiprocessing.forking as forking

if sys.platform.startswith('win'):
    # First define a modified version of Popen.
    class _Popen(forking.Popen):
        def __init__(self, *args, **kw):
            if hasattr(sys, 'frozen'):
                # We have to set original _MEIPASS2 value from sys._MEIPASS
                # to get --onefile mode working.
                os.putenv('_MEIPASS2', sys._MEIPASS)
            try:
                super(_Popen, self).__init__(*args, **kw)
            finally:
                if hasattr(sys, 'frozen'):
                    # On some platforms (e.g. AIX) 'os.unsetenv()' is not
                    # available. In those cases we cannot delete the variable
                    # but only set it to the empty string. The bootloader
                    # can handle this case.
                    if hasattr(os, 'unsetenv'):
                        os.unsetenv('_MEIPASS2')
                    else:
                        os.putenv('_MEIPASS2', '')

    # Second override 'Popen' class with our modified version.
    forking.Popen = _Popen
# endregion

if __name__ == "__main__":
    multiprocessing.freeze_support()
    gn = generator(PATH / "assets" / "music" / "Halloween LOOP.wav")
    gn.start()

    import src.tools.tools as tl
    tl.MixeurAudio.gn = gn
    tl.MixeurAudio.music_factor = gn.sound_factor

    # import the gamew
    import src.pygame_edit
    from src.game import Game as game

    try:
        game.run()
    except SystemExit:
        gn.p.terminate()
        print("bye !")
