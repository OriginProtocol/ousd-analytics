import sys
import json
import requests
from time import sleep
from datetime import datetime
from django.conf import settings
from django.core.mail import send_mail
from core.common import Severity

SEVERITY_COLOR = {
    Severity.CRITICAL: int('FF0000', 16),
    Severity.HIGH: int('FF981A', 16),
    Severity.NORMAL: int('1A82FF', 16),
    Severity.LOW: int('1AFF8A', 16),
}


class Action:
    """ An action to perform """
    def __init__(self, summary, details):
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
            print('E-mail not configured', file=sys.stderr)


class DiscordWebhook(Action):
    def __init__(self, summary, details,
                 color=SEVERITY_COLOR[Severity.NORMAL]):
        super().__init__(summary, details)
        self.color = color

    def _is_configured(self):
        return settings.DISCORD_WEBHOOK_URL is not None

    def execute(self):

        if self._is_configured():
            payload = {
                "username": settings.DISCORD_BOT_NAME or "analyticsbot",
                "avatar_url": "https://i.stack.imgur.com/RUxfR.jpg",
                "embeds": [
                    {
                        "title": self.summary,
                        "description": self.details,
                        "color": self.color,
                    }
                ]
            }

            # Retry request in specific cases
            while True:
                r = requests.post(
                    settings.DISCORD_WEBHOOK_URL,
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
                        print(
                            'Discord rate limit wait of {}sec is too long!  '
                            'Skipping.'.format(
                                retry_after
                            )
                        )
                        break

                    print(
                        'Discord rate limited us.  Retrying in {} seconds '
                        '(global: {})'.format(
                            retry_after,
                            response.get('global', False),
                        ),
                        file=sys.stderr
                    )

                    sleep(retry_after)
                    continue

                elif r.status_code in [200, 204]:
                    break

                else:
                    print(
                        'Error executing webhook ({}): {}'.format(
                            r.status_code,
                            r.text
                        ),
                        file=sys.stderr
                    )
                    break

        else:
            # If we're not configured, don't die, but don't be silent
            print('Discord webhook is not configured', file=sys.stderr)
