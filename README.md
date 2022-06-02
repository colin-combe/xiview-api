# xiSPEC_ms_parser

Back-end parser for xiSPEC mass spectrometry visualization tool.


### Requirements:
python3.10

pipenv

sqlite3

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
