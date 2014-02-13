from __future__ import division
from threading import Thread
from avida_support.evaluator import MutationEvaluator

class AnalyzeThread(Thread):
    """
    Base class for worker threads that access analyze mode.

    The default behavior of this thread is to load the task list for a
    single genome.
    
    Each worker thread maintains a reference to its parent L{LineageViewer}
    and sends results via the message queue. A lock is shared between worker
    threads to preserve mutual exclusion of analyze mode.
    """
    def __init__(self, lock=None, path='avida/', app=None, data=None, index=0,
                 daemon=None, *args, **kwargs):
        """
        Create a new worker thread.

        @param lock: the mutex associated with analyze mode.
        @param path: the relative file path of an avida instance.
        @param app: the parent L{LineageViewer} of this thread.
        @param data: the genome data to analyze.
        @param index: the index of the genome to analyze.
        @param daemon: the status of this thread as a daemon.
        """
        super(AnalyzeThread, self).__init__(*args, **kwargs)
        if daemon is not None:
            self.daemon = daemon
        self.lock = lock
        self.data = data
        self.index = index
        self.app = app
        self.index = index
        self.evaluator = MutationEvaluator(path)
        
    def run(self):
        """
        Run the thread behavior.

        The default behavior calls evaluate on the genome.
        Override to implement different behavior.
        """
        self.evaluate(self.index, self.data)


    def evaluate(self, index, data):
        """
        Evaluate a specific genome.

        The default behavior is to load the task list of the genome.
        Sends the results to the parent app. Override to evaluate different
        properties of the genome.

        @param index: the index of the genome.
        @param data: the genome data.
        """
        with self.lock:
            output = self.evaluator.get_sequence_data(data['genome'], ['task_list'])
        self.app.queue.put(('task_list', index, output['task_list']))        