import psycopg2
import psycopg2.extras
import io
import sys


class IteratorFile(io.TextIOBase):
    """ given an iterator which yields strings,
    return a file like object for reading those strings.
    Taken from https://gist.github.com/jsheedy/ed81cdf18190183b3b7d
    """

    def __init__(self, it, encoding='utf-8'):
        self._it = it
        self._f = io.StringIO()
        self.user_encoding = encoding

    def read(self, length=sys.maxsize):

        try:
            while self._f.tell() < length:
                self._f.write(
                    unicode(next(self._it), self.user_encoding).encode(self.user_encoding) + u"\n")

        except StopIteration as e:
            # soak up StopIteration. this block is not necessary because
            # of finally, but just to be explicit
            pass

        except Exception as e:
            print("uncaught exception: {}".format(e))

        finally:
            self._f.seek(0)
            data = self._f.read(length)

            # save the remainder for next read
            remainder = self._f.read()
            self._f.seek(0)
            self._f.truncate(0)
            self._f.write(remainder)
            return data

    def readline(self):
        return next(self._it)


class pg_connect():
    """
    Object for executing postgres queries
    """

    def __init__(self, database='gtc', user='ubuntu'):
        self.conn = psycopg2.connect(database=database, user='ubuntu')

    def close(self):
        self.conn.close()

    def query(self, sql):
        curs = self.conn.cursor()
        curs.execute(sql)
        results = curs.fetchall()
        curs.close()
        return results

    def query_dict(self, sql):
        curs = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        curs.execute(sql)
        results = curs.fetchall()
        curs.close()
        return results

    def load(self, tablename, data, encoding='utf-8'):
        try:
            curs = self.conn.cursor()
            table_width = len(data[0])
            template_string = "|".join(['{}'] * table_width)
            f = IteratorFile((template_string.format(*x)
                              for x in data), encoding=encoding)
            results = curs.copy_from(f, tablename, sep="|", null='None')
            curs.close()
            self.conn.commit()
            return results

        except Exception as s:
            print(s)
            raise

    def truncate(self, tablename):
        curs = self.conn.cursor()
        curs.execute("TRUNCATE TABLE %s" % tablename)
        curs.close()
        self.conn.commit()
        return
