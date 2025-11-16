---

# Orderly

## Project Overview
Orderly is a centralized platform designed to manage and interact with all video games installed on a user's system. By leveraging a client-server architecture, Orderly provides game tracking, social features, and a quick recording system. The server manages game data, statistics, and communication, while the client delivers a user-friendly interface for game management and launching.

## Key FeaturesAutomatic Game Scanning: Finds and identifies your installed games by detecting the main launcher executables.
- **Smart Cover Art System:** Fetches HD covers from RAWG and caches them locally for instant loading.
- **Game Info Fetching:** Automatically pulls descriptions, release dates, and platform data for every title.
- **Secure Login & Signup:** User accounts protected with salted SHA-256 hashing and full SSL/TLS encryption.
- **Friend System:** Add, remove, view, and manage friends with server-side validation and SQLite storage.
- **User Profiles:** Clean profile pages with usernames, IDs, and friend counts.
- **Modern UI:** Sleek Tkinter interface with a navigation sidebar and responsive content frames.
- **Game Launching:** Launch games directly from the app using their detected paths.
- **Threaded SSL Server:** Multithreaded Python server handling multiple clients over encrypted sockets.
- **Local Metadata Caching:** Saves game covers and data locally for faster reloads and reduced API calls.

## Tech Stack
- Language: Python
- Client-Server Communication: Socket programming using sockets and threading
- Database: SQLite for storing player stats, game information, etc.
- APIs: Integration with external game APIs for fetching game-specific stats (e.g., Tracker Network API for Call of Duty)
- Recording: Implementation of buffers and possibly third-party libraries for game capture and recording

## Getting Started

### Requirements
- Python 3.8+
- Libraries:
  - socket (built-in)
  - threading (for multi-threading)
  - asyncio (if using an async-based architecture)
  - sqlite3 (for database management)
  - Optional: keyboard (for handling the quick record shortcut)

### Installation

1. Clone the Repository:
   ```bash
   git clone https://github.com/ShloTC/Orderly.git
   cd orderly
   ```

2. Install Dependencies:  
   No external dependencies are required; all necessary libraries are built into Python.
   
  (Please note that code is hard wired to my computer drives and directories)
### Usage

- **Organize Your Game Library:** Automatically detect and catalog installed games into a clean, modern UI.

- **View Game Details Instantly:** Access descriptions, release dates, platforms, and high-quality cover art for every game.

- **Launch Games Directly:** Open any installed game straight from the Orderly interface with one click.

- **Manage Your Social Circle:** Add and remove friends, view profiles, and keep track of your gaming connections.

- **Maintain a Secure Account:** Create and log into your account using encrypted communication and hashed passwords.

- **Browse Profiles:** View user pages with IDs, usernames, and friend counts for easy navigation and sharing.

- **Personalize Your Experience:** Build your own curated library with locally cached covers and fast-loading metadata.

### Configuration

```python
SERVER_HOST = 'localhost'
SERVER_PORT = 5000
```

## Project Structure

```
Orderly/
├── client/                 # Client-side code
│   ├── main.py             # Main client application
│   ├── ui.py               # User interface code
│   └── game_scanner.py     # Game detection logic
├── server/                 # Server-side code
│   ├── server.py           # Main server application
│   ├── friendmanager.py    # Logic for social network
│   ├── cert.pem            # Certificate for allowing SSL to work
│   └── key.pem             # Key for allowing SSL to work
└── README.md               # Project documentation
```

## Contributing
Contributions are welcome! If you have suggestions or improvements, feel free to submit a pull request or open an issue.
---
