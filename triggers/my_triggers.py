from findrum.interfaces import EventTrigger
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time, threading, logging

class LocalFileTrigger(EventTrigger):
    def start(self):
        path_to_watch = self.config.get("path", ".")
        file_suffix = self.config.get("suffix", ".csv")

        logging.info(f"👀 Watching folder: {path_to_watch} (files *{file_suffix})")

        class Handler(FileSystemEventHandler):
            def __init__(self, trigger_instance):
                self.last_run_time = 0
                self.trigger = trigger_instance

            def on_modified(self, event):
                if event.is_directory or not event.src_path.endswith(file_suffix):
                    return

                now = time.time()
                if now - self.last_run_time < 2:
                    return
                self.last_run_time = now

                logging.info(f"📂 File modified: {event.src_path}")
                self.trigger._run_pipeline({"file_path": event.src_path})

        observer = Observer()
        handler = Handler(self)
        observer.schedule(handler, path=path_to_watch, recursive=False)

        def run_observer():
            observer.start()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
            observer.join()

        threading.Thread(target=run_observer, daemon=True).start()