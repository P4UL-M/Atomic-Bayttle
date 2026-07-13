from pathlib import Path

import pygame

from src.map.render_map import Map
from src.rendering import Camera2D, DamageStamp, RenderQueueSurface
from src.tools.constant import PATH
from src.tools.tools import animation_Manager, sprite_sheet


class RecordingRenderer:
    def __init__(self):
        self.updates = []

    def update_region(self, surface, rect):
        self.updates.append((surface, pygame.Rect(rect)))


def make_map():
    game_map = Map.__new__(Map)
    pygame.sprite.Sprite.__init__(game_map)
    game_map.image = pygame.Surface((20, 20), pygame.SRCALPHA)
    game_map.image.fill("white")
    game_map.rect = game_map.image.get_rect()
    game_map.mask = pygame.mask.from_surface(game_map.image)
    game_map.cave_bg = pygame.sprite.Sprite()
    game_map.cave_bg.image = pygame.Surface((8, 8), pygame.SRCALPHA)
    game_map.cave_bg.image.fill("white")
    game_map.cave_bg.rect = game_map.cave_bg.image.get_rect(topleft=(8, 8))
    game_map.cave_bg.mask = pygame.mask.from_surface(game_map.cave_bg.image)
    game_map.water_target = 20
    return game_map


def cross_stamp():
    surface = pygame.Surface((5, 5), pygame.SRCALPHA)
    pygame.draw.line(surface, "white", (2, 0), (2, 4))
    pygame.draw.line(surface, "white", (0, 2), (4, 2))
    return DamageStamp.from_surface(surface)


def test_camera_round_trip_and_clamping_across_aspects():
    for framebuffer in ((1920, 1080), (1920, 1200), (1280, 1024)):
        camera = Camera2D((1536, 864), framebuffer, x=0.1, y=-0.08, zoom=2.2)
        camera.clamp()
        point = (730, 410)
        window = camera.world_to_window(point)
        restored = camera.view_to_world(window)
        assert abs(restored[0] - point[0]) <= 2
        assert abs(restored[1] - point[1]) <= 2


def test_arbitrary_damage_stamp_preserves_transparent_corners():
    game_map = make_map()
    renderer = RecordingRenderer()
    stamp = cross_stamp()
    game_map.apply_damage((10, 10), stamp, renderer, radius=3)

    assert game_map.mask.get_at((10, 10)) == 0
    assert game_map.mask.get_at((8, 8)) == 1
    assert renderer.updates[0][1] == pygame.Rect(8, 8, 5, 5)
    assert renderer.updates[1][1] == pygame.Rect(0, 0, 5, 5)


def test_damage_stamp_is_clipped_at_map_edge():
    game_map = make_map()
    renderer = RecordingRenderer()
    game_map.apply_damage((0, 0), cross_stamp(), renderer, radius=3)
    assert renderer.updates[0][1] == pygame.Rect(0, 0, 3, 3)


def test_hud_queue_records_commands_without_allocating_a_framebuffer():
    queue = RenderQueueSurface((720, 480))
    image = pygame.Surface((10, 10), pygame.SRCALPHA)
    queue.blit(image, (4, 5))
    queue.blit_scaled(image, (20, 30, 40, 50), opacity=0.5)
    assert queue.get_size() == (720, 480)
    assert [command.rect for command in queue.commands] == [
        pygame.Rect(4, 5, 10, 10), pygame.Rect(20, 30, 40, 50)
    ]


def test_animation_manager_returns_cached_frames_without_copying(tmp_path):
    image_path = tmp_path / "frame.bmp"
    pygame.image.save(pygame.Surface((3, 3)), str(image_path))
    sheet = sprite_sheet(image_path, (3, 3))
    manager = animation_Manager()
    manager.add_annimation("idle", sheet, 100)
    manager.load("idle")
    assert manager.surface is manager.surface


def test_legacy_opengl_pipeline_is_not_referenced():
    source_root = Path(PATH) / "src"
    source = "\n".join(
        path.read_text(errors="ignore")
        for path in source_root.rglob("*.py")
        if path.name not in {"opengl_pygame.py", "Surface_class.py"}
    )
    assert "from OpenGL" not in source
    assert "glBegin(" not in source
    assert "pygame.image.tostring" not in source
