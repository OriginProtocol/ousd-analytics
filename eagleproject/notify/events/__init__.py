from datetime import datetime, timedelta
from Crypto.Hash import SHA3_256

from core.common import Severity
from notify.models import EventSeen


def event_order_comp(a, b) -> int:
    """ Compare to Events for ordering """

    if a._block_number < b._block_number:
        return -1

    if a._block_number > b._block_number:
        return 1

    if a._transaction_index < b._transaction_index:
        return -1

    if a._transaction_index > b._transaction_index:
        return 1

    if a._log_index < b._log_index:
        return -1

    if a._log_index > b._log_index:
        return 1

    return 0


class Event:
    """ An event worthy of an action """
    def __init__(self, title, details, severity=Severity.NORMAL,
                 stamp=datetime.utcnow(), tags=['default'], block_number=0,
                 transaction_index=0, log_index=0):
        self._severity = severity or Severity.NORMAL
        self._title = title
        self._details = details
        self._stamp = stamp
        self._tags = tags
        self._block_number = block_number
        self._transaction_index = transaction_index
        self._log_index = log_index

    def __str__(self):
        return "{} [{}] {}: {}".format(
            self.stamp,
            self.severity.name,
            self.title,
            self.details
        )

    def __eq__(self, other):
        """ Used for deduping equality, not ordering.  """
        return hash(self) == hash(other)

    def __ne__(self, other):
        """ Used for deduping equality, not ordering.  """
        return hash(self) != hash(other)

    def __hash__(self):
        return int(self.hash(), 16)

    def __lt__(self, other):
        return event_order_comp(self, other) < 0

    def __gt__(self, other):
        return event_order_comp(self, other) > 0

    def __le__(self, other):
        return event_order_comp(self, other) <= 0

    def __ge__(self, other):
        return event_order_comp(self, other) >= 0

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

    @property
    def tags(self):
        return self._tags


def event_critical(title, details, stamp=datetime.utcnow(), tags=None,
                   block_number=0, transaction_index=0, log_index=0):
    """ Create a critical severity event """
    return Event(
        title,
        details,
        stamp=stamp,
        severity=Severity.CRITICAL,
        tags=tags,
        block_number=block_number,
        transaction_index=transaction_index,
        log_index=log_index,
    )


def event_high(title, details, stamp=datetime.utcnow(), tags=None,
               block_number=0, transaction_index=0, log_index=0):
    """ Create a high severity event """
    return Event(
        title,
        details,
        stamp=stamp,
        severity=Severity.HIGH,
        tags=tags,
        block_number=block_number,
        transaction_index=transaction_index,
        log_index=log_index,
    )


def event_normal(title, details, stamp=datetime.utcnow(), tags=None,
                 block_number=0, transaction_index=0, log_index=0):
    """ Create a normal severity event """
    return Event(
        title,
        details,
        stamp=stamp,
        severity=Severity.NORMAL,
        tags=tags,
        block_number=block_number,
        transaction_index=transaction_index,
        log_index=log_index,
    )


def event_low(title, details, stamp=datetime.utcnow(), tags=None,
              block_number=0, transaction_index=0, log_index=0):
    """ Create a low severity event """
    return Event(
        title,
        details,
        stamp=stamp,
        severity=Severity.LOW,
        tags=tags,
        block_number=block_number,
        transaction_index=transaction_index,
        log_index=log_index,
    )


def seen_filter(events, since):
    """ Filter out any events seen since `since` and add newly discovered hashes
    to the DB """
    assert isinstance(since, timedelta), "since is not a timedelta object"

    hashes_since = [
        x.event_hash
        for x in EventSeen.objects.filter(
            last_seen__gt=datetime.utcnow() - since
        ).only('event_hash')
    ]

    filtered = []

    for ev in events:
        if ev.hash() not in hashes_since:
            filtered.append(ev)

            EventSeen.objects.update_or_create(event_hash=ev.hash(), defaults={
                'last_seen': datetime.utcnow()
            })

    return filtered
