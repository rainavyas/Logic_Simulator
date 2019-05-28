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
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT

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
        self.current_signal = None
        self.current_monitor_points = None

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
        if monitors != None:
            self.current_signal, self.current_monitor_points = monitors.get_signals()
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw specified text at position (10, 10)
        self.render_text(text, 10, 10)

        if self.current_signal != None:
            for j in range(len(self.current_signal)):
                GL.glColor3f(random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0))  # signal trace is blue
                GL.glBegin(GL.GL_LINE_STRIP)
                for i in range(len(self.current_signal[j])):
                    x = (i * 20) + 30
                    x_next = (i * 20) + 50
                    if self.current_signal[j][i] == 0:
                        y = 75*(j+1)
                    else:
                        y = 75*(j+1)+25
                    GL.glVertex2f(x, y)
                    GL.glVertex2f(x_next, y)
                GL.glEnd()
                self.render_text('0', 10, 75*(j+1))
                self.render_text('1', 10, 75*(j+1)+25)
                self.render_text(self.current_monitor_points[j], 10, 75*(j+1)-20)
                self.render_text(self.current_monitor_points[j], 10, 75*(j+1)-20)

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
        text = ""
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            text = "".join(["Mouse button pressed at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.ButtonUp():
            text = "".join(["Mouse button released at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Leaving():
            text = "".join(["Mouse left canvas at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join(["Mouse dragged to: ", str(event.GetX()),
                            ", ", str(event.GetY()), ". Pan is now: ",
                            str(self.pan_x), ", ", str(self.pan_y)])
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False
            text = "".join(["Negative mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False
            text = "".join(["Positive mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if text:
            self.render(text)
        else:
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

#Do the scanner, parser stuffs
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

    def __init__(self, title, names, devices, network, monitors, path=None):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.path = path
        
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

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self)

        # Configure the widgets
        self.panel =scrolled.ScrolledPanel(self, size = wx.Size(250,250), style = wx.SUNKEN_BORDER)
        self.panel.SetAutoLayout(1)
        self.panel.SetupScrolling(False, True)
        self.file_picker = wx.FilePickerCtrl(self, message='Select Source File', wildcard='Text Files (*.txt)|*.txt')
        self.text_cycles = wx.StaticText(self, wx.ID_ANY, "Cycles:")
        self.text_mps = wx.StaticText(self, wx.ID_ANY, "Monitor Points")
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.run_button.SetBackgroundColour(wx.Colour(100, 255, 100))
        self.continue_button = wx.Button(self, wx.ID_ANY, "Continue")
        self.continue_button.SetBackgroundColour(wx.Colour(255, 255, 100))
        self.exit_button = wx.Button(self, wx.ID_ANY, "Exit")
        self.exit_button.SetBackgroundColour(wx.Colour(255, 130, 130))
        self.add_button = wx.Button(self, wx.ID_ANY, "Add")
        self.mp_names = wx.Choice(self, wx.ID_ANY, choices=['SELECT'])
        self.mp_names.SetSelection(0)
        
        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button)
        self.exit_button.Bind(wx.EVT_BUTTON, self.on_exit_button)
        self.add_button.Bind(wx.EVT_BUTTON, self.onAddMP)
        self.file_picker.Bind(wx.EVT_FILEPICKER_CHANGED, self.checkFile)

        # Configure sizers for layout
        top_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.side_sizer = wx.BoxSizer(wx.VERTICAL)
        cycle_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mp_sizer = wx.BoxSizer(wx.VERTICAL)
        mp_sizer_all = wx.BoxSizer(wx.VERTICAL)
        mp_control_sizer = wx.BoxSizer(wx.HORIZONTAL)

        top_sizer.Add(self.file_picker, 1, wx.EXPAND | wx.ALL, 5, 10)
        top_sizer.Add(main_sizer, 10, wx.EXPAND)

        main_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.side_sizer, 1, wx.RIGHT, 5)

        self.side_sizer.Add(cycle_sizer, 0, wx.ALL, 5)
        self.side_sizer.Add(buttons_sizer, 0, wx.ALL, 5)
        self.side_sizer.Add(mp_sizer_all, 1, wx.ALL, 5)

        cycle_sizer.Add(self.text_cycles, 1, wx.EXPAND)
        cycle_sizer.Add(self.spin, 3, wx.LEFT | wx.RIGHT, 5)

        buttons_sizer.Add(self.run_button, 1)
        buttons_sizer.Add(self.continue_button, 1)
        buttons_sizer.Add(self.exit_button, 1)

        mp_control_sizer.Add(self.mp_names, 1, wx.ALIGN_CENTRE)
        mp_control_sizer.Add(self.add_button, 1, wx.ALIGN_CENTRE | wx.LEFT | wx.RIGHT, 5)

        mp_sizer_all.Add(self.text_mps, 0, wx.RIGHT, 5)
        mp_sizer_all.Add(mp_control_sizer, 0, wx.RIGHT|wx.TOP, 5)
        mp_sizer_all.Add(self.panel, 1, wx.RIGHT|wx.TOP|wx.EXPAND, 5)

        self.panel.SetSizer(self.mp_sizer)

        if self.path != None:
            self.loadNetwork()

        self.SetSizeHints(600, 800)
        self.SetSizer(top_sizer)

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Mojisola Agboola\n2017",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        text = "".join(["New spin control value: ", str(spin_value)])
        self.canvas.render(text)

    def run_network(self, cycles):
        """Run the network for the specified number of simulation cycles.

        Return True if successful.
        """
        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                print("Error! Network oscillating.")
                return False
        self.canvas.render('Drawing signal', self.monitors)
        return True

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        text = "Run button pressed."
        self.canvas.render(text)

        self.cycles_completed = 0
        cycles = self.spin.GetValue()

        if cycles is not None:
            self.monitors.reset_monitors()
            self.devices.cold_startup()
            if self.run_network(cycles):
                self.cycles_completed += cycles

    def on_continue_button(self, event):
        """Handle the event when the user clicks the continue button."""
        text = "Continue button pressed."
        self.canvas.render(text)

        cycles = self.spin.GetValue()
        if cycles is not None:
            if self.cycles_completed == 0:
                print("Error! Nothing to continue. Run first.")
            elif self.run_network(cycles):
                self.cycles_completed += cycles

    def on_exit_button(self, event):
        """Handle the event when the user clicks the exit button."""
        self.Close()

    def onAddMP(self, event):
        """"""
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
            monitor_error = self.monitors.make_monitor(device, port, self.cycles_completed)
                    
            reset_index = self.mp_names.FindString('SELECT')
            self.mp_names.SetSelection(reset_index)
            text = "Monitor Point {} added.".format(mp_name)
            self.canvas.render(text)
            self.number_of_mps += 1
            self.all_mp_names.append(mp_name)
            new_button = wx.Button(self.panel, label='Remove', name=mp_name)
            new_sizer = wx.BoxSizer(wx.HORIZONTAL)
            new_sizer.Add(wx.StaticText(self.panel, wx.ID_ANY, mp_name), 1, wx.ALIGN_CENTRE)
            new_sizer.Add(new_button, 1, wx.LEFT | wx.RIGHT | wx.TOP, 5)
            new_button.Bind(wx.EVT_BUTTON, self.onRemoveMP)
            self.mp_sizer.Add(new_sizer, 0, wx.RIGHT, 5)
            self.Layout()

    def onRemoveMP(self, event):
        """"""
        mp_name = event.GetEventObject().GetName()
        self.mp_names.Append(mp_name)
        mp = mp_name.split('.')
        if len(mp) == 1:
            device = self.names.query(mp[0])
            port = None
        else:
            device = self.names.query(mp[0])
            port = self.names.query(mp[1])
        self.monitors.remove_monitor(device, port)
        index = self.all_mp_names.index(mp_name)
        text = "Monitor Point {} removed.".format(mp_name)
        self.canvas.render(text)
        self.mp_sizer.Hide(index)
        self.mp_sizer.Remove(index)
        self.number_of_mps -= 1
        self.Layout()
        del self.all_mp_names[index]

    def onToggleButton(self, event):
        button = event.GetEventObject()
        switch_id = self.names.query(button.GetName())
        if button.GetValue():
            self.devices.set_switch(switch_id, 1)
            button.SetBackgroundColour(wx.Colour(100, 255, 100))
            button.SetLabel('On')
            text = "{} turned on.".format(button.GetName())
            self.canvas.render(text)
        else:
            self.devices.set_switch(switch_id, 0)
            button.SetBackgroundColour(wx.Colour(255, 130, 130))
            button.SetLabel('Off')
            text = "{} turned off.".format(button.GetName())
            self.canvas.render(text)

    def checkFile(self, event):
        self.names = Names()
        self.devices = Devices(self.names)
        self.network = Network(self.names, self.devices)
        self.monitors = Monitors(self.names, self.devices, self.network)
        self.path = event.GetEventObject().GetPath()
        scanner = Scanner(self.path, self.names)
        parser = Parser(self.names, self.devices, self.network, self.monitors, scanner)
        if parser.parse_network():
            self.loadNetwork()
        else:
            self.clearNetwork()

    def loadNetwork(self):
        for i in range(len(self.all_mp_names)-1, -1, -1):
            name = self.all_mp_names[i]
            self.mp_sizer.Hide(i)
            self.mp_sizer.Remove(i)
            self.number_of_mps -= 1
            self.Layout()
            self.all_mp_names.remove(name)
        
        if self.loaded_switches == True:
            self.side_sizer.Hide(3)
            self.side_sizer.Remove(3)
            self.Layout()
            self.loaded_switches = False

        signal_list = self.monitors.get_signal_names()
        monitored_signal_list = signal_list[0]
        unmonitored_signal_list = signal_list[1]
        self.mp_names.Clear()
        self.mp_names.Append('SELECT')
        self.mp_names.SetSelection(0)
        self.mp_names.Append(unmonitored_signal_list)
            
        device_kind = self.names.query('SWITCH')
        switch_ids = self.devices.find_devices(device_kind)
        switch_initials = []
        switch_names = []
        for i in switch_ids:
            switch = self.devices.get_device(i)
            switch_initials.append(switch.switch_state)
            switch_names.append(self.names.get_name_string(i))
        
        if monitored_signal_list != []:
            for i in monitored_signal_list:
                mp = i.split('.')
                if len(mp) == 1:
                    device = self.names.query(mp[0])
                    port = None
                else:
                    device = self.names.query(mp[0])
                    port = self.names.query(mp[1])
                monitor_error = self.monitors.make_monitor(device, port, self.cycles_completed)
                self.number_of_mps += 1
                self.all_mp_names.append(i)
                new_button = wx.Button(self.panel, label='Remove', name=i)
                new_sizer = wx.BoxSizer(wx.HORIZONTAL)
                new_sizer.Add(wx.StaticText(self.panel, wx.ID_ANY, i), 1, wx.ALIGN_CENTRE)
                new_sizer.Add(new_button, 1, wx.LEFT | wx.RIGHT | wx.TOP, 5)
                new_button.Bind(wx.EVT_BUTTON, self.onRemoveMP)
                self.mp_sizer.Add(new_sizer, 0, wx.RIGHT, 5)
            self.Layout()

        if switch_names != []:
            text_switches = wx.StaticText(self, wx.ID_ANY, "Initial Switch Values:")
            switchpanel =scrolled.ScrolledPanel(self, size = wx.Size(250,250), style = wx.SUNKEN_BORDER)
            switchpanel.SetAutoLayout(1)
            switchpanel.SetupScrolling(False, True)
            
            switch_sizer_container = wx.BoxSizer(wx.VERTICAL)
            switch_sizer_all = wx.BoxSizer(wx.VERTICAL)

            self.side_sizer.Add(switch_sizer_all, 1, wx.ALL, 5)
            
            switchpanel.SetSizer(switch_sizer_container)
            
            switch_sizer_all.Add(text_switches, 0, wx.RIGHT, 5)
            switch_sizer_all.Add(switchpanel, 1, wx.TOP|wx.RIGHT|wx.EXPAND, 5)

            for i in range(len(switch_ids)):
                switch_sizer = wx.BoxSizer(wx.HORIZONTAL)
                switch_sizer.Add(wx.StaticText(switchpanel, wx.ID_ANY, '{}'.format(switch_names[i])), 1, wx.ALIGN_CENTRE)
                if switch_initials[i] == 1:
                    button = wx.ToggleButton(switchpanel, wx.ID_ANY, 'On', name='{}'.format(switch_names[i]))
                    button.SetBackgroundColour(wx.Colour(100, 255, 100))
                    button.SetValue(True)
                else:
                    button = wx.ToggleButton(switchpanel, wx.ID_ANY, 'Off', name='{}'.format(switch_names[i]))
                    button.SetBackgroundColour(wx.Colour(255, 130, 130))
                button.Bind(wx.EVT_TOGGLEBUTTON, self.onToggleButton)
                switch_sizer.Add(button, 1, wx.ALIGN_CENTRE | wx.LEFT | wx.RIGHT, 5)
                switch_sizer_container.Add(switch_sizer, 0, wx.TOP|wx.RIGHT, 5)

            self.loaded_switches = True
            self.Layout()

    def clearNetwork(self):
        for i in range(len(self.all_mp_names)-1, -1, -1):
            name = self.all_mp_names[i]
            self.mp_sizer.Hide(i)
            self.mp_sizer.Remove(i)
            self.number_of_mps -= 1
            self.Layout()
            self.all_mp_names.remove(name)

        if self.loaded_switches == True:
            self.side_sizer.Hide(3)
            self.side_sizer.Remove(3)
            self.Layout()
            self.loaded_switches = False

        self.mp_names.Clear()
        self.mp_names.Append('SELECT')
        self.mp_names.SetSelection(0)
