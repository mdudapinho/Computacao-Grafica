##########################################################
################## TRABALHO 2 - CUBEMAP ##################
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
import math

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
modo = 0.0 # 0.0 - Nada, 1.0 - Iluminacao, 2.0 - Textura

vertices = np.array([], dtype='float32')

## Vertex shader.
vertex_code = """
#version 330 core
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec3 vNormal;
out vec3 fragPosition;
out vec3 aTexture;

void main()
{
    gl_Position = projection * view * model * vec4(position, 1.0);
    vNormal = mat3(transpose(inverse(model))) * normal;
    fragPosition = vec3(model * vec4(position, 1.0));
    aTexture = normal;//vNormal;
}
"""

## Fragment shader.
fragment_code = """
#version 330 core

in vec3 vNormal;
in vec3 fragPosition;
in vec3 aTexture;

out vec4 fragColor;

uniform int modo;
uniform vec3 objectColor;
uniform vec3 lightColor;
uniform vec3 lightPosition;
uniform vec3 cameraPosition;
uniform samplerCube ourTexture;

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

    vec3 light = objectColor;
    if(modo == 1){
        light = (ambient + diffuse + specular) * objectColor;
    }
    else if (modo == 2){
        light = (ambient + diffuse + specular) * textureColor;
    }
    fragColor = vec4(light, 1.0);
}
"""

def read_texture(texture_file):
    global texture

    img1 = Image.open(texture_file + "/right.jpg")
    img_data1 = np.array(list(img1.getdata()), np.int8)
    
    img2 = Image.open(texture_file + "/left.jpg")
    img_data2 = np.array(list(img2.getdata()), np.int8)
    
    img3 = Image.open(texture_file + "/top.jpg")
    img_data3 = np.array(list(img3.getdata()), np.int8)
    
    img4 = Image.open(texture_file + "/bottom.jpg")
    img_data4 = np.array(list(img4.getdata()), np.int8)
    
    img5 = Image.open(texture_file + "/front.jpg")
    img_data5 = np.array(list(img5.getdata()), np.int8)
    
    img6 = Image.open(texture_file + "/back.jpg")
    img_data6 = np.array(list(img6.getdata()), np.int8)
    
    texture = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, texture)

    format = gl.GL_RGB if img1.mode == "RGB" else gl.GL_RGBA   # if the texture is jpg or png
    
    gl.glTexImage2D(gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X, 0, gl.GL_RGB, img1.size[0], img1.size[1], 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, img_data1)
    gl.glTexImage2D(gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_X, 0, gl.GL_RGB, img1.size[0], img1.size[1], 0, format, gl.GL_UNSIGNED_BYTE, img_data2)
    gl.glTexImage2D(gl.GL_TEXTURE_CUBE_MAP_POSITIVE_Y, 0, gl.GL_RGB, img1.size[0], img1.size[1], 0, format, gl.GL_UNSIGNED_BYTE, img_data3)
    gl.glTexImage2D(gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_Y, 0, gl.GL_RGB, img1.size[0], img1.size[1], 0, format, gl.GL_UNSIGNED_BYTE, img_data4)
    gl.glTexImage2D(gl.GL_TEXTURE_CUBE_MAP_POSITIVE_Z, 0, gl.GL_RGB, img1.size[0], img1.size[1], 0, format, gl.GL_UNSIGNED_BYTE, img_data5)
    gl.glTexImage2D(gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_Z, 0, gl.GL_RGB, img1.size[0], img1.size[1], 0, format, gl.GL_UNSIGNED_BYTE, img_data6)
    
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE)
    
## Display function
def display():

    global vertices
    gl.glClearColor(0.2, 0.3, 0.3, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, texture)

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
    
    # Retrieve locatiovisualizacao_texturan of tranform variable in shader.
    loc = gl.glGetUniformLocation(program, "model")
    # Send matrix to shader.
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, M.transpose())
    
    view = ut.matTranslate(0.0, 0.0, t_z)
    loc = gl.glGetUniformLocation(program, "view")
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, view.transpose())
    
    projection = ut.matPerspective(np.radians(45.0), win_width/win_height, 0.1, 100.0)
    loc = gl.glGetUniformLocation(program, "projection")
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
    # visualizacao_textura.
    loc = gl.glGetUniformLocation(program, "modo")
    gl.glUniform1i(loc, np.int32(modo))

    if(visualizacao == "FACES"):
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
    elif (visualizacao == "WIREFRAME"):
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        
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
    if(modo == 0):
        print("Iluminacao selecionada: Cor")
    elif(modo == 1):
        print("Iluminacao selecionada: Iluminacao")
    elif(modo == 2):
        print("Iluminacao selecionada: Textura")

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
    if(key == b'w' or key == b'a' or key == b'd' or key == glut.GLUT_KEY_UP or key == glut.GLUT_KEY_DOWN or key == glut.GLUT_KEY_RIGHT or key == glut.GLUT_KEY_LEFT or key == b'0' or key == b'1' or key == b'2'):
        return true
    return false

def applyTransfromation(key):
    global translation_x, translation_y, translation_z, angle_x, angle_y, angle_z, scale_x, scale_y, scale_z, modo
    
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
        
    elif(transformacao == "TRANSLACAO"):
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
         
    if(key == b'0'): #Object color
        modo = 0
    elif(key == b'1'): #Object iluminacao
        modo = 1
    elif(key == b'2'): #Object texture
        modo = 2
      
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
        applyTransfromation(key)
    
    printInformation()
    glut.glutPostRedisplay()

## Init data.
def normalizeObject(obj, max_coord, x_medio, y_medio, z_medio):
    for i in range(int(len(obj)/3)):
        obj[i*3] = (obj[i*3] - x_medio) / max_coord
        obj[i*3+1] = (obj[i*3+1] - y_medio) / max_coord
        obj[i*3+2] = (obj[i*3+2] - z_medio) / max_coord
    return obj

def getIndexes(object_file):
    faces = []
    with open(object_file) as f:
        lines = f.readlines()
        for line in lines:
            if line[0] == 'f':
                space_split = line.split(' ')

                faces.append([int(space_split[1]) - 1,
                                int(space_split[2]) - 1,
                                int(space_split[3]) - 1])
                
                if len(space_split) == 5:
                    faces.append([int(space_split[1].split('/')[0]) - 1,
                                    int(space_split[3].split('/')[0]) - 1,
                                    int(space_split[4].split('/')[0]) - 1])
    
    return faces

def getIndexesAndNormals(object_file):
    faces = []
    normals = []
    with open(object_file) as f:
        lines = f.readlines()
        for line in lines:
            if line[0] == 'f':
                space_split = line.split(' ')

                faces.append([int(space_split[1].split('/')[0]) - 1,
                                int(space_split[2].split('/')[0]) - 1,
                                int(space_split[3].split('/')[0]) - 1])
                
                normals.append([int(space_split[1].split('/')[2]) - 1,
                                int(space_split[2].split('/')[2]) - 1,
                                int(space_split[3].split('/')[2]) - 1])

                if len(space_split) == 5:
                    faces.append([int(space_split[1].split('/')[0]) - 1,
                                    int(space_split[3].split('/')[0]) - 1,
                                    int(space_split[4].split('/')[0]) - 1])

                    normals.append([int(space_split[1].split('/')[2]) - 1,
                                    int(space_split[3].split('/')[2]) - 1,
                                    int(space_split[4].split('/')[2]) - 1])
    return faces, normals

def getIndexesFromObject(scene, object_file):
    normals = []
    if scene.parser.normals != []:
        face_indexes, normal_indexes = getIndexesAndNormals(object_file)
        normals = scene.parser.normals
    else:
        face_indexes = getIndexes(object_file)
        normal_indexes = face_indexes
        normals = scene.vertices 
    return face_indexes, normal_indexes, normals 
    
def getObject(face_indexes, normal_indexes, scene, normals):
    object_ = []
    max_coord = 0
    x_max = scene.vertices[0][0]
    x_min = scene.vertices[0][0]
    y_max = scene.vertices[0][1]
    y_min = scene.vertices[0][1]
    z_max = scene.vertices[0][2]
    z_min = scene.vertices[0][2]
    
    for face, normal in zip(face_indexes, normal_indexes):
        for v_face, v_normal in zip(face, normal):
            x, y, z = scene.vertices[v_face]    
            n1, n2, n3 = normals[v_normal]
            object_.append(x)
            object_.append(y)
            object_.append(z)
            #normal
            object_.append(n1)
            object_.append(n2)
            object_.append(n3)
            
            x_max = max(x_max, x)
            x_min = min(x_min, x)
            y_max = max(y_max, y)
            y_min = min(y_min, y)
            z_max = max(z_max, z)
            z_min = min(z_min, z)
            
    x_medio = (x_max + x_min)/2
    y_medio = (y_max + y_min)/2
    z_medio = (z_max + z_min)/2
    
    max_coord = max(abs(x_max - x_min), abs(y_max - y_min), abs(z_max - z_min))/2
    object_ = normalizeObject(object_, max_coord, x_medio, y_medio, z_medio)
    return object_
    

def loadObject(object_file):
    print("loading ", object_file)
    scene = pywavefront.Wavefront(object_file, create_materials=True, collect_faces=True)
       
    face_indexes, normal_indexes, normals = getIndexesFromObject(scene, object_file)
    object_ = getObject(face_indexes, normal_indexes, scene, normals)
        
    return np.array(object_, dtype='float32')  

def initData(object_file, texture_file):

    # Uses vertex arrays.
    global VAO, VBO, vertices

    # Set vertices.
    vertices = loadObject(object_file) 
    
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
    # Set normals
    gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 6*vertices.itemsize, c_void_p(3*vertices.itemsize))
    gl.glEnableVertexAttribArray(1)
         
    read_texture(texture_file)
    # Unbind Vertex Array Object.
    gl.glBindVertexArray(0)
    
    gl.glEnable(gl.GL_DEPTH_TEST)
    
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
    
    if(sys.argv[2]):
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
