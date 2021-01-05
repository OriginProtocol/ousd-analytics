from datetime import datetime, timedelta
from Crypto.Hash import SHA3_256

from core.common import Severity
from notify.models import EventSeen


class Event:
    """ An event worthy of an action """
    def __init__(self, title, details, severity=Severity.NORMAL,
                 stamp=datetime.now()):
        self._severity = severity or Severity.NORMAL
        self._title = title
        self._details = details
        self._stamp = stamp

    def __str__(self):
        return "{} [{}] {}: {}".format(
            self.stamp,
            self.severity.name,
            self.title,
            self.details
        )

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __ne__(self, other):
        return hash(self) != hash(other)

    def __hash__(self):
        return int(self.hash(), 16)

    def hash(self):
        """ Return a unique hash for this event, excluding timestamp """
        h = SHA3_256.new()
        h.update(self._severity.value.to_bytes(1, byteorder='big'))
        h.update(self.title.encode('utf-8'))
        h.update(self._details.encode('utf-8'))
        return h.hexdigest()

    """ Props are intentionally read-only to make this object immutable """

    @property
    def severity(self):
        return self._severity

    @property
    def title(self):
        return self._title

    @property
    def details(self):
        return self._details

    @property
    def stamp(self):
        return self._stamp


def event_critical(title, details, stamp=datetime.now()):
    """ Create a critical severity event """
    return Event(title, details, stamp=stamp, severity=Severity.CRITICAL)


def event_high(title, details, stamp=datetime.now()):
    """ Create a high severity event """
    return Event(title, details, stamp=stamp, severity=Severity.HIGH)


def event_normal(title, details, stamp=datetime.now()):
    """ Create a normal severity event """
    return Event(title, details, stamp=stamp, severity=Severity.NORMAL)


def event_low(title, details, stamp=datetime.now()):
    """ Create a low severity event """
    return Event(title, details, stamp=stamp, severity=Severity.LOW)


def seen_filter(events, since):
    """ Filter out any events seen since `since` and add newly discovered hashes
    to the DB """
    assert isinstance(since, timedelta), "since is not a timedelta object"

    hashes_since = [
        x.event_hash
        for x in EventSeen.objects.filter(
            last_seen__gt=datetime.now() - since
        ).only('event_hash')
    ]

    filtered = []

    for ev in events:
        if ev.hash() not in hashes_since:
            filtered.append(ev)

            EventSeen.objects.update_or_create(event_hash=ev.hash(), defaults={
                'last_seen': datetime.now()
            })

    return filtered
