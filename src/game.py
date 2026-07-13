"""Atomic Bayttle main loop and ModernGL scene orchestration."""

from __future__ import annotations

import sys

import pygame
from pygame.locals import DOUBLEBUF, FULLSCREEN, OPENGL

from src.rendering import Camera2D, RenderQueueSurface, Renderer2D
from src.tools.constant import PATH
from src.tools.tools import ScreenSize, Vector2


def _show_gl_error(error: Exception) -> None:
    """Show a readable diagnostic without providing a gameplay fallback."""
    message = f"OpenGL 3.3 is required. Update your graphics driver.\n\n{error}"
    print(message, file=sys.stderr)
    try:
        pygame.display.quit()
        pygame.display.init()
        screen = pygame.display.set_mode((760, 240))
        pygame.display.set_caption("Atomic Bayttle - OpenGL error")
        font = pygame.font.Font(None, 28)
        screen.fill((25, 22, 22))
        lines = [
            "Atomic Bayttle cannot create an OpenGL 3.3 context.",
            "Please update the graphics driver or use a compatible computer.",
            str(error)[:100],
            "Press any key to close.",
        ]
        for index, line in enumerate(lines):
            screen.blit(font.render(line, True, (245, 225, 225)), (24, 28 + index * 45))
        pygame.display.flip()
        deadline = pygame.time.get_ticks() + 15000
        while pygame.time.get_ticks() < deadline:
            event = pygame.event.wait(100)
            if event.type in (pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONUP):
                break
    except Exception:
        pass


pygame.init()
try:
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(
        pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE
    )
    pygame.display.set_mode(
        (0, 0), OPENGL | DOUBLEBUF | FULLSCREEN, depth=24, vsync=1
    )
    import moderngl

    GL_CONTEXT = moderngl.create_context(require=330)
except Exception as exc:
    _show_gl_error(exc)
    raise SystemExit(2) from exc

ScreenSize.resolution = Vector2(*pygame.display.get_window_size())
pygame.display.set_icon(pygame.image.load(PATH / "assets" / "ico.png"))
cursor_image = pygame.image.load(PATH / "assets" / "menu" / "mouse.png").convert_alpha()
cursor_image = pygame.transform.scale(
    cursor_image,
    (round(cursor_image.get_width() * 1.3), round(cursor_image.get_height() * 1.3)),
)
pygame.mouse.set_cursor(pygame.cursors.Cursor((0, 0), cursor_image))

# These modules load display-formatted assets, so import them after set_mode.
import src.end_menu as end_menu  # noqa: E402
import src.game_manager as game_manager  # noqa: E402
import src.map.Background as bg  # noqa: E402
import src.menu_main as menu_main  # noqa: E402
from pygame_easy_menu import ModernGLBackend  # noqa: E402
from src.tools.constant import EndPartie, TEAM  # noqa: E402
from src.tools.tools import MixeurAudio  # noqa: E402
from src.utils.presence import Presence  # noqa: E402


class Game:
    running = True
    clock = pygame.time.Clock()
    serialized = 0.0
    partie = None
    menu = None
    renderer = Renderer2D(GL_CONTEXT, pygame.display.get_window_size())

    rcp = Presence(id="970789165010649108")
    rcp.start()

    @staticmethod
    def menu_backend(logical_size=(1920, 1080)):
        return ModernGLBackend.from_context(
            GL_CONTEXT, logical_size, pygame.display.get_window_size()
        )

    @staticmethod
    def run():
        MixeurAudio.set_musique(path=PATH / "assets" / "music" / "main-loop.wav")
        MixeurAudio.play_until_Stop(
            PATH / "assets" / "sound" / "water_effect_loop.wav", volume=0.35
        )
        Game.start_menu()
        Camera.maximise = False

        while Game.running:
            if Game.partie:
                try:
                    Game.partie.Update()
                except EndPartie as event:
                    MixeurAudio.stop("all")
                    if event.args:
                        Game.start_end(*event.args)
                    else:
                        Game.start_menu()
                    Game.partie = None
            else:
                Game.menu.update()

            Game.renderer.begin_frame()
            if Game.partie:
                Camera.begin_world_pass()
                Camera.render_bg()
                Game.partie.Draw()
                Camera.render_hud()
                Game.renderer.end_frame()
            else:
                Game.menu.render()
            pygame.display.flip()

            Game.serialized = Game.clock.tick(60) / 16.7
        Game.shutdown()
        raise SystemExit

    @staticmethod
    def _release_menu():
        if Game.menu is not None:
            Game.menu.release()
            Game.menu = None

    @staticmethod
    def start_partie(j1, j2):
        Game._release_menu()
        Game.partie = game_manager.Partie()
        Game.partie.add_player("j1.1", j1)
        Game.partie.add_player("j2.1", j2, True)
        Game.partie.add_player("j1.2", j1, True)
        Game.partie.add_player("j2.2", j2, True)
        MixeurAudio.gn.reset()
        Camera.HUD = True
        Camera.maximise = True
        MixeurAudio.stop("music")

    @staticmethod
    def start_menu():
        Game._release_menu()
        Game.rcp.details.value = "In menu"
        Game.rcp.time.value = 0.0
        menu_main.setup_manager()
        Game.menu = menu_main.game

    @staticmethod
    def start_end(winner, loser):
        Game._release_menu()
        Game.rcp.details.value = f"team {TEAM[winner]['name']} has won !"
        Game.rcp.time.value = 0.0
        end_menu.setup_manager(winner=winner, loser=loser)
        Game.menu = end_menu.game

    @staticmethod
    def shutdown():
        Game._release_menu()
        Game.renderer.release()
        pygame.quit()


class Camera:
    WORLD_SIZE = (1536, 864)
    HUD_SIZE = (720, 480)
    x = 0.0
    y = 0.0
    zoom = 1.0
    zoom_offset = (1.0, 1.0)
    maximise = True
    HUD = True
    _screen_UI = RenderQueueSurface(HUD_SIZE)
    _camera = Camera2D(WORLD_SIZE, pygame.display.get_window_size())
    _bg = bg.BackgroundAssets()

    @staticmethod
    def _sync_camera():
        Camera._camera.framebuffer_size = pygame.display.get_window_size()
        Camera._camera.update(Camera.x, Camera.y, Camera.zoom, Camera.maximise)
        Camera.x = Camera._camera.x
        Camera.y = Camera._camera.y
        Camera.zoom = Camera._camera.zoom
        Camera.zoom_offset = Camera._camera.aspect_zoom

    @staticmethod
    def begin_world_pass():
        Camera._sync_camera()
        Game.renderer.begin_pass(Camera.WORLD_SIZE, Camera._camera)

    @staticmethod
    def render_hud():
        if not Camera.HUD:
            return
        Game.renderer.begin_pass(Camera.HUD_SIZE)
        Camera._screen_UI.render(Game.renderer)

    @staticmethod
    def to_virtual(x, y):
        Camera._sync_camera()
        return Camera._camera.view_to_world((x, y))

    @staticmethod
    def to_absolute(x, y):
        Camera._sync_camera()
        return Camera._camera.world_to_window((x, y))

    @staticmethod
    def render_bg():
        Camera._sync_camera()
        frame, back_cloud, front_cloud = Camera._bg.current()
        world_rect = pygame.Rect((0, 0), Camera.WORLD_SIZE)
        Game.renderer.draw(frame, world_rect)
        tick = pygame.time.get_ticks()
        back_x = (tick / 40000 % 0.5 - 0.25) * Camera.WORLD_SIZE[0]
        front_x = (tick / 80000 % 0.5 - 0.25) * Camera.WORLD_SIZE[0]
        cloud_rect = pygame.Rect(
            -Camera.WORLD_SIZE[0] // 2,
            0,
            Camera.WORLD_SIZE[0] * 2,
            Camera.WORLD_SIZE[1],
        )
        Game.renderer.draw(back_cloud, cloud_rect.move(back_x, 0))
        Game.renderer.draw(front_cloud, cloud_rect.move(front_x, 0))

    @staticmethod
    def Update(x=None, y=None, zoom=None):
        Camera._camera.update(
            Camera.x if x is None else x,
            Camera.y if y is None else y,
            Camera.zoom if zoom is None else zoom,
            Camera.maximise,
        )
        Camera.x, Camera.y, Camera.zoom = (
            Camera._camera.x,
            Camera._camera.y,
            Camera._camera.zoom,
        )


game_manager.GAME = menu_main.GAME = end_menu.GAME = Game
game_manager.CAMERA = menu_main.CAMERA = end_menu.CAMERA = Camera
