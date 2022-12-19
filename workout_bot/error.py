"""
General error for the application.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Error(Exception):
    """
    Error representation
    """

    title: str
    description: str
    datetime: datetime

    def __init__(self, title, description):
        self.title = title
        self.description = description
        self.datetime = datetime.utcnow()
        super().__init__(title + ": " + description)
