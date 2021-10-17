/**
 * @file window.cpp
 * Basic window creation.
 *
 * Set up and show a window using GLUT with simple keyboard, display and reshape functions.
 *
 * @author Ricardo Dutra da Silva
 */

#include <stdio.h>
#include <stdlib.h>
#include <GL/glew.h>
#include <GL/freeglut.h>


/* Globals */
/** Window width. */
int win_width  = 800;
/** Window height. */
int win_height = 600;


/* Functions. */
void display(void);
void reshape(int, int);
void keyboard(unsigned char, int, int);

/** 
 * Drawing function.
 *
 * A simple drawing function that only clears the color buffer.
 */
void display()
{
	/* Set RGBA color to "paint" cleared color buffer (background color). */
    	glClearColor(0.2, 0.3, 0.3, 1.0);

    	/* Clears color buffer to the RGBA defined values. */
    	glClear(GL_COLOR_BUFFER_BIT);


    	/* Demand to draw to the window.*/
    	glutSwapBuffers();
}

/**
 * Reshape function.
 *
 * Called when window is resized.
 *
 * @param width New window width.
 * @param height New window height.
 */
void reshape(int width, int height)
{
    // Save new window size in case it may be need elsewhere (not in this program).
    win_width = width;
    win_height = height;

    // Set the viewport (rectangle of visible area in the window).
    glViewport(0, 0, width, height);

    // Demand OpenGL to redraw scene (call display function).
    glutPostRedisplay();
}


/** 
 * Keyboard function.
 *
 * Called to treat pressed keys.
 *
 * @param key Pressed key.
 * @param x Mouse x coordinate when key pressed.
 * @param y Mouse y coordinate when key pressed.
 */

void keyboard(unsigned char key, int x, int y)
{
	/* Closing a window using the keyboard. */
        switch (key)
        {
                /* Escape key.*/
                case 27:
                        glutLeaveMainLoo();
                /* q key. */
                case 'q':
                case 'Q':
                        glutLeaveMainLoop();
        }
}

int main(int argc, char** argv)
{
	/* Init glut (always called). */
	glutInit(&argc, argv);
	
	/* Set OpenGL context version to use "Modern OpenGL" */
	glutInitContextVersion(3, 3);
	glutInitContextProfile(GLUT_CORE_PROFILE);

	/* Set glut to use double buffering with RGBA color attributes. */
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA);

	/* Set the size of the window. */
	glutInitWindowSize(win_width,win_height);

	/* Create window. */
	glutCreateWindow(argv[0]);

	/* Init GLEW, a extension loading library for different operating systems. */
	glewInit();
	
	/* Bind callback functions. */
    	glutReshapeFunc(reshape);
    	glutDisplayFunc(display);
    	glutKeyboardFunc(keyboard);

	/* Give control to GLUT, main loop that ends when the program ends. */
	glutMainLoop();
}
