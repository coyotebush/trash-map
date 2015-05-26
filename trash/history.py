import sqlite3
import os
import hmac

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


    def add(self, name, mac, value):
        """ Add a reading for a named sensor """
        c = self.conn.cursor()
        c.execute("insert or ignore into sensor (name) values (?)", (name,))
        self.conn.commit()
        c.execute("select id, key from sensor where name=?", (name,))
        (sensor_id, key) = c.fetchone()
        if key is not None:
            correct_mac = hmac.new(str(key), str(value)).digest()
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

