import json, pprint, requests

# url = 'http://vivo.brown.edu:8080/vivosolr/collection1/select?q=URI:http://vivo.brown.edu/individual/org-brown-univ-dept71&wt=json'
url = 'http://vivo.brown.edu:8080/vivosolr/collection1/select?q=URI:http://vivo.brown.edu/individual/org-brown-univ-dept71&wt=json&fl=json_txt'


r = requests.get( url )

dct = json.loads( r.content )

rsp_keys = dct['response'].keys()
# print( f'rsp_keys, ``{pprint.pformat(rsp_keys)}``' )

docs = dct['response']['docs']
# print( f'docs, ``{pprint.pformat(docs)}``' )

doc = docs[0]  # ah, because of the fl=json_txt, i only have one key; cool
doc_keys = doc.keys()
print( f'doc_keys, ``{doc_keys}``' )

jtxt_list: list = doc['json_txt']
# print( f'jtxt_list, ``{jtxt_list}`` ')
# print( f'type(jtxt_list), ``{type(jtxt_list)}``' )
# print( f'len(jtxt_list), ``{len(jtxt_list)}``' )

department_info_text: str = jtxt_list[0]
department_info: dict = json.loads(department_info_text)

people: list = department_info['people']

print( 'people in department 71 ------' )
print( '------------------------------')
pprint.pprint( people ) 

print( f'len(people), ``{len(people)}``' )

