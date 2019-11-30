""" scheduler.py

The schedule module manages the various Workers generated from the JSON request sent to 
the API. The scheduler works as such:
1. Determine mode of scheduling for the Workers
2. Run the setup functions for each of the Workers
3. Execute each of the Workers
"""
import threading
import time

from datetime import datetime

from worker.factory import WorkerFactory, FactoryError

class SchedulerError(Exception):
    """Exception to handle errors in the Scheduler class."""
    pass

class Scheduler:

    MODE_INSTANT = 1
    MODE_DELAY = 2
    MODE_ALARM = 3

    MODE_MAP = {
        'instant': MODE_INSTANT,
        'delay': MODE_DELAY,
        'alarm': MODE_ALARM
    }

    def __init__(self, meta, pid):
        """ Construct a new Scheduler
        
            Args:
                meta (Dict) - Metadata from the HTTP POST request
            Raises:
                SchedulerError - If the metadata passed in has bad data
            Returns:
                A new Scheduler
        """
        # Parse workers
        self.workers = []
        workers = meta.get("workers", None)
        if workers is None:
            raise SchedulerError(f"Requires 'workers' field")
        
        if not isinstance(workers, list):
            raise SchedulerError(f"Expected 'workers' as a list")

        for worker in workers:
            name = worker.get('type', None)
            background = worker.get('async', False)
            args = worker.get('args', {})
            if name is None:
                raise SchedulerError(f"Requires 'type' field")

            if not isinstance(background, bool):
                raise SchedulerError(f"Expected 'async' as a bool")

            try:
                worker = WorkerFactory.build(name, args, pid, background)
            except FactoryError as e:
                raise SchedulerError(f"Error building '{name}': {str(e)}")

            self.workers.append(worker)

        # Parse mode
        self.mode = None
        self.time = None
        schedule = meta.get('schedule', None)
        if schedule is None:
            self.mode = self.MODE_INSTANT
        else:
            mode = schedule.get('mode', None)
            if mode is None:
                raise SchedulerError(f"'schedule' requires 'mode' field")
            
            self.mode = self.MODE_MAP.get(mode, None)
            if self.mode is None:
                raise SchedulerError(f"Unrecognized value for 'mode': {mode}")

            # Get the delay
            if self.mode == self.MODE_DELAY:
                delay = schedule.get('delay', None)
                if delay is None:
                    raise SchedulerError(f"'schedule' requires 'seconds' field when in the specified mode")

                if not isinstance(delay, (int, float)):
                    raise SchedulerError(f"Expected 'seconds' as a float or int")

                self.time = delay
            elif self.mode == self.MODE_ALARM:
                time = schedule.get('time', None)
                if time is None:
                    raise SchedulerError(f"'schedule' requires 'time' field when in the specified mode")
                
                try:
                    trigger_time = datetime.strptime(time, '%m/%d/%y %H:%M:%S')
                except Exception as e:
                    print(e)
                    raise SchedulerError(f"Failed to parse '{time}' as a datetime object")

                self.time = trigger_time

    def run(self):
        """ Handles running the worker threads """
        begin = time.time()
        for worker in self.workers:
            worker.setup()

        # If 'delay' block until the delay has been reach
        if self.mode == self.MODE_DELAY:
            left = self.time - time.time() + begin
            if left > 0:
                time.sleep(left)
        # Else if 'alarm' wait until time arrives
        elif self.mode == self.MODE_ALARM:
            while(datetime.now() < self.time):
                time.sleep(0.5)

        # Actually execute the workers
        for worker in self.workers:
            worker.start()

        # Join all workers and teardown
        for worker in self.workers:
            worker.join()
            worker.teardown()
            
    def start(self):
        """ Launches the scheduling thread 
        
        Raises:
            SchedulerError - If the thread fails to start
        """
        thread = threading.Thread(target=self.run)
        try:
            thread.start()
        except RuntimeError as e:
            raise SchedulerError(f"Failed to start worker '{self.WORKER_ID}': " + str(e))