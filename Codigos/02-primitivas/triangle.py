#!/usr/bin/env python3

## @file triangulo.py
#  Draws a red triangle.
# 
#  Defines the basics for drawing in OpenGL, shaders, arrays, buffers, etc.
#
# @author Ricardo Dutra da Silva


import sys
import ctypes
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut
from ctypes import c_void_p


## Window width.
win_width  = 800
## Window height.
win_height = 600

## Program variable.
program = None
## Vertex array object.
VAO = None
## Vertex buffer object.
VBO = None

## Vertex shader.
vertex_code_ = """
#version 330 core
layout (location = 0) in vec3 position;

void main()
{
    gl_Position = vec4(position.x, position.y, position.z, 1.0);
}
"""
vertex_code = """
#version 330 core
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 color;

out vec3 vColor;

void main()
{
    gl_Position = vec4(position, 1.0);
    vColor = color;
}
"""

## Fragment shader.
fragment_code_ = """
#version 330 core
out vec4 FragColor;

void main()
{
    FragColor = vec4(1.0f, 1.0f, 0.0f, 1.0f);
} 
"""

fragment_code = """
#version 330 core
in vec3 vColor;

out vec4 FragColor;

void main()
{
    FragColor = vec4(vColor, 1.0f);
}
"""

## Drawing function.
#
# Draws a triangle.
def display():

    gl.glClearColor(0.2, 0.3, 0.3, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    gl.glUseProgram(program)
    gl.glBindVertexArray(VAO)
    # Draws the triangle.
    gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)

    glut.glutSwapBuffers()


## Reshape function.
# 
# Called when window is resized.
#
# @param width New window width.
# @param height New window height.
def reshape(width,height):

    win_width = width
    win_height = height
    gl.glViewport(0, 0, width, height)
    glut.glutPostRedisplay()


## Keyboard function.
#
# Called to treat pressed keys.
#
# @param key Pressed key.
# @param x Mouse x coordinate when key pressed.
# @param y Mouse y coordinate when key pressed.
def keyboard(key, x, y):

    if key == b'\x1b'or key == b'q':
        glut.glutLeaveMainLoop()


## Init vertex data.
#
# Defines the coordinates for vertices, creates the arrays for OpenGL.
def initData():

    # Uses vertex arrays.
    global VAO
    global VBO

    # Set triangle vertices.
    vertices_ = np.array([
        -0.5, -0.5, 0.0,
         0.5, -0.5, 0.0,
         0.0,  0.5, 0.0
    ], dtype='float32')

    vertices = np.array([
        0.0, 0.0, 0.0, 0.0, 0.0, 1.0,
        0.0, 0.0, 1.0, 1.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 1.0, 0.0, 0.0,
        0.0, 1.0, 1.0,0.0, 0.0, 1.0,
        1.0, 0.0, 0.0,0.0, 0.0, 1.0,
        1.0, 0.0, 1.0,0.0, 0.0, 1.0,
        1.0, 1.0, 0.0,0.0, 0.0, 1.0,
        1.0, 1.0, 1.0,0.0, 0.0, 1.0  
    ], dtype='float32')

    # Vertex array.
    VAO = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(VAO)

    # Vertex buffer
    VBO = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)
    
    # Set attributes.
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 6*vertices.itemsize, None)
    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 6*vertices.itemsize, c_void_p(3*vertices.itemsize))
    gl.glEnableVertexAttribArray(1)
    
    # Unbind Vertex Array Object.
    gl.glBindVertexArray(0)

## Create program (shaders).
#
# Compile shaders and create the program.
def initShaders():
    
    # Uses vertex arrays.
    global program

    # Request a program and shader slots from GPU
    program  = gl.glCreateProgram()
    vertex   = gl.glCreateShader(gl.GL_VERTEX_SHADER)
    fragment = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
    
    # Set shaders source
    gl.glShaderSource(vertex, vertex_code)
    gl.glShaderSource(fragment, fragment_code)

    # Compile shaders
    gl.glCompileShader(vertex)
    gl.glCompileShader(fragment)

    # Attach shader objects to the program
    gl.glAttachShader(program, vertex)
    gl.glAttachShader(program, fragment)

    # Link the program
    gl.glLinkProgram(program)

    # Get rid of shaders (not needed anymore)
    gl.glDetachShader(program, vertex)
    gl.glDetachShader(program, fragment)
    gl.glDeleteShader(vertex)
    gl.glDeleteShader(fragment)
    
    # Set the program to be used.
    gl.glUseProgram(program)


## Main function.
#
# Init GLUT and the window settings. Also, defines the callback functions used in the program.
def main():

    glut.glutInit()
    glut.glutInitContextVersion(3, 3)
    glut.glutInitContextProfile(glut.GLUT_CORE_PROFILE)
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA)
    glut.glutInitWindowSize(win_width,win_height)
    glut.glutCreateWindow('Triangle')

    # Init vertex data for the triangle.
    initData()
    
    # Create shaders.
    initShaders()

    glut.glutReshapeFunc(reshape)
    glut.glutDisplayFunc(display)
    glut.glutKeyboardFunc(keyboard)

    glut.glutMainLoop()

if __name__ == '__main__':
    main()
