from __future__ import division
from analyzethread import AnalyzeThread
from avida_support.evaluator import MutationEvaluator
from timeit import default_timer

class AnalyzeAllThread(AnalyzeThread):
    """
    A background process that loads task data for all genomes using
    analyze mode.
    """
    def __init__(self, max_time=.1, start_increment=128, *args, **kwargs):
        """
        Create a new worker thread.

        @param max_time: the maximum time to spend on any batch of genomes.
        @param start_increment: the default size of genome batches, a multiple of 2.
        """
        self.max_time = max_time
        self.start_increment = start_increment
        self.stable = False
        super(AnalyzeAllThread, self).__init__(*args, **kwargs)
        
    def run(self):
        """
        Worker function, runs batches of analyze jobs.

        Changes batch size as needed to run the maximum number of genomes within
        the time limit. Results are sent to the analyze message queue on the
        L{LineageViewer} object that started the thread.
        """
        index = 0
        increment = self.start_increment
        fit = None
        last_fit = None
        while index < len(self.data):
            if index + increment < len(self.data):
                sequences = [d['genome'] for d in self.data[index:index+increment]]
            else:
                sequences = [d['genome'] for d in self.data[index:]]

            start = default_timer()
            with self.lock:
                output = self.evaluator.get_batch_data(sequences, ['task_list'])
            time = default_timer() - start

            for i, out in enumerate(output):
                if index + i < len(self.data):
                    self.app.queue.put(('task_list', index + i, out['task_list']))

            index += increment
            
            last_fit = fit
            fit = time <= self.max_time

            if not self.stable:
                if last_fit is None:
                    increment *= 2 if fit else .5
                else:
                    if fit:
                        if last_fit:
                            increment *= 2
                        else:
                            self.stable = True
                    else:
                        if last_fit:
                            increment //= 2
                            self.stable = True
                        else:
                            increment //= 2
                        if increment < 1:
                            increment = 1
                            self.stable = True
                increment = int(increment)
