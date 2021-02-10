import json
import requests
from time import sleep
from django.conf import settings
from django.core.mail import send_mail
from core.common import Severity, first, truncate_elipsis
from core.logging import get_logger

log = get_logger(__name__)

SEVERITY_COLOR = {
    Severity.CRITICAL: int('FF0000', 16),
    Severity.HIGH: int('FF981A', 16),
    Severity.NORMAL: int('1A82FF', 16),
    Severity.LOW: int('1AFF8A', 16),
}
TAG_WEBHOOK_OVERRIDE = {
    'ogn': settings.OGN_DISCORD_WEBHOOK_URL
}


class Action:
    """ An action to perform """
    def __init__(self, summary, details, severity=Severity.NORMAL):
        self.summary = summary
        self.details = details

    def execute(self):
        raise NotImplementedError("execute() must be implemented")


class Email(Action):
    def _is_configured(self):
        return (
            settings.DEFAULT_FROM_EMAIL is not None
            and settings.ADMINS is not None
        )

    def execute(self):
        if self._is_configured():
            send_mail(
                self.summary,
                self.details,
                settings.DEFAULT_FROM_EMAIL,
                [a[1] for a in settings.ADMINS + settings.MANAGERS],
                fail_silently=False,  # TODO: Maybe this should be silent?
            )

        else:
            # If we're not configured, don't die, but don't be silent
            log.warning('E-mail not configured')


class DiscordWebhook(Action):
    def __init__(self, summary, details, severity=Severity.NORMAL,
                 color=SEVERITY_COLOR[Severity.NORMAL], tags=None):
        super().__init__(summary, details, severity)
        self.color = color
        self.severity = severity
        self.tags = tags

    def _is_configured(self):
        return settings.DISCORD_WEBHOOK_URL is not None

    def execute(self):

        if self._is_configured():
            url = settings.DISCORD_WEBHOOK_URL

            # Look for an override
            if (
                self.tags
                and any([tag in TAG_WEBHOOK_OVERRIDE for tag in self.tags])
            ):
                tag_match = first(
                    self.tags,
                    lambda t: t in TAG_WEBHOOK_OVERRIDE
                )
                url = TAG_WEBHOOK_OVERRIDE[tag_match]

            payload = {
                "username": settings.DISCORD_BOT_NAME or "analyticsbot",
                "avatar_url": "https://i.stack.imgur.com/RUxfR.jpg",
                "embeds": [
                    {
                        "title": self.summary,
                        "description": truncate_elipsis(self.details),
                        "color": self.color,
                    }
                ]
            }

            if self.severity > Severity.NORMAL and settings.DISCORD_WEBHOOK_AT:
                ats = settings.DISCORD_WEBHOOK_AT.split(',')
                payload["content"] = " ".join(
                    ["<@{}>".format(at) for at in ats]
                )

            # Retry request in specific cases
            while True:
                r = requests.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(payload)
                )

                if r.status_code == 429:
                    response = r.json()
                    # TODO: Maybe these should be queued up somewhere instead
                    # of sleeping for indeterminate amounts of time. Terrible.
                    retry_after = response.get('retry_after', 0)

                    # These long ones might be duplicate messages during my
                    # testing and may not show up IRL
                    if retry_after > 30:
                        log.error(
                            'Discord rate limit wait of {}sec is too long!  '
                            'Skipping. ({})'.format(
                                retry_after,
                                self.summary,
                            )
                        )
                        break

                    log.warning(
                        'Discord rate limited us.  Retrying in {} seconds '
                        '(global: {})'.format(
                            retry_after,
                            response.get('global', False),
                        )
                    )

                    sleep(retry_after)
                    continue

                elif r.status_code in [200, 204]:
                    break

                else:
                    log.error(
                        'Error executing webhook ({}): {}'.format(
                            r.status_code,
                            r.text
                        )
                    )
                    break

        else:
            # If we're not configured, don't die, but don't be silent
            log.info('Discord webhook is not configured')
