"""Repeatable 1080p renderer micro-benchmark.

It measures 300 alpha sprites (a particle-heavy match), forces GPU completion,
and exits non-zero if
the p95 render time exceeds the migration target of 8 ms.
"""

import os
import statistics
import sys
import time
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import moderngl
import pygame

from src.rendering import Renderer2D


def main() -> int:
    pygame.init()
    pygame.display.set_mode((64, 64))
    context = moderngl.create_standalone_context(require=330)
    framebuffer = context.simple_framebuffer((1920, 1080), components=4)
    framebuffer.use()
    renderer = Renderer2D(context, (1920, 1080))
    image = pygame.Surface((32, 32), pygame.SRCALPHA)
    image.fill("white")

    samples = []
    for frame in range(65):
        started = time.perf_counter()
        renderer.begin_frame()
        renderer.begin_pass((1920, 1080))
        for index in range(300):
            renderer.draw(image, (index % 40 * 48, index // 40 * 40, 32, 32))
        renderer.end_frame()
        context.finish()
        if frame >= 5:
            samples.append((time.perf_counter() - started) * 1000)

    p95 = statistics.quantiles(samples, n=20)[18]
    print(
        f"p50={statistics.median(samples):.3f}ms "
        f"p95={p95:.3f}ms max={max(samples):.3f}ms "
        f"textures={renderer.textures.texture_count}"
    )
    renderer.release()
    framebuffer.release()
    context.release()
    pygame.quit()
    return int(p95 >= 8.0)


if __name__ == "__main__":
    raise SystemExit(main())
