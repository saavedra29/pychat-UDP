import tkinter as tk
import tkinter.ttk as ttk
from random import randint
import sys
from os import system, getpid
import platform

# This dictionary is used until the use of configuration file is implemented.
ini = {
    'MyLastIP': '46.177.109.151',
    'MyName': 'OdyK',
    'PeerIP01': '178.128.65.157',
    'PeerName01': 'OdyP',
    'EnableEncryption': False,
    'EnableCompression': False
}


# This customization of the Text widget allows elements of the text to be colored.
class CustomText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)

    def highlight_pattern(self, pattern, tag, start="1.0", end="end", regexp=False):
        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)

        count = tk.IntVar()
        while True:
            index = self.search(pattern, "matchEnd", "searchLimit", count=count, regexp=regexp)
            if index == "": break
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
            self.tag_add(tag, "matchStart", "matchEnd")


# Nested windows
def AboutWindow():
    aboutWin = tk.Toplevel(bg="white")
    aboutWin.geometry('394x210')
    aboutWin.resizable(width=False, height=False)
    aboutWin.title('About')

    # Top frame for the title
    top_frame = tk.Frame(aboutWin, borderwidth=2, bg="white")
    top_frame.pack(side="top", fill="x")

    labelTitle = tk.Label(top_frame, font="Arial 18", text="Chat v0.0000001", fg="#B62034",
                          bg="white")
    labelTitle.pack(side="left", pady=10, padx=40)

    # Middle frame for the authors
    mid_frame = tk.Frame(aboutWin, borderwidth=2, bg="white")
    mid_frame.pack(side="top", fill="x", padx=30)

    labelAuthors = tk.Label(mid_frame, text="Authors:\n", bg="white")
    labelAuthors.pack(side="left", pady=2, padx=10)

    if randint(1, 2) == 1:
        labelA = tk.Label(mid_frame, text="Aris\nOdy", bg="white")
    else:
        labelA = tk.Label(mid_frame, text="Ody\nAris", bg="white")
    labelA.pack(side="left", pady=0, padx=0)

    # OK button
    buttonOK = ttk.Button(aboutWin, text="OK", command=aboutWin.destroy)
    buttonOK.pack(side="bottom", pady=12)


# tkinter code
class MainWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.minsize(width=400, height=300)
        self.geometry("580x400")
        self.title("JUST GUI")
        self.protocol('WM_DELETE_WINDOW', self.on_exit)

        # Create a menubar and associate it with the window
        self.menubar = tk.Menu()
        self.config(menu=self.menubar)

        # Create File menu and add it to the menubar
        file_menu = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.on_exit)

        # Options menu
        options_menu = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label="Options", menu=options_menu)
        options_menu.add_command(label="Manage peers", command=self.on_manage_peers)
        options_menu.add_command(label="Settings", command=self.on_settings)

        # Server menu
        server_menu = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label="Server", menu=server_menu)
        server_menu.add_command(label="Start server", command=self.on_start_server)
        server_menu.add_command(label="Stop server", command=self.on_stop_server)

        # Help menu
        help_menu = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_cascade(label="About", command=AboutWindow)

        # Create Connection frame
        self.connection_frame = tk.Frame(self, borderwidth=5)
        self.connection_frame.pack(side="top", fill="x")

        # # Create Peer combobox and add it to Connection frame
        # self.peer_combobox = ttk.Combobox(self.connection_frame)
        # self.peer_combobox.pack(side = "left")

        # Create Peer combobox and add it to Connection frame
        self.ipEntry = ttk.Entry(self.connection_frame)
        self.ipEntry.pack(side="left")

        # Create Connect button and add it to Connection frame
        self.connect_button = ttk.Button(self.connection_frame, text="Connect",
                                         command=self.on_connect)
        self.connect_button.pack(side="left", padx=5)

        # Create Disconnect button and add it to Connection frame
        self.disconnect_button = ttk.Button(self.connection_frame, text="Disconnect",
                                            command=self.on_disconnect)
        self.disconnect_button.pack(side="left", padx=5)

        # Create Status label
        self.status_label = ttk.Label(self.connection_frame, text="Disconnected", width=17,
                                      foreground="red",
                                      relief='ridge', borderwidth=3, justify='center',
                                      anchor='center')
        self.status_label.pack(side="right", padx=5, ipadx=3, ipady=3)

        # Create Output frame
        self.output_frame = tk.Frame(self, borderwidth=5)
        self.output_frame.pack(side="top", padx=0, fill="both", expand=True)

        # Create Scrollbar and add it to the Output frame. This has to be packed before the Text widget
        self.scrollbar = tk.Scrollbar(self.output_frame)
        self.scrollbar.pack(side="right", fill="y", padx=5)

        # Create Text widget and add it to the Output frame
        self.output_text = CustomText(self.output_frame, height=10, width=40,
                                      yscrollcommand=self.scrollbar.set)
        self.output_text.tag_configure("green", foreground="green")
        self.output_text.pack(side="left", fill="both", expand=True)

        # Create Input frame
        self.input_frame = tk.Frame(self, borderwidth=5)
        self.input_frame.pack(side="top", fill="x")

        # Create User input entry and add it to Input frame
        self.userInputEntry = tk.Entry(self.input_frame)
        self.userInputEntry.bind("<Return>",
                                 self.on_enter_press)  # <Return> key binding for sending the data
        self.userInputEntry.pack(side="left", fill="x", expand=True)

        # # Create Send button and add it to Input frame
        # self.send_button = ttk.Button(self.input_frame, text="Send", command=self.on_enter_press)
        # self.send_button.pack(side="left", padx=5)


        # Create Debug frame
        self.debug_frame = tk.Frame(self)
        self.debug_frame.pack(side="top", fill="x")

        # Create Separator and add it to Debug frame
        self.sep = ttk.Separator(self.debug_frame)
        self.sep.pack(fill="x", pady=3)

        self.debug_label = tk.Label(self.debug_frame, text="Pending packets: ")
        self.debug_label.pack(side="left")

    # Functions of the menu buttons
    def insert_text(self, txt):
        self.output_text.insert("end", txt + "\n")
        self.output_text.see("end")

    def on_manage_peers(self):
        pass

    def on_settings(self):
        pass

    def on_start_server(self):
        self.insert_text("TODO: Start server")

    def on_stop_server(self):
        self.insert_text("TODO: Stop server")

    # Exit function
    def on_exit(self):
        id = getpid()
        os = platform.system()
        if os == 'Linux':
            command = 'kill ' + str(id)
            system(command)
        else:
            command = 'taskkill /pid ' + str(id)
            system(command)

    # Connect button function
    def on_connect(self):
        print("connect button pressed")

    # Disconnect button function
    def on_disconnect(self):
        print("disconnect button pressed")

    # Send_data function
    def on_enter_press(self, event):
        print("enter key pressed")


# app = MainWindow()
# app.mainloop()
