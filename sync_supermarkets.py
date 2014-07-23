import overpass, overpass.execute, overpass.nodes
from models import SuperMarket
import database

def get_supermarkets():
    """Returns a list of supermarket objects"""
    overpass.init()
    query = 'node[shop="supermarket"](52.0630454,-106.7706299,52.2067651,-106.5103912);out body;'
    results = overpass.execute.execute_QL(query)
    supermarkets = results['elements']
    supermarkets_list = []
    
    for market in supermarkets:
        supermarkets_list.append(
            SuperMarket(
                post_code=market['tags'].get('addr:postcode'),
                street=market['tags'].get('addr:street'),
                operator=market['tags'].get('operator'),
                name=market['tags'].get('name'),
                city=market['tags'].get('addr:city'),
                phone=market['tags'].get('phone'),
                house_number=market['tags'].get('addr:housenumber'),
                latitude=market.get('lat'),
                longitude=market.get('lon')))
    overpass.end()
    return supermarkets_list