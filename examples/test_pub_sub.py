from time import sleep

from experimentor.models.experiments.base_experiment import Experiment

# logger = multiprocessing.log_to_stderr()
# logger.setLevel(logging.DEBUG)
# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# ch.setFormatter(formatter)
# logger.addHandler(ch)


exp = Experiment()

test_func = lambda x: print(x)

exp.start.connect(test_func)
sleep(3)
exp.start.emit('AAAA')
exp.finalize()
