from datetime import datetime, timedelta, timezone
from Crypto.Hash import SHA3_256

from core.common import Severity
from notify.models import EventSeen

EVENT_DUPE_WINDOW_SECONDS = timedelta(seconds=3600)  # 1hr

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

    if int(a._log_index) < int(b._log_index):
        return -1

    if int(a._log_index) > int(b._log_index):
        return 1

    return 0


class Event:
    """ An event worthy of an action """
    def __init__(self, title, details, severity=Severity.NORMAL,
                 stamp=datetime.utcnow(), tags=['default'], block_number=0,
                 transaction_index=0, log_index=0, deduplicate_time_window=EVENT_DUPE_WINDOW_SECONDS):
        
        assert isinstance(deduplicate_time_window, timedelta), "since is not a timedelta object"

        self._severity = severity or Severity.NORMAL
        self._title = title
        self._details = details
        self._stamp = stamp
        self._tags = tags
        self._block_number = block_number
        self._transaction_index = transaction_index
        self._log_index = log_index
        self.vague_hash = False
        self.deduplicate_time_window = deduplicate_time_window

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
        if not self.vague_hash:
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
                   block_number=0, transaction_index=0, log_index=0,
                   log_model=None, deduplicate_time_window=EVENT_DUPE_WINDOW_SECONDS):
    """ Create a critical severity event """

    if log_model is not None:
        block_number = log_model.block_number
        transaction_index = log_model.transaction_index
        log_index = log_model.log_index

    return Event(
        title,
        details,
        stamp=stamp,
        severity=Severity.CRITICAL,
        tags=tags,
        block_number=block_number,
        transaction_index=transaction_index,
        log_index=log_index,
        deduplicate_time_window=deduplicate_time_window,
    )


def event_high(title, details, stamp=datetime.utcnow(), tags=None,
               block_number=0, transaction_index=0, log_index=0,
               log_model=None, deduplicate_time_window=EVENT_DUPE_WINDOW_SECONDS):
    """ Create a high severity event """

    if log_model is not None:
        block_number = log_model.block_number
        transaction_index = log_model.transaction_index
        log_index = log_model.log_index

    return Event(
        title,
        details,
        stamp=stamp,
        severity=Severity.HIGH,
        tags=tags,
        block_number=block_number,
        transaction_index=transaction_index,
        log_index=log_index,
        deduplicate_time_window=deduplicate_time_window,
    )


def event_normal(title, details, stamp=datetime.utcnow(), tags=None,
                 block_number=0, transaction_index=0, log_index=0,
                 log_model=None, deduplicate_time_window=EVENT_DUPE_WINDOW_SECONDS):
    """ Create a normal severity event """

    if log_model is not None:
        block_number = log_model.block_number
        transaction_index = log_model.transaction_index
        log_index = log_model.log_index

    return Event(
        title,
        details,
        stamp=stamp,
        severity=Severity.NORMAL,
        tags=tags,
        block_number=block_number,
        transaction_index=transaction_index,
        log_index=log_index,
        deduplicate_time_window=deduplicate_time_window,
    )


def event_low(title, details, stamp=datetime.utcnow(), tags=None,
              block_number=0, transaction_index=0, log_index=0,
              log_model=None, deduplicate_time_window=EVENT_DUPE_WINDOW_SECONDS):
    """ Create a low severity event """

    if log_model is not None:
        block_number = log_model.block_number
        transaction_index = log_model.transaction_index
        log_index = log_model.log_index

    return Event(
        title,
        details,
        stamp=stamp,
        severity=Severity.LOW,
        tags=tags,
        block_number=block_number,
        transaction_index=transaction_index,
        log_index=log_index,
        deduplicate_time_window=deduplicate_time_window,
    )


def seen_filter(events):
    """ Filter out any events seen since `event.deduplicate_time_window` and 
    add newly discovered hashes to the DB """
    filtered = []
    events_parsed = []

    for ev in events:
        event_hash = ev.hash()

        # Deduplicate unprocessed events
        if event_hash in events_parsed:
            continue

        events_parsed.append(event_hash)

        try:
            _, created = EventSeen.objects.get_or_create(
                event_hash=event_hash,
                last_seen__gt=datetime.now(tz=timezone.utc) - ev.deduplicate_time_window,
                defaults={
                    'event_hash': event_hash,
                    'last_seen': datetime.now(tz=timezone.utc)
                }
            )

            if not created:
                # Do not send duplicate alert within the defined time window
                continue

        except:
            print("Failed to apply seen filter")

        filtered.append(ev)

    return filtered
