#!/usr/bin/env python

import logging
l = logging.getLogger("simuvex.plugins.log")

from .plugin import SimStatePlugin

import sys
import itertools

event_id_count = itertools.count()

class SimEvent(SimStatePlugin):
    #def __init__(self, address=None, stmt_idx=None, message=None, exception=None, traceback=None):
    def __init__(self, state, event_id, event_type, **kwargs):
        SimStatePlugin.__init__(self)
        self.id = event_id
        self.type = event_type
        self.bbl_addr = state.bbl_addr
        self.stmt_idx = state.stmt_idx
        self.kwargs = kwargs

    def __repr__(self):
        return "<SimEvent %s %d, with fields %s>" % (self.type, self.id, self.kwargs.keys())

class SimStateLog(SimStatePlugin):
    def __init__(self, old_events=None):
        SimStatePlugin.__init__(self)
        self.new_events = [ ]
        self.old_events = [ ] if old_events is None else old_events

    def add_event(self, event_type, **kwargs):
        try:
            e_id = event_id_count.next()
            new_event = SimEvent(self.state, e_id, event_type, **kwargs)
            self.new_events.append(new_event)
        except TypeError:
            e_type, value, traceback = sys.exc_info()
            raise SimEventError, ("Exception when logging event:", e_type, value), traceback

    def events_of_type(self, event_type):
        return [ e for e in itertools.chain(self.new_events, self.old_events) if e.type == event_type ]

    def copy(self):
        return SimStateLog(old_events=self.old_events + self.new_events)

    def merge(self, others, flag, flag_values): #pylint:disable=unused-argument
        all_events = [ e.old_events + e.new_events for e in itertools.chain([self], others) ]
        self.new_events = [ ]
        self.old_events = [ SimEvent(self.state, event_id_count.next(), 'merge', event_lists=all_events) ]
        return False, [ ]

from ..s_errors import SimEventError
SimStateLog.register_default('log', SimStateLog)
