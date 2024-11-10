import json
import os
import shutil
import time
import logging
import schedule
from daemon import DaemonContext
from datetime import datetime
import signal
import sys

CONFIG_FILE = '/etc/backupd.conf'
is_running = True

def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)

def backup(config):
    timestamp = datetime.now().strftime(config['timestamp_format'])
    backup_dir = os.path.join(config['backup_directory'], f"backup_{timestamp}")
    shutil.copytree(config['source_directory'], backup_dir)
    logging.info(f"Backup created: {backup_dir}")

def daemon_loop(config):
    # Планируем резервное копирование каждую минуту
    schedule.every().minute.do(backup, config)

    while True:
        if is_running:
            schedule.run_pending()
        time.sleep(1)

def pause_handler(signum, frame):
    global is_running
    is_running = False
    logging.info("Daemon paused.")

def continue_handler(signum, frame):
    global is_running
    is_running = True
    logging.info("Daemon continued.")

def terminate_handler(signum, frame):
    logging.info("Daemon terminated.")
    sys.exit(0)

def status_handler(signum, frame):
    if is_running:
        logging.info("Daemon is running.")
    else:
        logging.info("Daemon is paused.")

def setup_signal_handlers():
    signal.signal(signal.SIGTSTP, pause_handler)
    signal.signal(signal.SIGCONT, continue_handler)
    signal.signal(signal.SIGTERM, terminate_handler)
    signal.signal(signal.SIGUSR1, status_handler)

def main():
    config = load_config()
    logging.basicConfig(filename=config['log_file'], level=logging.INFO)

    setup_signal_handlers()

    with DaemonContext():
        daemon_loop(config)

if __name__ == "__main__":
    main()
