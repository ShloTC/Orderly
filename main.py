import tkinter as tk
from tkinter import messagebox, ttk
from game_scanner import GameScanner
import os


class OrderlyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Orderly")
        self.geometry("800x600")

        # Initialize game scanner with debug print
        print("Initializing GameScanner...")
        self.game_scanner = GameScanner()

        # Test scan immediately
        test_games = self.game_scanner.scan()
        print(f"Initial test scan found {len(test_games)} games:")
        for game in test_games:
            print(f"- {game['name']}: {game['path']}")

        self.games_list = []  # This will be populated on login

        # Rest of your init code...

        # Frame for login content (initially visible)
        self.login_frame = tk.Frame(self, bg="white")
        self.login_frame.pack(side="right", fill="both", expand=True)

        # Create the main content area (empty at first)
        self.content_frame = tk.Frame(self, bg="white")

        # Sidebar is initially not created, will be created after login
        self.nav_frame = None

        self.create_login_form()

    def create_nav_frame(self):
        """ Create the sidebar (nav) frame. """
        self.nav_frame = tk.Frame(self, bg="lightgray", width=200)
        self.home_button = tk.Button(self.nav_frame, text="Home", command=self.show_home)
        self.home_button.pack(fill="x", pady=5)

        self.library_button = tk.Button(self.nav_frame, text="Game Library", command=self.show_library)
        self.library_button.pack(fill="x", pady=5)

        self.stats_button = tk.Button(self.nav_frame, text="Statistics", command=self.show_statistics)
        self.stats_button.pack(fill="x", pady=5)

        self.friends_button = tk.Button(self.nav_frame, text="Friends", command=self.show_friends)
        self.friends_button.pack(fill="x", pady=5)

        self.leaderboard_button = tk.Button(self.nav_frame, text="Leaderboards", command=self.show_leaderboards)
        self.leaderboard_button.pack(fill="x", pady=5)

        self.settings_button = tk.Button(self.nav_frame, text="Settings", command=self.show_settings)
        self.settings_button.pack(fill="x", pady=5)

        self.help_button = tk.Button(self.nav_frame, text="Help", command=self.show_help)
        self.help_button.pack(fill="x", pady=5)

        self.about_button = tk.Button(self.nav_frame, text="About", command=self.show_about)
        self.about_button.pack(fill="x", pady=5)

        self.logout_button = tk.Button(self.nav_frame, text="Logout", command=self.logout)
        self.logout_button.pack(fill="x", pady=5)

    def create_login_form(self):
        """ Create the login form. """
        email_label = tk.Label(self.login_frame, text="Email:")
        email_label.pack(pady=(20, 5))
        self.email_entry = tk.Entry(self.login_frame)
        self.email_entry.pack(pady=5)

        password_label = tk.Label(self.login_frame, text="Password:")
        password_label.pack(pady=(20, 5))
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.pack(pady=5)

        login_button = tk.Button(self.login_frame, text="Login", command=self.login)
        login_button.pack(pady=20)

    def login(self):
        """ Handle login logic. """
        email = self.email_entry.get()
        password = self.password_entry.get()

        if email == "admin@example.com" and password == "password":
            print("Login successful, scanning for games...")
            self.games_list = self.game_scanner.scan()  # Scan for games
            print(f"Login scan found {len(self.games_list)} games:")
            for game in self.games_list:
                print(f"- {game['name']}: {game['path']}")

            self.login_frame.pack_forget()
            self.create_nav_frame()
            self.show_home()
        else:
            messagebox.showerror("Login Failed", "Invalid email or password.")
    def show_library(self):
        """ Show the game library page with games in a grid. """
        self.clear_content_frame()

        print(f"Displaying {len(self.games_list)} games")  # Debug print

        # Main container
        main_container = tk.Frame(self.content_frame, bg="white")
        main_container.pack(fill="both", expand=True)

        # Create a frame for the title and scan button
        title_frame = tk.Frame(main_container, bg="white")
        title_frame.pack(fill="x", pady=10)

        # Title
        title_label = tk.Label(title_frame, text="Game Library", font=("Arial", 16), bg="white")
        title_label.pack(side="left", padx=10)

        # Scan button
        scan_button = tk.Button(title_frame, text="Rescan Games", command=self.rescan_games)
        scan_button.pack(side="right", padx=10)

        # Create a frame to hold the canvas and scrollbar
        game_container = tk.Frame(main_container, bg="white")
        game_container.pack(fill="both", expand=True, padx=10, pady=5)

        # Create canvas and scrollbar
        canvas = tk.Canvas(game_container, bg="white")
        scrollbar = ttk.Scrollbar(game_container, orient="vertical", command=canvas.yview)

        # Create the frame that will contain the games grid
        games_frame = tk.Frame(canvas, bg="white")

        # Configure the canvas
        canvas.configure(yscrollcommand=scrollbar.set)

        # Grid configuration
        COLUMNS = 3
        row = 0
        col = 0

        if not self.games_list:  # If no games found
            no_games_label = tk.Label(
                games_frame,
                text="No games found. Click 'Rescan Games' to search for games.",
                font=("Arial", 12),
                bg="white"
            )
            no_games_label.grid(row=0, column=0, pady=20, padx=20)
        else:
            # Create game tiles
            for game in self.games_list:
                # Create frame for each game
                game_frame = tk.Frame(
                    games_frame,
                    relief="solid",
                    borderwidth=1,
                    width=200,
                    height=100,
                    bg="white"
                )
                game_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                game_frame.grid_propagate(False)

                # Game name
                name_label = tk.Label(
                    game_frame,
                    text=game['name'],
                    wraplength=180,
                    font=("Arial", 10, "bold"),
                    bg="white"
                )
                name_label.pack(pady=(10, 5))

                # Launch button
                launch_button = tk.Button(
                    game_frame,
                    text="Launch",
                    command=lambda g=game: self.launch_game(g['path'])
                )
                launch_button.pack(pady=5)

                # Update grid position
                col += 1
                if col >= COLUMNS:
                    col = 0
                    row += 1

        # Configure grid weights for proper spacing
        games_frame.grid_columnconfigure(tuple(range(COLUMNS)), weight=1)

        # Create the window in the canvas
        canvas.create_window((0, 0), window=games_frame, anchor="nw")

        # Update the scroll region
        games_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Pack the main frames
        self.content_frame.pack(side="right", fill="both", expand=True)
        self.nav_frame.pack(side="left", fill="y")
    def launch_game(self, path):
        """Launch the game using its executable path"""
        try:
            os.startfile(path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch game: {str(e)}")

    def rescan_games(self):
        """Rescan for games and refresh the library view"""
        print("Rescanning for games...")
        self.games_list = self.game_scanner.scan()
        print(f"Rescan found {len(self.games_list)} games:")
        for game in self.games_list:
            print(f"- {game['name']}: {game['path']}")
        self.show_library()

    def show_home(self):
        self.clear_content_frame()
        self.title_label = tk.Label(self.content_frame, text="Home Page", font=("Arial", 16))
        self.title_label.pack(pady=10)
        self.content_frame.pack(side="right", fill="both", expand=True)
        self.nav_frame.pack(side="left", fill="y")

    def show_statistics(self):
        self.clear_content_frame()
        self.title_label = tk.Label(self.content_frame, text="Statistics", font=("Arial", 16))
        self.title_label.pack(pady=10)
        self.content_frame.pack(side="right", fill="both", expand=True)

    def show_friends(self):
        self.clear_content_frame()
        self.title_label = tk.Label(self.content_frame, text="Friends list", font=("Arial", 16))
        self.title_label.pack(pady=10)
        self.content_frame.pack(side="right", fill="both", expand=True)

    def show_leaderboards(self):
        self.clear_content_frame()
        self.title_label = tk.Label(self.content_frame, text="Leaderboards", font=("Arial", 16))
        self.title_label.pack(pady=10)
        self.content_frame.pack(side="right", fill="both", expand=True)

    def show_settings(self):
        self.clear_content_frame()
        self.title_label = tk.Label(self.content_frame, text="Settings", font=("Arial", 16))
        self.title_label.pack(pady=10)
        self.content_frame.pack(side="right", fill="both", expand=True)

    def show_help(self):
        self.clear_content_frame()
        self.title_label = tk.Label(self.content_frame, text="Help", font=("Arial", 16))
        self.title_label.pack(pady=10)
        self.content_frame.pack(side="right", fill="both", expand=True)

    def show_about(self):
        self.clear_content_frame()
        self.title_label = tk.Label(self.content_frame, text="About", font=("Arial", 16))
        self.title_label.pack(pady=10)
        self.content_frame.pack(side="right", fill="both", expand=True)

    def logout(self):
        """ Log out and return to login screen. """
        self.clear_content_frame()
        self.login_frame.pack(side="right", fill="both", expand=True)
        self.nav_frame.pack_forget()
        self.content_frame.pack_forget()

    def clear_content_frame(self):
        """ Clear the current content frame before showing new page. """
        for widget in self.content_frame.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    app = OrderlyApp()
    app.mainloop()