import argparse, json, os, pprint, requests, sys

import web_client


vivo_session = web_client.Session()
SOLR_URL_SEGMENT = os.environ['VIVO_SOLR_URL_SEGMENT']


def add_delegate(delegate_id, target_fac_id):
	the_payload_dict = {'additions': f'@prefix afn: <http://jena.hpl.hp.com/ARQ/function#> .\n@prefix bcite: <http://vivo.brown.edu/ontology/citation#> .\n@prefix bdisplay: <http://vivo.brown.edu/ontology/display#> .\n@prefix bibo: <http://purl.org/ontology/bibo/> .\n@prefix blocal: <http://vivo.brown.edu/ontology/vivo-brown/> .\n@prefix bprofile: <http://vivo.brown.edu/ontology/profile#> .\n@prefix bwday: <http://vivo.brown.edu/ontology/workday#> .\n@prefix d: <http://vivo.brown.edu/individual/> .\n@prefix dcterms: <http://purl.org/dc/terms/> .\n@prefix foaf: <http://xmlns.com/foaf/0.1/> .\n@prefix owl: <http://www.w3.org/2002/07/owl#> .\n@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n@prefix skos: <http://www.w3.org/2004/02/skos/core#> .\n@prefix tmp: <http://localhost/tmp#> .\n@prefix vitro: <http://vitro.mannlib.cornell.edu/ns/vitro/0.7#> .\n@prefix vitropublic: <http://vitro.mannlib.cornell.edu/ns/vitro/public#> .\n@prefix vivo: <http://vivoweb.org/ontology/core#> .\n@prefix xml: <http://www.w3.org/XML/1998/namespace> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\nd:{target_fac_id} blocal:hasDelegate d:{delegate_id} ;\n\n', 'retractions': '@prefix ns1: <http://vivo.brown.edu/ontology/vivo-brown/> .\n@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n@prefix xml: <http://www.w3.org/XML/1998/namespace> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\n'}
	
	vs = get_session()
	resp = vs.session.post(
		vs.url + 'edit/primitiveRdfEdit',
		data=the_payload_dict,
		verify=False
	)
	if resp.status_code != 200:
		# vlog.error("VIVO app response:\n" + resp.text)
		# vlog.error("Add graph:\n" + add_graph.serialize(format='nt').decode('utf8'))
		# vlog.error("Subtract graph:\n" + subtract_graph.serialize(format='nt').decode('utf8'))
		# raise VIVOEditError('VIVO data editing failed')
		print('VIVO data editing failed')
	else:
		print(f'Added {delegate_id} as delegate for {target_fac_id}')

def get_session():
	"""
	Verify that user is logged in by issuing
	a HEAD request.  This adds overheard to
	each edit but should be minimal as it just
	verifies the session and does not follow
	redirects.
	"""
	ping = vivo_session.session.head(vivo_session.url + 'siteAdmin', verify=False)
	if ping.status_code == 302:
		vivo_session.login()
	return vivo_session

def get_dept_members( dept_num: str ):
	url = f'{SOLR_URL_SEGMENT}/select?q=URI:http://vivo.brown.edu/individual/org-brown-univ-dept{dept_num}&wt=json&fl=json_txt'

	r = requests.get( url )
	dct = json.loads( r.content )
	docs = dct['response']['docs']
	doc = docs[0]
	jtxt_list: list = doc['json_txt']

	department_info_text: str = jtxt_list[0]
	department_info: dict = json.loads(department_info_text)

	dept_name = department_info['name']
	people: list = department_info['people']
	fac_ids = [i['faculty_uri'].split('/')[-1] for i in people]

	return(dept_name, fac_ids)


def parse_args() -> dict:
	""" Parses arguments when module called via __main__ """
	parser = argparse.ArgumentParser( description='Required: a vivo department id, like `71` for Emergency Medicine and the short id of the person to add as a delegate' )
	parser.add_argument( '--department', required=True )
	parser.add_argument( '--delegate', required=True )
	args: dict = vars( parser.parse_args() )
	if None in args.values():
		parser.print_help()
		sys.exit()
	return args


if __name__ == '__main__':
	args: dict = parse_args()
	department: str  = args['department']
	print('\n-= Starting =-')
	dept_name, dept_members = get_dept_members( department )
	delegate_id: str = args['delegate']
	print(f"Will add '{delegate_id}' as delegate for {len(dept_members)} members of '{dept_name}'")
	input('Press Enter/Return to continue')
	for n, faculty_member in enumerate(dept_members):
		print(n+1,end=' ')
		add_delegate(delegate_id=delegate_id, target_fac_id=faculty_member)
	print('-= Completed =-')
