#!/usr/bin/env python3
"""Parse command line options and arguments for the Logic Simulator.

This script parses options and arguments specified on the command line, and
runs either the command line user interface or the graphical user interface.

Usage
-----
Show help: logsim.py -h
Command line user interface: logsim.py -c <file path>
Graphical user interface: logsim.py <file path>
"""
import getopt
import sys
import os

import wx

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from userint import UserInterface
from gui import Gui
import app_const as appC
import app_base as ab

class MyDialog(wx.Dialog): 
   def __init__(self, parent, title): 
      super(MyDialog, self).__init__(parent, title = title, size = (250,100)) 
      panel = wx.Panel(self)
      self.languages = list(appC.supLang.keys())
      static_text = wx.StaticText(panel, wx.ID_ANY, 'Select Language')
      self.selector = wx.Choice(panel, wx.ID_ANY, choices=self.languages)
      self.selector.SetSelection(0)
      okayButton = wx.Button(panel, wx.ID_ANY, 'Ok')
      okayButton.Bind(wx.EVT_BUTTON, self.okayButton)
      cancelButton = wx.Button(panel, wx.ID_ANY, 'Cancel')
      cancelButton.Bind(wx.EVT_BUTTON, self.cancelButton)
      
      selector_sizer = wx.BoxSizer(wx.HORIZONTAL)
      control_sizer = wx.BoxSizer(wx.HORIZONTAL)
      main_sizer = wx.BoxSizer(wx.VERTICAL)

      selector_sizer.Add(static_text, 1, wx.EXPAND | wx.ALIGN_CENTER)
      selector_sizer.Add(self.selector, 1, wx.EXPAND)

      control_sizer.Add(okayButton, 1, wx.EXPAND)
      control_sizer.Add(cancelButton, 1, wx.EXPAND)

      main_sizer.Add(selector_sizer, 0, wx.EXPAND)
      main_sizer.Add(control_sizer, 0, wx.EXPAND)

      panel.SetSizer(main_sizer)

   def okayButton(self, event):
       self.EndModal(self.selector.GetSelection())

   def cancelButton(self, event):
       self.EndModal(-1)

def main(arg_list):
    """Parse the command line options and arguments specified in arg_list.

    Run either the command line user interface, the graphical user interface,
    or display the usage message.
    """
    usage_message = ("Usage:\n"
                     "Show help: logsim.py -h\n"
                     "Command line user interface: logsim.py -c <file path>\n"
                     "Graphical user interface: logsim.py <file path>")
    try:
        options, arguments = getopt.getopt(arg_list, "hc:")
    except getopt.GetoptError:
        print("Error: invalid command line arguments\n")
        print(usage_message)
        sys.exit()

    # Initialise instances of the four inner simulator classes
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)

    for option, path in options:
        if option == "-h":  # print the usage message
            print(usage_message)
            sys.exit()
        elif option == "-c":  # use the command line user interface
            scanner = Scanner(path, names)
            parser = Parser(names, devices, network, monitors, scanner)
            if parser.parse_network():
                # Initialise an instance of the userint.UserInterface() class
                userint = UserInterface(names, devices, network,
                                        monitors, scanner)
                userint.command_interface()

    if not options:  # no option given, use the graphical user interface

        if len(arguments) > 1:  # wrong number of arguments
            print("Error: one file path required\n")
            print(usage_message)
            sys.exit()

        if len(arguments) == 1:
            [path] = arguments
            scanner = Scanner(path, names)
            parser = Parser(names, devices, network, monitors, scanner)
            if parser.parse_network():
                app = wx.App()
                a = MyDialog(None, 'Language Selection')
                index = a.ShowModal()
                a.Destroy()
                if index != -1:
                    main_app = ab.BaseApp(redirect=False)
                    main_app.updateLanguage(list(appC.supLang.keys())[index])
                    gui = Gui("Logic Simulator", names, devices, network,
                              monitors, os.path.abspath(path), scanner, parser)
                    gui.Show(True)
                    main_app.MainLoop()

        if len(arguments) == 0:
            app = wx.App()
            a = MyDialog(None, 'Language Selection')
            index = a.ShowModal()
            a.Destroy()
            if index != -1:
                main_app = ab.BaseApp(redirect=False)
                main_app.updateLanguage(list(appC.supLang.keys())[index])
                gui = Gui("Logic Simulator", names, devices, network, monitors)
                gui.Show(True)
                main_app.MainLoop()


if __name__ == "__main__":
    main(sys.argv[1:])
