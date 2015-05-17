import requests
import config

fake_data = [
    {'lat': 35.27876, 'lon': -120.65777, 'distance': 100, 'name': 'Mitchell'},
    {'lat': 35.28037, 'lon': -120.66333, 'distance': 100, 'name': 'Mission'},
    {'lat': 35.26796, 'lon': -120.64693, 'distance': 100, 'name': 'Sinsheimer'},
    {'lat': 35.26879, 'lon': -120.65926, 'distance': 100, 'name': 'Meadow'},
    {'lat': 35.26301, 'lon': -120.68394, 'distance': 100, 'name': 'Laguna'},
    {'lat': 35.28997, 'lon': -120.66535, 'distance': 100, 'name': 'Santa Rosa'}
]

def get_resources(server, auth, domain, wanted):
    endpoints = []
    url = '{}/{}/endpoints'.format(server, domain)
    for e in (e['name'] for e in requests.get(url, auth=auth).json()):
        endpoint = {'name': e}
        endpoints.append(endpoint)
        url = '{}/{}/endpoints/{}'.format(server, domain, e)
        for r in (r['uri'] for r in requests.get(url, auth=auth).json()
                  if r['uri'] in wanted):
            url = '{}/{}/endpoints/{}{}?sync=true'.format(server, domain, e, r)
            endpoint[wanted[r]] = requests.get(url, auth=auth).text

    return endpoints

def trashcans():
    server = config.DEVICE_SERVER
    domain = config.DEVICE_SERVER_DOMAIN
    auth   = config.DEVICE_SERVER_AUTH 
    wanted = {
        '/6/0/0': 'lat',
        '/6/0/1': 'lon',
        '/3302/0/5600': 'distance'
    }

    return get_resources(server, auth, domain, wanted) + fake_data

