import sqlite3

DATABASE = 'trash.db'

class TrashDB:

    def __init__(self):
        self.conn = sqlite3.connect(DATABASE)

    def close(self):
        self.conn.close()

    def initialize(self):
        """ Initialize the database schema """
        db = self.conn
        with open('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


    def add(self, name, value):
        """ Add a reading for a named sensor """
        c = self.conn.cursor()
        c.execute("insert or ignore into sensor (name) values (?)", (name,))
        c.execute("select id from sensor where name=?", (name,))
        (sensor_id,) = c.fetchone()
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

    def list(self):
        """ Return an iterable of (name, lat, lon, max, units) for sensors """
        return self.conn.cursor().execute(
            "select name, latitude, longitude, value_max, value_units " +
            "from sensor order by name"
        )

    def get(self, name):
        """ Return an iterable of (time, value) tuples for a sensor """
        return self.conn.cursor().execute(
            "select time, value from sensor, reading " +
            "where sensor_id = sensor.id and name=? order by time desc",
            (name,)
        )

