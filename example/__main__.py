from datetime import datetime
import os
import signal
import sys
from time import sleep

import luigi

from example.tasks import PipelineTask


def load_env_variables():
    try:
        return {
            'initial_sleep': int(os.getenv('INITIAL_SLEEP', 600)),
        }
    except KeyError as key_err:
        error_message = 'Could not load the: {} environment variable, exiting\n'.format(datetime.now(), key_err)
        sys.stderr.write(error_message)
        shutdown(error_message)


def send_notification(message=None):
    print(message)


def shutdown(message=None):
    if not message:
        message = "Shutdown"
    send_notification(message)
    sys.exit(1)


def signal_handler(signum, frame):
    sys.stderr.write(
        '{}: Application exiting on signal: {}\n'.format(
            datetime.now(), str(signum)))
    sys.exit(0)


def trace(env_vars, message):
    if bool(env_vars['verbose']):
        print(message)
        send_notification(str(message))


def main():
    print('Starting...')
    print("Loading config from {0}".format(os.getenv("LUIGI_CONFIG_PATH")))
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    env_vars = load_env_variables()

    while True:
        print('Sleeping for {}'.format(env_vars['initial_sleep']))
        sleep(env_vars['initial_sleep'])
        luigi.build([PipelineTask()])


if __name__ == '__main__':
    main()
