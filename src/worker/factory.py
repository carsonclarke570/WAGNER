""" factory.py

    Provides a factory to build Worker classes from a given WORKER_ID and dictionary of 
    arguments.
"""
import logging

from . import Worker, WorkerError

class FactoryError(Exception):
    """Exception to handle errors in the WorkerFactory class."""
    pass

class WorkerFactory:
    """Implements a factory design patten for Workers"""

    REGISTRY = {}

    @classmethod
    def init(cls):
        """ Initialize the factory by populating the module registry"""
        cls.REGISTRY = {}

        # Recursely gather all submodules
        def recurse(subclasses):
            for subclass in subclasses:
                cls.REGISTRY[subclass.WORKER_ID] = subclass
                recurse(subclass.__subclasses__())

        recurse(Worker.__subclasses__())
            
    @classmethod
    def build(cls, id, args, pid, background):
        """ Attempts to build a Worker class from a given WORKER_ID and set of arguments.

        Args:
            id - The WORKER_ID of the class to build.
            args - A dictionary of arguments

        Returns:
            A new Worker class.

        Raises:
            FactoryError: If unable to build the Worker class
        """
        # Attempt to find the Worker subclass from the given id
        class_type = cls.REGISTRY.get(id, None)
        if class_type is None:
            raise FactoryError(f"No worker found for WORKER_ID '{id}'")
        
        # Validate the class
        worker = class_type(args, pid, background)
        try:
            worker.validate()
        except WorkerError as e:
            raise FactoryError(f"Error validating worker: {str(e)}")
        
        return worker
