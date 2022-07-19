import telegram_bot
import schedule
import time
import threading
import os.path


def scheduler():
    schedule.every().day.at("03:00").do(telegram_bot.update_workout_library)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    # print version
    version_file = 'git_commit_version.txt'
    if os.path.isfile(version_file):
        with open(version_file) as f:
            version = f.readline().strip()
            print('workout_bot ' + version)

    scheduleThread = threading.Thread(target=scheduler)
    scheduleThread.daemon = True
    scheduleThread.start()

    telegram_bot.start_bot()
