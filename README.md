# Atomic-Bayttle

### disclaimer : ALL ASSETS ARE UNDER THEIR OWN LICENSE, ONLY THE CODE OF THE GAME IS UNDER THE MIT LICENSE

How to launch:

- Install Python 3.10 and [Poetry](https://python-poetry.org/docs/#installation).
- Install the dependencies with `poetry install`.
- Start the game with `poetry run python main.py`.

The renderer requires an OpenGL 3.3 capable GPU and driver. This includes the
large majority of Intel, AMD and NVIDIA computers released since 2012. If a
3.3 core context cannot be created, the game displays a diagnostic and exits;
there is intentionally no slower gameplay renderer fallback.

To build the application with PyInstaller, install the build dependency group (included
by default by `poetry install`) and run `poetry run pyinstaller Atomic-Bayttle.spec`.

Controls:
- Z Q S D to move, you can change keybinds in settings
- TAB to active inventory then Z Q D to choose the weapon
- SPACE to jump and double jump
- E to shoot and respawn
- ENTER to pass turn
- ESC to leave
  *control can be changed in settings*

About the code :
- the code used to emulate the physics of the game is defined in the file ``src/weapons/physique.py``, it is used to calculate trajectory of all bullets in the game.
- Pygame owns input, audio, rectangles, masks, physics and collisions.
- ModernGL renders the world, destructible terrain, water, HUD and menus. Static
  assets are uploaded once; explosions update only the affected terrain region.
- Menus use the native OpenGL backend from `pygame-easy-menu[opengl]` 0.0.63.

Run the rendering regression tests with
`poetry run pytest`. They cover camera transforms, arbitrary-alpha terrain
stamps, GPU menu composition and the absence of legacy immediate-mode OpenGL.
Use `poetry run python scripts/benchmark_renderer.py` for the synchronized
1080p/300-sprite performance gate (p95 below 8 ms).

à finir : 
- sticky chainsaw when hitting ennemis
