"""
Atomic Bay'ttle
Paul Mairesse, Axel Loones, Louis Le Meilleur, Joseph Bénard, Théo de Aranjo
This file launches the program
"""
# only library that the new process need
import sys
import os
import multiprocessing
import pathlib

from src.tools.generate_music import generator

PATH = pathlib.Path(__file__).parent


def renderer_smoke_test():
    """Headless packaged-build check for the GL context and shader pipeline."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    import moderngl
    import pygame

    from src.rendering import Renderer2D

    pygame.init()
    pygame.display.set_mode((32, 32))
    context = moderngl.create_standalone_context(require=330)
    framebuffer = context.simple_framebuffer((32, 32), components=4)
    framebuffer.use()
    renderer = Renderer2D(context, (32, 32))
    image = pygame.Surface((1, 1), pygame.SRCALPHA)
    image.fill("white")
    renderer.begin_frame()
    renderer.begin_pass((32, 32))
    renderer.draw(image, (0, 0, 32, 32))
    renderer.end_frame()
    assert framebuffer.read(components=4)[0:4] == bytes((255, 255, 255, 255))
    renderer.release()
    framebuffer.release()
    context.release()
    pygame.quit()


# region windows build support
# Module multiprocessing is organized differently in Python 3.4+
if sys.platform.startswith('win'):
    import multiprocessing.popen_spawn_win32 as forking
else:
    import multiprocessing.popen_fork as forking

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
    if "--renderer-smoke" in sys.argv:
        renderer_smoke_test()
        raise SystemExit(0)
    gn = generator(PATH / "assets" / "music" / "Halloween LOOP.wav")
    gn.start()

    import src.tools.tools as tl
    tl.MixeurAudio.gn = gn
    tl.MixeurAudio.music_factor = gn.sound_factor

    from src.game import Game as game

    try:
        game.run()
    except SystemExit:
        gn.p.terminate()
        game.rcp.p.terminate()
        print("bye !")
