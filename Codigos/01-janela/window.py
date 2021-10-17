#!/usr/bin/env python3

## @file window.py
#  Basic window creation.
# 
#  Set up and show a window using GLUT with simple keyboard, display and reshape functions.
#
# @author Ricardo Dutra da Silva


import sys
import OpenGL.GL as gl
import OpenGL.GLUT as glut


## Window width.
win_width  = 800
## Window height.
win_height = 600


## Drawing function.
#
# A simple drawing function that only clears the color buffer.
def display():

    # Set RGBA color to "paint" cleared color buffer (background color). 
    gl.glClearColor(0.2, 0.3, 0.3, 1.0)

    # Clears color buffer to the RGBA defined values.
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    # Demand to draw to the window.
    glut.glutSwapBuffers()


## Reshape function.
# 
# Called when window is resized.
#
# @param width New window width.
# @param height New window height.
def reshape(width,height):

    # Save new window size in case it may be need elsewhere (not in this program).
    win_width = width
    win_height = height

    # Set the viewport (rectangle of visible area in the window).
    gl.glViewport(0, 0, width, height)

    # Demand OpenGL to redraw scene (call display function).
    glut.glutPostRedisplay()


## Keyboard function.
#
# Called to treat pressed keys.
#
# @param key Pressed key.
# @param x Mouse x coordinate when key pressed.
# @param y Mouse y coordinate when key pressed.
def keyboard(key, x, y):

    # Exit program when ESC or q keys are pressed.
    if key == b'\x1b'or key == b'q':
        glut.glutLeaveMainLoop()


## Main function.
#
# Init GLUT and the window settings. Also, defines the callback functions used in the program.
def main():

    # Init glut (always called).
    glut.glutInit()

    # Set OpenGL context version to use "Modern OpenGL".
    glut.glutInitContextVersion(3, 3);
    glut.glutInitContextProfile(glut.GLUT_CORE_PROFILE);

    # Set glut to use double buffering with RGBA color attributes.
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA)

    # Set the size of the window.
    glut.glutInitWindowSize(win_width,win_height)
        
    # Create and set window name.
    glut.glutCreateWindow('Window')

    # Set used callbacks.
    glut.glutReshapeFunc(reshape)
    glut.glutDisplayFunc(display)
    glut.glutKeyboardFunc(keyboard)

    # Call glut main loop that ends when the program ends.
    glut.glutMainLoop()

if __name__ == '__main__':
    main()
