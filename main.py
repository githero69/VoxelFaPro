import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy
import pyrr
import TextureLoader
from Camera import Camera
from Component import Component
from Step import Step
from Tool import Tool
from Point import Point
import math
import csv

WIDTH, HEIGHT = 1440, 920
CONST_SCALE = 1

# Camera
cam = Camera()
lastX, lastY = WIDTH / 2, HEIGHT / 2
first_mouse = True
left, right, forward, backward = False, False, False, False


def to_int(arg):
    return int(float(arg) * CONST_SCALE)


def remove_duplicates(lis):
    new_list = []
    new_list.append(lis[0])
    new_list_count = 0

    for i in range(len(lis)):
        if lis[i].y != new_list[new_list_count].y:
            new_list.append(lis[i])
            new_list_count += 1
    return new_list


def calculate_circle(tool_):
    circle_points = []
    radius = tool_.diameter / 2

    for i in range(91 * CONST_SCALE):
        point_x = int(radius * math.cos((i / CONST_SCALE) * math.pi / 180) * CONST_SCALE)
        point_y = int(radius * math.sin((i / CONST_SCALE) * math.pi / 180) * CONST_SCALE)

        point = Point(point_x, point_y)
        circle_points.append(point)
    return circle_points


def calculate_height(current_step, component):
    old_height = component.getArrayAt(current_step.x, current_step.y)
    diff = old_height - (current_step.z - 15)
    if diff > 0:
        new_height = old_height - diff
    else:
        new_height = old_height
    return new_height


# Key-Callbacks
# the keyboard input callback
def key_input_clb(window, key, scancode, action, mode):
    global left, right, forward, backward
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)

    if key == glfw.KEY_W and action == glfw.PRESS:
        forward = True
    elif key == glfw.KEY_W and action == glfw.RELEASE:
        forward = False
    if key == glfw.KEY_S and action == glfw.PRESS:
        backward = True
    elif key == glfw.KEY_S and action == glfw.RELEASE:
        backward = False
    if key == glfw.KEY_A and action == glfw.PRESS:
        left = True
    elif key == glfw.KEY_A and action == glfw.RELEASE:
        left = False
    if key == glfw.KEY_D and action == glfw.PRESS:
        right = True
    elif key == glfw.KEY_D and action == glfw.RELEASE:
        right = False


# do the movement, call this function in the main loop
def do_movement():
    if left:
        cam.process_keyboard("LEFT", 1.0)
    if right:
        cam.process_keyboard("RIGHT", 1.0)
    if forward:
        cam.process_keyboard("FORWARD", 1.0)
    if backward:
        cam.process_keyboard("BACKWARD", 1.0)


# the mouse position callback function
def mouse_look_clb(window, xpos, ypos):
    global first_mouse, lastX, lastY

    if first_mouse:
        lastX = xpos
        lastY = ypos
        first_mouse = False

    xoffset = xpos - lastX
    yoffset = lastY - ypos

    lastX = xpos
    lastY = ypos

    cam.process_mouse_movement(xoffset, yoffset)


def window_resize(window, width, height):
    glViewport(0, 0, width, height)


def main():
    length = 70
    width = 70
    height = 30
    steps = []

    with open('tasche.csv') as tasche:
        reader = csv.reader(tasche, delimiter=' ')
        for zeile in reader:
            step = Step(to_int(zeile[0]),
                        to_int(zeile[1]),
                        to_int(zeile[2]),
                        to_int(zeile[3]),
                        to_int(zeile[4]),
                        to_int(zeile[5]))
            steps.append(step)

    tool = Tool(8, 30, 0, 2)
    component = Component(length, width, height)

    points = calculate_circle(tool)
    new_points = remove_duplicates(points)
    new_points.reverse()

    # initialize glfw
    if not glfw.init():
        return

    w_width, w_height = 1280, 720
    aspect_ratio = w_width / w_height

    window = glfw.create_window(w_width, w_height, "My OpenGL window", None, None)

    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_window_size_callback(window, window_resize)
    # set the callback function for window resize
    # glfw.set_window_size_callback(win, window_resize_clb)
    # set the mouse position callback
    glfw.set_cursor_pos_callback(window, mouse_look_clb)
    # set the keyboard input callback
    glfw.set_key_callback(window, key_input_clb)
    # capture the mouse cursor
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    #        positions        texture_coords
    cube = [-0.5, -0.5, 0.5, 0.0, 0.0,
            0.5, -0.5, 0.5, 1.0, 0.0,
            0.5, 0.5, 0.5, 1.0, 1.0,
            -0.5, 0.5, 0.5, 0.0, 1.0,

            -0.5, -0.5, -0.5, 0.0, 0.0,
            0.5, -0.5, -0.5, 1.0, 0.0,
            0.5, 0.5, -0.5, 1.0, 1.0,
            -0.5, 0.5, -0.5, 0.0, 1.0,

            0.5, -0.5, -0.5, 0.0, 0.0,
            0.5, 0.5, -0.5, 1.0, 0.0,
            0.5, 0.5, 0.5, 1.0, 1.0,
            0.5, -0.5, 0.5, 0.0, 1.0,

            -0.5, 0.5, -0.5, 0.0, 0.0,
            -0.5, -0.5, -0.5, 1.0, 0.0,
            -0.5, -0.5, 0.5, 1.0, 1.0,
            -0.5, 0.5, 0.5, 0.0, 1.0,

            -0.5, -0.5, -0.5, 0.0, 0.0,
            0.5, -0.5, -0.5, 1.0, 0.0,
            0.5, -0.5, 0.5, 1.0, 1.0,
            -0.5, -0.5, 0.5, 0.0, 1.0,

            0.5, 0.5, -0.5, 0.0, 0.0,
            -0.5, 0.5, -0.5, 1.0, 0.0,
            -0.5, 0.5, 0.5, 1.0, 1.0,
            0.5, 0.5, 0.5, 0.0, 1.0]

    cube = numpy.array(cube, dtype=numpy.float32)

    indices = [0, 1, 2, 2, 3, 0,
               4, 5, 6, 6, 7, 4,
               8, 9, 10, 10, 11, 8,
               12, 13, 14, 14, 15, 12,
               16, 17, 18, 18, 19, 16,
               20, 21, 22, 22, 23, 20]

    indices = numpy.array(indices, dtype=numpy.uint32)

    vertex_shader = """
    #version 330
    in layout(location = 0) vec3 position;
    in layout(location = 1) vec2 texture_cords;
    in layout(location = 2) vec3 offset;
    uniform mat4 model;
    uniform mat4 projection;
    uniform mat4 view;
    out vec2 textures;
    void main()
    {
        vec3 final_pos = vec3(position.x + offset.x, position.y + offset.y, position.z + offset.z);
        gl_Position =  projection * view * model * vec4(final_pos, 1.0f);
        textures = texture_cords;
    }
    """

    fragment_shader = """
    #version 330
    in vec2 textures;
    out vec4 color;
    uniform sampler2D tex_sampler;
    void main()
    {
        color = texture(tex_sampler, textures);
    }
    """
    shader = OpenGL.GL.shaders.compileProgram(OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
                                              OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))

    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, cube.itemsize * len(cube), cube, GL_STATIC_DRAW)

    EBO = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.itemsize * len(indices), indices, GL_STATIC_DRAW)

    # position
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, cube.itemsize * 5, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    # textures
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, cube.itemsize * 5, ctypes.c_void_p(12))
    glEnableVertexAttribArray(1)

    # instances
    instance_array = []
    offset = 1
    for z in range(0, length, 1):
        for y in range(0, height, 1):
            for x in range(0, width, 1):
                translation = pyrr.Vector3([0.0, 0.0, 0.0])
                translation.x = x + offset
                translation.y = y + offset
                translation.z = z + offset
                instance_array.append(translation)

    instance_array = numpy.array(instance_array, numpy.float32)

    instanceVBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, instanceVBO)
    glBufferData(GL_ARRAY_BUFFER, instance_array.nbytes, instance_array, GL_STATIC_DRAW)

    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
    glEnableVertexAttribArray(2)
    glVertexAttribDivisor(2, 1)

    textures = glGenTextures(1)
    TextureLoader.load_texture("crate.jpg", textures)

    glUseProgram(shader)

    glClearColor(0.1, 0.1, 0.2, 1.0)
    glEnable(GL_DEPTH_TEST)

    # model = matrix44.create_from_translation(Vector3([-14.0, -8.0, 0.0]))
    # view = matrix44.create_from_translation(Vector3([0.0, 0.0, -20.0]))
    projection = pyrr.matrix44.create_perspective_projection_matrix(45.0, aspect_ratio, 0.1, 300.0)
    cube_pos = pyrr.matrix44.create_from_translation(pyrr.Vector3([-20.0, 0.0, -50.0]))

    # mv = matrix44.multiply(model, view)
    # mvp = matrix44.multiply(mv, projection)

    # mvp_loc = glGetUniformLocation(shader, "mvp")
    # glUniformMatrix4fv(mvp_loc, 1, GL_FALSE, mvp)

    model_loc = glGetUniformLocation(shader, "model")
    proj_loc = glGetUniformLocation(shader, "projection")
    view_loc = glGetUniformLocation(shader, "view")

    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, cube_pos)

    index = 0
    heights = []

    while not glfw.window_should_close(window):
        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        do_movement()

        view = cam.get_view_matrix()
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

        height = calculate_height(steps[index], component)
        for i in range(new_points[0].y):
            component.remove_circle(steps[index].x, steps[index].y, new_points[i].x, new_points[i].y, height)

        for outer in range(width):
            for inner in range(length):
                heights.append((component.array[inner][outer], inner, outer))
        for runner in range(0, len(heights), 1):
            if heights[runner][0] < 30:
                a = heights[runner][0]
                b = heights[runner][1]
                c = heights[runner][2]
                for a in range(a, 30*70, 70):
                    d = a + b + c * 2100
                    if d < 146999:
                        instance_array[d] = None

        glBufferData(GL_ARRAY_BUFFER, instance_array.nbytes, instance_array, GL_STATIC_DRAW)
        glDrawElementsInstanced(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None, len(instance_array))

        heights.clear()
        if index < len(steps) - 1:
            index += 1
        else:
            print("finito")

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
