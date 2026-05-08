"""
Implementation of the Singleton Design Pattern for a SessionManager.
Ensures only one instance of the session data store exists within a process.
"""

class SessionManager:
    """
    A singleton class to manage temporary session data.
    
    _instance: Holds the single instance of this class.
    _session_data (dict): Storage for key-value session information.
    """
    _instance = None

    def __new__(cls):
        """
        Overrides the creation of the object to return the existing instance 
        if it exists, or create a new one if it doesn't.
        """
        if cls._instance is None:
            cls._instance = object.__new__(SessionManager)
            cls._instance._session_data = {}
        return cls._instance

    def set(self, key: str, value):
        """Stores a value in the session data dictionary."""
        self._session_data[key] = value

    def get(self, key: str):
        """Retrieves a value from the session data dictionary by key."""
        return self._session_data.get(key)

    def clear(self):
        """Wipes all data from the session storage."""
        self._session_data.clear()