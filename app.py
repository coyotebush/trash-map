from flask import Flask, render_template, jsonify, g
from trash import device, config, history

app = Flask(__name__)
app.debug = True

@app.route('/')
def map():
    return render_template(
        'map.html',
        mapbox_id=config.MAPBOX_ID,
        mapbox_token=config.MAPBOX_TOKEN
    )

@app.route('/trashcans')
def trashcans():
    data = []
    db = get_db()
    for (name, lat, lon, maximum, units) in db.list():
        distance = db.get(name).fetchone()[1]
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
