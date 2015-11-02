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
    for time, value in c:
        value = json.loads(value)
        data.insert(0, ', '.join(
            [time.strftime("%Y/%m/%d %H:%M:%S")] +
            [str(value.get(f, '')) for f in fields]
        ))
    return Response('\n'.join(data), mimetype='text/csv')

@app.route('/trashcans')
def sensors():
    def to_percent(maximum, distance):
        if distance is None:
            return None
        return '{0:.0f}'.format(100 * (maximum - distance) / maximum)
    data = []
    db = get_db()
    for (name, lat, lon, maximum, units) in db.list():
        row = db.get(name).fetchone()
        distance = None if row is None else json.loads(row[1]).get('distance')
        data.append({
            'name': name,
            'lat': lat,
            'lon': lon,
            'max_distance': maximum,
            'units': units,
            'distance': distance,
            'percent': to_percent(maximum, distance)
        })
    return jsonify({'trashcans': data})

@app.route('/sensor', methods=['POST'])
def add_reading():
    db = get_db()
    form = request.form
    if not db.add(form['name'], form['value'], mac=form.get('mac')):
        return '', 403

    form_json = json.loads(form['value'])
    first = form_json.get('first')
    if first:
        sms.send('hello, I am a trashcan!')
    distance = form_json.get('distance')
    if distance is not None and db.should_alert(form['name'], distance):
        sms.send('the trashcan "{}" is full!'.format(form['name']))

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
