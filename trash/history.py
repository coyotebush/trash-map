import sqlite3
import os
import hmac
import hashlib
import binascii

DATABASE = os.path.join(os.path.dirname(__file__), '..', 'trash.db')

class TrashDB:

    def __init__(self):
        self.conn = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_COLNAMES)

    def close(self):
        self.conn.close()

    def initialize(self):
        """ Initialize the database schema """
        db = self.conn
        with open('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


    def add(self, name, value, mac=None):
        """ Add a reading for a named sensor """
        c = self.conn.cursor()
        c.execute("insert or ignore into sensor (name) values (?)", (name,))
        self.conn.commit()
        c.execute("select id, key from sensor where name=?", (name,))
        (sensor_id, key) = c.fetchone()
        if key is not None:
            if mac is None:
                return False
            key = binascii.unhexlify(key)
            mac = binascii.unhexlify(mac)
            correct_mac = hmac.new(key, str(value), hashlib.sha1)
            correct_mac = correct_mac.digest()
            print str(value), binascii.hexlify(correct_mac), binascii.hexlify(mac)
            if not hmac.compare_digest(correct_mac, mac):
                return False
        c.execute(
            "update sensor set value_max=? " +
            "where id=? and value_max is null or value_max < ?",
            (value, sensor_id, value)
        )
        c.execute(
            "insert into reading (sensor_id, value, time) " +
            "values (?, ?, datetime('now', 'localtime'))",
            (sensor_id, value)
        )
        self.conn.commit()
        return True

    def list(self):
        """ Return an iterable of (name, lat, lon, max, units) for sensors """
        return self.conn.cursor().execute(
            "select name, latitude, longitude, value_max, value_units " +
            "from sensor order by name"
        )

    def get(self, name):
        """ Return an iterable of (time, value) tuples for a sensor """
        return self.conn.cursor().execute(
            "select time as \"[timestamp]\", value from sensor, reading " +
            "where sensor_id = sensor.id and name=? order by time desc",
            (name,)
        )
