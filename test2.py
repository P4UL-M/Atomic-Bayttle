#!coding: utf-8
from __future__ import print_function, division

from OpenGL.GL import *
from OpenGL.GL import shaders
import ctypes
import pygame
import numpy as np

vertexShader = """
# version 330 core
layout (location = 0) in vec3 attrPosition;
layout (location = 1) in vec3 attrColor;
layout (location = 2) in vec2 attrTexCoords;

out vec3 vsColor;
out vec2 vsTexCoords;

void main()
{
    gl_Position = vec4(attrPosition, 1.0);
    vsColor = attrColor;
    vsTexCoords = attrTexCoords;
}
"""

vertexShader = """
#version 330 core
in vec4 position;
void main()
{
   gl_Position = position;
}
"""

fragmentShader = """
# version 330 core
uniform sampler2D texUniform;

in vec3 vsColor;
in vec2 vsTexCoords;

out vec4 FragColor;
void main()
{
    FragColor = vec4(texture(texUniform, vsTexCoords).rgb, 1);
}
"""

fragmentShader = """
#version 330 core
out vec4 fragColor;
void main()
{
    fragColor = vec4(1.0, 0.0, 0.0, 1.0);
}
"""


NB_POSITION_AXES = 3
NB_COLOR_AXES = 3
NB_TEX_COORDS_AXES = 2

vertices1 = np.array([
    # positions        # colors         # texture coords
    0.5, 0.5, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0,   # top right
    0.5, -0.5, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0,   # bottom right
    -0.5, -0.5, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0,   # bottom left
    -0.5, 0.5, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0,   # top left
], dtype=np.float32)

indices1 = np.array([
    0, 1, 3,  # first triangle
    1, 2, 3,  # second triangle
], dtype=np.uint32)


def createObject(shaderProgram, vertices, indices):

    # Create a new VAO (Vertex Array Object)
    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    EBO = glGenBuffers(1)

    # Bind the Vertex Array Object first
    glBindVertexArray(VAO)

    # Bind the Vertex Buffer
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(vertices), vertices, GL_STATIC_DRAW)

    # Bind the Entity Buffer
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(indices), indices, GL_STATIC_DRAW)

    # Configure vertex attribute

    # - Position attribute
    attrPositionIndex = glGetAttribLocation(shaderProgram, 'attrPosition')
    if (attrPositionIndex != -1):
        glVertexAttribPointer(attrPositionIndex, NB_POSITION_AXES, GL_FLOAT, GL_FALSE, 8 * ctypes.sizeof(ctypes.c_float), ctypes.c_void_p(0))
        glEnableVertexAttribArray(attrPositionIndex)

    # - Color attribute
    attrColorIndex = glGetAttribLocation(shaderProgram, 'attrColor')  # doesn't work ?
    if (attrColorIndex != -1):
        glVertexAttribPointer(attrColorIndex, NB_COLOR_AXES, GL_FLOAT, GL_FALSE, 8 * ctypes.sizeof(ctypes.c_float), ctypes.c_void_p(3 * ctypes.sizeof(ctypes.c_float)))
        glEnableVertexAttribArray(attrColorIndex)

    # - Texture coordinates attribute
    attrTexCoordsIndex = glGetAttribLocation(shaderProgram, 'attrTexCoords')
    if (attrTexCoordsIndex != -1):
        glVertexAttribPointer(attrTexCoordsIndex, NB_TEX_COORDS_AXES, GL_FLOAT, GL_FALSE, 8 * ctypes.sizeof(ctypes.c_float), ctypes.c_void_p(6 * ctypes.sizeof(ctypes.c_float)))
        glEnableVertexAttribArray(attrTexCoordsIndex)

    # Texture

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    # Set the texture wrapping parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)  # Set texture wrapping to GL_REPEAT (default wrapping method)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    # Set texture filtering parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    image = pygame.image.load('assets/ico.png').convert_alpha()
    imageData = pygame.image.tostring(image, 'RGBA', 1)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.get_width(), image.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, imageData)
    glGenerateMipmap(GL_TEXTURE_2D)

    # Unbind the VAO
    glBindVertexArray(0)

    # Unbind the VBO
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    if (attrPositionIndex != -1):
        glDisableVertexAttribArray(attrPositionIndex)
    if (attrColorIndex != -1):
        glDisableVertexAttribArray(attrColorIndex)
    if (attrTexCoordsIndex != -1):
        glDisableVertexAttribArray(attrTexCoordsIndex)

    # Unbind the EBO
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    return VAO, texture


def initDisplay(shaderProgram):
    glEnable(GL_DEPTH_TEST)

    glUseProgram(shaderProgram)
    textureUniformIndex = glGetUniformLocation(shaderProgram, 'texUniform')
    glUniform1i(textureUniformIndex, 0)


def prepareDisplay():
    glClearColor(0.2, 0.3, 0.3, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


def drawObject(shaderProgram, VAO, texture):

    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, texture)

    glUseProgram(shaderProgram)
    glBindVertexArray(VAO)
    glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, ctypes.c_void_p(0))
    # glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)


def display():
    glBindVertexArray(0)
    glUseProgram(0)


def main():
    pygame.init()
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
    screen = pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)

    glEnable(GL_DEPTH_TEST)

    shaderProgram = shaders.compileProgram(
        shaders.compileShader(vertexShader, GL_VERTEX_SHADER),
        shaders.compileShader(fragmentShader, GL_FRAGMENT_SHADER))

    print("Shader program compiled")

    initDisplay(shaderProgram)

    VAO, texture = createObject(shaderProgram, vertices1, indices1)

    clock = pygame.time.Clock()

    done = False
    while not done:
        print(clock.get_fps())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        prepareDisplay()
        drawObject(shaderProgram, VAO, texture)
        display()
        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    try:
        main()
    finally:
        pygame.quit()
