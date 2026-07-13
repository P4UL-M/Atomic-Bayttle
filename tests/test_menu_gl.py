import moderngl
import pytest

from pygame_easy_menu import ModernGLBackend

import src.menu_main as menu_main


def test_main_menu_renders_natively_in_shared_context(monkeypatch):
    try:
        context = moderngl.create_standalone_context(require=330)
    except Exception as error:
        pytest.skip(f"OpenGL 3.3 context unavailable on this runner: {error}")
    framebuffer = context.simple_framebuffer((320, 180), components=4)
    framebuffer.use()

    class FakeGame:
        menu_backend = staticmethod(
            lambda size: ModernGLBackend.from_context(context, size, (320, 180))
        )
        start_partie = staticmethod(lambda *_args: None)

    menu_main.GAME = FakeGame
    menu_main.CAMERA = type("Camera", (), {})
    monkeypatch.setattr(menu_main.MixeurAudio, "load", lambda *_args: None)
    monkeypatch.setattr(menu_main.Keyboard, "load", lambda *_args: None)
    menu_main.setup_manager()
    menu_main.game.update([])
    menu_main.game.render()

    assert len(menu_main.game.menus) == 6
    assert menu_main.game.backend.texture_count > 0
    menu_main.game.release()
    framebuffer.release()
    context.release()
