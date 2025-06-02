# event_service/service.py
from .repository import EventRepository

class EventService:
    @staticmethod
    def save_event(data: dict):
        EventRepository.insert_event(data)
