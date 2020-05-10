from collections import namedtuple

import pygame

EventType = namedtuple('EventType', ['action', 'need_event'])


class EventHandler:

    def __init__(self):
        self.types: {str: EventType} = {}
        self.key_ups = {}
        self.key_downs = {}

    def register_types(self, event_type: {str: EventType}):
        self.types = event_type

    def _is_type_available(self, event_type):
        return event_type in self.types.keys()

    def execute_event(self, event):
        if self._is_type_available(event.type):
            if self.types[event.type].need_event:
                self.types[event.type].action(event)
            else:
                self.types[event.type].action()

    def register_key_down_actions(self, key_down_actions):
        if pygame.KEYDOWN in self.types.keys():
            self.key_downs = key_down_actions
        else:
            raise ValueError('Event KEYDOWN not registered.')

    def _is_key_down_available(self, event_key):
        return event_key in self.key_downs.keys()

    def execute_key_down(self, event_key):
        if self._is_key_down_available(event_key):
            self.key_downs[event_key]()

    def register_key_up_actions(self, key_up_actions):
        if pygame.KEYUP in self.types.keys():
            self.key_ups = key_up_actions
        else:
            raise ValueError('Event KEYUP not registered.')

    def _is_key_up_available(self, event_key):
        return event_key in self.key_ups.keys()

    def execute_key_up(self, event_key):
        if self._is_key_up_available(event_key):
            self.key_ups[event_key]()
