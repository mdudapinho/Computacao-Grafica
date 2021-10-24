##########################################################
################### TRABALHO 1 - MESH ####################
############### MARIA EDUARDA REBELO PINHO ###############
##########################################################

import sys
import ctypes
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut
sys.path.append('../lib/')
import utils as ut
from ctypes import c_void_p
import pywavefront


## Window setup
win_width  = 800
win_height = 600

## Program variable.
program = None
## Vertex array object.
VAO = None
## Vertex buffer object.
VBO = None

#Translation
translation_x = 0.0
translation_y = 0.0
translation_z = 0.0
translation_inc = 0.1

#Scale
scale_x = 1.0
scale_y = 1.0
scale_z = 1.0

## Rotation 
angle_x = 0.0
angle_y = 0.0
angle_z = 0.0
angle_inc = 1.0

## Modes
transformacao = 0 #ROTACAO, TRANSLACAO, ESCALA
visualizacao = "FACES" #FACES, WIREFRAME


cube = np.array([
    # coordinate
    -0.25, -0.25,  0.25, 1.0, 0.0, 0.0,
     0.25, -0.25,  0.25, 0.0, 0.0, 0.0,
     0.25,  0.25,  0.25, 0.0, 0.0, 0.0,
    -0.25, -0.25,  0.25, 0.0, 0.0, 0.0,
     0.25,  0.25,  0.25, 1.0, 0.0, 1.0,
    -0.25,  0.25,  0.25, 1.0, 0.0, 1.0,
     0.25, -0.25,  0.25, 0.0, 0.0, 1.0,
     0.25, -0.25, -0.25, 0.0, 0.0, 0.0,
     0.25,  0.25, -0.25, 0.0, 0.0, 0.0,
     0.25, -0.25,  0.25, 0.0, 0.0, 0.0,
     0.25,  0.25, -0.25, 0.0, 0.0, 1.0,
     0.25,  0.25,  0.25, 0.0, 0.0, 0.0,
     0.25, -0.25, -0.25, 0.0, 0.0, 0.0,
    -0.25, -0.25, -0.25, 0.0, 0.0, 0.0,
    -0.25,  0.25, -0.25, 0.0, 0.0, 0.0,
     0.25, -0.25, -0.25, 0.0, 0.0, 0.0,
    -0.25,  0.25, -0.25, 1.0, 0.0, 0.0,
     0.25,  0.25, -0.25, 1.0, 0.0, 0.0,
    -0.25, -0.25, -0.25, 1.0, 0.0, 0.0,
    -0.25, -0.25,  0.25, 1.0, 0.0, 0.0,
    -0.25,  0.25,  0.25, 1.0, 0.0, 0.0,
    -0.25, -0.25, -0.25, 1.0, 0.0, 0.0,
    -0.25,  0.25,  0.25, 0.0, 0.0, 0.0,
    -0.25,  0.25, -0.25, 0.0, 0.0, 0.0,
    -0.25,  0.25,  0.25, 0.0, 0.0, 0.0,
     0.25,  0.25,  0.25, 0.0, 0.0, 0.0,
     0.25,  0.25, -0.25, 0.0, 0.0, 0.0,
    -0.25,  0.25,  0.25, 0.0, 0.0, 1.0,
     0.25,  0.25, -0.25, 1.0, 0.0, 1.0,
    -0.25,  0.25, -0.25, 1.0, 0.0, 1.0,
    -0.25, -0.25,  0.25, 1.0, 0.0, 1.0,
    -0.25, -0.25, -0.25, 1.0, 0.0, 1.0,
     0.25, -0.25,  0.25, 1.0, 0.0, 1.0,
    -0.25, -0.25, -0.25, 1.0, 0.0, 0.0,
     0.25, -0.25, -0.25, 1.0, 0.0, 0.0,
     0.25, -0.25,  0.25, 1.0, 0.0, 0.0
], dtype='float32') 

colors_ = np.array([
    0.0, 0.0, 0.0,
    0.0, 0.0, 1.0,
    0.0, 1.0, 0.0,
    0.0, 1.0, 1.0,
    1.0, 0.0, 0.0,
    1.0, 0.0, 1.0,
    1.0, 1.0, 0.0,
    1.0, 1.0, 1.0
], dtype='float32') 

USE_COLORS = True

vertices = np.array([], dtype='float32')

## Vertex shader.
vertex_code = """
#version 330 core
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 color;

out vec3 vColor;

uniform mat4 transform;

void main()
{
    gl_Position = transform * vec4(position, 1.0);
    vColor = color;
}
"""

## Fragment shader.
fragment_code = """
#version 330 core

in vec3 vColor;
out vec4 FragColor;

void main()
{
    FragColor = vec4(vColor, 1.0f);
} 
"""

## Display function
def display():

    global vertices
    gl.glClearColor(0.2, 0.3, 0.3, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    gl.glUseProgram(program)
    gl.glBindVertexArray(VAO)

    # Translation. 
    T  = ut.matTranslate(translation_x, translation_y, translation_z)
    # Rotation around z-axis.
    Rx = ut.matRotateX(np.radians(angle_x)) 
    Ry = ut.matRotateY(np.radians(angle_y)) 
    Rz = ut.matRotateZ(np.radians(angle_z)) 
    # Scale.
    S  = ut.matScale(scale_x, scale_y, scale_z)
    
    M = np.matmul(Ry,Rx)
    M = np.matmul(Rz,M)
    M = np.matmul(S, M)
    M = np.matmul(T,M)
    
    # Retrieve location of tranform variable in shader.
    loc = gl.glGetUniformLocation(program, "transform")
    # Send matrix to shader.
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, M.transpose())
    
    if(visualizacao == "FACES"):
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(vertices))
    elif (visualizacao == "WIREFRAME"):
        gl.glDrawArrays(gl.GL_LINE_STRIP, 0, len(vertices))
    glut.glutSwapBuffers()


## Reshape function.
def reshape(width,height):

    win_width = width
    win_height = height
    gl.glViewport(0, 0, width, height)
    glut.glutPostRedisplay()

def printInformations():
    print("Transformacao selecionada: ", transformacao)
    print("Visualizacao selecionada: ", visualizacao)

    if(transformacao == "TRANSLACAO"):
        print("translacao x: ", translation_x)
        print("translacao y: ", translation_y)
        print("translacao z: ", translation_z)
    elif(transformacao == "ROTACAO"):
        print("angulo x: ", angle_x)
        print("angulo y: ", angle_y)
        print("angulo z: ", angle_z)
    elif(transformacao == "ESCALA"):
        print("escala x: ", scale_x)
        print("escala y: ", scale_y)
        print("escala z: ", scale_z)

## Keyboard function.
def hasTransformation(key):
    if(key == b'w' or key == b'a' or key == b'd' or key == glut.GLUT_KEY_UP or key == glut.GLUT_KEY_DOWN or key == glut.GLUT_KEY_RIGHT or key == glut.GLUT_KEY_LEFT):
        return true
    return false

def aplyTransfromation(key):
    global translation_x, translation_y, translation_z, angle_x, angle_y, angle_z, scale_x, scale_y, scale_z
    
    if(key == b'w'):
        translation_x = 0.0
        translation_y = 0.0
        translation_z = 0.0
        angle_x = 0
        angle_y = 0
        angle_z = 0
        scale_x = 1.0
        scale_y = 1.0
        scale_z = 1.0
        
    if(transformacao == "TRANSLACAO"):
        if(key == glut.GLUT_KEY_UP): #y+
            translation_y = translation_y + translation_inc
        elif(key == glut.GLUT_KEY_DOWN): #y-
            translation_y = translation_y - translation_inc
        elif(key == glut.GLUT_KEY_RIGHT): #x+
            translation_x = translation_x + translation_inc
        elif(key == glut.GLUT_KEY_LEFT): #x-
            translation_x = translation_x - translation_inc
        elif(key == b'a'): #z+
            translation_z = translation_z + translation_inc
        elif(key == b'd'): # z-
            translation_z = translation_z - translation_inc
            
    elif(transformacao == "ROTACAO"):
        if(key == glut.GLUT_KEY_UP): #x+
            angle_x = angle_x + angle_inc
        elif(key == glut.GLUT_KEY_DOWN): #x-
            angle_x = angle_x - angle_inc
        elif(key == glut.GLUT_KEY_RIGHT): #y+
            angle_y = angle_y + angle_inc
        elif(key == glut.GLUT_KEY_LEFT): #y-
            angle_y = angle_y - angle_inc
        elif(key == b'a'): #z+
            angle_z = angle_z + angle_inc
        elif(key == b'd'): #z-
            angle_z = angle_z - angle_inc
    
    elif(transformacao == "ESCALA"):
        if(key == glut.GLUT_KEY_UP): #y>
            scale_y = 1.5
        elif(key == glut.GLUT_KEY_DOWN): #y<
            scale_y = 0.5
        elif(key == glut.GLUT_KEY_RIGHT): #x>
            scale_x = 1.5
        elif(key == glut.GLUT_KEY_LEFT): #x<
            scale_x = 0.5
        elif(key == b'a'): #z>
            scale_z = 1.5
        elif(key == b'd'): #z<
            scale_z = 0.0
            
def keyboard(key, x, y):

    global type_primitive
    global transformacao
    global visualizacao
    
    if key == b'\x1b' or key == b'q':
        glut.glutLeaveMainLoop()
    
    print("key:", key)
    
    if key == b'r':
        transformacao = "ROTACAO"
    elif key == b't':
        transformacao = "TRANSLACAO"
    
    elif key == b'e':
        transformacao = "ESCALA"    
        
    if key == b'v':
        if(visualizacao == "FACES"):
            visualizacao = "WIREFRAME"
        else:
            visualizacao = "FACES"
        
    if(hasTransformation):
        aplyTransfromation(key)
    
    printInformations()
    glut.glutPostRedisplay()


## Idle function.
def idle():
    glut.glutPostRedisplay()

## Init data.
def loadColors(tam):
    object_ = []
    global colors_
    for i in range(int(tam/3)):
        object_.append(colors_[(i*3)%len(colors_)])
        object_.append(colors_[(i*3+1)%len(colors_)])
        object_.append(colors_[(i*3+2)%len(colors_)])

    return object_ 
    
def loadObject():
    scene = pywavefront.Wavefront("cube.obj", collect_faces=True)
    object_ = []
    for mesh in scene.mesh_list:
        for face in mesh.faces:
            for vertex_i in face:
                x, y, z = scene.vertices[vertex_i]
                object_.append(x)
                object_.append(y)
                object_.append(z)
    
    if(not USE_COLORS):
        return np.array(object_, dtype='float32')  
    
    colors = loadColors(len(object_))
    
    obj_colored = []
    
    for i in range (int(len(object_)/3)):
        obj_colored.append(object_[i*3])
        obj_colored.append(object_[i*3+1])
        obj_colored.append(object_[i*3+2])
        obj_colored.append(colors[i*3])
        obj_colored.append(colors[i*3+1])
        obj_colored.append(colors[i*3+2])
        
    object_np = np.array(obj_colored, dtype='float32')
    
    return object_np 

def initData():

    # Uses vertex arrays.
    global VAO
    global VBO
    global vertices

    # Set vertices.
    vertices = loadObject() 
    
    # Vertex array.
    VAO = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(VAO)

    # Vertex buffer
    VBO = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)
    
    # Set attributes.
    if(not USE_COLORS):
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 3*vertices.itemsize, None)
        gl.glEnableVertexAttribArray(0)
    else:
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 6*vertices.itemsize, None)
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 6*vertices.itemsize, c_void_p(6*vertices.itemsize))
        gl.glEnableVertexAttribArray(1)
    
    gl.glEnable(gl.GL_DEPTH_TEST)
    # Unbind Vertex Array Object.
    gl.glBindVertexArray(0)

## Create program (shaders).
def initShaders():

    global program
    program = ut.createShaderProgram(vertex_code, fragment_code)


## Main function.
def main():

    glut.glutInit()
    glut.glutInitContextVersion(3, 3);
    glut.glutInitContextProfile(glut.GLUT_CORE_PROFILE);
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_DEPTH)
    glut.glutInitWindowSize(win_width,win_height)
    glut.glutCreateWindow('MESH')

    # Init vertex data for the triangle.
    initData()
    
    # Create shaders.
    initShaders()

    glut.glutReshapeFunc(reshape)
    glut.glutDisplayFunc(display)
    glut.glutKeyboardFunc(keyboard)
    glut.glutSpecialFunc(keyboard)
    glut.glutIdleFunc(idle);
    print("here")

    glut.glutMainLoop()

if __name__ == '__main__':
    main()
