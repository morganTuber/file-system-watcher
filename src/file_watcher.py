import logging
from typing import Callable
from watchdog.events import FileSystemEvent, PatternMatchingEventHandler


class FileWatcher(PatternMatchingEventHandler):
    def __init__(self, callback: Callable[[], None]):
        # Callback is called when any event happens
        self.callback = callback
        PatternMatchingEventHandler.__init__(
            self, patterns=["*.zip"], ignore_directories=True, case_sensitive=False
        )

    def on_any_event(self, event: FileSystemEvent):
        logging.info("Detected file changes..running function")
        self.callback()
