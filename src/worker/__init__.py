""" __init__.py

    The worker library provides an interface to spin off threads of execution. Workers 
    get spun up whenever a call to the trigger endpoint occurs with valid valid 
    parameters.
"""
import threading

from abc import ABC, abstractmethod 

class WorkerError(Exception):
    """Exception to handle errors in the Worker class"""
    pass

class Worker(ABC):
    """ Workers are wrappers for code segments that run in their own thread"""

    # Every Worker should implement WORKER_ID
    WORKER_ID = ""

    def __init__(self, app, args):
        """ Construct a new Worker class
        
            Args:
                app - The current flask application
                args - A dictionary of arguments to pull parameters from

            Returns:
                A new Worker
        """
        self.app = app
        self.args = args
        self.thread = None

    @abstractmethod
    def run(self):
        """ Performs whatever work the Worker is designed to do """
        raise NotImplementedError

    @abstractmethod
    def validate(self):
        """ Validates the fields passed in through the args parameters """
        raise NotImplementedError
        
    @staticmethod
    def setup():
        pass
        
    @staticmethod
    def teardown():
        pass

    def start(self):
        """ Starts a thread targetting the workers run() function"""
        self.app.logger.info(f"Starting worker '{self.WORKER_ID}'")
        if self.thread is None:
            self.thread = threading.Thread(target=self.run)
        
        try:
            self.thread.start()
        except RuntimeError as e:
            raise WorkerError(f"Failed to start worker '{self.WORKER_ID}': " + str(e))

    def join(self, timeout=None):
        """ Calls join on the worker's thread with a specified timeout
        
            Args:
                timeout - The time in seconds to wait for the thread to join
        """
        self.app.logger.info(f"Joining worker '{self.WORKER_ID}'")
        if self.thread is not None:
            try:
                if timeout is None:
                    self.thread.join()
                else:
                    self.thread.join(timeout=timeout)
            except RuntimeError as e:
                raise WorkerError(f"Failed to join worker '{self.WORKER_ID}': " + str(e))
        else:
            self.app.logger.warning(f"No thread to join")
        
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
            
class MessageWorker(Worker):
    
    WORKER_ID = "message"
    
    def run(self):
        
