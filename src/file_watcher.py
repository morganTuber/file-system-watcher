from typing import Callable
from watchdog.events import FileSystemEvent, LoggingEventHandler


class FileWatcher(LoggingEventHandler):
    def __init__(self, callback: Callable[[], None]):
        # Callback is called when any event happens
        self.callback = callback

    def on_any_event(self, event: FileSystemEvent):
        self.callback()
