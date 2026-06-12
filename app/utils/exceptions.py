class TokenException(Exception):
    def __init__(self, name):
        self.is_api = "api" in name
        self.name = f"you have not token to pass the page: {name}"