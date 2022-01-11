import datetime, json, logging, os, shutil, smtplib, sys
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
    ( updated_lines, err ) = update_lines( lines )
    if err:
        email_admins( err ); sys.exit()
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
    ( updated_lines, err ) = ( [], None )
    AUTH_ID = settings['CHANGES'][0]['auth_id']
    SEARCH_TEXT = settings['CHANGES'][0]['target']
    REPLACE_TEXT = settings['CHANGES'][0]['replacement']
    found_flag = 'init'
    for line in lines:
        if AUTH_ID in line and SEARCH_TEXT in line:
            updated_line = line.replace( SEARCH_TEXT, REPLACE_TEXT )
            updated_lines.append( updated_line )
            found_flag = 'found_match'
        else:
            updated_lines.append( line )
    if found_flag == 'init':
        err = 'odd; no match found'
    return ( updated_lines, err )

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
