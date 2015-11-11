create table sensor (
    id integer primary key,
    name text unique,
    display_name text,
    key text,
    latitude real,
    longitude real,
    value_max real,
    value_units text
);

create table reading (
    id integer primary key,
    sensor_id integer,
    time text,
    value real
);
