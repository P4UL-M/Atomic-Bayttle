import numpy as np
import pygame as pg
from OpenGL.GL import *

pg.init()

windowSize = (1280, 800)
# pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 1)
# pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 0)
pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

pg.display.set_mode(windowSize, pg.DOUBLEBUF | pg.OPENGL)
pg.display.set_caption("TEST")

version = glGetString(GL_VERSION)

print(version)

glClearColor(0.0, 0.0, 0.0, 1.0)

# All components of our scene
vertices = np.array([
    [-0.5, -0.5],
    [-0.5, 0.5],
    [0.5, 0.5],
    [0.5, -0.5],
    [-0.3, -0.7],
    [-0.3, 0.3],
    [0.7, 0.3],
    [0.7, -0.7]
], dtype=np.float32)

faces = np.array([
    [0, 1, 2, 3],
    [4, 5, 6, 7]
], dtype=np.uint)
faceCount = faces.shape[0]
print(faceCount)

# Create one Vertex Array Object (VAO)
vaoId = glGenVertexArrays(1)
# We will be working on this VAO
glBindVertexArray(vaoId)

# Create three Vertex Buffer Objects (VBO)
vboIds = glGenBuffers(2)
# Commodity variables to memorize the id of each VBO
vertexVboId = vboIds[0]
indexVboId = vboIds[1]

# Copy vertices data to GPU
glBindBuffer(GL_ARRAY_BUFFER, vertexVboId)
vertices = np.ascontiguousarray(vertices.flatten())
glBufferData(GL_ARRAY_BUFFER, 4 * len(vertices), vertices, GL_DYNAMIC_DRAW)
glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, None)

# Copy index data to GPU
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, indexVboId)
faces = np.ascontiguousarray(faces.flatten())
glBufferData(GL_ELEMENT_ARRAY_BUFFER, 4 * len(faces), faces, GL_DYNAMIC_DRAW)

# Release focus on VBO and VAO
glBindBuffer(GL_ARRAY_BUFFER, 0)
glBindVertexArray(0)

# Main loop
clock = pg.time.Clock()
running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
            break
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
                break

    glClear(GL_COLOR_BUFFER_BIT)

    glBindVertexArray(vaoId)
    glEnableVertexAttribArray(0)
    print(glGetError())
    glDrawElements(GL_TRIANGLES, 4 * faceCount, GL_UNSIGNED_INT, None)
    glDisableVertexAttribArray(0)
    glBindVertexArray(0)

    glFlush()

    pg.display.flip()
    clock.tick(60)

glDeleteBuffers(2, vboIds)
glDeleteVertexArrays(1, vaoId)

pg.quit()
quit()
