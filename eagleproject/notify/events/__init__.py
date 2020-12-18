from datetime import datetime
from core.common import Severity


class Event:
    """ An event worthy of an action """
    def __init__(self, title, details, severity=Severity.NORMAL,
                 stamp=datetime.now()):
        self.severity = severity or Severity.NORMAL
        self.title = title
        self.details = details
        self.stamp = stamp

    def __str__(self):
        return "{} [{}] {}: {}".format(
            self.stamp,
            self.severity.name,
            self.title,
            self.details
        )


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
