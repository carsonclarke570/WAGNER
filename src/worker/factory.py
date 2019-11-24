""" factory.py

    Provides a factory to build Worker classes from a given WORKER_ID and dictionary of 
    arguments.
"""
from . import Worker, WorkerError

class FactoryError(Exception):
    """Exception to handle errors in the WorkerFactory class."""
    pass

class WorkerFactory:
    """Implements a factory design patten for Workers"""

    @staticmethod
    def setup(app):
        """ Calls setup() on all Worker modules
        
        Args:
            app - The current Flask application
        """
        types = Worker.__subclasses__()
        for subclass in types:
            app.logger.info(f"Setting up '{subclass.WORKER_ID}' module")
            subclass.setup()
            
    @staticmethod
    def teardown(app):
        """Calls teardown() on all Worker modules
        
        Args:
            app - The current Flask application
        """
        types = Worker.__subclasses__()
        for subclass in types:
            app.logger.info(f"Tearing down '{subclass.WORKER_ID}' module")
            subclass.teardown()

    @staticmethod
    def build(app, id, args):
        """ Attempts to build a Worker class from a given WORKER_ID and set of arguments.

        Args:
            app - The current flask application
            id - The WORKER_ID of the class to build.
            args - A dictionary of arguments

        Returns:
            A new Worker class.

        Raises:
            FactoryError: If unable to build the Worker class
        """
        # Attempt to find the Worker subclass from the given id
        types = Worker.__subclasses__()
        derived_class = None
        for subclass in types:
            if subclass.WORKER_ID == id:
                derived_class = subclass(app, args)

        if derived_class is None:
            raise FactoryError(f"Failed to build for Worker ID '{id}'")
        
        # Validate the class
        try:
            derived_class.validate()
        except WorkerError as e:
            raise FactoryError(f"Error validating worker: {str(e)}")
        
        return derived_class
