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
from PIL import Image
from ctypes import c_void_p
import pywavefront
import random


USE_COLORS = False

texture_file = None
texture = None

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

t_z = -5

#Scale
scale_x = 1.0
scale_y = 1.0
scale_z = 1.0
scale_inc = 0.1

## Rotation 
angle_x = 0.0
angle_y = 0.0
angle_z = 0.0
angle_inc = 1.0

## Modes
transformacao = 0 #ROTACAO, TRANSLACAO, ESCALA
visualizacao = "FACES" #FACES, WIREFRAME


colors_ = np.array([
    0.0, 0.0, 0.0, 
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 1.0,
    0.0, 0.0, 1.0,
    0.0, 0.0, 1.0,
    0.0, 1.0, 0.0,
    0.0, 1.0, 0.0,
    0.0, 1.0, 0.0,
    0.0, 1.0, 1.0,
    0.0, 1.0, 1.0,
    0.0, 1.0, 1.0,
    1.0, 0.0, 0.0,
    1.0, 0.0, 0.0,
    1.0, 0.0, 0.0,
    1.0, 0.0, 1.0,
    1.0, 0.0, 1.0,
    1.0, 0.0, 1.0,
    1.0, 1.0, 0.0,
    1.0, 1.0, 0.0,
    1.0, 1.0, 0.0,
    1.0, 1.0, 1.0,
    1.0, 1.0, 1.0,
    1.0, 1.0, 1.0
], dtype='float32') 

vertices = np.array([], dtype='float32')

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

    img = Image.open(texture_file)
    img_data = np.array(list(img.getdata()), np.int8)
    texture = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture)

    gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_BORDER)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_BORDER)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR_MIPMAP_LINEAR)
    # gl.glTexEnvf(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_DECAL)

    format = gl.GL_RGB if img.mode == "RGB" else gl.GL_RGBA   # if the texture is jpg or png
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, img.size[0], img.size[1], 0,
                    format, gl.GL_UNSIGNED_BYTE, img_data)
    gl.glGenerateMipmap(gl.GL_TEXTURE_2D)


## Display function
def display():

    global vertices
    gl.glClearColor(0.2, 0.3, 0.3, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    gl.glBindTexture(gl.GL_TEXTURE_2D, texture)

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
    loc = gl.glGetUniformLocation(program, "model")
    # Send matrix to shader.
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, M.transpose())
    
    view = ut.matTranslate(0.0, 0.0, t_z)
    loc = gl.glGetUniformLocation(program, "view")
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


    
    #if(visualizacao == "FACES"):
        #gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
    #elif (visualizacao == "WIREFRAME"):
        #gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        
    gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(vertices))
    glut.glutSwapBuffers()

## Reshape function.
def reshape(width,height):

    win_width = width
    win_height = height
    gl.glViewport(0, 0, width, height)
    glut.glutPostRedisplay()

def printInformation():
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
            scale_y = scale_y + scale_inc
        elif(key == glut.GLUT_KEY_DOWN): #y<
            scale_y = scale_y - scale_inc
        elif(key == glut.GLUT_KEY_RIGHT): #x>
            scale_x = scale_x + scale_inc
        elif(key == glut.GLUT_KEY_LEFT): #x<
            scale_x = scale_x - scale_inc
        elif(key == b'a'): #z>
            scale_z = scale_z + scale_inc
        elif(key == b'd'): #z<
            scale_z = scale_z - scale_inc
            
def keyboard(key, x, y):

    global type_primitive, transformacao, visualizacao
    
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
    
    printInformation()
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
    
def normalizeObj(obj, max_coord):
    for i in range(int(len(obj)/8)):
        obj[i*8] = obj[i*8] / max_coord
        obj[i*8+1] = obj[i*8+1] / max_coord
        obj[i*8+2] = obj[i*8+2] / max_coord
    return obj
    
def loadObject(object_file, texture_file):
    print("loading ", object_file)
    scene = pywavefront.Wavefront(object_file, collect_faces=True)
    object_ = []
    max_coord = 0
    for mesh in scene.mesh_list:
        for face in mesh.faces:
            for vertex_i in face:
                x, y, z = scene.vertices[vertex_i]
                object_.append(x/3)
                object_.append(y/3)
                object_.append(z/3)
                 #normal
                object_.append(random.random())
                object_.append(random.random())
                object_.append(random.random())
                #texture
                object_.append(random.random())
                object_.append(random.random())
                max_coord = max(max_coord, x, y, z)
    
    #object_ = normalizeObj(object_, int(max_coord))
    
    if(not USE_COLORS):
        return np.array(object_, dtype='float32')  
    
    colors = loadColors(len(object_))
    obj_colored = []
    ind = 0
    print("len(object_): ", len(object_))
    print("len(object_)/3: ", len(object_)/3)
    print("len(colors_): ", len(colors))
    for i in range (int(len(object_)/3)):
        obj_colored.append(object_[i*3])
        obj_colored.append(object_[i*3+1])
        obj_colored.append(object_[i*3+2])
        obj_colored.append(colors[ind])
        obj_colored.append(colors[ind+1])
        obj_colored.append(colors[ind+2])
        obj_colored.append(colors[ind+3])
        obj_colored.append(colors[ind+4])
        ind = ind+4
        
    object_np = np.array(obj_colored, dtype='float32')

    return object_np 

def initData(object_file, texture_file):

    # Uses vertex arrays.
    global VAO, VBO, vertices

    # Set vertices.
    vertices = loadObject(object_file, texture_file) 
    
    # Vertex array.
    VAO = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(VAO)

    # Vertex buffer
    VBO = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)
    
    # Set attributes.
    if(not USE_COLORS):
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 8*vertices.itemsize, None)
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 8*vertices.itemsize, c_void_p(3*vertices.itemsize))
        gl.glEnableVertexAttribArray(1)
        # texture coord attribute
        gl.glVertexAttribPointer(2, 2, gl.GL_FLOAT, gl.GL_FALSE, 8*vertices.itemsize, c_void_p(6*vertices.itemsize))
        gl.glEnableVertexAttribArray(2)
    else:
        #gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 6*vertices.itemsize, None)
        #gl.glEnableVertexAttribArray(0)
        #gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 6*vertices.itemsize, c_void_p(3*vertices.itemsize))
        #gl.glEnableVertexAttribArray(1)
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

## Create program (shaders).
def initShaders():
    global program
    program = ut.createShaderProgram(vertex_code, fragment_code)

## Main function.
def main():
    global texture_file

    glut.glutInit()
    glut.glutInitContextVersion(3, 3)
    glut.glutInitContextProfile(glut.GLUT_CORE_PROFILE)
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_DEPTH)
    glut.glutInitWindowSize(win_width,win_height)
    glut.glutCreateWindow('Texture')

    # Init vertex data for the object.
    object_file = sys.argv[1]
    print("object_file: ", object_file)
    
    texture_file = sys.argv[2]
    print("texture_file: ", texture_file)
    
    initData(object_file, texture_file)
    
    # Create shaders.
    initShaders()

    glut.glutReshapeFunc(reshape)
    glut.glutDisplayFunc(display)
    glut.glutKeyboardFunc(keyboard)
    glut.glutSpecialFunc(keyboard)

    glut.glutMainLoop()

if __name__ == '__main__':
    main()
