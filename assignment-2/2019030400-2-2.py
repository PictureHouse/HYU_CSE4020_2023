import glfw
from OpenGL.GL import * 
from OpenGL.GLU import *
import numpy as np

def render(current_mode):
    glClear(GL_COLOR_BUFFER_BIT) 
    glLoadIdentity()
    glBegin(current_mode)
    glColor3ub(255, 255, 255)
    th = np.linspace(0, np.radians(360), 13)
    vertices = np.array([np.cos(th), np.sin(th)])
    for i in np.arange(12):
        glVertex2f(vertices[0][i], vertices[1][i])
    glEnd()

def key_callback(window, key, scancode, action, mods):
    global current_mode
    if key == glfw.KEY_1:
        if action == glfw.PRESS:
            current_mode = GL_POINTS
    elif key == glfw.KEY_2:
        if action == glfw.PRESS:
            current_mode = GL_LINES
    elif key == glfw.KEY_3:
        if action == glfw.PRESS:
            current_mode = GL_LINE_STRIP
    elif key == glfw.KEY_4:
        if action == glfw.PRESS:
            current_mode = GL_LINE_LOOP
    elif key == glfw.KEY_5:
        if action == glfw.PRESS:
            current_mode = GL_TRIANGLES
    elif key == glfw.KEY_6:
        if action == glfw.PRESS:
            current_mode = GL_TRIANGLE_STRIP
    elif key == glfw.KEY_7:
        if action == glfw.PRESS:
            current_mode = GL_TRIANGLE_FAN
    elif key == glfw.KEY_8:
        if action == glfw.PRESS:
            current_mode = GL_QUADS
    elif key == glfw.KEY_9:
        if action == glfw.PRESS:
            current_mode = GL_QUAD_STRIP
    elif key == glfw.KEY_0:
        if action == glfw.PRESS:
            current_mode = GL_POLYGON
    
def main():
    if not glfw.init():
        return
    window = glfw.create_window(480, 480, "2019030400-2-2", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    global current_mode
    current_mode = GL_LINE_LOOP
    while not glfw.window_should_close(window):
        glfw.set_key_callback(window, key_callback)
        glfw.poll_events()
        render(current_mode)
        glfw.swap_buffers(window)
    glfw.terminate()

if __name__ == "__main__":
    main()
