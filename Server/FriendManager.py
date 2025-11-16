import sqlite3


class FriendManager:
    def __init__(self, db_path='orderly_users.db'):
        self.db_path = db_path
        self.static = None

    def get_friends_count(self, user_id):
        """Get the total number of friends a user has."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*)
                FROM friends
                WHERE user_id = ?
            """, (user_id,))
            return cursor.fetchone()[0]

    def get_friends(self, user_id):
        """Get a list of friends for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.id, u.username 
                FROM users u 
                JOIN friends f ON u.id = f.friend_id 
                WHERE f.user_id = ?
            """, (user_id,))
            return [{"id": row[0], "username": row[1]} for row in cursor.fetchall()]

    def add_friend(self, user_id, friend_id):
        """Add a friend to user's friend list"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Check if friend exists
                cursor.execute("SELECT id FROM users WHERE id = ?", (friend_id,))
                if not cursor.fetchone():
                    return False, "User not found"

                # Check if already friends
                cursor.execute("""
                    SELECT 1 FROM friends 
                    WHERE user_id = ? AND friend_id = ?
                """, (user_id, friend_id))
                if cursor.fetchone():
                    return False, "Already friends"

                # Add friendship
                cursor.execute("""
                    INSERT INTO friends (user_id, friend_id) 
                    VALUES (?, ?)
                """, (user_id, friend_id))
                return True, "Friend added successfully"
        except sqlite3.Error as e:
            return False, f"Database error: {str(e)}"

    def remove_friend(self, user_id, friend_id):
        """Remove a friend from user's friend list"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM friends 
                    WHERE user_id = ? AND friend_id = ?
                """, (user_id, friend_id))
                return True, "Friend removed successfully"
        except sqlite3.Error as e:
            return False, f"Database error: {str(e)}"

    def are_friends(self, user_id, friend_id):
        """Check if two users are friends"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 1 FROM friends 
                WHERE user_id = ? AND friend_id = ?
            """, (user_id, friend_id))
            return cursor.fetchone() is not None

    def handle_friendlist(self, request):
        """Handle friendlist operations using FriendManager"""
        self.static = None

        user_id = request.get('user_id')
        action = request.get('action')
        friend_id = request.get('friend_id')

        if not user_id or not action:
            return {
                'type': 'friendlist_response',
                'status': 'failed',
                'message': 'Missing required parameters.'
            }

        friend_manager = FriendManager()

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

            return {
                'type': 'friendlist_response',
                'status': 'failed',
                'message': f"Invalid action '{action}'. Expected 'get', 'add', or 'remove'."
            }

        except Exception as e:
            print(f"[!] Error in friend operation: {e}")
            return {
                'type': 'friendlist_response',
                'status': 'failed',
                'message': 'An error occurred while processing your request.'
            }
