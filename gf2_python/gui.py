"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import wx
import wx.lib.scrolledpanel as scrolled
import random
import os
import wx.glcanvas as wxcanvas
import numpy as np
import math
from OpenGL import GL, GLUT, GLU

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser


class MyGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self, text): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.
    """

    def __init__(self, parent):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)
        self.current_signal = []
        self.current_monitor_points = []
        self.signal_colours = []

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise variables for zooming
        self.zoom = 1

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def render(self, text, monitors=None):
        """Handle all drawing operations."""
        if monitors is not None:
            self.current_signal, self.current_monitor_points = (
                monitors.get_signals())
            for i in range(len(self.current_monitor_points)):
                self.signal_colours.append([random.uniform(0.0, 1.0), (
                    random.uniform(0.0, 1.0)), random.uniform(0.0, 1.0)])
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw specified text at position (10, 10)
        self.render_text(text, 10, 10)

        # Draw signals
        if self.current_signal != []:
            # Draw each signal
            for j in range(len(self.current_signal)):
                GL.glColor3f(self.signal_colours[j][0], (
                    self.signal_colours[j][1]), self.signal_colours[j][2])
                GL.glBegin(GL.GL_LINE_STRIP)
                for i in range(len(self.current_signal[j])):
                    x = (i * 20) + 40
                    x_next = (i * 20) + 60
                    if self.current_signal[j][i] == 0:
                        y = 75*(j+1)+30
                    else:
                        y = 75*(j+1)+55
                    GL.glVertex2f(x, y)
                    GL.glVertex2f(x_next, y)
                GL.glEnd()
                self.render_text('0', 10, 75*(j+1)+30)
                self.render_text('1', 10, 75*(j+1)+55)
                self.render_text(self.current_monitor_points[j], 10, (
                    75*(j+1)+10))
                self.render_text(self.current_monitor_points[j], 10, (
                    75*(j+1)+10))

            # Draw time-step axis
            GL.glColor3f(0, 0, 0)
            GL.glBegin(GL.GL_LINE_STRIP)
            for i in range(len(self.current_signal[0])):
                x = (i * 20) + 40
                x_next = (i * 20) + 60
                y = 50
                GL.glVertex2f(x, y)
                GL.glVertex2f(x_next, y)
            GL.glEnd()
            for i in range(len(self.current_signal[0])+1):
                GL.glColor3f(0, 0, 0)
                GL.glBegin(GL.GL_LINE_STRIP)
                x = (i * 20) + 40
                y_bottom = 45
                y_top = 55
                GL.glVertex2f(x, y_bottom)
                GL.glVertex2f(x, y_top)
                GL.glEnd()

            # Label time-step axis
            for i in range(len(self.current_signal[0])+1):
                self.render_text(str(i), (i * 20) + 39, 25)
            self.render_text('time', 10, 45)

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        text = ""
        self.render(text)

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        text = ""
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False
        self.render(text)
        self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

    def reset(self):
        """Resets the viewframe to original position"""
        GL.glLoadIdentity()
        self.pan_x = 0
        self.pan_y = 0
        self.zoom = 1

    def clear(self):
        """Clears the canvas and resets position"""
        self.reset()
        self.current_signal = []
        self.current_monitor_points = []
        self.signal_colours = []
        self.render('Canvas Cleared')


class My3DGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos, z_pos): Handles text drawing
                                                  operations.
    """

    def __init__(self, parent):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        self.current_signal = []
        self.current_monitor_points = []
        self.signal_colours = []

        # Constants for OpenGL materials and lights
        self.mat_diffuse = [0.0, 0.0, 0.0, 1.0]
        self.mat_no_specular = [0.0, 0.0, 0.0, 0.0]
        self.mat_no_shininess = [0.0]
        self.mat_specular = [0.5, 0.5, 0.5, 1.0]
        self.mat_shininess = [50.0]
        self.top_right = [1.0, 1.0, 1.0, 0.0]
        self.straight_on = [0.0, 0.0, 1.0, 0.0]
        self.no_ambient = [0.0, 0.0, 0.0, 1.0]
        self.dim_diffuse = [0.5, 0.5, 0.5, 1.0]
        self.bright_diffuse = [1.0, 1.0, 1.0, 1.0]
        self.med_diffuse = [0.75, 0.75, 0.75, 1.0]
        self.full_specular = [0.5, 0.5, 0.5, 1.0]
        self.no_specular = [0.0, 0.0, 0.0, 1.0]

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise the scene rotation matrix
        self.scene_rotate = np.identity(4, 'f')

        # Initialise variables for zooming
        self.zoom = 1

        # Offset between viewpoint and origin of the scene
        self.depth_offset = 1000

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)


    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)

        GL.glViewport(0, 0, size.width, size.height)

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluPerspective(45, size.width / size.height, 10, 10000)

        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()  # lights positioned relative to the viewer
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_AMBIENT, self.no_ambient)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_DIFFUSE, self.med_diffuse)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_SPECULAR, self.no_specular)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, self.top_right)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_AMBIENT, self.no_ambient)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_DIFFUSE, self.dim_diffuse)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_SPECULAR, self.no_specular)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_POSITION, self.straight_on)

        GL.glMaterialfv(GL.GL_FRONT, GL.GL_SPECULAR, self.mat_specular)
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_SHININESS, self.mat_shininess)
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_AMBIENT_AND_DIFFUSE,
                        self.mat_diffuse)
        GL.glColorMaterial(GL.GL_FRONT, GL.GL_AMBIENT_AND_DIFFUSE)

        GL.glClearColor(0.0, 0.0, 0.0, 0.0)
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glShadeModel(GL.GL_SMOOTH)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glCullFace(GL.GL_BACK)
        GL.glEnable(GL.GL_COLOR_MATERIAL)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_LIGHTING)
        GL.glEnable(GL.GL_LIGHT0)
        GL.glEnable(GL.GL_LIGHT1)
        GL.glEnable(GL.GL_NORMALIZE)

        # Viewing transformation - set the viewpoint back from the scene
        GL.glTranslatef(0.0, 0.0, -self.depth_offset)

        # Modelling transformation - pan, zoom and rotate
        GL.glTranslatef(self.pan_x, self.pan_y, 0.0)
        GL.glMultMatrixf(self.scene_rotate)
        GL.glScalef(self.zoom, self.zoom, self.zoom)

    def render(self, text, monitors=None):
        """Handle all drawing operations."""

        """if monitors is not None:
            self.current_signal, self.current_monitor_points = (
                monitors.get_signals())
            for i in range(len(self.current_monitor_points)):
                self.signal_colours.append([random.uniform(0.0, 1.0), (
                    random.uniform(0.0, 1.0)), random.uniform(0.0, 1.0)])
        self.SetCurrent(self.context)"""

        if monitors is not None:
            self.current_signal, self.current_monitor_points = (
                monitors.get_signals())
            for i in range(len(self.current_monitor_points)):
                self.signal_colours.append([random.uniform(0.0, 1.0), (
                    random.uniform(0.0, 1.0)), random.uniform(0.0, 1.0)])

        if not self.init:
            # Configure the OpenGL rendering context
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        # Draw a sample signal trace, make sure its centre of gravity
        # is at the scene origin
        GL.glColor3f(1.0, 0.7, 0.5)  # signal trace is beige
        for i in range(-10, 10):
            z = i * 20
            if i % 2 == 0:
                self.draw_cuboid(0, z, 5, 10, 1)
            else:
                self.draw_cuboid(0, z, 5, 10, 11)

        GL.glColor3f(1.0, 1.0, 1.0)  # text is white
        self.render_text("D1.QBAR", 0, 0, 210)

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def draw_cuboid(self, x_pos, z_pos, half_width, half_depth, height):
        """Draw a cuboid.

        Draw a cuboid at the specified position, with the specified
        dimensions.
        """
        GL.glBegin(GL.GL_QUADS)
        GL.glNormal3f(0, -1, 0)
        GL.glVertex3f(x_pos - half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos + half_depth)
        GL.glVertex3f(x_pos - half_width, -6, z_pos + half_depth)
        GL.glNormal3f(0, 1, 0)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos + half_depth)
        GL.glNormal3f(-1, 0, 0)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6, z_pos + half_depth)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos + half_depth)
        GL.glNormal3f(1, 0, 0)
        GL.glVertex3f(x_pos + half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos + half_depth)
        GL.glNormal3f(0, 0, -1)
        GL.glVertex3f(x_pos - half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos - half_depth)
        GL.glNormal3f(0, 0, 1)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos + half_depth)
        GL.glVertex3f(x_pos - half_width, -6, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos + half_depth)
        GL.glEnd()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the OpenGL rendering context
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(size.width), ", ", str(size.height)])
        self.render(text)

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        self.SetCurrent(self.context)

        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()

        if event.Dragging():
            GL.glMatrixMode(GL.GL_MODELVIEW)
            GL.glLoadIdentity()
            x = event.GetX() - self.last_mouse_x
            y = event.GetY() - self.last_mouse_y
            if event.LeftIsDown():
                GL.glRotatef(math.sqrt((x * x) + (y * y)), y, x, 0)
            if event.MiddleIsDown():
                GL.glRotatef((x + y), 0, 0, 1)
            if event.RightIsDown():
                self.pan_x += x
                self.pan_y -= y
            GL.glMultMatrixf(self.scene_rotate)
            GL.glGetFloatv(GL.GL_MODELVIEW_MATRIX, self.scene_rotate)
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False

        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False

        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False

        self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos, z_pos):
        """Handle text drawing operations."""
        GL.glDisable(GL.GL_LIGHTING)
        GL.glRasterPos3f(x_pos, y_pos, z_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_10

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos3f(x_pos, y_pos, z_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

        GL.glEnable(GL.GL_LIGHTING)

    def reset(self):
        """Resets the viewframe to original position"""
        self.pan_x = 0
        self.pan_y = 0
        self.zoom = 1
        self.scene_rotate = np.identity(4, 'f')
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslatef(0.0, 0.0, -self.depth_offset)

    def clear(self):
        """Clears the canvas and resets position"""
        self.reset()
        self.current_signal = []
        self.current_monitor_points = []
        self.signal_colours = []
        self.render('Canvas Cleared')


class Gui(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: title of the window.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_text_box(self, event): Event handler for when the user enters text.
    """

    def __init__(self, title, names, devices, network,
                 monitors, path=None, scanner=None, parser=None):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        # Configure locally global variables
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.path = path
        self.scanner = scanner
        self.parser = parser

        self.loaded_network = False
        self.number_of_mps = 0
        self.all_mp_names = []
        self.cycles_completed = 0
        self.loaded_switches = False

        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)

        # Create panels for the frame
        self.main_panel = wx.Panel(self)
        self.top_panel = wx.Panel(self)
        self.mp_panel = scrolled.ScrolledPanel(self.main_panel,
                                               size=wx.Size(250, 250),
                                               style=wx.SUNKEN_BORDER)
        self.mp_panel.SetAutoLayout(1)
        self.mp_panel.SetupScrolling(False, True)

        # Canvas for drawing signals
        self.canvas = My3DGLCanvas(self.main_panel)

        # Configure the widgets
        self.file_picker = (
            wx.FilePickerCtrl(self.top_panel, message='Select Source File',
                              wildcard='Text Files (*.txt)|*.txt'))
        self.text_cycles = wx.StaticText(self.main_panel, wx.ID_ANY, "Cycles:")
        self.text_mps = wx.StaticText(self.main_panel, wx.ID_ANY,
                                      "Monitor Points")
        self.spin = wx.SpinCtrl(self.main_panel, wx.ID_ANY, "10", min=1)
        self.run_button = wx.Button(self.main_panel, wx.ID_ANY, "Run")
        self.run_button.SetBackgroundColour(wx.Colour(100, 255, 100))
        self.continue_button = wx.Button(self.main_panel, wx.ID_ANY,
                                         "Continue")
        self.continue_button.SetBackgroundColour(wx.Colour(255, 255, 100))
        self.exit_button = wx.Button(self.main_panel, wx.ID_ANY, "Exit")
        self.exit_button.SetBackgroundColour(wx.Colour(255, 130, 130))
        self.add_button = wx.Button(self.main_panel, wx.ID_ANY, "Add")
        self.canvas_button = wx.Button(self.main_panel, wx.ID_ANY, 'Switch to 2D Traces')
        self.mp_names = wx.Choice(self.main_panel, wx.ID_ANY,
                                  choices=['SELECT'])
        self.mp_names.SetSelection(0)

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button)
        self.exit_button.Bind(wx.EVT_BUTTON, self.on_exit_button)
        self.add_button.Bind(wx.EVT_BUTTON, self.onAddMP)
        self.file_picker.Bind(wx.EVT_FILEPICKER_CHANGED, self.checkFile)
        self.canvas_button.Bind(wx.EVT_BUTTON, self.switchCanvas)

        # Configure sizers for layout
        frame_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.side_sizer = wx.BoxSizer(wx.VERTICAL)
        cycle_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mp_sizer = wx.BoxSizer(wx.VERTICAL)
        mp_sizer_all = wx.BoxSizer(wx.VERTICAL)
        mp_control_sizer = wx.BoxSizer(wx.HORIZONTAL)

        frame_sizer.Add(self.top_panel, 1, wx.EXPAND)
        frame_sizer.Add(self.main_panel, 10, wx.EXPAND)

        self.main_panel.SetSizer(self.main_sizer)
        self.top_panel.SetSizer(top_sizer)

        top_sizer.Add(self.file_picker, 1, wx.EXPAND | wx.ALL, 5, 10)

        self.main_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)
        self.main_sizer.Add(self.side_sizer, 1, wx.RIGHT, 5)

        self.side_sizer.Add(cycle_sizer, 0, wx.ALL, 5)
        self.side_sizer.Add(buttons_sizer, 0, wx.ALL, 5)
        self.side_sizer.Add(mp_sizer_all, 1, wx.ALL, 5)
        self.side_sizer.Add(self.canvas_button, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        cycle_sizer.Add(self.text_cycles, 1, wx.EXPAND)
        cycle_sizer.Add(self.spin, 3, wx.LEFT | wx.RIGHT, 5)

        buttons_sizer.Add(self.run_button, 1)
        buttons_sizer.Add(self.continue_button, 1)
        buttons_sizer.Add(self.exit_button, 1)

        mp_control_sizer.Add(self.mp_names, 1, wx.ALIGN_CENTRE)
        mp_control_sizer.Add(self.add_button, 1,
                             wx.ALIGN_CENTRE | wx.LEFT | wx.RIGHT, 5)

        mp_sizer_all.Add(self.text_mps, 0, wx.RIGHT, 5)
        mp_sizer_all.Add(mp_control_sizer, 0, wx.RIGHT | wx.TOP, 5)
        mp_sizer_all.Add(self.mp_panel, 1, wx.RIGHT | wx.TOP | wx.EXPAND, 5)

        self.mp_panel.SetSizer(self.mp_sizer)

        # If filepath given in command line, loads network
        if self.path is not None:
            abs_path = os.path.abspath(self.path)
            self.file_picker.SetPath(abs_path)
            self.file_picker.Update()
            self.loadNetwork()

        # Sets minimum screen size and frame's sizer
        self.SetSizeHints(800, 800)
        self.SetSizer(frame_sizer)

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox(
                ("Logic Simulator\nCreated by Jonty Page," +
                 " Vyas Raina and James Crossley\n2019"),
                "About Logsim", wx.ICON_INFORMATION | wx.OK)

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        text = "".join(["New spin control value: ", str(spin_value)])
        self.canvas.render(text)

    def run_network(self, cycles):
        """Run the network for the specified number of simulation cycles.

        If successful, return True. If unsuccessful, display error message.
        """
        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
                self.canvas.render('Drawing signal', self.monitors)
            else:
                text = "Error! Network oscillating."
                print(text)
                self.displayError(text)
                return False
        return True

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        # Reset canvas and render notification
        self.canvas.reset()
        text = "Run button pressed."
        self.canvas.render(text)

        # Reset number of cycles and run network as desired
        if self.loaded_network:
            self.cycles_completed = 0
            cycles = self.spin.GetValue()

            if cycles is not None:
                self.monitors.reset_monitors()
                self.devices.cold_startup()
                if self.run_network(cycles):
                    self.cycles_completed += cycles

    def on_continue_button(self, event):
        """Handle the event when the user clicks the continue button."""
        # Render notification
        text = "Continue button pressed."
        self.canvas.render(text)

        # Run network for desired cycles continuing from previous point
        if self.loaded_network:
            cycles = self.spin.GetValue()
            if cycles is not None:
                if self.cycles_completed == 0:
                    text = "Error! Nothing to continue. Run first."
                    print(text)
                    self.displayError(text)
                elif self.run_network(cycles):
                    self.cycles_completed += cycles

    def on_exit_button(self, event):
        """Handle the event when the user clicks the exit button."""
        self.Close()

    def onAddMP(self, event):
        """Handle the event when the user clicks the Add button"""
        # Finds selected monitor points and adds to monitor object
        index = self.mp_names.GetSelection()
        mp_name = self.mp_names.GetString(index)
        if mp_name != 'SELECT':
            self.mp_names.Delete(index)
            mp = mp_name.split('.')
            if len(mp) == 1:
                device = self.names.query(mp[0])
                port = None
            else:
                device = self.names.query(mp[0])
                port = self.names.query(mp[1])
            self.monitors.make_monitor(
                device, port, self.cycles_completed)

            # Removes monitor point from drop-down list
            reset_index = self.mp_names.FindString('SELECT')
            self.mp_names.SetSelection(reset_index)

            # Adds monitor point and remove button to GUI
            text = "Monitor Point {} added.".format(mp_name)
            self.canvas.render(text)
            self.number_of_mps += 1
            self.all_mp_names.append(mp_name)
            new_button = wx.Button(self.mp_panel, label='Remove', name=mp_name)
            new_sizer = wx.BoxSizer(wx.HORIZONTAL)
            new_sizer.Add(wx.StaticText(self.mp_panel, wx.ID_ANY, mp_name),
                          1, wx.ALIGN_CENTRE)
            new_sizer.Add(new_button, 1, wx.LEFT | wx.RIGHT | wx.TOP, 5)
            new_button.Bind(wx.EVT_BUTTON, self.onRemoveMP)
            self.mp_sizer.Add(new_sizer, 0, wx.RIGHT, 5)
            self.Layout()

    def onRemoveMP(self, event):
        """Handle the event when the user clicks the remove button"""
        # Finds selected monitor points and removes from monitor object
        mp_name = event.GetEventObject().GetName()
        mp = mp_name.split('.')
        if len(mp) == 1:
            device = self.names.query(mp[0])
            port = None
        else:
            device = self.names.query(mp[0])
            port = self.names.query(mp[1])
        self.monitors.remove_monitor(device, port)

        # Adds monitor point to drop-down list
        self.mp_names.Append(mp_name)

        # Removes monitor point and remove button from GUI
        index = self.all_mp_names.index(mp_name)
        text = "Monitor Point {} removed.".format(mp_name)
        self.canvas.render(text)
        self.mp_sizer.Hide(index)
        self.mp_sizer.Remove(index)
        self.number_of_mps -= 1
        self.Layout()
        del self.all_mp_names[index]

    def onToggleButton(self, event):
        """Handle the event when the user clicks a switch's toggle button"""
        button = event.GetEventObject()
        switch_id = self.names.query(button.GetName())
        if button.GetValue():
            # Switch is off, so turn button on and green
            self.devices.set_switch(switch_id, 1)
            button.SetBackgroundColour(wx.Colour(100, 255, 100))
            button.SetLabel('On')
            text = "{} turned on.".format(button.GetName())
            self.canvas.render(text)
        else:
            # Switch is on, so turn button off and red
            self.devices.set_switch(switch_id, 0)
            button.SetBackgroundColour(wx.Colour(255, 130, 130))
            button.SetLabel('Off')
            text = "{} turned off.".format(button.GetName())
            self.canvas.render(text)

    def checkFile(self, event):
        """Check file selected by filepickerctrl is successfully parsed

        If succesful, load network. If unsuccessful, display error message.
        """
        # Run selected file path through scanner and parser
        self.names = Names()
        self.devices = Devices(self.names)
        self.network = Network(self.names, self.devices)
        self.monitors = Monitors(self.names, self.devices, self.network)
        self.path = event.GetEventObject().GetPath()
        self.scanner = Scanner(self.path, self.names)
        self.parser = Parser(self.names, self.devices,
                             self.network, self.monitors, self.scanner)
        # Check network definition file is correctly configured
        if self.parser.parse_network():
            # Clear old network, load new and reset file picker colour
            self.top_panel.SetBackgroundColour(wx.NullColour)
            self.clearNetwork()
            self.loadNetwork()
        else:
            # Clear old network, display error message and change colour
            self.clearNetwork()
            self.displaySyntaxErrors()
            self.top_panel.SetBackgroundColour(wx.Colour(255, 130, 130))

    def loadNetwork(self):
        """Loads switches and monitoring points from file into GUI"""
        # Find list of monitored and unmonitored signals
        signal_list = self.monitors.get_signal_names()
        monitored_signal_list = signal_list[0]
        unmonitored_signal_list = signal_list[1]
        self.mp_names.Append(unmonitored_signal_list)

        # Find list of switch names
        device_kind = self.names.query('SWITCH')
        switch_ids = self.devices.find_devices(device_kind)
        switch_initials = []
        switch_names = []
        for i in switch_ids:
            switch = self.devices.get_device(i)
            switch_initials.append(switch.switch_state)
            switch_names.append(self.names.get_name_string(i))

        # Load monitored signals from file to GUI
        if monitored_signal_list != []:
            for i in monitored_signal_list:
                mp = i.split('.')
                if len(mp) == 1:
                    device = self.names.query(mp[0])
                    port = None
                else:
                    device = self.names.query(mp[0])
                    port = self.names.query(mp[1])
                self.monitors.make_monitor(
                    device, port, self.cycles_completed)
                self.number_of_mps += 1
                self.all_mp_names.append(i)
                new_button = wx.Button(self.mp_panel, label='Remove', name=i)
                new_sizer = wx.BoxSizer(wx.HORIZONTAL)
                new_sizer.Add(wx.StaticText(self.mp_panel, wx.ID_ANY, i),
                              1, wx.ALIGN_CENTRE)
                new_sizer.Add(new_button, 1, wx.LEFT | wx.RIGHT | wx.TOP, 5)
                new_button.Bind(wx.EVT_BUTTON, self.onRemoveMP)
                self.mp_sizer.Add(new_sizer, 0, wx.RIGHT, 5)
            self.Layout()

        # Load switches from file to GUI
        if switch_names != []:
            text_switches = wx.StaticText(
                self.main_panel, wx.ID_ANY, "Switch Values:")
            switchpanel = scrolled.ScrolledPanel(
                self.main_panel, size=wx.Size(250, 250),
                style=wx.SUNKEN_BORDER)
            switchpanel.SetAutoLayout(1)
            switchpanel.SetupScrolling(False, True)

            switch_sizer_container = wx.BoxSizer(wx.VERTICAL)
            switch_sizer_all = wx.BoxSizer(wx.VERTICAL)

            self.side_sizer.Add(switch_sizer_all, 1, wx.ALL, 5)

            switchpanel.SetSizer(switch_sizer_container)

            switch_sizer_all.Add(text_switches, 0, wx.RIGHT, 5)
            switch_sizer_all.Add(switchpanel, 1,
                                 wx.TOP | wx.RIGHT | wx.EXPAND, 5)

            for i in range(len(switch_ids)):
                switch_sizer = wx.BoxSizer(wx.HORIZONTAL)
                switch_sizer.Add(wx.StaticText(
                    switchpanel, wx.ID_ANY, '{}'.format(switch_names[i])),
                    1, wx.ALIGN_CENTRE)
                if switch_initials[i] == 1:
                    button = wx.ToggleButton(
                        switchpanel, wx.ID_ANY, 'On',
                        name='{}'.format(switch_names[i]))
                    button.SetBackgroundColour(wx.Colour(100, 255, 100))
                    button.SetValue(True)
                else:
                    button = wx.ToggleButton(
                        switchpanel, wx.ID_ANY, 'Off',
                        name='{}'.format(switch_names[i]))
                    button.SetBackgroundColour(wx.Colour(255, 130, 130))
                button.Bind(wx.EVT_TOGGLEBUTTON, self.onToggleButton)
                switch_sizer.Add(button, 1,
                                 wx.ALIGN_CENTRE | wx.LEFT | wx.RIGHT, 5)
                switch_sizer_container.Add(switch_sizer, 0,
                                           wx.TOP | wx.RIGHT, 5)

            self.loaded_switches = True
            self.Layout()

        self.loaded_network = True

    def clearNetwork(self):
        """Clears the switches and monitoring points from the GUI"""
        # Clear monitored points from GUI
        for i in range(len(self.all_mp_names)-1, -1, -1):
            name = self.all_mp_names[i]
            self.mp_sizer.Hide(i)
            self.mp_sizer.Remove(i)
            self.number_of_mps -= 1
            self.Layout()
            self.all_mp_names.remove(name)

        self.mp_names.Clear()
        self.mp_names.Append('SELECT')
        self.mp_names.SetSelection(0)

        # Clear switches from GUI
        if self.loaded_switches is True:
            self.side_sizer.Hide(3)
            self.side_sizer.Remove(3)
            self.Layout()
            self.loaded_switches = False

        # Clears canvas of previous signals
        self.canvas.clear()

        # Clears cycles completed
        self.cycles_completed = 0

        self.loaded_network = False

    def displaySyntaxErrors(self):
        """Displays message dialog containing nature of syntax error"""
        # Create message dialog
        error_message = wx.MessageDialog(
            self, '',
            'ERROR - FILE INVALID - {} Errors'.format(str(len(self.scanner.error_list))),
            style=wx.OK | wx.CENTRE | wx.STAY_ON_TOP)
        error_string = ''
        font = error_message.GetFont()
        dc = wx.ScreenDC()
        dc.SetFont(font)
        # Create error string and ensures correct caret location
        for i in self.scanner.error_list:
            error_string += i.msg
            error_string += '\n'
            error_string += i.line_num
            error_string += '\n'
            error_string += i.line
            error_string += '\n'
            caret_string = list(i.caret_pos)
            sub_string = i.line[:len(caret_string)-1]
            w, h = dc.GetTextExtent(sub_string)
            space_w, space_h = dc.GetTextExtent(' ')
            error_string += ' '*round(w/space_w) + '^'
            error_string += '\n'
        error_message.SetMessage(error_string)
        error_message.ShowModal()
        error_message.Destroy()
        self.file_picker.SetPath('')

    def displayError(self, text):
        """Displays message dialog containing nature of runtime error"""
        # Create message dialog with error string
        error_message = wx.MessageDialog(
            self, text, caption='RUNTIME ERROR',
            style=wx.OK | wx.CENTRE | wx.STAY_ON_TOP)
        error_message.ShowModal()
        error_message.Destroy()

    def switchCanvas(self, event):
        button = event.GetEventObject()
        if button.GetLabel() == 'Switch to 2D Traces':
            self.main_sizer.Hide(0)
            self.main_sizer.Remove(0)
            self.canvas = MyGLCanvas(self.main_panel)
            self.main_sizer.Insert(0, self.canvas, 5, wx.EXPAND | wx.ALL, 5)
            button.SetLabel('Switch to 3D Traces')
            self.Layout()
        else:
            self.main_sizer.Hide(0)
            self.main_sizer.Remove(0)
            self.canvas = My3DGLCanvas(self.main_panel)
            self.main_sizer.Insert(0, self.canvas,5, wx.EXPAND | wx.ALL, 5)
            button.SetLabel('Switch to 2D Traces')
            self.Layout()
