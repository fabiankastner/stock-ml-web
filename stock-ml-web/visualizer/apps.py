from multiprocessing import Process

from django.apps import AppConfig

from common.util.retrieve_data import load_data


class VisualizerConfig(AppConfig):
    name = 'visualizer'

    def ready(self):
        import os
        if os.environ.get('RUN_MAIN', None) == 'true':
            

            # load_data()
            p = Process(target=load_data)
            p.start()
            