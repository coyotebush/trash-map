from flask import Flask, render_template, jsonify, g, request
from trash import device, config, history, sms
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
def graph(name):
    db = get_db()
    c = db.get(name)
    data = []
    for time, value in c:
        value = json.loads(value)
        data.insert(0, '[ new Date("{}"), {}, {} ]'.format(
            time.strftime("%Y/%m/%d %H:%M:%S"),
            value.get('distance', 'null'),
            value.get('temperature', 'null')
        ))
    return render_template(
        'graph.html',
        data="[\n" + ",\n".join(data) + "\n]"
    )

@app.route('/trashcans')
def trashcans():
    data = device.fake_data[:]
    db = get_db()
    for (name, lat, lon, maximum, units) in db.list():
        distance = json.loads(db.get(name).fetchone()[1])['distance']
        print distance
        data.append({
            'name': name,
            'lat': lat,
            'lon': lon,
            'max_distance': maximum,
            'units': units,
            'distance': distance,
            'percent': '{0:.0f}'.format(100 * (maximum - distance) / maximum)
        })
    return jsonify({'trashcans': data})

@app.route('/sensor', methods=['POST'])
def add_reading():
    db = get_db()
    form = request.form
    if not db.add(form['name'], form['value'], mac=form.get('mac')):
        return '', 403
    distance = json.loads(form['value']).get('distance')
    if distance is not None and distance < 15:
        sms.send('"{}" is full!'.format(form['name']))
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
