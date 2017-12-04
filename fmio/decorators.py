# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type
from fmio.redisinterface import conn

def one_at_time(function=None, key="", timeout=None, blocking=True,
                blocking_timeout=None, logger=None):
    """Enforce only one task at a time."""
    def _dec(run_func):
        """Decorator."""
        def _caller(*args, **kwargs):
            """Caller."""
            return_value = None
            have_lock = False
            lock = conn.lock(key, timeout=timeout)
            try:
                if logger:
                    logger.info('Trying to acquire {} lock.'.format(key))
                have_lock = lock.acquire(blocking=blocking,
                                         blocking_timeout=blocking_timeout)
                if have_lock:
                    if logger:
                        logger.info('Got {} lock.'.format(key))
                    return_value = run_func(*args, **kwargs)
                elif logger:
                    logger.info('Did not acquire lock. The {} is busy.'.format(key))
            finally:
                if have_lock:
                    lock.release()
            return return_value
        return _caller
    return _dec(function) if function is not None else _dec
