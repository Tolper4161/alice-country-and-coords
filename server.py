from flask import Flask, request, jsonify
import logging
import json
from geo import get_country, get_distance, get_coordinates

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, filename='app.log', format='%(asctime)s %(levelname)s %(name)s %(message)s')


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Request: %r', response)
    return jsonify(response)


def get_geo_info(city_name, type_info):
    if type_info == 'country':
        return get_country(city_name[0])
    if type_info == 'coordinates':
        city_info = (get_coordinates(city_name[0]), get_coordinates(city_name[1]))
        return get_distance(city_info[0], city_info[1])


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = 'Привет! Я могу показать город или сказать расстояние между городами!'
        return
    cities = get_cities(req)
    if not cities:
        res['response']['text'] = 'Ты не написал название ни одного города!'
    elif len(cities) == 1:
        res['response']['text'] = 'Этот город в стране - ' + get_geo_info(cities, 'country')
    elif len(cities) == 2:
        distance = get_geo_info(cities, 'coordinates')
        res['response']['text'] = 'Расстояние между этими городами: ' + str(round(distance)) + ' км.'
    else:
        res['response']['text'] = 'Слишком много городов!'


def get_cities(req):
    cities = []
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            if 'city' in entity['value']:
                cities.append(entity['value']['city'])
    return cities


if __name__ == '__main__':
    app.run()
