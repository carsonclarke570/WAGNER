""" __init__.py

    The worker library provides an interface to spin off threads of execution. Workers 
    get spun up whenever a call to the trigger endpoint occurs with valid valid 
    parameters.
"""
import threading
import logging
import os
import time

from abc import ABC, abstractmethod 
from gtts import gTTS
from io import BytesIO

class WorkerError(Exception):
    """Exception to handle errors in the Worker class"""
    pass

class Worker(ABC):
    """ Workers are wrappers for code segments that run in their own thread
    """

    # Every Worker should implement WORKER_ID
    WORKER_ID = ""

    def __init__(self, args, pid, background=False):
        """ Construct a new Worker class
        
            Args:
                args (Dict) - A dictionary of arguments to pull parameters from
                background (bool) - Boolean determining whether or not run in a thread
            Returns:
                A new Worker
        """
        self.args = args
        self.background = background
        self.pid = pid
        if background:
            self.thread = threading.Thread(target=self.run)
        else:
            self.thread = None

    @abstractmethod
    def run(self):
        """ Performs whatever work the Worker is designed to do """
        raise NotImplementedError

    @abstractmethod
    def validate(self):
        """ Validates the fields passed in through the args parameters """
        raise NotImplementedError
        
    def setup(self):
        """ If the worker requires some sort of set up, implement this function"""
        pass
        
    def teardown(self):
        """ If the worker requires some sort of tear down, implement this 
        function"""
        pass

    def start(self):
        """ Starts a thread targetting the workers run() function"""
        if self.background:
            logging.info(f"Process {self.pid} - Starting worker '{self.WORKER_ID}' in the background")
            try:
                self.thread.start()
            except RuntimeError as e:
                raise WorkerError(f"Failed to start worker '{self.WORKER_ID}': " + str(e))
        else:
            logging.info(f"Process {self.pid} - Starting worker '{self.WORKER_ID}'")
            self.run()

    def join(self, timeout=None):
        """ Calls join on the worker's thread with a specified timeout
        
            Args:
                timeout - The time in seconds to wait for the thread to join
        """
        logging.info(f"Joining worker '{self.WORKER_ID}'")
        if not self.background:
            return

        try:
            self.thread.join(timeout=timeout)
        except RuntimeError as e:
            raise WorkerError(f"Failed to join worker '{self.WORKER_ID}': " + str(e))
        
class PrintWorker(Worker):
    """ Prints a message to the terminal"""

    WORKER_ID = "print"

    def run(self):
        """ Prints a message to the terminal """
        print (self.args["message"])

    def validate(self):
        """ Ensures the PrintWorker has a 'message' parameter """
        if "message" not in self.args:
            raise WorkerError(f"'message' argument required")
            
# class SoundWorker(Worker):
#     """ Plays a sound to the terminal """
#     WORKER_ID = "sound"

#     def run(self):
#         """ Plays a sound from the ./sounds folder """
#         path = os.path.dirname(__file__) + "/sounds/" + self.args["sound"] + ".wav"
#         sound = pygame.mixer.Sound(path)
#         sound.play()

#     def validate(self):
#         """ Ensures SoundWorker has a `sound' parameter"""
#         if "sound" not in self.args:
#             raise WorkerError(f"'sound' argument required")
        
# class MessageWorker(Worker):
#     """ Plays a text to speech of a message passed in"""
#     WORKER_ID = "message"

#     def __init__(self, args, pid, background=False):
#         """ Construct a new MessageWorker class
        
#             Args:
#                 args (Dict) - A dictionary of arguments to pull parameters from
#                 background (bool) - Boolean determining whether or not run in a thread
#             Returns:
#                 A new MessageWorker
#         """
#         self.fp = BytesIO()
#         super().__init__(args, pid, background)

#     def setup(self):
#         """ Begin the text to speech conversion """
#         tts = gTTS(text=self.args["message"], lang='en', slow=False)
#         tts.write_to_fp(self.fp)
#         self.fp.seek(0)

#     def teardown(self):
#         """ Dispose of the file pointer """
#         self.fp.close()

#     def run(self):
#         """ Converts and saves a message to a .wav file and plays it"""
#         pygame.mixer.music.load(self.fp)
#         pygame.mixer.music.play()

#     def validate(self):
#         """ Ensures the SoundWorker has a 'message' parameter """
#         if "message" not in self.args:
#             raise WorkerError(f"'message' argument required")
            
