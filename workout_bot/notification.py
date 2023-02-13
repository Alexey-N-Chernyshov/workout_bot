"""
General error for the application.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Notification(Exception):
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

    def __eq__(self, other):
        return (self.title == other.title
                and self.description == other.description)

    def __hash__(self):
        return hash((self.title, self.description))
