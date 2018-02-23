import nltk
from geotext import GeoText
import dateparser
from nltk.corpus import stopwords
from time import strftime

FILE_PATH = 'resources/destinations.csv'

stopWords = set(stopwords.words('english'))

def translate_human_request(request):
    request = request.replace("'", "")      # Workarround for the I in I'm treated as number 1.
    tokens = nltk.word_tokenize(request)
    tags = nltk.pos_tag(tokens)

    destinations_map = destinations_mapper()

    places = extract_places(tags, destinations_map)

    dates = extract_dates(tags)

    return { 'places':places, 'dates': dates }

def extract_dates(tags):
    dates = []
    words = tags[:]
    
    for w in words:
        if w[1] == 'NN':
            date = dateparser.parse(w[0])
            if date != None:
                dates.append(date.strftime("%Y-%m-%d"))
                words.remove(w)
    
    sentence = ' '.join([w for w,t in words])
    pairs = nltk.bigrams(sentence.split())
    for p in pairs:
        try:
            if sum([c in stopWords for c in p]) == 0:
                date = dateparser.parse(' '.join(p))
                if date != None:
                    dates.append(date.strftime("%Y-%m-%d"))
        except:
            pass
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
        place = tag[0]
        cities = GeoText(place.upper()).cities
        if cities.__len__() > 0:
            for city in cities:
                places.append(destination_map[city])
                return places

    return places

