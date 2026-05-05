
class SessionManager:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(SessionManager)
            cls._instance._session_data = {}
        return cls._instance

    def set(self, key: str, value):
        self._session_data[key] = value

    def get(self, key: str):
        return self._session_data.get(key)

    def clear(self):
        self._session_data.clear()

