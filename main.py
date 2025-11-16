import threading
import tkinter as tk
from tkinter import ttk, messagebox
from game_scanner import GameScanner
from MetaDataRetrieval import GameMetadataRetriever
import os
from PIL import Image, ImageTk
from io import BytesIO
import requests
import json
import socket
import ssl

# VARIABLES
host = '127.0.0.1'
port = 5000


class OrderlyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        # VARIABLES
        self.login_frame = None
        self.signup_frame = None
        self.socket = None
        self.host = "localhost"
        self.port = 5000
        self.cover_fetch_index = 0
        self.password_entry = None
        self.email_entry = None
        self.username_entry = None
        self.user = None
        self.static = None  # Variable for preventing "Function may be static" warning
        self.friend_window = None
        self.lock = threading.Lock()
        self.thread_flag = False

        # Connect to the server
        self.connect_to_server()

        # self.notification_thread = threading.Thread(target=self.handle_server_responses, daemon=True)

        # use RAWG.IO to receive game data
        self.metadata_retriever = GameMetadataRetriever('74206afbba5d4287927acbdd696485f3')

        # Configure the root window
        self.title("Orderly")
        self.geometry("1024x768")
        self.configure(bg="#f0f2f5")

        # Set style
        self.style = ttk.Style()
        self.style.configure('Modern.TFrame', background='#f0f2f5')
        self.style.configure('Nav.TFrame', background='#1a2238')
        self.style.configure('Content.TFrame', background='#ffffff')

        # Different buttons for the UI
        self.style.configure('ModernButton.TButton',
                             padding=10,
                             background='#2962ff',
                             foreground='black',
                             borderwidth=0,
                             relief='flat')

        self.style.map('ModernButton.TButton',
                       background=[('active', '#2962ff'), ('pressed', '#2962ff')],
                       relief=[('pressed', 'flat'), ('!pressed', 'flat')],
                       borderwidth=[('pressed', '0'), ('!pressed', '0')])

        self.style.configure('NavButton.TButton',
                             padding=10,
                             background='#1a2238',
                             foreground='black')

        # start game scanner
        self.game_scanner = GameScanner()
        self.games_list = []

        # Create main containers
        self.login_frame = ttk.Frame(self, style='Modern.TFrame')
        self.content_frame = ttk.Frame(self, style='Content.TFrame')
        self.nav_frame = None

        # Create the first login form
        self.create_login_form()

    def create_login_form(self):
        """Create the login form"""
        if self.signup_frame:  # Destroy signup frame if it exists, when function called from sign-out
            self.signup_frame.destroy()

        # create\recreate the login frame
        self.login_frame = ttk.Frame(self, style="Modern.TFrame")
        self.login_frame.pack(fill="both", expand=True)

        login_container = ttk.Frame(self.login_frame, style="Content.TFrame")
        login_container.place(relx=0.5, rely=0.5, anchor="center")

        # App title
        title_label = ttk.Label(login_container,
                                text="Orderly",
                                font=("Helvetica", 24, "bold"),
                                background="white")
        title_label.pack(pady=20)

        # Email field
        email_frame = ttk.Frame(login_container, style="Content.TFrame")
        email_frame.pack(fill="x", padx=20, pady=5)

        email_label = ttk.Label(email_frame,
                                text="Email",
                                font=("Helvetica", 10),
                                background="white")
        email_label.pack(anchor="w")

        self.email_entry = ttk.Entry(email_frame, width=30)
        self.email_entry.pack(fill="x", pady=5)

        # Password field
        password_frame = ttk.Frame(login_container, style="Content.TFrame")
        password_frame.pack(fill="x", padx=20, pady=5)

        password_label = ttk.Label(password_frame,
                                   text="Password",
                                   font=("Helvetica", 10),
                                   background="white")
        password_label.pack(anchor="w")

        self.password_entry = ttk.Entry(password_frame, show="\u2022", width=30)
        self.password_entry.pack(fill="x", pady=5)

        # Login button
        login_button = ttk.Button(login_container,
                                  text="Login",
                                  style="ModernButton.TButton",
                                  command=self.login)
        login_button.pack(pady=10)

        # Signup button
        signup_button = ttk.Button(login_container,
                                   text="Sign Up",
                                   style="ModernButton.TButton",
                                   command=self.create_signup_form)
        signup_button.pack()

    def submit_signup(self):
        while True:
            username = self.username_entry.get()
            email = self.email_entry.get()
            password = self.password_entry.get()

            if email and "@" and "." not in email:
                tk.messagebox.showwarning("Wrong format", "Email is of an invalid email format. Please try an email of "
                                                          "this format 'mail@example.com' ")
                self.email_entry.delete(0, tk.END)
            if password and not any(c.isupper() for c in password):
                tk.messagebox.showwarning("Invalid Password", "Password must contain one uppercase letter")
                self.password_entry.delete(0, tk.END)
            else:
                break

        if not self.socket:
            messagebox.showerror("Connection Error", "Not connected to the server.")
            return

        if username and email and password:
            request = {
                'type': 'signup',
                'username': username,
                'email': email,
                'password': password
            }
            self.socket.send(json.dumps(request).encode('utf-8'))
            response_data = self.socket.recv(1024).decode('utf-8')

            if not response_data:
                raise ValueError("Empty response from server")

            response = json.loads(response_data)

            if response['status'] == 'success':
                self.clear_content_frame()
                self.create_login_form()
            else:
                messagebox.showerror("Signup Failed", response.get('message', 'Signup failed.'))

        else:
            messagebox.showerror("Error", "Please fill in all fields.")

    def create_nav_frame(self):
        """Create the navigation sidebar"""
        if self.nav_frame:  # Destroy existing nav frame if present
            self.nav_frame.destroy()

        self.nav_frame = ttk.Frame(self, style='Nav.TFrame', width=200)
        self.nav_frame.pack(side="left", fill="y")

        # Navigation buttons
        nav_buttons = [
            ("🏠 Home", self.show_home),
            ("🎮 Library", self.show_library),
            ("👥 Friends", self.show_friends),
            ("👤 Profile", self.show_profile),
            ("ℹ️ About", self.show_about),
            ("➡️ Logout", self.logout)
        ]

        for text, command in nav_buttons:
            btn = ttk.Button(self.nav_frame,
                             text=text,
                             style='NavButton.TButton',
                             command=command)
            btn.pack(fill='x', padx=5, pady=5)

    def launch_game(self, path):
        """Launch game with error handling"""
        self.static = None
        try:
            print(path)
            os.startfile(path)
        except Exception as e:
            messagebox.showerror("Error",
                                 f"Failed to launch game: {str(e)}",
                                 icon='error')
            pass

    def fetch_covers(self):
        self.cover_fetch_index = 0
        self.process_next_cover()

    def process_next_cover(self):
        if self.cover_fetch_index < len(self.games_list):
            game = self.games_list[self.cover_fetch_index]
            try:
                # Construct the local file path
                local_path = os.path.join(r'C:\Users\User\PycharmProjects\Orderly\Icons',
                                          f"{game['name']}.jpg")

                image = None
                # First try to load local file
                if os.path.exists(local_path):
                    try:
                        image_data = open(local_path, 'rb')
                        image = Image.open(image_data)
                    except Exception as e:
                        print(f"Error loading local cover for {game['name']}: {e}")

                # If no local file, fetch from internet
                if not image:
                    cover_url = self.metadata_retriever.get_cover_url(game['name'])
                    if cover_url:
                        response = requests.get(cover_url)
                        # Save the cover locally
                        with open(local_path, 'wb') as f:
                            f.write(response.content)
                        image_data = BytesIO(response.content)
                        image = Image.open(image_data)

                if image:
                    image = image.resize((200, 200))
                    photo = ImageTk.PhotoImage(image)
                    # Update the corresponding label in the UI
                    for game_card in (self.content_frame.winfo_children()[1]
                                      .winfo_children()[0].winfo_children()[0].winfo_children()):
                        name_label = game_card.winfo_children()[0]  # Label for game name
                        if name_label.cget('text') == game['name']:
                            cover_label = game_card.winfo_children()[1]  # Label for the cover image
                            if isinstance(cover_label, tk.Label):  # Ensure it's a tk.Label
                                cover_label.configure(image=photo)
                                cover_label.image = photo  # Keep a reference
            except Exception as e:
                print(f"Error processing cover for {game['name']}: {e}")

            # Move to the next game
            self.cover_fetch_index += 1
            self.after(55, self.process_next_cover)  # Schedule the next cover processing

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        if email and password:
            request = {
                'type': 'login',
                'email': email,
                'password': password
            }
            try:
                self.socket.send(json.dumps(request).encode('utf-8'))
                response_data = self.socket.recv(1024).decode('utf-8')

                if not response_data:
                    raise ValueError("Empty response from server")

                response = json.loads(response_data)

                if response['status'] == 'success':
                    self.user = response['user']
                    if self.login_frame:
                        self.login_frame.destroy()  # Destroy the login frame
                        self.login_frame = None

                    self.create_nav_frame()  # Create and show the navigation frame
                    self.show_home()  # Show the home page
                else:
                    messagebox.showerror("Login Failed", response.get('message', 'Invalid login credentials.'))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send login request: {e}")
        else:
            messagebox.showerror("Error", "Please fill in all fields.")

    def show_friends(self):
        """Display the friends page with friend list and management options"""
        self.clear_content_frame()

        # Create main friends page container
        friends_frame = ttk.Frame(self, style='Content.TFrame')
        friends_frame.pack(fill="both", expand=True)

        # Header section
        header_frame = ttk.Frame(friends_frame, style='Content.TFrame')
        header_frame.pack(fill="x", padx=20, pady=10)

        title_label = ttk.Label(header_frame,
                                text="Friends",
                                font=('Helvetica', 20, 'bold'),
                                background='white')
        title_label.pack(side='left')

        # Add friend section
        add_friend_frame = ttk.Frame(friends_frame, style='Content.TFrame')
        add_friend_frame.pack(fill="x", padx=20, pady=10)

        add_friend_label = ttk.Label(add_friend_frame,
                                     text="Add Friend",
                                     font=('Helvetica', 14, 'bold'),
                                     background='white')
        add_friend_label.pack(anchor='w')

        friend_id_entry = ttk.Entry(add_friend_frame, width=30)
        friend_id_entry.pack(side='left', padx=(0, 10))

        def add_friend():
            friend_username = friend_id_entry.get()
            if friend_username:
                request = {
                    'type': 'friendlist',
                    'action': 'add',
                    'user_id': self.user['id'],
                    'friend_id': friend_username
                }
                try:
                    self.socket.send(json.dumps(request).encode('utf-8'))
                    response = json.loads(self.socket.recv(1024).decode('utf-8'))

                    if response['status'] == 'success':
                        messagebox.showinfo("Success", "Friend added successfully!")
                        refresh_friends_list()  # Refresh the list after adding
                    else:
                        messagebox.showerror("Error", response.get('message', 'Failed to add friend'))
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to add friend: {e}")

        add_button = ttk.Button(add_friend_frame,
                                text="Add Friend",
                                style='ModernButton.TButton',
                                command=add_friend)
        add_button.pack(side='left')

        # Friends list section
        friends_list_frame = ttk.Frame(friends_frame, style='Content.TFrame')
        friends_list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        friends_list_label = ttk.Label(friends_list_frame,
                                       text="Your Friends",
                                       font=('Helvetica', 14, 'bold'),
                                       background='white')
        friends_list_label.pack(anchor='w')

        # Create scrollable frame for friends list
        canvas = tk.Canvas(friends_list_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(friends_list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Content.TFrame')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_reqwidth())
        canvas.configure(yscrollcommand=scrollbar.set)

        def refresh_friends_list():
            # Clear existing friends
            for widget in scrollable_frame.winfo_children():
                widget.destroy()

            # Request friends list from server
            request = {
                'type': 'friendlist',
                'action': 'get',
                'user_id': self.user['id']
            }
            try:
                self.socket.send(json.dumps(request).encode('utf-8'))
                self.lock.acquire()
                response = self.socket.recv(1024).decode('utf-8')
                self.lock.release()
                response = json.loads(response)

                if response['status'] == 'success':
                    friends = response.get('friends', [])

                    if not friends:
                        no_friends_label = ttk.Label(scrollable_frame,
                                                     text="No friends added yet.",
                                                     font=('Helvetica', 12),
                                                     background='white')
                        no_friends_label.pack(pady=20)
                    else:
                        for friend in friends:
                            friend_frame = ttk.Frame(scrollable_frame, style='Content.TFrame')
                            friend_frame.pack(fill='x', pady=5)

                            friend_name = ttk.Label(friend_frame,
                                                    text=friend['username'],
                                                    font=('Helvetica', 12),
                                                    background='white')
                            friend_name.pack(side='left', padx=5)

                            def remove_friend(friend_id=friend['id']):
                                f_request = {
                                    'type': 'friendlist',
                                    'action': 'remove',
                                    'user_id': self.user['id'],
                                    'friend_id': friend_id
                                }
                                try:
                                    self.socket.send(json.dumps(f_request).encode('utf-8'))
                                    f_response = json.loads(self.socket.recv(1024).decode('utf-8'))

                                    if f_response['status'] == 'success':
                                        messagebox.showinfo("Success", "Friend removed successfully!")
                                        refresh_friends_list()  # Refresh the list after removing
                                    else:
                                        messagebox.showerror("Error",
                                                             f_response.get('message', 'Failed to remove friend'))
                                except (socket.error, json.JSONDecodeError, KeyError) as error:
                                    messagebox.showerror("Error", f"Failed to remove friend: {error}")

                            remove_btn = ttk.Button(friend_frame,
                                                    text="Remove",
                                                    style='ModernButton.TButton',
                                                    command=lambda f=friend['id']: remove_friend(f))
                            remove_btn.pack(side='right')

                            friend_prof_btn = ttk.Button(friend_frame,
                                                         text="Profile",
                                                         style='ModernButton.TButton',
                                                         command=lambda f=friend['id']: self.show_profile(f))
                            friend_prof_btn.pack(side='right', padx=5)

            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch friends list: {e}")

        # Initial friends list load
        refresh_friends_list()

        # Configure canvas resize behavior
        def configure_canvas(event):
            canvas.itemconfig(canvas.find_all()[0], width=event.width)

        canvas.bind('<Configure>', configure_canvas)

        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Refresh button
        refresh_button = ttk.Button(header_frame,
                                    text="🔄 Refresh",
                                    style='ModernButton.TButton',
                                    command=refresh_friends_list)
        refresh_button.pack(side='right')

    def show_library(self):
        """Display the game library"""
        self.games_list = self.game_scanner.scan()
        self.clear_content_frame()  # Clear existing content

        # create the content frame for the library view
        self.content_frame = ttk.Frame(self, style='Content.TFrame')
        self.content_frame.pack(fill="both", expand=True)

        # Header with title and scan button
        header_frame = ttk.Frame(self.content_frame, style='Content.TFrame')
        header_frame.pack(fill="x", padx=20, pady=10)

        title_label = ttk.Label(header_frame,
                                text="Game Library",
                                font=('Helvetica', 20, 'bold'),
                                background='white')
        title_label.pack(side='left')

        scan_button = tk.Button(header_frame,
                                text="🔄 Rescan Games",
                                command=self.rescan_games,
                                bg='white',
                                fg='black',
                                bd=0,
                                relief='flat',
                                padx=10,
                                pady=5)
        scan_button.pack(side='right')

        # Create the game library content here (grid view)
        game_container = ttk.Frame(self.content_frame, style='Content.TFrame')
        game_container.pack(fill='both', expand=True, padx=20, pady=10)

        # Configure scrolling frame
        canvas = tk.Canvas(game_container, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(game_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Content.TFrame')

        # Bind the scrollable frame to the canvas scroll region
        def configure_scroll_region(_):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scrollable_frame.bind("<Configure>", configure_scroll_region)

        def on_mouse_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", on_mouse_wheel)

        # Create a window inside the canvas
        canvas_frame = canvas.create_window((0, 0),
                                            window=scrollable_frame,
                                            anchor="nw",
                                            width=canvas.winfo_reqwidth())

        # Configure canvas to expand with window
        def configure_canvas(_):
            canvas.itemconfig(canvas_frame, width=canvas.winfo_width())

        canvas.bind('<Configure>', configure_canvas)

        # Grid configuration
        COLUMNS = 3
        row = 0
        col = 0

        if not self.games_list:
            no_games_label = ttk.Label(scrollable_frame,
                                       text="No games found. Click 'Rescan Games' to search for games.",
                                       font=('Helvetica', 12),
                                       background='white')
            no_games_label.grid(row=0, column=0, pady=20, padx=20)
        else:
            # Prepare a placeholder image
            placeholder_image = Image.new('RGB', (200, 200), color='lightgray')
            placeholder_photo = ImageTk.PhotoImage(placeholder_image)

            for game in self.games_list:
                game_card = ttk.Frame(scrollable_frame, style='Content.TFrame')
                game_card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

                name_label = ttk.Label(game_card,
                                       text=game['name'],
                                       font=('Helvetica', 12, 'bold'),
                                       background='white',
                                       wraplength=180)
                name_label.pack(pady=(10, 5))

                # Use the placeholder image initially
                cover_label = tk.Label(game_card, image=placeholder_photo)
                cover_label.image = placeholder_photo  # Keep a reference
                cover_label.pack(pady=5)

                # Create a frame to hold the buttons and center them
                button_container = ttk.Frame(game_card, style='Content.TFrame')
                button_container.pack(pady=5)  # Add some padding below the buttons

                # Create a frame for the buttons (this will be centered inside button_container)
                button_frame = ttk.Frame(button_container, style='Content.TFrame')
                button_frame.pack()  # This will center the button_frame inside button_container

                # Create launch button
                launch_button = tk.Button(button_frame,
                                          text="▶️ Launch",
                                          command=lambda g=game: self.launch_game(g['path']),
                                          bg='lightgray',
                                          fg='black',
                                          bd=0,
                                          relief='flat',
                                          padx=10,
                                          pady=5)
                launch_button.pack(side='left', padx=5)  # Place on the left side

                # Create info button
                info_button = tk.Button(button_frame,
                                        text="ⓘ",
                                        command=lambda g=game: self.show_game_info(g),
                                        bg='lightgray',
                                        fg='black',
                                        bd=0,
                                        relief='flat',
                                        padx=10,
                                        pady=5)
                info_button.pack(side='left', padx=5)  # Place next to the launch button

                col += 1
                if col >= COLUMNS:
                    col = 0
                    row += 1

            # Configure grid weights
            for i in range(COLUMNS):
                scrollable_frame.grid_columnconfigure(i, weight=1)

        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Configure the canvas scroll command
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack the main frames
        self.content_frame.pack(side="right", fill="both", expand=True)
        self.nav_frame.pack(side="left", fill="y")

        # Call fetch_covers to start loading images
        self.fetch_covers()

    def rescan_games(self):
        """Rescan games"""
        self.games_list = self.game_scanner.scan()
        self.show_library()

    def show_profile(self, user_id=None):
        """Display user profile with detailed information"""
        self.clear_content_frame()

        # If no user_id is provided, show the current user's profile
        if user_id is None:
            user_id = self.user['id']

        # Request user information from server
        request = {
            'type': 'user_info',
            'user_id': user_id
        }
        try:
            self.socket.send(json.dumps(request).encode('utf-8'))
            response = json.loads(self.socket.recv(1024).decode('utf-8'))

            if response['status'] == 'success':
                user_data = response['user']
                # Store the current user temporarily
                current_user = self.user
                # Set the viewed user's data
                self.user = user_data
                # Show the profile
                self._display_profile()
                # Restore the current user's data
                self.user = current_user
            else:
                messagebox.showerror("Error", "Failed to fetch user profile")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch user profile: {e}")

    def show_home(self):
        """Display the home page"""
        self.clear_content_frame()
        # self.notification_thread.start()
        # Create and pack the home content frame
        home_frame = ttk.Frame(self, style='Content.TFrame')
        home_frame.pack(fill="both", expand=True)

        welcome_label = ttk.Label(home_frame,
                                  text="Welcome to Orderly",
                                  font=("Helvetica", 24, "bold"),
                                  background="white")
        welcome_label.pack(pady=20)

        subtitle_label = ttk.Label(home_frame,
                                   text="Your Modern Game Library Manager \r\n",
                                   font=("Helvetica", 14),
                                   background="white")
        subtitle_label.pack()

        subtext_label = ttk.Label(home_frame,
                                  text="Made By: Shlomo Toussia-Cohen \r\n"
                                       "Under Guidance from: Eti Hershkovitz \r\n"
                                       "Special Thanks To: Noam Sela, Eitan Solonik",
                                  font=("Helvetica", 12),
                                  background="lightgray")
        subtext_label.pack()

    def show_user_profile(self, user_id):
        """Display profile for a specific user"""
        # Request user information from server
        request = {
            'type': 'profile',
            'user_id': user_id
        }
        try:
            self.socket.send(json.dumps(request).encode('utf-8'))
            response = json.loads(self.socket.recv(1024).decode('utf-8'))

            if response['status'] == 'success':
                user_data = response['user']
                # Store the current user temporarily
                current_user = self.user
                # Set the viewed user's data
                self.user = user_data
                # Show the profile
                self._display_profile()
                # Restore the current user's data
                self.user = current_user
            else:
                messagebox.showerror("Error", "Failed to fetch user profile")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch user profile: {e}")

    def _display_profile(self):
        """Helper method to display the profile of the current user"""
        # Create main profile container
        profile_frame = ttk.Frame(self, style='Content.TFrame')
        profile_frame.pack(fill="both", expand=True)

        # Header section
        header_frame = ttk.Frame(profile_frame, style='Content.TFrame')
        header_frame.pack(fill="x", padx=20, pady=10)

        title_label = ttk.Label(header_frame,
                                text="Profile",
                                font=('Helvetica', 20, 'bold'),
                                background='white')
        title_label.pack(side='left')

        # Profile content
        content_frame = ttk.Frame(profile_frame, style='Content.TFrame')
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Profile picture placeholder
        profile_pic_frame = ttk.Frame(content_frame, style='Content.TFrame')
        profile_pic_frame.pack(pady=20)

        # Create a circular placeholder for profile picture
        canvas = tk.Canvas(profile_pic_frame, width=100, height=100, bg='white', highlightthickness=0)
        canvas.pack()

        # Draw a circle with user's first letter
        canvas.create_oval(2, 2, 98, 98, fill='white', width=2)
        canvas.create_text(50, 50,
                           text=self.user['username'][0].upper(),
                           fill='black',
                           font=('Helvetica', 36, 'bold'))

        # User information section
        info_frame = ttk.Frame(content_frame, style='Content.TFrame')
        info_frame.pack(fill="x", pady=20)

        # Username
        username_frame = ttk.Frame(info_frame, style='Content.TFrame')
        username_frame.pack(fill="x", pady=10)

        username_label = ttk.Label(username_frame,
                                   text="Username:",
                                   font=('Helvetica', 12, 'bold'),
                                   background='white')
        username_label.pack(side='left', padx=5)

        username_value = ttk.Label(username_frame,
                                   text=self.user['username'],
                                   font=('Helvetica', 12),
                                   background='white')
        username_value.pack(side='left', padx=5)

        # User ID (with copy button)
        id_frame = ttk.Frame(info_frame, style='Content.TFrame')
        id_frame.pack(fill="x", pady=10)

        id_label = ttk.Label(id_frame,
                             text="User ID:",
                             font=('Helvetica', 12, 'bold'),
                             background='white')
        id_label.pack(side='left', padx=5)

        id_value = ttk.Label(id_frame,
                             text=self.user['id'],
                             font=('Helvetica', 12),
                             background='white')
        id_value.pack(side='left', padx=5)

        def copy_id():
            self.clipboard_clear()
            self.clipboard_append(self.user['id'])
            messagebox.showinfo("Success", "User ID copied to clipboard!")

        copy_button = ttk.Button(id_frame,
                                 text="Copy ID",
                                 style='ModernButton.TButton',
                                 command=copy_id)
        copy_button.pack(side='left', padx=5)

        # Friends count section
        friends_frame = ttk.Frame(info_frame, style='Content.TFrame')
        friends_frame.pack(fill="x", pady=10)

        friends_label = ttk.Label(friends_frame,
                                  text="Friends:",
                                  font=('Helvetica', 12, 'bold'),
                                  background='white')
        friends_label.pack(side='left', padx=5)

        def get_friends_count():
            request = {
                'type': 'friendlist',
                'action': 'count',
                'user_id': self.user['id']
            }
            try:
                self.socket.send(json.dumps(request).encode('utf-8'))
                response = json.loads(self.socket.recv(1024).decode('utf-8'))
                return response.get('message', '0') if response['status'] == 'success' else '0'
            except (socket.error, json.JSONDecodeError, KeyError) as e:
                print(f"Error: {e}")
                return '0'

        friends_count = ttk.Label(friends_frame,
                                  text=get_friends_count(),
                                  font=('Helvetica', 12),
                                  background='white')
        friends_count.pack(side='left', padx=5)

        view_friends_button = ttk.Button(friends_frame,
                                         text="View Friends",
                                         style='ModernButton.TButton',
                                         command=self.show_friends)
        view_friends_button.pack(side='left', padx=5)

    def show_about(self):
        self.static = None
        os.startfile(r'C:\\Users\\User\PycharmProjects\Orderly\README.txt')

    def logout(self):
        """Handle logout"""
        self.user = None
        self.nav_frame.pack_forget()
        self.content_frame.pack_forget()
        self.clear_content_frame()
        self.create_login_form()

    def clear_content_frame(self):
        """Clear all content widgets except the navigation frame"""
        for widget in self.winfo_children():
            if widget != self.nav_frame:  # Keep the navigation frame to avoid too much processing
                widget.destroy()

    def connect_to_server(self):
        """Establish a connection to the server"""
        try:
            # create SSL context
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            self.socket = context.wrap_socket(raw_socket,
                                              server_hostname=self.host)

            self.socket.connect((self.host, self.port))
            print("[+] SSL connection established")

        except Exception as e:
            messagebox.showerror("Connection Error",
                                 f"Failed to connect to server: {e}")
            self.socket = None

    def create_signup_form(self):
        """Create the signup form"""
        if self.login_frame:  # Destroy login frame if it exists
            self.login_frame.destroy()

        # Recreate the signup frame
        self.signup_frame = ttk.Frame(self, style="Modern.TFrame")
        self.signup_frame.pack(fill="both", expand=True)

        signup_container = ttk.Frame(self.signup_frame, style="Content.TFrame")
        signup_container.place(relx=0.5, rely=0.5, anchor="center")

        # App title
        title_label = ttk.Label(signup_container,
                                text="Create your Orderly account",
                                font=("Helvetica", 18, "bold"),
                                background="white")
        title_label.pack(pady=20)

        # Username field
        username_label = ttk.Label(signup_container, text="Username", background="white")
        username_label.pack(anchor="w", padx=20, pady=5)
        self.username_entry = ttk.Entry(signup_container, width=30)
        self.username_entry.pack(padx=20, pady=5)

        # Email field
        email_label = ttk.Label(signup_container, text="Email", background="white")
        email_label.pack(anchor="w", padx=20, pady=5)
        self.email_entry = ttk.Entry(signup_container, width=30)
        self.email_entry.pack(padx=20, pady=5)

        # Password field
        password_label = ttk.Label(signup_container, text="Password", background="white")
        password_label.pack(anchor="w", padx=20, pady=5)
        self.password_entry = ttk.Entry(signup_container, show="\u2022", width=30)
        self.password_entry.pack(padx=20, pady=5)

        # Submit button
        submit_button = ttk.Button(signup_container,
                                   text="Submit",
                                   style="ModernButton.TButton",
                                   command=self.submit_signup)
        submit_button.pack(pady=10)

        # Back to Log in button
        back_button = ttk.Button(signup_container,
                                 text="Back to Login",
                                 style="ModernButton.TButton",
                                 command=self.create_login_form)
        back_button.pack()

    def show_game_info(self, game):
        """Displays the game info after button press"""
        self.clear_content_frame()

        # Create main container frame
        info_frame = ttk.Frame(self, style='Content.TFrame')
        info_frame.pack(fill="both", expand=True)

        # Create left side container for title and description
        left_content = ttk.Frame(info_frame, style='Content.TFrame')
        left_content.pack(side='left', fill='both', expand=True, padx=20, pady=20)

        # Create right side container for image
        right_content = ttk.Frame(info_frame, style='Content.TFrame')
        right_content.pack(side='right', padx=20, pady=20)

        # Game title in left container
        game_label = ttk.Label(left_content,
                               text=game['name'],
                               font=("Helvetica", 24, "bold"),
                               background="white")
        game_label.pack(anchor='w')

        # Description right below title in left container
        description_label = ttk.Label(left_content,
                                      text=self.metadata_retriever.get_description(game['name']),
                                      font=("Helvetica", 10),
                                      background="white",
                                      wraplength=600,
                                      justify="left")
        description_label.pack(anchor='w', pady=(10, 0))

        release_date_label = ttk.Label(right_content,
                                       text=f"Released on: {self.metadata_retriever.get_release_date(game['name'])}",
                                       font=("Helvetica", 10),
                                       background="white",
                                       justify="center")
        release_date_label.pack(anchor="e", pady=10)

        platforms_label = ttk.Label(left_content,
                                    text=f"Available On: {self.metadata_retriever.get_platforms(game['name'])}",
                                    font=("Helvetica", 10),
                                    background="white",
                                    justify="center")
        platforms_label.pack(anchor="e", pady=10)

        # Cover image in right container
        try:
            # Construct the local file path
            local_path = os.path.join(r'C:\Users\User\PycharmProjects\Orderly\Icons',
                                      f"{game['name']}.jpg")

            # Create a placeholder image initially
            placeholder_image = Image.new('RGB', (200, 200), color='lightgray')
            placeholder_photo = ImageTk.PhotoImage(placeholder_image)

            # Create the cover label with placeholder
            cover_label = tk.Label(right_content, image=placeholder_photo)
            cover_label.image = placeholder_photo
            cover_label.pack()

            image = None
            # First try to load local file
            if os.path.exists(local_path):
                try:
                    image_data = open(local_path, 'rb')
                    image = Image.open(image_data)
                except Exception as e:
                    print(f"Error loading local cover for {game['name']}: {e}")

            # If no local file, fetch from internet
            if not image:
                cover_url = self.metadata_retriever.get_cover_url(game['name'])
                if cover_url:
                    response = requests.get(cover_url)
                    # Save the cover locally
                    with open(local_path, 'wb') as f:
                        f.write(response.content)
                    image_data = BytesIO(response.content)
                    image = Image.open(image_data)

            if image:
                image = image.resize((200, 200))
                photo = ImageTk.PhotoImage(image)
                cover_label.configure(image=photo)
                cover_label.image = photo

        except Exception as e:
            print(f"Error loading cover image for {game['name']}: {e}")


if __name__ == "__main__":
    OrderlyApp().mainloop()
