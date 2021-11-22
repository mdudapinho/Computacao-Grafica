#!/usr/bin/env python3

## @file phong.py
#  Applies the Phong method.
# 
# @author Ricardo Dutra da Silva


import sys
import ctypes
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut
from PIL import Image
sys.path.append('../lib/')
import utils as ut
from ctypes import c_void_p


try:
    PATH_TEXTURE = sys.argv[1]
except:
    PATH_TEXTURE = None

texture = None

angle_x = 0.0
angle_x_inc = 0.02
angle_y = 0
angle_y_inc = -0.04
angle_z = 0.0
angle_z_inc = 0.06

t_z = -5
t_z_inc = 0.001

## Window width.
win_width  = 600
## Window height.
win_height = 600

## Program variable.
program = None
## Vertex array object.
VAO = None
## Vertex buffer object.
VBO = None

## Vertex shader.
vertex_code = """
#version 330 core
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;
layout (location = 2) in vec2 texture;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec3 vNormal;
out vec3 fragPosition;
out vec2 aTexture;

void main()
{
    gl_Position = projection * view * model * vec4(position, 1.0);
    vNormal = mat3(transpose(inverse(model))) * normal;
    // vNormal = normal;
    fragPosition = vec3(model * vec4(position, 1.0));
    aTexture = texture;
}
"""

## Fragment shader.
fragment_code = """
#version 330 core

in vec3 vNormal;
in vec3 fragPosition;
in vec2 aTexture;

out vec4 fragColor;

uniform vec3 objectColor;
uniform vec3 lightColor;
uniform vec3 lightPosition;
uniform vec3 cameraPosition;
uniform sampler2D ourTexture;

void main()
{
    float ka = 0.5;
    vec3 ambient = ka * lightColor;

    float kd = 0.8;
    vec3 n = normalize(vNormal);
    vec3 l = normalize(lightPosition - fragPosition);
    
    float diff = max(dot(n,l), 0.0);
    vec3 diffuse = kd * diff * lightColor;

    float ks = 1.0;
    vec3 v = normalize(cameraPosition - fragPosition);
    vec3 r = reflect(-l, n);

    float spec = pow(max(dot(v, r), 0.0), 3.0);
    vec3 specular = ks * spec * lightColor;

    vec3 textureColor = texture(ourTexture, aTexture).xyz;

    vec3 light = (ambient + diffuse + specular) * textureColor;
    fragColor = vec4(light, 1.0);

    // fragColor = texture(ourTexture, aTexture);
}
"""


def read_texture():
    global texture

    img = Image.open(PATH_TEXTURE)
    img_data = np.array(list(img.getdata()), np.int8)
    texture = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture)

    gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR_MIPMAP_LINEAR)
    # gl.glTexEnvf(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_DECAL)

    format = gl.GL_RGB if img.mode == "RGB" else gl.GL_RGBA   # if the texture is jpg or png
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, img.size[0], img.size[1], 0,
                    format, gl.GL_UNSIGNED_BYTE, img_data)
    gl.glGenerateMipmap(gl.GL_TEXTURE_2D)


## Drawing function.
#
# Draws primitive.
def display():

    gl.glClearColor(0.2, 0.3, 0.3, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
    
    gl.glUseProgram(program)
    gl.glBindVertexArray(VAO)

    Rx = ut.matRotateX(np.radians(angle_x))
    Ry = ut.matRotateY(np.radians(angle_y))
    Rz = ut.matRotateZ(np.radians(angle_z))
    model=np.matmul(Rx,Ry)
    model=np.matmul(Rz,model)
    loc = gl.glGetUniformLocation(program, "model");
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, model.transpose())

    view = ut.matTranslate(0.0, 0.0, t_z)
    loc = gl.glGetUniformLocation(program, "view");
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, view.transpose())
    
    projection = ut.matPerspective(np.radians(45.0), win_width/win_height, 0.1, 100.0)
    loc = gl.glGetUniformLocation(program, "projection");
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, projection.transpose())

    # Object color.
    loc = gl.glGetUniformLocation(program, "objectColor")
    gl.glUniform3f(loc, 0.5, 0.1, 0.1)
    # Light color.
    loc = gl.glGetUniformLocation(program, "lightColor")
    gl.glUniform3f(loc, 1.0, 1.0, 1.0)
    # Light position.
    loc = gl.glGetUniformLocation(program, "lightPosition")
    gl.glUniform3f(loc, 1.0, 0.0, 2.0)
    # Camera position.
    loc = gl.glGetUniformLocation(program, "cameraPosition")
    gl.glUniform3f(loc, 0.0, 0.0, 0.0)

    gl.glDrawArrays(gl.GL_TRIANGLES, 0, 12*3)

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


def idle():
    global angle_x, angle_y, angle_z, t_z, t_z_inc

    angle_x = angle_x+angle_x_inc if (angle_x+angle_x_inc) < 360.0 else (360.0-angle_x+angle_x_inc)
    angle_y = angle_y+angle_y_inc if (angle_y+angle_y_inc) < 360.0 else (360.0-angle_y+angle_y_inc)
    angle_z = angle_z+angle_z_inc if (angle_z+angle_z_inc) < 360.0 else (360.0-angle_z+angle_z_inc)

    t_z = t_z+t_z_inc
    if t_z > -3 or t_z < -5:
        t_z_inc *= -1

    glut.glutPostRedisplay()


## Keyboard function.
#
# Called to treat pressed keys.
#
# @param key Pressed key.
# @param x Mouse x coordinate when key pressed.
# @param y Mouse y coordinate when key pressed.
def keyboard(key, x, y):

    global type_primitive
    global mode

    if key == b'\x1b'or key == b'q':
        glut.glutLeaveMainLoop()

    glut.glutPostRedisplay()


## Init vertex data.
#
# Defines the coordinates for vertices, creates the arrays for OpenGL.
def initData():

    # Uses vertex arrays.
    global VAO, VBO

    # Set triangle vertices.
    vertices = np.array([ 
        # coordinate        # normal           # texture
        -0.5, -0.5,  0.5,   0.0,  0.0,  1.0,   0.1,  0.5,
         0.5, -0.5,  0.5,   0.0,  0.0,  1.0,   0.2,  0.5,
         0.5,  0.5,  0.5,   0.0,  0.0,  1.0,   0.0,  0.5,
        -0.5, -0.5,  0.5,   0.0,  0.0,  1.0,   0.5,  0.3,
         0.5,  0.5,  0.5,   0.0,  0.0,  1.0,   0.4,  0.5,
        -0.5,  0.5,  0.5,   0.0,  0.0,  1.0,   0.5,  0.1,
         0.5, -0.5,  0.5,   1.0,  0.0,  0.0,   0.2,  0.5, 
         0.5, -0.5, -0.5,   1.0,  0.0,  0.0,   0.5,  0.6,
         0.5,  0.5, -0.5,   1.0,  0.0,  0.0,   0.5,  0.7,
         0.5, -0.5,  0.5,   1.0,  0.0,  0.0,   0.5,  0.8,
         0.5,  0.5, -0.5,   1.0,  0.0,  0.0,   0.5,  0.9,
         0.5,  0.5,  0.5,   1.0,  0.0,  0.0,   0.5,  0.9,
         0.5, -0.5, -0.5,   0.0,  0.0, -1.0,   0.5,  0.8,
        -0.5, -0.5, -0.5,   0.0,  0.0, -1.0,   0.5,  0.7,
        -0.5,  0.5, -0.5,   0.0,  0.0, -1.0,   0.5,  0.6,
         0.5, -0.5, -0.5,   0.0,  0.0, -1.0,   0.5,  0.4,
        -0.5,  0.5, -0.5,   0.0,  0.0, -1.0,   0.5,  0.3,
         0.5,  0.5, -0.5,   0.0,  0.0, -1.0,   0.5,  0.2,
        -0.5, -0.5, -0.5,  -1.0,  0.0,  0.0,   0.5,  0.1,
        -0.5, -0.5,  0.5,  -1.0,  0.0,  0.0,   0.5,  0.0,
        -0.5,  0.5,  0.5,  -1.0,  0.0,  0.0,   0.5,  0.9,
        -0.5, -0.5, -0.5,  -1.0,  0.0,  0.0,   0.5,  0.7,
        -0.5,  0.5,  0.5,  -1.0,  0.0,  0.0,   0.5,  0.8,
        -0.5,  0.5, -0.5,  -1.0,  0.0,  0.0,   0.5,  0.6,
        -0.5,  0.5,  0.5,   0.0,  1.0,  0.0,   0.5,  0.6,
         0.5,  0.5,  0.5,   0.0,  1.0,  0.0,   0.5,  0.2,
         0.5,  0.5, -0.5,   0.0,  1.0,  0.0,   0.5,  0.0,
        -0.5,  0.5,  0.5,   0.0,  1.0,  0.0,   0.5,  0.1,
         0.5,  0.5, -0.5,   0.0,  1.0,  0.0,   0.5,  0.2,
        -0.5,  0.5, -0.5,   0.0,  1.0,  0.0,   0.5,  0.3,
        -0.5, -0.5,  0.5,   0.0, -1.0,  0.0,   0.5,  0.3,
        -0.5, -0.5, -0.5,   0.0, -1.0,  0.0,   0.5,  0.4,
         0.5, -0.5,  0.5,   0.0, -1.0,  0.0,   0.5,  0.1,
        -0.5, -0.5, -0.5,   0.0, -1.0,  0.0,   0.5,  0.2,
         0.5, -0.5, -0.5,   0.0, -1.0,  0.0,   0.5,  0.8,
         0.5, -0.5,  0.5,   0.0, -1.0,  0.0,   0.5,  0.9
    ], dtype='float32') 

    # Vertex array.
    VAO = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(VAO)

    # Vertex buffer
    VBO = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

    # Set attributes.
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 8*vertices.itemsize, None)
    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 8*vertices.itemsize, c_void_p(3*vertices.itemsize))
    gl.glEnableVertexAttribArray(1)
    # texture coord attribute
    gl.glVertexAttribPointer(2, 2, gl.GL_FLOAT, gl.GL_FALSE, 8*vertices.itemsize, c_void_p(6*vertices.itemsize))
    gl.glEnableVertexAttribArray(2)
    
    # Unbind Vertex Array Object.
    gl.glBindVertexArray(0)

    gl.glEnable(gl.GL_DEPTH_TEST)

    read_texture()

    # gl.glEnable(gl.GL_TEXTURE_2D)
    # gl.glEnable(gl.GL_TEXTURE_GEN_S)
    # gl.glEnable(gl.GL_TEXTURE_GEN_T)
    # gl.glTexGeni(gl.GL_S, gl.GL_TEXTURE_GEN_MODE, gl.GL_SPHERE_MAP)
    # gl.glTexGeni(gl.GL_T, gl.GL_TEXTURE_GEN_MODE, gl.GL_SPHERE_MAP)

## Create program (shaders).
#
# Compile shaders and create programs.
def initShaders():

    global program

    program = ut.createShaderProgram(vertex_code, fragment_code)


## Main function.
#
# Init GLUT and the window settings. Also, defines the callback functions used in the program.
def main():
    glut.glutInit()
    glut.glutInitContextVersion(3, 3);
    glut.glutInitContextProfile(glut.GLUT_CORE_PROFILE);
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_DEPTH)
    glut.glutInitWindowSize(win_width,win_height)
    glut.glutCreateWindow('Phong')

    # Init vertex data for the triangle.
    initData()
    
    # Create shaders.
    initShaders()

    glut.glutReshapeFunc(reshape)
    glut.glutDisplayFunc(display)
    glut.glutKeyboardFunc(keyboard)
    glut.glutIdleFunc(idle)

    glut.glutMainLoop()

if __name__ == '__main__':
    main()
