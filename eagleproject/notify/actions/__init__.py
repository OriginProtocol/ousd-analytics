from core.common import Severity
from notify.actions.objects import SEVERITY_COLOR, Email, DiscordWebhook


def create_all_actions(*args, **kwargs):
    """ Create actions for all notification paths """
    return (Email(*args, **kwargs), DiscordWebhook(*args, **kwargs))


def create_webhook_actions(*args, **kwargs):
    """ Create actions for all notification paths """
    return (DiscordWebhook(*args, **kwargs), )


def create_actions_from_events(events):
    """ Create actions from events """
    actions = []
    email_events = []
    highest_severity = Severity.LOW

    for ev in events:
        # Only E-mail above normal events
        # TODO: Make this configurable?
        if ev.severity > Severity.NORMAL:
            email_events.append(ev)

        # Everything goes to the webhook
        actions.append(DiscordWebhook(
            summary=ev.title,
            details=ev.details,
            color=SEVERITY_COLOR[ev.severity],
        ))

        if ev.severity > highest_severity:
            highest_severity = ev.severity

    if email_events:
        summary = '[{}] {}'.format(highest_severity, 'OUSD Alerts')
        details = '{}\n'.join([
            '{} [{}] {}'.format(ev.stamp, ev.severity.name, ev.details)
            for ev in email_events
        ])
        actions.append(Email(summary=summary, details=details))

    return actions


def execute_all_actions(actions):
    """ Execute all of the given actions """
    for act in actions:
        act.execute()
