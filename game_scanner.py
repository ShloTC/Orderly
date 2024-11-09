import os


class GameScanner:
    def __init__(self, custom_directories=None):
        # Default directories to scan
        self.directories_to_scan = custom_directories or [
            r"C:\Program Files",
            r"C:\Program Files (x86)"
        ]

        # Common game installation folders
        self.GAME_FOLDERS = [
            "steamapps\\common",
            "Epic Games",
            "GOG",
            "Ubisoft",
            "Origin",
            "Games"
        ]

        # Folders to exclude
        self.EXCLUDE_FOLDERS = [
            "bin", "redist", "redistrib", "installer", "cleaner",
            "compiler", "_commonredist", "thirdparty", "distribution",
            "projects"
        ]

        # Files to exclude
        self.EXCLUDE_FILES = [
            "easyanticheat", "uninstall", "installscript", "crashhandler",
            "setup", "redist", "installer", "cleaner", "modcompiler",
            "dotnet", "vcredist", "dxsetup", "applicationwallpaper"
        ]

        # Store found games
        self.games = []

    def add_search_directory(self, directory):
        """Add a new directory to scan"""
        if directory not in self.directories_to_scan:
            self.directories_to_scan.append(directory)

    def add_game_folder(self, folder_name):
        """Add a new game folder pattern to search for"""
        if folder_name not in self.GAME_FOLDERS:
            self.GAME_FOLDERS.append(folder_name)

    def _find_main_launcher(self, game_path):
        """Find the main executable in a game directory"""
        try:
            # Get all .exe files in the root directory
            exe_files = [
                f for f in os.listdir(game_path)
                if (os.path.isfile(os.path.join(game_path, f)) and
                    f.endswith(".exe") and
                    not any(excl.lower() in f.lower() for excl in self.EXCLUDE_FILES) and
                    not any(excl.lower() in game_path.lower() for excl in self.EXCLUDE_FOLDERS))
            ]

            if exe_files:
                return exe_files[0]  # Return the first valid exe file

        except PermissionError:
            print(f"Permission denied: {game_path}")
        except Exception as e:
            print(f"Error reading {game_path}: {e}")

        return None

    def _scan_directory(self, directory):
        """Scan a single directory for games"""
        games_in_directory = []

        for root, dirs, _ in os.walk(directory):
            # Check if we're in a likely game folder
            if not any(folder in root for folder in self.GAME_FOLDERS):
                continue

            # Skip if we're in a subfolder of a game directory
            parent_dir = os.path.dirname(root)
            if any(folder in parent_dir for folder in self.GAME_FOLDERS):
                continue

            # Process each folder within the game directories
            for dir_name in dirs:
                # Skip known utility folders
                if any(excl.lower() in dir_name.lower() for excl in self.EXCLUDE_FOLDERS):
                    continue

                game_path = os.path.join(root, dir_name)
                main_exe = self._find_main_launcher(game_path)

                if main_exe:
                    launcher_path = os.path.join(game_path, main_exe)
                    games_in_directory.append({
                        "name": dir_name,
                        "path": launcher_path
                    })

        return games_in_directory

    def scan(self):
        """Perform the game scan on all directories"""
        self.games = []  # Reset games list

        for directory in self.directories_to_scan:
            if os.path.exists(directory):
                detected_games = self._scan_directory(directory)
                self.games.extend(detected_games)

        return self.games

    def get_games(self):
        """Return the list of found games"""
        return self.games

    def print_games(self):
        """Print a summary of found games"""
        if self.games:
            print("\nSummary of games found:")
            for game in self.games:
                print(f"Game: {game['name']}, Path: {game['path']}")
        else:
            print("No games found in the specified directories.")


# Example usage:
if __name__ == "__main__":
    # Create scanner instance
    scanner = GameScanner()

    # Optionally add additional search directories
    # scanner.add_search_directory(r"D:\Games")

    # Perform scan
    scanner.scan()

    # Print results
    scanner.print_games()