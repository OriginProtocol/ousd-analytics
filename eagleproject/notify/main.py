from notify.actions import execute_all_actions, create_actions_from_events
from notify.events import seen_filter
from notify.triggers import run_all_triggers

def run_all():
    events = run_all_triggers()
    events = seen_filter(events)
    actions = create_actions_from_events(events)
    execute_all_actions(actions)
