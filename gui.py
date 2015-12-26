import tkinter as tk
import tkinter.ttk as ttk
from os import system, getpid
import platform


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


# tkinter code
class MainWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.minsize(width=400, height=300)
        self.geometry("580x400")
        self.title("JUST GUI")
        self.protocol('WM_DELETE_WINDOW', self.on_exit)
        self.keyFromWindowInput = ''
        self.imageOrangePath = 'images/orange15.png'
        self.imageGreenPath = 'images/green15.png'
        self.orangeImg = tk.PhotoImage(file=self.imageOrangePath)
        self.greenImg = tk.PhotoImage(file=self.imageGreenPath)

        # Create a menubar and associate it with the window
        self.menubar = tk.Menu()
        self.config(menu=self.menubar)

        # Create File menu and add it to the menubar
        self.file_menu = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Exit", command=self.on_exit)

        # Server menu
        self.server_menu = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label="Server", menu=self.server_menu)
        self.server_menu.add_command(label="Start server", command=self.on_start_server)
        self.server_menu.add_command(label="Stop server", command=self.on_stop_server)

        # Encryption menu
        self.gen_key_menu = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label="Encryption", menu=self.gen_key_menu)
        self.gen_key_menu.add_command(label="Encryption on", command=self.on_encryption_on)
        self.gen_key_menu.add_command(label="Encryption off", command=self.on_encryption_off)
        self.gen_key_menu.add_command(label="Generate key", command=self.on_generate_key)
        self.gen_key_menu.add_command(label="Place remote key", command=self.on_place_key)




        # Create Connection frame
        self.connection_frame = tk.Frame(self, borderwidth=5)
        self.connection_frame.pack(side="top", fill="x")

        # Create Peer combobox and add it to Connection frame
        self.ipEntry = ttk.Entry(self.connection_frame)
        self.ipEntry.pack(side="left")

        # Create setPeer button and add it to Connection frame
        self.setPeer_button = ttk.Button(self.connection_frame, text="Set peer",
                                         command=self.on_setPeer)
        self.setPeer_button.pack(side="left", padx=5)

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
        self.output_text.tag_configure("red", foreground="red")
        self.output_text.pack(side="left", fill="both", expand=True)

        # Create Input frame
        self.input_frame = tk.Frame(self, borderwidth=5)
        self.input_frame.pack(side="top", fill="x")

        # Create User input entry and add it to Input frame
        self.userInputEntry = tk.Entry(self.input_frame)
        self.userInputEntry.bind("<Return>",
                                 self.on_enter_press)  # <Return> key binding for sending the data
        self.userInputEntry.pack(side="left", fill="x", expand=True)

        self.encryption_indicator = tk.Label(self.input_frame, image=self.orangeImg)
        self.encryption_indicator.pack(side='right')

        # Create Debug frame
        self.debug_frame = tk.Frame(self)
        self.debug_frame.pack(side="top", fill="x")

        # Create Separator and add it to Debug frame
        self.sep = ttk.Separator(self.debug_frame)
        self.sep.pack(fill="x", pady=3)

        self.debug_label = tk.Label(self.debug_frame)
        self.debug_label.pack(side="left")


    # Functions of the menu buttons
    def insert_text(self, txt):
        self.output_text.insert("end", txt + "\n")
        self.output_text.highlight_pattern('Server ==>', 'red')
        self.output_text.highlight_pattern('Peer ==>', 'green')
        self.output_text.see("end")

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

    # Set peer function
    def on_setPeer(self):
        print("set peer pressed")

    # Connect button function
    def on_connect(self):
        print("connect button pressed")

    # Disconnect button function
    def on_disconnect(self):
        print("disconnect button pressed")

    # Send_data function
    def on_enter_press(self, event):
        print("enter key pressed")

    def on_encryption_on(self):
        pass

    def on_encryption_off(self):
        pass

    def on_generate_key(self):
        pass

    def on_place_key(self):
        pass

    def on_create_key_window(self, key):
        create_key_window = tk.Toplevel()
        create_key_window.minsize(360, 200)
        create_key_window.grab_set()
        create_key_window.title('Key Generation')
        instructions_message = tk.Message(create_key_window,
                                               text='This is the automatically generated key. '
                                                    'The remote peer should have exactly the '
                                                    'same for the encryption-decryption to be '
                                                    'possible.\nUse Ctrl-C to copy.')
        instructions_message.bind("<Configure>", lambda e:
        instructions_message.configure(width=e.width - 10))
        instructions_message.pack(fill=tk.X, expand=True)
        messageEntry = tk.Entry(create_key_window, state='readonly')
        var = tk.StringVar()
        print(key)
        print(key.decode('utf8'))
        var.set(key.decode('utf8'))
        messageEntry.config(textvariable=var)
        messageEntry.pack(expand=True, fill=tk.X)
        generate_key_button = tk.Button(create_key_window, text='OK',
                                      command=create_key_window.destroy)
        generate_key_button.pack()

    def assign(self):
        pass

    def on_place_key_window(self):
        self.place_key_window = tk.Toplevel()
        self.place_key_window.minsize(360, 200)
        self.place_key_window.grab_set()
        self.place_key_window.title('Key Generation')
        self.instructions_message = tk.Message(self.place_key_window,
                                         text='Please place the remote peer key.')
        self.instructions_message.bind('<Configure>', lambda e:
        self.instructions_message.configure(width=e.width - 10))
        self.instructions_message.pack(fill=tk.X, expand=True)
        self.keyEntry = tk.Entry(self.place_key_window)
        self.keyEntry.pack()
        self.submit_key_button = tk.Button(self.place_key_window, text='Submit',
                                      command = self.assign)
        self.submit_key_button.pack()




