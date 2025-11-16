---

# Orderly

## Project Overview
Orderly is a centralized platform designed to manage and interact with all video games installed on a user's system. By leveraging a client-server architecture, Orderly provides game tracking, social features, and a quick recording system. The server manages game data, statistics, and communication, while the client delivers a user-friendly interface for game management and launching.

## Key Features
- **Game Library Consolidation**: Automatically detects and consolidates installed games from various platforms (e.g., Steam, Epic Games, standalone installations) into a unified library.
- **Stat Tracking**: Tracks gameplay statistics such as playtime, achievements, and other in-game metrics. For supported games, statistics can be retrieved from public APIs.
- **Leaderboards**: Displays leaderboards allowing players to compare their performance and achievements with others.
- **Quick Recording System**: Enables users to capture the last 30 seconds of gameplay using a simple keyboard shortcut, perfect for saving important moments.
- **Client-Server Architecture**: Utilizes socket programming for efficient communication between the client (user interface) and the server (game and stat management).

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

- **Game Library**: Upon connecting the client to the server, Orderly will automatically scan the system for installed games and display them in the interface.
- **Stat Tracking**: The server automatically tracks statistics for supported games, including playtime and achievements.
- **Recording**: Press the designated hotkey (e.g., F10) to record the last 30 seconds of gameplay.

### Configuration
Modify the configuration settings (e.g., server address, ports) in `shared/config.py`:

```python
# Example Configuration
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345
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
│   └── stat_tracking.py    # Logic for tracking player stats
├── shared/                 # Shared utilities between client and server
│   └── config.py           # Configuration (e.g., host/port settings)
└── README.md               # Project documentation
```

## Contributing
Contributions are welcome! If you have suggestions or improvements, feel free to submit a pull request or open an issue.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

---
