'''
Performance and accuracy of HyperLogLog
'''
import time, logging, random, pickle
from datasketch.hyperloglog import HyperLogLog, HyperLogLogPlusPlus, SparseHyperLogLogPlusPlus

logging.basicConfig(level=logging.INFO)

# Produce some bytes
int_bytes = lambda x: ("a-%d-%d" % (x, x)).encode('utf-8')


def run_perf(card, p, _class):
    logging.info(f'{_class.__name__} using p = {p}')
    h = _class(p=p)
    start = time.clock()
    for i in range(card):
        h.update(int_bytes(i))
    duration = time.clock() - start
    logging.info("Digested %d hashes in %.4f sec" % (card, duration))
    return duration


def run_acc(size, seed, p, _class):
    logging.info(f'{_class.__name__} using p = {p}')
    h = _class(p=p)
    s = set()
    random.seed(seed)
    for i in range(size):
        v = int_bytes(random.randint(1, size))
        h.update(v)
        s.add(v)
    perr = abs(float(len(s)) - h.count()) / float(len(s))
    return perr


def run_pickle(card, p, _class):
    logging.info(f'{_class.__name__} using p = {p}')
    h = _class(p=p)
    for i in range(card):
        h.update(int_bytes(i))
    start = time.clock()
    pickle.loads(pickle.dumps(h))
    duration = time.clock() - start
    logging.info("Pickle and unpickled in %.4f sec with %d cards" % (duration, card))
    return duration


def run_bench(card, size, _class):
    ps = range(4, 17)
    output = f"{_class.__name__}_benchmark.png"

    logging.info("> Running performance tests")
    run_times = [run_perf(card, p, _class) for p in ps]

    logging.info("> Running accuracy tests")
    errs = [run_acc(size, 1, p, _class) for p in ps]

    logging.info("> Plotting result")
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axe = plt.subplots(1, 2, sharex=True, figsize=(10, 4))
    ax = axe[1]
    ax.plot(ps, run_times, marker='+')
    ax.set_xlabel("P values")
    ax.set_ylabel("Running time (sec)")
    ax.ticklabel_format(axis='y', style='sci', scilimits=(-2,2))
    ax.set_title(f"{_class.__name__} performance")
    ax.grid()
    ax = axe[0]
    ax.plot(ps, errs, marker='+')
    ax.set_xlabel("P values")
    ax.set_ylabel("Error rate in cardinality estimation")
    ax.set_title(f"{_class.__name__} accuracy")
    ax.grid()

    fig.savefig(output)
    logging.info("Plot saved to %s" % output)


run_bench(5000, 5000, HyperLogLog)
run_bench(5000, 5000, HyperLogLogPlusPlus)
run_bench(5000, 5000, SparseHyperLogLogPlusPlus)
