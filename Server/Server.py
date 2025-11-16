import socket
import threading
import sqlite3
import hashlib
import uuid
import json
from FriendManager import FriendManager
import ssl


class OrderlyServer:
    def __init__(self, host='localhost', port=5000):
        # VARIABLES
        self.static = None  # variable to prevent "function may be static"
        self.e = None  # variable to prevent "too broad exception clause"

        self.init_database()

        # Socket setup
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)

        # create SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')

        # wrap it
        self.server = context.wrap_socket(self.server, server_side=True)
        print(f"SSL server started on {host}:{port}")

        # Connected clients
        self.clients = {}  # {user_id: (socket, username)}

    def init_database(self):
        """Initialize SQLite database for user management"""
        self.static = None
        with sqlite3.connect('orderly_users.db') as conn:
            cursor = conn.cursor()

            # Create the `users` table with the correct schema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL
                )
            ''')

            # Create the `friends` table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS friends (
                    user_id TEXT,
                    friend_id TEXT,
                    PRIMARY KEY (user_id, friend_id),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (friend_id) REFERENCES users (id)
                )
            ''')
            cursor.execute('''
                            CREATE TABLE IF NOT EXISTS messages (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            sender_id TEXT,
                            receiver_id TEXT,
                            message TEXT,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                        );
                        ''')

            conn.commit()

    def hash_password(self, password, salt=None):
        self.static = None
        """
        Create a secure hash for the password

        :param password: Plain text password
        :param salt: Optional salt (generated if not provided)
        :return: (salt, hashed_password)
        """
        if salt is None:
            salt = uuid.uuid4().hex

        # Hash password with salt using SHA-256
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return salt, password_hash

    def register_user(self, username, email, password):
        """
        Register a new user in the database

        :param username: Unique username
        :param email: User's email
        :param password: User's password
        :return: User ID or None if registration fails
        """
        try:
            user_id = uuid.uuid4().hex
            salt, password_hash = self.hash_password(password)

            with sqlite3.connect('orderly_users.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users 
                    (id, username, email, password_hash, salt) 
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, username, email, password_hash, salt))
                conn.commit()

            return user_id
        except sqlite3.IntegrityError:
            print(f"[!] Username or email already exists")
            return None

    def authenticate_user(self, email, password):
        """
        Authenticate a user

        :param email: Email
        :param password: Password
        :return: User info or None
        """
        try:
            with sqlite3.connect('orderly_users.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, email, password_hash, salt 
                    FROM users 
                    WHERE username = ?
                ''', (email,))
                user = cursor.fetchone()

                if user:
                    # Verify password
                    _, provided_hash = self.hash_password(password, user[3])
                    if provided_hash == user[2]:
                        return {
                            'id': user[0],
                            'username': user[1]
                        }
            return None
        except Exception as e:
            print(f"[!] Authentication error: {e}")
            return None

    def handle_client(self, client_socket, address):
        """Handle client connection and requests"""
        print(f"[+] Client connected from IP: {address[0]}")

        # Initialize FriendManager
        friend_manager = FriendManager()

        def send_response(response_data):
            """Helper function to send JSON responses"""
            client_socket.send(json.dumps(response_data).encode('utf-8'))

        def handle_login(login_request):
            """Handle login requests"""
            user = self.authenticate_user(login_request['email'], login_request['password'])
            if user:
                self.clients[user['id']] = (client_socket, user['username'])
                print(f"[+] User '{user['username']}' logged in from IP: {address[0]}")
                return {
                    'type': 'auth_response',
                    'status': 'success',
                    'user': user
                }
            return {
                'type': 'auth_response',
                'status': 'failed',
                'message': 'Invalid email or password.'
            }

        def handle_signup(signup_request):
            """Handle signup requests"""
            success = self.register_user(
                signup_request['username'],
                signup_request['email'],
                signup_request['password']
            )
            if success:
                return {
                    'type': 'signup_response',
                    'status': 'success',
                    'message': 'Signup successful!'
                }
            return {
                'type': 'signup_response',
                'status': 'failed',
                'message': 'Username or email already exists.'
            }

        def handle_friendlist(friendlist_request):
            """Handle friendlist operations using FriendManager"""
            user_id = friendlist_request.get('user_id')
            action = friendlist_request.get('action')
            friend_id = friendlist_request.get('friend_id')

            if not user_id or not action:
                return {
                    'type': 'friendlist_response',
                    'status': 'failed',
                    'message': 'Missing required parameters.'
                }

            try:
                if action == 'get':
                    friends = friend_manager.get_friends(user_id)
                    return {
                        'type': 'friendlist_response',
                        'status': 'success',
                        'friends': friends
                    }

                elif action == 'add':
                    if not friend_id:
                        return {
                            'type': 'friendlist_response',
                            'status': 'failed',
                            'message': 'Friend ID required for adding friend.'
                        }

                    success, message = friend_manager.add_friend(user_id, friend_id)
                    return {
                        'type': 'friendlist_response',
                        'status': 'success' if success else 'failed',
                        'message': message
                    }

                elif action == 'remove':
                    if not friend_id:
                        return {
                            'type': 'friendlist_response',
                            'status': 'failed',
                            'message': 'Friend ID required for removing friend.'
                        }

                    success, message = friend_manager.remove_friend(user_id, friend_id)
                    return {
                        'type': 'friendlist_response',
                        'status': 'success' if success else 'failed',
                        'message': message
                    }
                elif action == 'count':
                    count = friend_manager.get_friends_count(user_id)
                    return {
                        'type': 'friendlist_response',
                        'status': 'success',
                        'message': str(count)
                    }

                return {
                    'type': 'friendlist_response',
                    'status': 'failed',
                    'message': f"Invalid action '{action}'. Expected 'get', 'add', 'remove', or 'count'."
                }

            except Exception as error:
                print(f"[!] Error in friend operation: {error}")
                return {
                    'type': 'friendlist_response',
                    'status': 'failed',
                    'message': 'An error occurred while processing your request.'
                }

        def handle_profile(profile_request):
            """Handle profile requests by fetching user details from the database."""
            user_id = profile_request.get('user_id')
            if not user_id:
                return {
                    'type': 'user_info_response',
                    'status': 'failed',
                    'message': 'User ID is required.'
                }

            try:
                with sqlite3.connect('orderly_users.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT id, username FROM users WHERE id = ?
                    ''', (user_id,))
                    user = cursor.fetchone()

                    if user:
                        return {
                            'type': 'user_info_response',
                            'status': 'success',
                            'user': {
                                'id': user[0],
                                'username': user[1]
                            }
                        }
                    else:
                        return {
                            'type': 'user_info_response',
                            'status': 'failed',
                            'message': 'User not found.'
                        }
            except Exception as error:
                print(f"[!] Error fetching user profile: {error}")
                return {
                    'type': 'user_info_response',
                    'status': 'failed',
                    'message': 'Internal server error.'
                }

        # Main client handling loop
        while True:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break

                request = json.loads(data)

                # Route request to appropriate handler
                handlers = {
                    'login': handle_login,
                    'signup': handle_signup,
                    'friendlist': handle_friendlist,
                    'user_info': handle_profile
                }
                print(request)
                handler = handlers.get(request['type'])

                if handler:
                    response = handler(request)
                else:
                    response = {
                        'type': 'error_response',
                        'status': 'failed',
                        'message': f"Unknown request type: {request['type']}"
                    }

                client_socket.sendall(json.dumps(response).encode('utf-8'))

            except json.JSONDecodeError:
                send_response({
                    'type': 'error_response',
                    'status': 'failed',
                    'message': 'Invalid JSON format'
                })
            except Exception as e:
                print(f"[!] Error handling client request: {e}")
                send_response({
                    'type': 'error_response',
                    'status': 'failed',
                    'message': 'Internal server error'
                })

    def start(self):
        """Accept and handle client connections"""
        try:
            while True:
                # Wait for a client connection
                client_socket, address = self.server.accept()
                print(f"Connection from {address}")

                # Start thread to handle this client
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.start()

        except KeyboardInterrupt:
            print("\nServer shutting down...")

        finally:
            self.server.close()


def main():
    # Create server instance
    server = OrderlyServer()

    # Start the server
    server.start()


if __name__ == "__main__":
    main()
