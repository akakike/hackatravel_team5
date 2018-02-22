import nltk
from geotext import GeoText
import dateparser

FILE_PATH = 'resources/destinations.csv'

def translate_human_request(request):
    print(request)
    tokens = nltk.word_tokenize(request)
    print(tokens)
    tags = nltk.pos_tag(tokens)
    print(tags)

    destinations_map = destinations_mapper()

    places = extract_places(tags, destinations_map)

    dates = extract_dates(tags)

    print(places)
    print(dates)


def extract_dates(tags):
    dates = []
    for tag in tags:
        if "NN" == tag[1]:
            date = dateparser.parse(tag[0])
            if date != None:
                dates.append(date)
    return dates


def destinations_mapper():
    destinations_map = {}
    destinations_file = open(FILE_PATH, 'r', encoding='UTF8')
    for row in destinations_file:
        destinations_array = row.split(',')
        destinations_map[destinations_array[1].replace("\n", "")] = destinations_array[0]
    destinations_file.close()
    return destinations_map


def extract_places(tags, destination_map):
    places = []
    for tag in tags:
        if "NN" == tag[1]:
            place = tag[0]
            cities = GeoText(place.upper()).cities
            if cities.__len__() > 0:
                for city in cities:
                    places.append(destination_map[city])
    return places


translate_human_request('hi bitches!')
translate_human_request("i'm in london tomorrow, anything interesting there?")