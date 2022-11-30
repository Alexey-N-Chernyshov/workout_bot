"""
General error for the application.
"""

import uuid


class Error(Exception):
    """
    Error representation
    """

    error_id: uuid
    title: str
    description: str

    def __init__(self, title, description):
        self.error_id = uuid.uuid4()
        self.title = title
        self.description = description
        super().__init__(title + ": " + description)

    def __eq__(self, other):
        return self.error_id == other.error_id
