import argparse, json, pprint, requests, sys


def get_dept_members( dept_num: str ):
    url = f'http://vivo.brown.edu:8080/vivosolr/collection1/select?q=URI:http://vivo.brown.edu/individual/org-brown-univ-dept{dept_num}&wt=json&fl=json_txt'

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



def parse_args() -> dict:
    """ Parses arguments when module called via __main__ """
    parser = argparse.ArgumentParser( description='Required: a vivo department id, like `71` for Emergency Medicine' )
    parser.add_argument( '--department', required=True )
    args: dict = vars( parser.parse_args() )
    if args == {'department': None}:
        parser.print_help()
        sys.exit()
    # log.debug( f'args, ``{args}``' )
    return args


if __name__ == '__main__':
    args: dict = parse_args()
    department: str  = args['department']
    get_dept_members( department )
