import overpass, overpass.execute, overpass.nodes
from models import School
import database
import logging
logging.basicConfig(level=logging.DEBUG)

EXCLUDE_LIST = (
                'dance',
                )

def get_schools():
    """Returns a list of school objects"""
    overpass.init()
    saskatoon_query = 'way[amenity="school"](52.0630454,-106.7706299,52.2067651,-106.5103912);out body;'
    warman_query = 'way[amenity="school"](52.30491,-106.6092682,52.336388,-106.5591431);out body;'
    martensville_query = 'way[amenity="school"](52.2757204,-106.681366,52.3059596,-106.636734);out body;'

    results = overpass.execute.execute_QL(saskatoon_query)
    schools = results['elements']

    results = overpass.execute.execute_QL(warman_query)
    schools += results['elements']

    results = overpass.execute.execute_QL(martensville_query)
    schools += results['elements']

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

def in_database(school):
    query = database.session.query(School)
    return query.filter_by(name=school.name).first()

def excludable(school):
    for item in EXCLUDE_LIST:
        if item in school.name.lower():
            return True
    return False

def serialise(school, update=False, debug=True):
    if not excludable(school):
        if not debug:
            school_query = in_database(school)
            if school_query and update:
                school_query.update(school)
                database.session.merge(school_query)
            elif not school_query:
                database.session.add(school)

            database.session.commit()
            logging.info('Saved {name} in {city} to database.'.format(name=school.name, city=school.city))
        else:
            logging.debug('Saved {name} in {city} to database.'.format(name=school.name, city=school.city))
            return
    else:
        logging.info('Excluding. {name} in {city}.'.format(name=school.name, city=school.city))
        

def main(debug=True, update=False):
    schools = get_schools()
    for school in schools:
        serialise(school, debug=debug, update=update)

if '__name__' == '__main__':
    main(debug=False)