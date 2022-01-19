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


def process_csv():
    """ Manages processing.
        Called by ```if __name__ == '__main__':``` """
    source_file_path = settings['FILEPATH_SOURCE']
    destination_filepath = settings['FILEPATH_ARCHIVE_DESTINATION']
    ## backup original --------------------------
    err = backup_original( source_file_path, destination_filepath )
    if err:
        email_admins( err )
        sys.exit()
    ## load source-data -------------------------
    ( lines, err ) = get_lines()
    if err:
        email_admins( err )
        sys.exit()
    ## update each change-dict w/index ----------
    err = set_indices()
    if err:
        email_admins( err )
        sys.exit()
    ## update lines -----------------------------
    ( updated_lines, err ) = update_lines( lines )
    if err:  # notify admins, but continue processing
        email_admins( err )
    ## write new file ---------------------------
    err = write_file( updated_lines )
    if err:
        email_admins( err )
        sys.exit()


def backup_original( source_file_path, destination_filepath ):
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


def set_indices():
    """ Updates each change-dict with the target line-index...
        ...by first creating a dict from the source-file, where the key is the row's auth-id,
        ...and the value is a dict of index and data elements.
        Then iterates through the change-dicts, looking up the auth-id and adding the row-index to the change-dict.
        Called by process_csv() """
    err = None
    try:
        source_file_path = settings['FILEPATH_SOURCE']
        file_dct = {}
        with open( source_file_path, 'r' ) as file_reader:
            dr = csv.DictReader( file_reader)
            file_dct = { row['Auth_ID']: {'index': i, 'data': row} for i, row in enumerate(dr) }
            # log.debug( f'file_dct, ``\n{pprint.pformat(file_dct)[0:5000]}``' )
        for change_dct in settings['CHANGES']:
            change_auth_id = change_dct['auth_id']
            index = file_dct[change_auth_id]['index']
            change_dct['idx'] = index
    except Exception as e:
        err = repr(e)
        log.exception( 'Problem assigning row indices; admins will be emailed.' )
    return err


def update_lines( lines ):
    """ Updates proper row for each change-dct entry.
        Called by process_csv() """
    assert type( lines ) == list
    ( updated_lines, err ) = ( [], [] )
    try:
        for change_dct in settings['CHANGES']:
            log.debug( f'changing ``{change_dct["auth_id"]}``' )
            ## setup change vars --------------------
            lookup_index = change_dct['idx']
            trgt = change_dct['target']
            rplcmnt = change_dct['replacement']
            ## get line to update -------------------
            evaluation_line = lines[lookup_index+1]
            log.debug( f'before, ``{evaluation_line}``')
            ## update -------------------------------
            if trgt in evaluation_line:
                evaluation_line = evaluation_line.replace( trgt, rplcmnt )
                lines[lookup_index+1] = evaluation_line
            else:
                err.append( f' no target for ``{change_dct["auth_id"]}`` found')
            log.debug( f'after, ``{evaluation_line}``')
        updated_lines = lines
        err = repr(err)
    except Exception as e:
        err = repr(e)
        log.exception( 'Problem updating lines; admins will be emailed.' )
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
        body = f'datetime: ``{str(datetime.datetime.now())}``\n\nerror...\n``{err}``\n\n[END]'
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
