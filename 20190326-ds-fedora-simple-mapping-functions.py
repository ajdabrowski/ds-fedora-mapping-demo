# Written in Python 3.7
import json
import requests

## Mapping dictionary and functions for DesignSafe experiment-type project
## from: DesignSafe JSON keys and values (strings or lists) 
## to: DCTerm URIs (later generically referred to as RDF predicate URIs), 
## values (later all transformed into lists and referred to as RDF object lists), 
## and anticipated RDF object types
 
json_map_dict = {
    'uuid': {
        'dc_term_uri':'http://purl.org/dc/terms/identifier',
        'rdf_object_type': 'string_literal',
        'get_json_value': lambda ds_json: ds_json.get('uuid')
    },
    'doi': {
        'dc_term_uri': 'http://purl.org/dc/terms/identifier',
        'rdf_object_type': 'string_literal',
        'get_json_value': lambda ds_json: ds_json.get('doi')
    },
    'type': {
        'dc_term_uri': 'http://purl.org/dc/terms/type',
        'rdf_object_type': 'string_literal',
        'get_json_value': lambda ds_json: derive_dcterm_type_value(ds_json.get('name'))
    },
    'publication_date': {
        'dc_term_uri': 'http://purl.org/dc/terms/date',
        'rdf_object_type': 'datetime_literal',
        'get_json_value': lambda ds_json: ds_json.get('lastUpdated')
    },
    'title': {
        'dc_term_uri': 'http://purl.org/dc/terms/title',
        'rdf_object_type': 'string_literal',
        'get_json_value': lambda ds_json: ds_json['value'].get('title')
    },
    'team_members': {
        'dc_term_uri': 'http://purl.org/dc/terms/creator',
        'rdf_object_type': 'string_literal',
        'get_json_value': lambda ds_json: ds_json['value'].get('teamMembers')
    },
    'co_pis': {
        'dc_term_uri': 'http://purl.org/dc/terms/creator',
        'rdf_object_type': 'string_literal',
        'get_json_value': lambda ds_json: ds_json['value'].get('coPis')
    },
    'pi': {
        'dc_term_uri': 'http://purl.org/dc/terms/creator',
        'rdf_object_type': 'string_literal',
        'get_json_value': lambda ds_json: ds_json['value'].get('pi')
    },
    'authors': {
        'dc_term_uri': 'http://purl.org/dc/terms/creator',
        'rdf_object_type': 'string_literal',
        'get_json_value': lambda ds_json: ds_json['value'].get('authors')
    },
    'project_type': {
        'dc_term_uri': 'http://purl.org/dc/terms/type',
        'rdf_object_type': 'string_literal',
        'get_json_value': lambda ds_json: ds_json['value'].get('projectType')
    },
    'award_number': {
        'dc_term_uri': 'http://purl.org/dc/terms/contributor',
        'rdf_object_type': 'string_literal',
        'get_json_value': lambda ds_json: ds_json['value'].get('awardNumber')
    },
    'project_id': {
        'dc_term_uri': 'http://purl.org/dc/terms/identifier',
        'rdf_object_type': 'string_literal',
        'get_json_value': lambda ds_json: ds_json['value'].get('projectId')
    },
    'description': {
        'dc_term_uri': 'http://purl.org/dc/terms/description',
        'rdf_object_type': 'string_literal',
        'get_json_value': lambda ds_json: ds_json['value'].get('description')
    },
    'keywords': {
        'dc_term_uri': 'http://purl.org/dc/terms/subject',
        'rdf_object_type': 'string_literal',
        'get_json_value': lambda ds_json: split_keywords(ds_json['value'].get('keywords'))
    },
    'experimental_facility': {
        'dc_term_uri': 'http://purl.org/dc/terms/contributor',
        'rdf_object_type': 'string_literal',
        'get_json_value': lambda ds_json: ds_json['value'].get('experimentalFacility')
    },
    'experimental_facility_other': {
        'dc_term_uri': 'http://purl.org/dc/terms/contributor',
        'rdf_object_type': 'string_literal',
        'get_json_value': lambda ds_json: ds_json['value'].get('experimentalFacilityOther')
    },
    'experiment_type': {
        'dc_term_uri': 'http://purl.org/dc/terms/subject',
        'rdf_object_type': 'string_literal',
        'get_json_value': lambda ds_json: ds_json['value'].get('experimentType')
    },
    'experiment_type_other': {
        'dc_term_uri': 'http://purl.org/dc/terms/subject',
        'rdf_object_type': 'string_literal',
        'get_json_value': lambda ds_json: ds_json['value'].get('experimentTypeOther')
    },
    'equipment_type': {
        'dc_term_uri': 'http://purl.org/dc/terms/subject',
        'rdf_object_type': 'string_literal',
        'get_json_value': lambda ds_json: ds_json['value'].get('equipmentType')
    },
    'equipment_type_other': {
        'dc_term_uri': 'http://purl.org/dc/terms/subject',
        'rdf_object_type': 'string_literal',
        'get_json_value': lambda ds_json: ds_json['value'].get('equipmentTypeOther')
    },
}

def derive_dcterm_type_value(name):    
    if name == 'designsafe.project':
        type_value = 'collection'
    else:
        type_value = 'dataset'
    
    return type_value

def split_keywords(keywords):
    if keywords:
        return keywords.replace(';',',').split(',')
    else:
        return
        
## Functions for using the mapping dictionary to create an RDF dictionary 
## for a single JSON object aligned with a data model entity
## Data model entities include: project, experiment, analysis, report, model configuration, sensor, event
## RDF dictionary format: {rdf_predicate_uri:{'subject_uri': '', 'object_list': rdf_object_list, 'object_type': rdf_object_type}}

# Takes a JSON object aligned with a single data model entity (e.g. an event) 
# and maps to DCTerms for Fedora resource container properties
def map_ds_json_to_rdf(ds_json, map_dict):
    rdf_dict = {}
    
    for entity_property, term_dict in map_dict.items():
        rdf_object_value = term_dict['get_json_value'](ds_json)
        
        if rdf_object_value:
            rdf_object_type = term_dict['rdf_object_type']
            dc_term_predicate_uri = term_dict['dc_term_uri']
            rdf_object_list = convert_to_list(rdf_object_value)
            rdf_relation = {'subject_uri': '', 'object_list': rdf_object_list, 'object_type': rdf_object_type}
            add_to_rdf_dict(dc_term_predicate_uri, rdf_relation, rdf_dict)
    
    return rdf_dict

# Converts a string to a list containing the string
def convert_to_list(value):
    if isinstance(value,str):
        value = [value]
    
    return value

# Adds new dictionaries to the RDF dictionary based on RDF predicate URIs, 
# checks if a RDF predicate URI already exists in the RDF dictionary
# if so, appends RDF object list to existing list
def add_to_rdf_dict(rdf_predicate_uri, rdf_relation, rdf_dict):
    if rdf_predicate_uri in rdf_dict:
        rdf_dict[rdf_predicate_uri]['object_list'] = rdf_dict[rdf_predicate_uri]['object_list'] + rdf_relation['object_list']

    else:
        rdf_dict.update({rdf_predicate_uri:rdf_relation})
    
    return

## Functions to create Fedora container paths and and RDF dictionary with container relations
## for a single JSON object aligned with a data model entity
## Uses 'uuid' to construct paths
## Data model entities include: project, experiment, analysis, report, model configuration, sensor, event

# Linked Data RDF dictionary format: 
# {'http://purl.org/dc/terms/isPartOf': 
#  {'subject_uri': '', 
#   'object_list': [related_container_path], 
#   'object_type': 'uri'
#  },
#  'http://purl.org/dc/terms/hasPart': 
#  {'subject_uri': related_container_path, 
#   'object_list': [container_path], 
#   'object_type': 'uri'
#  },
# }

# Takes a JSON object aligned with a single data model entity (e.g. an event)
# Returns a dictionary of paths: 
# {'container_path': container_path, 'related_container_path': related_container_path}
def create_paths(fedora_url, ds_json):
    name = ds_json.get('name')
    
    if name == 'designsafe.project':
        related_container_path = None
        container_path = create_path([fedora_url, 
                                      ds_json['uuid']])
    
    elif name == 'designsafe.project.experiment' or name == 'designsafe.project.analysis' or name == 'designsafe.project.report':
        related_container_path = create_path([fedora_url, 
                                              ds_json['value']['project'][0]])
        container_path = create_path([fedora_url,
                                      ds_json['value']['project'][0], 
                                      ds_json['uuid']])
    
    elif name == 'designsafe.project.model_config':
        related_container_path = create_path([fedora_url, 
                                              ds_json['value']['project'][0], 
                                              ds_json['value']['experiments'][0]])
        container_path = create_path([fedora_url, 
                                      ds_json['value']['project'][0], 
                                      ds_json['value']['experiments'][0],
                                      ds_json['uuid']])
    
    elif name == 'designsafe.project.sensor_list': 
        related_container_path = create_path([fedora_url, 
                                              ds_json['value']['project'][0], 
                                              ds_json['value']['experiments'][0]])
        container_path = create_path([fedora_url, 
                                      ds_json['value']['project'][0], 
                                      ds_json['value']['experiments'][0], 
                                      ds_json['value']['modelConfigs'][0],
                                      ds_json['uuid']])
    
    elif name == 'designsafe.project.event':
        related_container_path = create_path([fedora_url, 
                                              ds_json['value']['project'][0], 
                                              ds_json['value']['experiments'][0], 
                                              ds_json['value']['modelConfigs'][0]])
        container_path = create_path([fedora_url, 
                                      ds_json['value']['project'][0], 
                                      ds_json['value']['experiments'][0], 
                                      ds_json['value']['modelConfigs'][0],
                                      ds_json['uuid']])
    
    path_dict = {'container_path': container_path, 
                 'related_container_path': related_container_path
                }
    
    return path_dict

# Takes a dictionary of paths:
# {'container_path': container_path, 'related_container_path': related_container_path}
# Returns a Linked Data RDF dictionary
def create_ld_rdf_dict(path_dict):
    if path_dict['related_container_path']:
        ld_rdf_dict = {'http://purl.org/dc/terms/isPartOf': 
                       {'subject_uri': '', 
                        'object_list': [path_dict['related_container_path']], 
                        'object_type': 'uri'
                       },
#                        'http://purl.org/dc/terms/hasPart': 
#                        {'subject_uri': path_dict['related_container_path'], 
#                         'object_list': [path_dict['container_path']], 
#                         'object_type': 'uri'
#                        },
                      }
    
    else: 
        ld_rdf_dict = {}
    
    return ld_rdf_dict

# Joins a list of strings with '/'
def create_path(path_elements):
    path = '/'.join(path_elements)
    
    return path
    
## Functions for creating SPARQL request body from RDF dictionaries
## RDF dictionary format: {rdf_predicate_uri:{'subject': '', 'object_list': [], 'object_type': rdf_object_type}}
## RDF object type values: 'uri', string_literal', 'datetime_literal', 'integer_literal', 'decimal_literal'

# Formats a SPAQRL request body according to request type, 
# currently only functions with a default of insert request
def create_sparql_request(rdf_dict, ld_rdf_dict, request_type='insert'):
    rdf_dict.update(ld_rdf_dict)

    if request_type == 'insert':
        sparql_request = format_sparql_insert_request(rdf_dict)
    
    return sparql_request

# Formats the body of a SPARQL insert request
def format_sparql_insert_request(rdf_dict):
    rdf_triples_string = format_sparql_rdf_triples(rdf_dict)
    insert_request = "INSERT {{\n{}}} \nWHERE {{}}".format(rdf_triples_string)
    return insert_request

# Formats a string of RDF triples to place within a SPARQL request body
def format_sparql_rdf_triples(rdf_dict):
    rdf_triples = []
    for rdf_predicate_uri, rdf_relation in rdf_dict.items():
#         print(rdf_relation)
        rdf_subject_uri = rdf_relation['subject_uri']
        rdf_object_string = format_object_by_type(rdf_relation['object_list'],rdf_relation['object_type'])
#         print(rdf_object_string)
        triple = "<{}> <{}> {} .".format(rdf_subject_uri, rdf_predicate_uri, rdf_object_string)
        rdf_triples.append(triple)
    rdf_triples_string = '\n'.join(rdf_triples)
#     print(rdf_string)
    return rdf_triples_string

# Formats the object list for one RDF triple into a string of objects 
def format_object_by_type(object_list, object_type):
    temp_object_list = []
    for rdf_object in object_list:
        rdf_object = check_object_type(rdf_object, object_type)
        temp_object_list.append(rdf_object)
    rdf_object_string = ', '.join(temp_object_list)
    return rdf_object_string

# Checks the type of an RDF object and creates appropriate string specifying type for SPARQL
# RDF object type values: 'uri', string_literal', 'datetime_literal', 'integer_literal', 'decimal_literal'
def check_object_type(rdf_object, object_type):
    if object_type == 'string_literal':
            rdf_object = '"{}"'.format(rdf_object)
    
    elif object_type == 'datetime_literal':
        rdf_object = '"{}"^^<http://www.w3.org/2001/XMLSchema#dateTime>'.format(rdf_object)

    elif object_type == 'uri':
        rdf_object = '<{}>'.format(rdf_object)
    
    else:
        rdf_object = '"{}"'.format(rdf_object)

    return rdf_object

## Simple functions for Fedora 4 HTTP API
## Documentation URL: https://wiki.duraspace.org/display/FEDORA4x/RESTful+HTTP+API

# Create (Put) new Fedora container-type resource at a specified path
def request_create_container(container_path):
    r = requests.put(container_path)
    # Need to catch errors
    print(r.text)
    
    return

# Add (Put) new Fedora binary-type resource at a specified path, 
# needs headers with mimetype and checksum
# def request_add_binary(container_path, file, http_headers={'Content-Type':'image/png', 'digest':'sha1=2713434466f21932f702c9150e6fbf70a47909fb'}):
#     with open(file, 'rb') as data:
#         r = requests.put(container_path, headers=http_headers, data=data)
#     print(r.text)
#
#     return

# Get JSON-LD metadata from a Fedora container-type resource at a specified path
def request_get_container_jsonld(container_path, http_headers={'Accept': 'application/ld+json'}):
    r = requests.get(container_path, headers=http_headers)
    # Need to catch errors
    container_jsonld = r.json()
    print(container_jsonld)
    
    return container_jsonld

# Replace (Put) JSON-LD metadata in a Fedora container-type resource at a specified path
# Note: This replaces the triples associated with a resource with the triples provided in the request body
# def request_replace_container_jsonld(container_path, jsonld, http_headers={'Content-Type': 'application/ld+json'}):
#     r = requests.put(container_path, headers=http_headers, json=container_jsonld)
#     # Need to catch errors
#     print(r.text)
#
#     return

# Modify the triples associated with a Fedora resource with SPARQL-Update
def request_modify_container_triples(container_path, sparql_request, http_headers={'Content-Type': 'application/sparql-update'}):
    r = requests.patch(container_path, headers=http_headers, data=sparql_request)
    # Need to catch errors
    print(r.text)
    
    return

## Simple control functions

def create_fedora_container_with_metadata(fedora_url, ds_json, map_dict=json_map_dict):
    path_dict = create_paths(fedora_url, ds_json)
    new_fedora_container(path_dict)
    add_metadata_to_fedora_container(path_dict, ds_json, map_dict)
    
    return

def new_fedora_container(path_dict):
    container_path = path_dict['container_path']
    request_create_container(container_path)
    
    return

def add_metadata_to_fedora_container(path_dict, ds_json, map_dict):
    ld_rdf_dict = create_ld_rdf_dict(path_dict)
    rdf_dict = map_ds_json_to_rdf(ds_json, map_dict)
    sparql_request = create_sparql_request(rdf_dict, ld_rdf_dict)
    request_modify_container_triples(container_path, sparql_request)
    
    return