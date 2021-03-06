from flask import Flask, render_template, jsonify, g, request, Response
from trash import config, history, sms
import json

app = Flask(__name__)
app.debug = True

@app.route('/')
def map():
    return render_template(
        'map.html',
        mapbox_id=config.MAPBOX_ID,
        mapbox_token=config.MAPBOX_TOKEN
    )

@app.route('/graph/<name>')
def sensor_graph(name):
    return render_template(
        'graph.html',
        name=name
    )

@app.route('/history/<name>')
def sensor_history(name):
    db = get_db()
    c = db.get(name)
    fields = request.args.get('fields', 'distance,temperature').split(',')
    data = []

    def convert(reading, field):
        if field not in reading:
            return ''
        v = reading[field]
        if field == 'distance':
            return 100.0 * (50.0 - v) / 50.0
        if field == 'temperature':
            return 1.8 * v + 32
        if field == 'moisture':
            return v * 100
        return v

    for time, reading in c:
        reading = json.loads(reading)
        data.insert(0, ', '.join(
            [time.strftime("%Y/%m/%d %H:%M:%S")] +
            [str(convert(reading, f)) for f in fields]
        ))
    headers = {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Expires': '-1'
    }
    return Response('\n'.join(data), mimetype='text/csv', headers=headers)

@app.route('/trashcans')
def sensors():
    def to_percent(maximum, distance):
        if distance is None:
            return None
        return '{0:.0f}'.format(100 * (maximum - distance) / maximum)
    data = []
    db = get_db()
    for (name, display_name, lat, lon, maximum, units) in db.list():
        #row = db.get(name).fetchone()
        #distance = None if row is None else json.loads(row[1]).get('distance')
        data.append({
            'name': name,
            'display': display_name,
            'lat': lat,
            'lon': lon,
            'max_distance': maximum,
            'units': units
            #'distance': distance,
            #'percent': to_percent(maximum, distance)
        })
    return jsonify({'trashcans': data})

@app.route('/sim')
def simulator():
    db = get_db()
    return render_template(
        'simulator.html',
        trashcans=[t[0] for t in db.list()]
    )

@app.route('/sensor', methods=['POST'])
def add_reading():
    db = get_db()
    form = request.form
    if not db.add(form['name'], form['value'], mac=form.get('mac')):
        return '', 403

    form_json = json.loads(form['value'])
    first = form_json.get('first')
    if first:
        sms.send('Hello, I am a trashcan!')
    distance = form_json.get('distance')
    if distance is not None and db.should_alert(form['name'], distance):
        sms.send('The trashcan is full!'.format(form['name']))

    return '', 204

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = history.TrashDB()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    app.run()
