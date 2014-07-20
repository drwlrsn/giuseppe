import overpass, overpass.execute, overpass.nodes
from models import School
import database

def get_schools():
    """Returns a list of school objects"""
    overpass.init()
    query = 'way[amenity="school"](52.0630454,-106.7706299,52.2067651,-106.5103912);out body;'
    results = overpass.execute.execute_QL(query)
    schools = results['elements']
    schools_list = []
    for school in schools:
        try:
            print("DEBUG: Retriving {0}...".format(school['tags'].get('name', school['id'])))
        except KeyError:
            print(school['id'])
        school['geom'] = []
        for node in school['nodes']:
            node_results = overpass.nodes.get(node)
            school['geom'].append('{lon} {lat}'.format( \
                                  lat=node_results['lat'], \
                                  lon = node_results['lon']))
        
        schools_list.append(School(
                            geom=school.get('geom'),
                            post_code=school['tags'].get('addr:postcode'),
                            street=school['tags'].get('addr:street'),
                            operator=school['tags'].get('operator'),
                            religion=school['tags'].get('religion'),
                            denomination=school['tags'].get('denomation'),
                            name=school['tags'].get('name'),
                            city=school['tags'].get('addr:city'),
                            phone=school['tags'].get('phone'),
                            house_number=school['tags'].get('addr:housenumber'),
                            osm_id=school['id']
                            ))
    overpass.end()
    return schools_list