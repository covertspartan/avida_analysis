from __future__ import division
from analyzethread import AnalyzeThread
from avida_support.evaluator import MutationEvaluator
from timeit import default_timer

class AnalyzeUpdateThread(AnalyzeThread):
    """
    Worker thread that loads all data about a group of genomes in batches.

    See L{AnalyzeAllThread}.
    """
    def __init__(self, max_time=.1, start_increment=128, *args, **kwargs):
        self.max_time = max_time
        self.start_increment = start_increment
        self.stable = False
        super(AnalyzeUpdateThread, self).__init__(*args, **kwargs)
        
    def run(self):
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
                output = self.evaluator.get_batch_data(sequences, ['task_list', 'fitness',
                                                                   'gest_time', 'merit'])
            time = default_timer() - start

            for i, out in enumerate(output):
                if index + i < len(self.data):
                    self.app.queue.put(('update', index + i, out))

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
        self.app.queue.put(('update_all'))
