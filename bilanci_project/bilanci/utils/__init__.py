from _csv import register_dialect, QUOTE_ALL
import csv
import codecs
import cStringIO
import math


def nearly_equal(a, b, threshold=1):
    """
    Return true if the numbers are equals or close matches
    """
    return (a==b or math.fabs(a-b) <= threshold)


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    encoding = None
    def __init__(self, f, encoding="utf-8"):
        self.encoding=encoding
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode(self.encoding)

class UnicodeDictReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """
    encoding = None

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.encoding=encoding
        self.reader = csv.DictReader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return dict((k, unicode(s, self.encoding)) for k, s in row.iteritems() if s is not None)

    def __iter__(self):
        return self


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """
    encoding = None

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.encoding=encoding
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()

        return (unicode(s, self.encoding) for s in row if s is not None)

    def __iter__(self):
        return self


class UnicodeDictWriter(object):
    def __init__(self, f, fieldnames, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.DictWriter(self.queue, fieldnames, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()
        self.writer.writeheader()

    def writerow(self, D):
        self.writer.writerow(
            dict(
                [
                    (k,v.encode("utf-8")) for k,v in D.items()]))
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for D in rows:
            self.writerow(D)


class excel_semicolon(csv.excel):
    """Extends excel Dialect in order to set semicolon as delimiter."""
    delimiter = ';'
    quoting = QUOTE_ALL

register_dialect("excel_semicolon", excel_semicolon)

class excel_quote_all(csv.excel):
    """Extends excel Dialect in order to set semicolon as delimiter."""
    delimiter = ','
    quotechar = '"'
    quoting = QUOTE_ALL

register_dialect("excel_quote_all", excel_semicolon)


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

