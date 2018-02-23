import nltk
from geotext import GeoText
import dateparser

FILE_PATH = 'resources/destinations.csv'

def translate_human_request(request):
    tokens = nltk.word_tokenize(request)
    tags = nltk.pos_tag(tokens)

    destinations_map = destinations_mapper()

    places = extract_places(tags, destinations_map)

    dates = extract_dates(tags)

    return { 'places':places, 'dates': dates }


def extract_dates(tags):
    dates = []
    d = []
    for tag in tags:
        if "NN" == tag[1]:
            date = dateparser.parse(tag[0])
            if date != None:
                #print(date.strftime("%Y-%m-%d"))
                dates.append(date.strftime("%Y-%m-%d"))
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
        if "NNP" == tag[1]:
            place = tag[0]
            cities = GeoText(place.upper()).cities
            if cities.__len__() > 0:
                for city in cities:
                    places.append(destination_map[city])
    return places

