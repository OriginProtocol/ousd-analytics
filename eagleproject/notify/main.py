from notify.actions import execute_all_actions, create_actions_from_events
from notify.triggers import run_all_triggers


def run_all():
    events = run_all_triggers()
    actions = create_actions_from_events(events)
    execute_all_actions(actions)
