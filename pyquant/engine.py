' models definition '

__author__ = 'Michael Liao'

import time
import threading
from queue import Queue, Empty

from pyquant import model

class Event(object):
    def __init__(self):
        pass

class TimerEvent(Event):
    '''
    Timer event
    '''
    def __init__(self, name):
        self.name = name

class TickEvent(Event):
    '''
    Tick event
    '''

class TradeEvent(Event):
    '''
    Trade event
    '''
    pass

class OrderEvent(Event):
    pass

class Handler(object):

    def accept(self, evt):
        return True

    def process(self, evt):
        '''
        Process this event. return True to continue process the event,
        or False stop future processing.
        '''
        print('process event %s...' % evt)
        return True

class DataEngine(object):
    '''
    Data engine that can query, store, update data.
    '''
    def __init__(self, vendors):
        self._vendors = vendors

    def query(self, symbol, fromTime, endTime):
        pass

class EventEngine(object):

    def __init__(self):
        self._queue = Queue()
        self._handlers = []
        self._running = False
        self._timers = []

    def add_timer(self, name, interval):
        t = RepeatedTimer(interval, lambda: self.put_event(TimerEvent(name)))
        self._timers.append(t)

    def add_handler(self, handler):
        self._handlers.append(handler)

    def put_event(self, evt):
        assert isinstance(evt, Event)
        self._queue.put(evt)

    def start(self):
        '''
        Start new thread to process event in the engine.
        '''
        self._running = True
        t = threading.Thread(target=self._run, name='EngineThread')
        t.start()
        for timer in self._timers:
            timer.start()

    def stop(self):
        print('stopping engine...')
        for timer in self._timers:
            timer.stop()
        self._running = False

    def _handle(self, evt):
        for handler in self._handlers:
            if handler.accept(evt):
                if not handler.process(evt):
                    break

    def _run(self):
        print('start engine in %s...' % threading.current_thread().name)
        while self._running:
            try:
                evt = self._queue.get(timeout=1)
                self._handle(evt)
            except Empty:
                pass
        print('engine stopped.')

class RepeatedTimer:
    def __init__(self, interval, func):
        self._interval = interval
        self._function = func
        self._event = threading.Event()
        self._thread = threading.Thread(target=self._target)

    def start(self):
        self._start = time.time()
        self._thread.start()

    def _target(self):
        while not self._event.wait(self._time):
            self._function()

    @property
    def _time(self):
        return self._interval - ((time.time() - self._start) % self._interval)

    def stop(self):
        self._event.set()
        self._thread.join()

if __name__ == '__main__':
    engine = EventEngine()
    engine.add_handler(Handler())
    engine.add_timer('1s', 0.2)
    engine.start()
    time.sleep(1)
    engine.put_event(Event())
    time.sleep(1)
    engine.put_event(Event())
    time.sleep(1)
    engine.put_event(Event())
    engine.put_event(Event())
    engine.put_event(Event())
    time.sleep(1)
    engine.put_event(Event())
    engine.put_event(Event())
    engine.stop()
