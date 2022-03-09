from OpenGL.GL import *
import pygame

info = pygame.display.Info()

# basic opengl configuration
def config(info):
    glViewport(0, 0, info.current_w, info.current_h)
    glDepthRange(0, 1)
    glMatrixMode(GL_PROJECTION)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glShadeModel(GL_SMOOTH)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
    glEnable(GL_BLEND)

texID = glGenTextures(1)
texUI = glGenTextures(1)
def surfaceToTexture(pygame_surface:pygame.Surface,rgba=False):
    global texID
    rgb_surface = pygame.image.tostring( pygame_surface, 'RGBA' if rgba else 'RGB')
    glBindTexture(GL_TEXTURE_2D, texID if not rgba else texUI)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    surface_rect = pygame_surface.get_rect()
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA if rgba else GL_RGB, surface_rect.width, surface_rect.height, 0, GL_RGBA if rgba else GL_RGB, GL_UNSIGNED_BYTE, rgb_surface)
    glGenerateMipmap(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, 0)

def surfaceToScreen(pygame_surface:pygame.Surface,pos:tuple[float,float],zoom:float,maximize=True) -> tuple[float,float,tuple[float,float]]:
    global texID
    x,y = pos

    surf_ratio = pygame_surface.get_width()/pygame_surface.get_height() # 10/5 -> 2
    screen_ratio = info.current_w/info.current_h # 9/5 -> 1.8
    if maximize:
        if surf_ratio > screen_ratio:
            y_zoom = 1
            x_zoom = surf_ratio/screen_ratio
        else:
            x_zoom = 1
            y_zoom = screen_ratio/surf_ratio
    else:
        y_zoom = 1
        x_zoom = 1

    x = max(min((zoom-1)/(zoom*2)+(x_zoom - 1)/2/zoom,x),-(zoom-1)/(zoom*2)-(x_zoom - 1)/2/zoom)
    y = max(min((zoom-1)/(zoom*2)+(y_zoom -1)/2/zoom,y),-(zoom-1)/(zoom*2)-(y_zoom -1)/2/zoom)

    # draw texture openGL Texture
    surfaceToTexture(pygame_surface, False)

    glBindTexture(GL_TEXTURE_2D, texID)
    glBegin(GL_QUADS)
    glTexCoord2f(x, y); glVertex2f(-zoom*x_zoom, zoom*y_zoom)
    glTexCoord2f(x, y+1); glVertex2f(-zoom*x_zoom, -zoom*y_zoom)
    glTexCoord2f(x+1, y+1); glVertex2f(zoom*x_zoom, -zoom*y_zoom)
    glTexCoord2f(x+1, y); glVertex2f(zoom*x_zoom, zoom*y_zoom)
    glEnd()

    return x,y,(x_zoom,y_zoom)

def uiToScreen(pygame_surface:pygame.Surface):
    global texUI
    if pygame_surface:
        surfaceToTexture(pygame_surface, True)

    glBindTexture(GL_TEXTURE_2D, texUI)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(-1, 1)
    glTexCoord2f(0, 1); glVertex2f(-1, -1)
    glTexCoord2f(1, 1); glVertex2f(1, -1)
    glTexCoord2f(1, 0); glVertex2f(1, 1)
    glEnd()

def cleangl():
    # prepare to render the texture-mapped rectangle
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glDisable(GL_LIGHTING)
    glEnable(GL_TEXTURE_2D)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glClearColor(0, 0, 0, 1.0)
