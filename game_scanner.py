import os
import string
from ctypes import windll
import time


class GameScanner:
    def __init__(self, custom_directories=None):
        # Get all available drives
        self.available_drives = self._get_available_drives()

        # Default directories to scan
        base_directories = [
            r"C:\Program Files",
            r"C:\Program Files (x86)",
        ]

        # Add root of non-system drives to scan
        for drive in self.available_drives:
            if not drive.startswith("C:"):
                base_directories.append(drive)

        self.directories_to_scan = custom_directories or base_directories

        # Common paths where game libraries might be installed
        self.LIBRARY_PATHS = [
            r"Steam\steamapps\common",
            r"SteamLibrary\steamapps\common",
            "Epic Games",
            r"GOG Galaxy\Games",
            r"Ubisoft\Ubisoft Game Launcher\games",
            "Origin Games",
            "Games"
        ]

        # Common game-related file patterns
        self.GAME_FILE_PATTERNS = [
            "game.ini", "gameconfig.xml", "steam_api", "steam_api64",
            "unity", "unreal", "cryengine", "fmod", "havok",
            "dx11", "vulkan", "opengl", "game_data", "levels",
            "save", "checkpoint", ".pak", ".gpk", ".dat"
        ]

        # Folders to exclude
        self.EXCLUDE_FOLDERS = [
            "windows", "$recycle.bin", "system volume information",
            "appdata", "temp", "tmp", "cache", "crash reports",
            "common files", "windowsapps", "drivers"
        ]

        # Files to exclude
        self.EXCLUDE_FILES = [
            "uninstall", "setup", "installer", "update", "patch",
            "crash", "debug", "error", "log", "report", "epic"
        ]

        # Store found games
        self.games = []

    def _get_available_drives(self):
        """Get all available drives on the system"""
        drives = []
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drive_path = f"{letter}:\\"
                if os.path.exists(drive_path):
                    drives.append(drive_path)
            bitmask >>= 1
        return drives

    def _is_likely_game_directory(self, path):
        """Check if a directory is likely to be a game directory"""
        try:
            if not os.path.isdir(path):
                return False

            dir_name = os.path.basename(path).lower()

            # Skip excluded folders
            if any(excl.lower() in dir_name for excl in self.EXCLUDE_FOLDERS):
                return False

            contents = os.listdir(path)

            # Look for executable with matching name to directory
            has_matching_exe = any(
                file.lower().startswith(dir_name.lower()) and file.endswith('.exe')
                for file in contents
            )

            # Look for common game folders
            has_game_folders = any(
                folder.lower() in ['data', 'content', 'assets', 'bin', 'media']
                for folder in contents
                if os.path.isdir(os.path.join(path, folder))
            )

            return has_matching_exe or has_game_folders

        except (PermissionError, OSError):
            return False

    def _find_main_launcher(self, game_path):
        """Find the main executable in a game directory"""
        try:
            dir_name = os.path.basename(game_path).lower()
            exe_files = []

            # Check both root and bin directory for executables
            directories_to_check = [game_path]
            bin_path = os.path.join(game_path, 'bin')
            if os.path.isdir(bin_path):
                directories_to_check.append(bin_path)

            for check_dir in directories_to_check:
                for file in os.listdir(check_dir):
                    if not file.endswith('.exe'):
                        continue

                    if any(excl.lower() in file.lower() for excl in self.EXCLUDE_FILES):
                        continue

                    file_path = os.path.join(check_dir, file)
                    if not os.path.isfile(file_path):
                        continue

                    # Assign priority based on filename matching
                    priority = 0
                    if file.lower().startswith(dir_name):
                        priority = 3  # Highest priority for exact name match
                    elif dir_name in file.lower():
                        priority = 2  # Medium priority for partial name match
                    elif 'game' in file.lower():
                        priority = 1  # Low priority for generic game executables

                    exe_files.append((file, file_path, priority))

            if exe_files:
                # Sort by priority first, then by file size
                sorted_exes = sorted(
                    exe_files,
                    key=lambda x: (x[2], os.path.getsize(x[1])),
                    reverse=True
                )
                return sorted_exes[0][0], sorted_exes[0][1]

        except PermissionError:
            print(f"Permission denied: {game_path}")
        except Exception as e:
            print(f"Error reading {game_path}: {e}")

        return None, None

    def _scan_directory(self, directory):
        """Scan a single directory for games"""
        games_in_directory = []
        print(f"Scanning directory: {directory}")

        try:
            # Skip if directory doesn't exist
            if not os.path.exists(directory):
                return games_in_directory

            # Scan for games in library paths
            for lib_path in self.LIBRARY_PATHS:
                # For drive roots (D:\, E:\, etc.), also check root-level library paths
                if directory.endswith(':\\'):
                    # Check direct subfolders for library paths (e.g., D:\Steam\steamapps\common)
                    for item in os.listdir(directory):
                        item_path = os.path.join(directory, item)
                        if not os.path.isdir(item_path):
                            continue

                        # Check if this folder contains the library path
                        potential_lib_path = os.path.join(item_path,
                                                          lib_path.split('\\')[1] if '\\' in lib_path else lib_path)
                        if os.path.exists(potential_lib_path):
                            print(f"Found library in drive root: {potential_lib_path}")
                            # Scan all subdirectories in the library
                            try:
                                for game_dir in os.listdir(potential_lib_path):
                                    game_path = os.path.join(potential_lib_path, game_dir)
                                    if os.path.isdir(game_path):
                                        exe_name, exe_path = self._find_main_launcher(game_path)
                                        if exe_name and exe_path:
                                            print(f"Found library game: {game_dir} ({exe_name})")
                                            games_in_directory.append({
                                                "name": game_dir,
                                                "path": exe_path,
                                                "exe_name": exe_name,
                                                "type": "library"
                                            })
                            except PermissionError:
                                print(f"Permission denied accessing {potential_lib_path}")
                            except Exception as e:
                                print(f"Error scanning library path {potential_lib_path}: {e}")

                # Standard library path check (for Program Files, etc.)
                full_lib_path = os.path.join(directory, lib_path)
                if os.path.exists(full_lib_path):
                    print(f"Found library: {full_lib_path}")
                    # Scan all subdirectories in the library
                    for item in os.listdir(full_lib_path):
                        item_path = os.path.join(full_lib_path, item)
                        if os.path.isdir(item_path):
                            exe_name, exe_path = self._find_main_launcher(item_path)
                            if exe_name and exe_path:
                                print(f"Found library game: {item} ({exe_name})")
                                games_in_directory.append({
                                    "name": item,
                                    "path": exe_path,
                                    "exe_name": exe_name,
                                    "type": "library"
                                })

            # Then check for standalone games in root directory
            if directory.endswith(':\\'):  # Only for drive roots
                for item in os.listdir(directory):
                    item_path = os.path.join(directory, item)

                    # Skip if not a directory or in excluded folders
                    if not os.path.isdir(item_path) or any(
                            excl.lower() in item.lower()
                            for excl in self.EXCLUDE_FOLDERS
                    ):
                        continue

                    if self._is_likely_game_directory(item_path):
                        exe_name, exe_path = self._find_main_launcher(item_path)
                        if exe_name and exe_path:
                            print(f"Found standalone game: {item} ({exe_name})")
                            games_in_directory.append({
                                "name": item,
                                "path": exe_path,
                                "exe_name": exe_name,
                                "type": "standalone"
                            })

        except PermissionError:
            print(f"Permission denied accessing {directory}")
        except Exception as e:
            print(f"Error scanning {directory}: {e}")

        return games_in_directory

    def scan(self):
        """Perform the game scan on all directories"""
        self.games = []
        print("Starting game scan...")
        print(f"Available drives: {', '.join(self.available_drives)}")

        for directory in self.directories_to_scan:
            if os.path.exists(directory):
                detected_games = self._scan_directory(directory)
                self.games.extend(detected_games)
            else:
                print(f"Directory does not exist: {directory}")
            time.sleep(0.1)  # Small delay to prevent system overload

        print(f"Scan complete. Found {len(self.games)} games.")
        return self.games

    def get_games(self):
        """Return the list of found games"""
        return self.games

    def print_games(self):
        """Print a summary of found games"""
        if self.games:
            print("\nSummary of found games:")
            print("\nLibrary Games:")
            lib_games = [g for g in self.games if g.get('type') == 'library']
            for game in lib_games:
                print(f"Game: {game['name']}")
                print(f"Executable: {game['exe_name']}")
                print(f"Full Path: {game['path']}")
                print("-" * 50)

            print("\nStandalone Games:")
            standalone_games = [g for g in self.games if g.get('type') == 'standalone']
            for game in standalone_games:
                print(f"Game: {game['name']}")
                print(f"Executable: {game['exe_name']}")
                print(f"Full Path: {game['path']}")
                print("-" * 50)
        else:
            print("No games found in the specified directories.")


# Example usage:
if __name__ == "__main__":
    # Create scanner instance
    scanner = GameScanner()

    # Perform scan
    scanner.scan()

    # Print results
    scanner.print_games()
