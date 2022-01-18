import csv, datetime, json, logging, os, pprint, shutil, smtplib, sys
from email.mime.text import MIMEText


settings = json.loads( os.environ['VIVO_MODIFY_CSV_ENV_SETTINGS_JSON'] )
assert type(settings) == dict

logging.basicConfig(
    # filename=settings['LOG_PATH'],
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S',
    )
log = logging.getLogger(__name__)
log.debug( '\n\nstarting log\n============' )


# def csv_get_indices():
#     source_file_path = settings['FILEPATH_SOURCE']
#     # destination_filepath = settings['FILEPATH_ARCHIVE_DESTINATION']

#     file_dct = {}
#     with open( source_file_path, 'r' ) as file_reader:
#         # dr = csv.DictReader( file_reader, delimiter=',', quoting=csv.QUOTE_NONE )

#         # dialect = csv.Sniffer().sniff(file_reader.read(1024))
#         # log.debug( f'dialect, ``{pprint.pformat(dialect.__dict__)}``' )

#         dr = csv.DictReader( file_reader)#, dialect=dialect )
#         # log.debug( f'type(dr), ``{type(dr)}``' )
#         # log.debug( f'dr, ``{pprint.pformat(dr)}``' )
#         file_dct = { row['Auth_ID']: {'index': i, 'data': row} for i, row in enumerate(dr) }
#         # log.debug( f'file_dct, ``\n{pprint.pformat(file_dct)[0:5000]}``' )
#         # log.debug( f'x, ``{x}``' )
#         log.debug( f'aabbasi2_dct, ``{file_dct["aabbasi2"]["data"]}``')

#     ids = [ i['auth_id'] for i in settings['CHANGES'] ]
#     log.debug( f'ids, ``{ids}``')
#     lookup_indices = [ file_dct[i]['index'] for i in ids ]

#     return lookup_indices

# myDict = {x: x**2 for x in [1,2,3,4,5]}


def set_indices():
    source_file_path = settings['FILEPATH_SOURCE']
    # destination_filepath = settings['FILEPATH_ARCHIVE_DESTINATION']

    file_dct = {}
    with open( source_file_path, 'r' ) as file_reader:
        # dr = csv.DictReader( file_reader, delimiter=',', quoting=csv.QUOTE_NONE )

        # dialect = csv.Sniffer().sniff(file_reader.read(1024))
        # log.debug( f'dialect, ``{pprint.pformat(dialect.__dict__)}``' )

        dr = csv.DictReader( file_reader)#, dialect=dialect )
        # log.debug( f'type(dr), ``{type(dr)}``' )
        # log.debug( f'dr, ``{pprint.pformat(dr)}``' )
        file_dct = { row['Auth_ID']: {'index': i, 'data': row} for i, row in enumerate(dr) }
        # log.debug( f'file_dct, ``\n{pprint.pformat(file_dct)[0:5000]}``' )
        # log.debug( f'x, ``{x}``' )
        log.debug( f'aabbasi2_dct, ``{file_dct["aabbasi2"]["data"]}``')

    for change_dct in settings['CHANGES']:
        change_auth_id = change_dct['auth_id']
        index = file_dct[change_auth_id]['index']
        change_dct['idx'] = index

    # ids = [ i['auth_id'] for i in settings['CHANGES'] ]
    # log.debug( f'ids, ``{ids}``')
    # lookup_indices = [ file_dct[i]['index'] for i in ids ]

    return



def process_csv():
    """ Manages processing.
        Called by ```if __name__ == '__main__':``` """
    # source_file_path = 'foo'
    source_file_path = settings['FILEPATH_SOURCE']
    destination_filepath = settings['FILEPATH_ARCHIVE_DESTINATION']

    err = copy_original_to_archives( source_file_path, destination_filepath )
    if err:
        email_admins( err ); sys.exit()

    ( lines, err ) = get_lines()
    if err:
        email_admins( err ); sys.exit()


    set_indices()


    ( updated_lines, err ) = update_lines( lines )

    log.debug( 'hereA')
    if err:
        log.debug( 'hereB')
        email_admins( repr(err) )
    log.debug( 'hereC')

    err = write_file( updated_lines )
    if err:
        email_admins( err ); sys.exit()

def copy_original_to_archives(source_file_path, destination_filepath ):
    """ Archives original before doing anything else.
        Called by process_csv() """
    err = None
    try:
        # shutil.copy2( source_file_path, destination_filepath )
        shutil.copyfile( source_file_path, destination_filepath )
    except Exception as e:
        err = repr(e)
        log.exception( 'Problem with copy; admins will be emailed.' )
    # log.debug( f'err, ``{err}``' )
    return err

def get_lines():
    """ Opens file & grabs text.
        Called by process_csv() """
    FILE_PATH = settings['FILEPATH_SOURCE']
    ( lines, err ) = ( [], None )
    try:
        with open( FILE_PATH, 'r' ) as file_reader:
            lines = file_reader.readlines()
    except Exception as e:
        err = repr(e)
        log.exception( 'Problem opening file; admins will be emailed.' )
        return err
    return ( lines, err )

def update_lines( lines ):
    """ Updates data.
        Called by process_csv() """
    assert type( lines ) == list
    ( updated_lines, err ) = ( [], [] )

    for change_dct in settings['CHANGES']:
        log.debug( f'changing ``{change_dct["auth_id"]}``' )
        lookup_index = change_dct['idx']
        log.debug( f'lookup_index, `{lookup_index}``')

        trgt = change_dct['target']
        rplcmnt = change_dct['replacement']

        evaluation_line = lines[lookup_index+1]
        log.debug( f'before, ``{evaluation_line}``')

        if trgt in evaluation_line:
            evaluation_line = evaluation_line.replace( trgt, rplcmnt )
            lines[lookup_index+1] = evaluation_line
        else:
            err.append( f' no target for ``{change_dct["auth_id"]}`` found')

        log.debug( f'after, ``{evaluation_line}``')
        log.debug( f'after idx, ``{lines[lookup_index+1]}``')


    updated_lines = lines

    return ( updated_lines, err )

        # log.debug( f'before, ``{lines[lookup_index+1]}``' )
        # lines[lookup_index+1] = lines[lookup_index+1].replace( change_dct['target'], change_dct['replacement'] )
        # log.debug( f'after, ``{lines[lookup_index+1]}``' )


    # AUTH_ID = settings['CHANGES'][0]['auth_id']
    # SEARCH_TEXT = settings['CHANGES'][0]['target']
    # REPLACE_TEXT = settings['CHANGES'][0]['replacement']
    # found_flag = 'init'
    # for line in lines:
    #     if AUTH_ID in line and SEARCH_TEXT in line:
    #         updated_line = line.replace( SEARCH_TEXT, REPLACE_TEXT )
    #         updated_lines.append( updated_line )
    #         found_flag = 'found_match'
    #     else:
    #         updated_lines.append( line )
    # if found_flag == 'init':
    #     err = 'odd; no match found'

    return ( updated_lines, err )




# def update_lines( lines ):
#     """ Updates data.
#         Called by process_csv() """
#     assert type( lines ) == list
#     ( updated_lines, err ) = ( [], None )
#     AUTH_ID = settings['CHANGES'][0]['auth_id']
#     SEARCH_TEXT = settings['CHANGES'][0]['target']
#     REPLACE_TEXT = settings['CHANGES'][0]['replacement']
#     found_flag = 'init'
#     for line in lines:
#         if AUTH_ID in line and SEARCH_TEXT in line:
#             updated_line = line.replace( SEARCH_TEXT, REPLACE_TEXT )
#             updated_lines.append( updated_line )
#             found_flag = 'found_match'
#         else:
#             updated_lines.append( line )
#     if found_flag == 'init':
#         err = 'odd; no match found'
#     return ( updated_lines, err )

def write_file( updated_lines ):
    """ Writes new file.
        Called by process_csv() """
    assert type( updated_lines ) == list
    FILE_PATH = settings['FILEPATH_SOURCE']
    err = None
    try:
        with open(FILE_PATH, 'w') as file_writer:
            file_writer.writelines( updated_lines )
    except Exception as e:
        err = repr(e)
        log.exception( 'Problem writing file; admins will be emailed.' )
    return err

def email_admins( err ):
    """ Sends error mail.
        Called by process_csv() """
    log.debug( 'starting email_admins()' )
    assert type( err ) == str
    EMAIL_HOST = settings['MAIL_HOST']
    EMAIL_PORT = settings['MAIL_PORT']
    EMAIL_FROM = settings['MAIL_FROM']
    EMAIL_RECIPIENTS = settings['MAIL_RECIPIENTS']
    try:
        s = smtplib.SMTP( EMAIL_HOST, EMAIL_PORT )
        body = f'datetime: `{str(datetime.datetime.now())}`\n\nerror...`\n\n{err}[END]'
        eml = MIMEText( f'{body}' )
        eml['Subject'] = 'error in vivo modify_csv.py processing'
        eml['From'] = EMAIL_FROM
        eml['To'] = ';'.join( EMAIL_RECIPIENTS )
        s.sendmail( EMAIL_FROM, EMAIL_RECIPIENTS, eml.as_string())
        log.debug( 'mail sent' )
    except Exception as e:
        err = repr( e )
        log.exception( f'Problem sending mail, ``{err}``' )
    return


if __name__ == '__main__':
    process_csv()
    # print(csv_get_indices())
