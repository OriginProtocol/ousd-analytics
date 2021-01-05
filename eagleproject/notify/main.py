from datetime import timedelta

from notify.actions import execute_all_actions, create_actions_from_events
from notify.events import seen_filter
from notify.triggers import run_all_triggers

EVENT_DUPE_WINDOW_SECONDS = timedelta(seconds=3600)  # 1hr


def run_all():
    events = run_all_triggers()
    events = seen_filter(events, since=EVENT_DUPE_WINDOW_SECONDS)
    actions = create_actions_from_events(events)
    execute_all_actions(actions)
