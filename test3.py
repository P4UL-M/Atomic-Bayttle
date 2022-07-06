import OpenGL.GL as GL
import OpenGL.GL.shaders
import pygame as pg


#-------------not my code, credit to: Morgan Borman--------------#
vertex_shader = """
#version 410 
in vec4 position;
void main()
{
   gl_Position = position;
}
"""

fragment_shader = """
#version 410 
void main()
{
   gl_FragColor = vec4(1.0f, 1.0f, 1.0f, 1.0f);
}
"""
#----------------------------------------------------------------#


def main():
    pg.init()
    pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

    DISPLAY_DIMENSIONS = (640, 480)
    display = pg.display.set_mode(DISPLAY_DIMENSIONS, pg.DOUBLEBUF | pg.OPENGL)
    #-------------not my code, credit to: Morgan Borman--------------#
    GL.glClearColor(0.5, 0.5, 0.5, 1.0)
    GL.glEnable(GL.GL_DEPTH_TEST)

    shader = OpenGL.GL.shaders.compileProgram(
        OpenGL.GL.shaders.compileShader(vertex_shader, GL.GL_VERTEX_SHADER),
        OpenGL.GL.shaders.compileShader(fragment_shader, GL.GL_FRAGMENT_SHADER)
    )
    #----------------------------------------------------------------#

    clock = pg.time.Clock()
    FPS = 60

    while True:
        clock.tick(FPS)
        for e in pg.event.get():
            if e.type == pg.QUIT:
                return

        pg.display.flip()


if __name__ == '__main__':
    try:
        main()
    finally:
        pg.quit()
