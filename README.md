# Web Service  

django front end web service displaying historical data and prediction data from the database.

## Configuration

Configuration for environment specific things is done via env variables.

### User Database

The database must be a postgres instance, fallback is a local db.sqlite3 database, which is not persisted.

Following values can be specified:

* `DB_NAME`
* `DB_USER`
* `DB_PASSWORD`
* `DB_HOST`
* `DB_PORT`

If any of them is not available, service will fall back to aforementioned sqlite db.

### Stock Database

* `DATA_DB_USER`, default: `root`
* `DATA_DB_PASSWORD`, default: `password`
* `DATA_DB_HOST`, default: `0.0.0.0`
* `DATA_DB_PORT`, default: `3306`
* `DATA_DB_PORT`, default: `stock_db`

### Config Service

* `CONFIG_ADDRESS`, default: `0.0.0.0:5000`