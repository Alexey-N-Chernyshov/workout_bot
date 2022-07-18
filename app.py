import telegram_bot
import schedule
import time
import threading

def scheduler():
    schedule.every().day.at("03:00").do(telegram_bot.update_workout_library)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    scheduleThread = threading.Thread(target=scheduler)
    scheduleThread.daemon = True
    scheduleThread.start()

    telegram_bot.start_bot()
