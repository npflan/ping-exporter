import subprocess
import concurrent.futures
import prometheus_client.core
import csv
import os

basedir = os.path.abspath(os.path.dirname(__file__))
targets = os.path.join(basedir, 'network_data.csv')

with open('network_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    nodes = {row[1]: (row[0], row[2]) for row in reader}


class PingCollector(object):

    def collect(self):
        pings = prometheus_client.core.GaugeMetricFamily(
            'ping',
            'Does instance respond to ping',
            labels=['name', 'instance', 'dist'])
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=100)
        futures = {}
        for key in nodes.keys():
            host, name, dist = key, *nodes[key]
            future = executor.submit(
                subprocess.run,
                ["ping", "-c", "1", '-t', '1', host],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)
            futures[future] = name, host, dist
        for future in concurrent.futures.as_completed(futures):
            name, host, dist = futures.pop(future)
            res = future.result()
            pings.add_metric([name, host, dist], int(res.returncode == 0))
        executor.shutdown()
        yield pings


# For running with a wsgi server like gunicorn
prometheus_client.core.REGISTRY.register(PingCollector())
app = prometheus_client.make_wsgi_app()

# For easy debugging
if __name__ == '__main__':
    r = PingCollector()
    from pprint import pprint
    from operator import attrgetter
    pprint(list(map(attrgetter('samples'), r.collect())))
