# xi-mzidentml-converter
[![Codeship Status for Rappsilber-Laboratory/xiSPEC_ms_parser](https://app.codeship.com/projects/9efffa03-5f03-4cc6-b2b3-0a9eddbe0678/status?branch=python3)](https://app.codeship.com/projects/451392)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Parser for mzIdentML for 1.2.0 files extracting crosslink information. Results are written to a relational database (PostgreSQL or SQLite).

### Requirements:
python3.10

pipenv

sqlite3 or postgresql

### Installation

Clone git repository into your web-server directory (e.g. /var/www/html):

```git clone https://github.com/Rappsilber-Laboratory/xiSPEC_ms_parser.git```

cd into the repository:

```cd xiSPEC_ms_parser```

Checkout python3 branch:

```git checkout python3```

Create pipenv:

```pipenv install --python 3.10```

Create uploads directory:

```mkdir ../uploads```

Change owner of uploads directory to www-data:

```sudo chown www-data:www-data ../uploads/```

Change owner of log directory to www-data:

```sudo chown www-data:www-data log```

Change owner of dbs directory (and sub directories) to www-data:

```sudo chown -R www-data:www-data dbs```


### Run tests

make sure we have the right db user available
```
psql -p 5432 -c "create role ximzid_unittests with password 'ximzid_unittests';"
psql -p 5432 -c 'alter role ximzid_unittests with login;'
psql -p 5432 -c 'alter role ximzid_unittests with createdb;'
psql -p 5432 -c 'GRANT pg_signal_backend TO ximzid_unittests;'
```
run the tests

```pipenv run pytest```
