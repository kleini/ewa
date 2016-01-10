import sched
from threading import Thread, Lock, Timer
import time


def run():
    while True:
        with lock:
            # print('Starting scheduler %s %s' % (scheduler.empty(), scheduler.run(blocking=False)))
            scheduler.run()
            # print('Scheduled? %s' % scheduler.empty())
    print('Thread ended')


def periodic(task, interval):
    run_next = time.time() + (interval / 1000)
    with lock:
        scheduler.enterabs(time=run_next, priority=1, action=schedule_next, argument=(task, run_next, interval))
        print('Scheduled task %10.4f' % run_next)


def schedule_next(task, previous, interval):
    run_next = previous + (interval / 1000)
    with lock:
        print('run scheduled periodic task')
        scheduler.enterabs(time=run_next, priority=1, action=schedule_next, argument=(task, run_next, interval))
        print('scheduled next and run finished')
    print('Starting task')
    task_thread = Thread(target=task.call())
    task_thread.start()
    task.call()

# TODO we need something to stop a task
# TODO try https://stackoverflow.com/questions/2398661/schedule-a-repeating-event-in-python-3

scheduler = sched.scheduler(timefunc=time.time)
print('%10.4f %10.4f' % (time.time(), scheduler.timefunc()))
scheduler.delayfunc(0.9)
print('%10.4f %10.4f' % (time.time(), scheduler.timefunc()))
lock = Lock()
t = Thread(target=run)
t.start()
print('Started thread %s' % t)
