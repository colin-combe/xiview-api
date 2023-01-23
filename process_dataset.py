import argparse
import sys
import os
import socket
import requests
import time
import ftplib
from urllib.parse import urlparse
import logging

from parser.MzIdParser import MzIdParser
from parser.writer import Writer

import credentials as db


def get_ftp_login(ftp_ip):
    time.sleep(10)
    try:
        ftp = ftplib.FTP(ftp_ip)
        ftp.login()  # Uses password: anonymous@
        return ftp
    except ftplib.all_errors as e:
        print('FTP fail at ' + time.strftime("%c"))
        print(e)


def get_ftp_file_list(ftp_ip, dir):
    ftp = get_ftp_login(ftp_ip)
    try:
        ftp.cwd(dir)
    except ftplib.error_perm as e:
        error_msg = "%s: %s" % (dir, e.args[0])
        print(error_msg)
        ftp.quit()
        return []
    filelist = []
    try:
        filelist = ftp.nlst()
    except ftplib.error_perm as resp:
        if str(resp) == "550 No files found":
            print("FTP: No files in this directory")
        else:
            error_msg = "%s: %s" % (dir, ftplib.error_perm.args[0])
            print(error_msg)
    ftp.close()
    return filelist


if __name__ == "__main__":
    # arguments, one of three options to specify location of data
    parser = argparse.ArgumentParser(
        description='Process mzIdentML files in a dataset and load them into a relational database.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-p', '--pxid',
                       help='proteomeXchange accession, should be of the form PXDnnnnnn or numbers only', )
    group.add_argument('-f', '--ftp',
                       help='process files from specified ftp location, e.g. ftp://ftp.jpostdb.org/JPST001914/')
    group.add_argument('-d', '--dir',
                       help='process files in specified local directory, e.g. /home/user/data/JPST001914')
    args = parser.parse_args()
    # only one of the three options will be specified
    px_accession = args.pxid
    ftp_url = args.ftp
    local_dir = args.dir

    temp_dir = os.path.expanduser('~/mzId_convertor_temp')

    if px_accession:
        # get ftp location from PX
        px_url = 'http://proteomecentral.proteomexchange.org/cgi/GetDataset?ID=' + px_accession + '&outputMode=JSON'
        print('GET request to ProteomeExchange: ' + px_url)
        pxresponse = requests.get(px_url)
        r = requests.get(px_url)
        if r.status_code == 200:
            print('ProteomeExchange returned status code 200')
            px_json = pxresponse.json()
            for dataSetLink in px_json['fullDatasetLinks']:
                # name check is necessary because some things have wrong acc, e.g. PXD006574
                if dataSetLink['accession'] == "MS:1002852" or dataSetLink['name'] == "Dataset FTP location":
                    ftp_url = dataSetLink['value']
                    break
            if not ftp_url:
                print('Error: Dataset FTP location not found in ProteomeXchange response')
                sys.exit(1)
            for identifier in px_json['identifiers']:
                if identifier['accession'] == "MS:1001919":
                    px_accession = identifier['value']
                    break
        else:
            print('Error: ProteomeXchange returned status code ' + str(pxresponse.status_code))
            sys.exit(1)

    if ftp_url:
        if not ftp_url.startswith('ftp://'):
            print('Error: FTP location must start with ftp://')
            sys.exit(1)
        if not os.path.isdir(temp_dir):
            try:
                os.mkdir(temp_dir)
            except OSError as e:
                print('Failed to create temp directory ' + temp_dir)
                print('Error: ' + e.strerror)
                sys.exit(1)
        print('FTP url: ' + ftp_url)
        parsed_url = urlparse(ftp_url)
        if not px_accession:
            px_accession = parsed_url.path.rsplit("/", 1)[-1]
        path = os.path.join(temp_dir, px_accession)
        try:
            os.mkdir(path)
        except OSError:
            pass
        ftp_ip = socket.getaddrinfo(parsed_url.hostname, 21)[0][4][0]
        files = get_ftp_file_list(ftp_ip, parsed_url.path)
        for f in files:
            # check file not already in temp dir
            if not (os.path.isfile(os.path.join(path, f))
                    or f.lower == "generated"  # dunno what these files are but they seem to make ftp break
                    or f.lower().endswith('raw')
                    or f.lower().endswith('raw.gz')
                    or f.lower().endswith('all.zip')):
                print('Downloading ' + f + ' to ' + path)
                ftp = get_ftp_login(ftp_ip)
                try:
                    ftp.cwd(parsed_url.path)
                    ftp.retrbinary("RETR " + f, open(os.path.join(path, f), 'wb').write)
                    ftp.quit()
                except ftplib.error_perm as e:
                    ftp.quit()
                    error_msg = "%s: %s" % (f, e.args[0])
                    # self.logger.error(error_msg)
                    raise e
                    System.exit(1)
        local_dir = path

    #  iterate over files in local_dir
    for file in os.listdir(local_dir):
        if file.endswith(".mzid") or file.endswith(".mzid.gz"):
            print("Processing " + file)
            logging.basicConfig(level=logging.DEBUG,
                                format='%(asctime)s %(levelname)s %(name)s %(message)s')

            logger = logging.getLogger(__name__)
            conn_str = f'postgresql://{db.username}:{db.password}@{db.hostname}:{db.port}/{db.database}'
            writer = Writer(conn_str, pxid=px_accession)
            id_parser = MzIdParser(os.path.join(local_dir, file), local_dir, local_dir, writer, logger)
            try:
                id_parser.parse()
                # print(id_parser.warnings + "\n")
            except Exception as e:
                logger.exception(e)
                raise e
                System.exit(1)
            mzid_parser = None
            # gc.collect()
        else:
            continue

    # remove downloaded files
    if ftp_url:
        try:
            shutil.rmtree(local_dir)
        except OSError as e:
            print('Failed to delete temp directory ' + local_dir)
            print('Error: ' + e.strerror)
            sys.exit(1)
