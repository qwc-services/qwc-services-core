QWC Services Core
=================

Shared modules for QWC services and documentation for setup.


Table of Contents
-----------------

- [Overview](#overview)
- [QWC Services](#qwc-services)
- [Quick start](#quick-start)
- [Configuration](#configuration)
    - [Configuration database](#configuration-database)
    - [Service configurations](#service-configurations)
- [Development](#development)


Overview
--------

The QWC Services are a collection of microservices providing configurations for and authorized access to different QWC Map Viewer components.

                                   external services    |    internal services    
                                                        |
    +-------------------+
    |                   |
    |  Admin GUI        +-----------------------------------------------------------------------------+
    |                   |                                                                             |
    +-------------------+                                                                             |
                                                                                                      |
                                +-------------------+                                                 |
                 authentication |                   |                                                 |
              +----------------->  Auth Service     +-----------------------------------------+       |
              |                 |  (qwc-db-auth)    |                                         |       |
              |                 +-------------------+                                         |       |
              |                                                                               |       |
    +---------+---------+                                                                     |       |
    |                   |  viewer config and maps                                             |       |
    |  QWC Map Viewer   +---------------------------------------------+                       |       |
    |                   |                                             |                       |       |
    +---------+---------+                                             |                       |       |
              |                                                       |                       |       |
              |                 +-------------------+       +---------v---------+       .-----v-------v-----.
              |  GeoJSON        |                   |       |                   +------->                   |
              +----------------->  Data Service     +---+--->  Config Service   |       |  Config DB        |
              |                 |                   |   |   |                   +---+   |                   |
              |                 +-------------------+   |   +---------+---------+   |   '-------------------'
              |                                         |             |             |
              |                 +-------------------+   |   +---------v---------+   |   .-------------------.
              |  WMS            |                   +---+   |                   |   +--->                   |
              +----------------->  OGC Service      |       |  QGIS Server      |       |  Geo DB           |
                                |                   +------->                   +------->                   |
                                +-------------------+       +-------------------+       '-------------------'


QWC Services
------------

Applications:
* [Map Viewer](https://github.com/qwc-services/qwc-map-viewer)
* [QWC configuration backend](https://github.com/qwc-services/qwc-admin-gui)

REST services:
* [Config service](https://github.com/qwc-services/qwc-config-service)
* [OGC service](https://github.com/qwc-services/qwc-ogc-service)
* [Data service](https://github.com/qwc-services/qwc-data-service)
* [Authentication service with local user database](https://github.com/qwc-services/qwc-db-auth)

Configuration database:
* [DB schema and migrations](https://github.com/qwc-services/qwc-config-db)

Docker:
* [Docker containers for QWC services](https://github.com/qwc-services/qwc-docker)


Quick start
-----------

### Docker containers for QWC services

Create a QWC services dir:

    mkdir qwc-services
    cd qwc-services/

Clone [Docker containers for QWC services](https://github.com/qwc-services/qwc-docker):

    git clone https://github.com/qwc-services/qwc-docker.git

Install Docker and setup containers (see [qwc-docker README](https://github.com/qwc-services/qwc-docker#setup)):

    cd qwc-docker/
    cp docker-compose-example.yml docker-compose.yml
    cp volumes/qwc2/themesConfig-example.json volumes/qwc2/themesConfig.json
    docker-compose build

Clone and build QWC2 Demo App (see [Quick start](https://github.com/qgis/qwc2-demo-app/blob/master/doc/QWC2_Documentation.md#quick-start)) (or use your custom QWC2 build):

    cd ..
    git clone --recursive https://github.com/qgis/qwc2-demo-app.git
    cd qwc2-demo-app/
    yarn install
    yarn run build

**NOTE:** The basic [QWC2 Demo App](https://github.com/qgis/qwc2-demo-app) build does not include a sign in menu entry or editing.

Copy QWC2 files from a build:

    cd ../qwc-docker/
    SRCDIR=../qwc2-demo-app/ DSTDIR=$PWD/volumes
    cd $SRCDIR && \
    cp -r assets $DSTDIR/qwc2 && \
    cp -r translations/data.* $DSTDIR/qwc2 && \
    cp dist/QWC2App.js $DSTDIR/qwc2/dist/ && \
    cp index.html $DSTDIR/qwc2/ && \
    sed -e '/proxyServiceUrl/d' \
      -e 's!permalinkServiceUrl":\s*".*"!permalinkServiceUrl": "/permalink"!' \
      -e 's!elevationServiceUrl":\s*".*"!elevationServiceUrl": "/elevation"!' \
      -e 's!searchServiceUrl":\s*".*"!searchServiceUrl": "/search"!' \
      -e 's!editServiceUrl":\s*".*"!editServiceUrl": "/data"!' \
      -e 's!authServiceUrl":\s*".*"!authServiceUrl": "/auth"!' \
      -e 's!mapInfoService":\s*".*"!mapInfoService": "/mapinfo"!' \
      -e 's!featureReportService":\s*".*"!featureReportService": "/document"!' \
      -e 's!{"key": "Login", "icon": "img/login.svg"}!{{ login_logout_item }}!g' \
      config.json > $DSTDIR/qwc2/config.json && \
    cd -

Start all containers:

    docker-compose up -d

Follow log output:

    docker-compose logs -f

Open map viewer:

    http://localhost:8088/

Open Admin GUI (Admin user: `admin:admin`, requires password change on first login):

    http://localhost:8088/qwc_admin

Sign in (Demo user: `demo:demo`):

    http://localhost:8088/auth/login

Sign out:

    http://localhost:8088/auth/logout

Stop all containers:

    docker-compose down


Configuration
-------------

### Configuration database

The [Configuration database](https://github.com/qwc-services/qwc-config-db) (ConfigDB) contains the database schema `qwc_config` for configurations and permissions of QWC services.

This database uses the PostgreSQL connection service `qwc_configdb` by default, which can be setup for the corresponding database in the PostgreSQL connection service file `pg_service.conf`. This default can be overridden by setting the environment variable `CONFIGDB_URL` to a custom DB connection string (see [below](#service-configurations)).

Additional user fields are saved in the table `qwc_config.user_infos` with a a one-to-one relation to `qwc_config.users` via the `user_id` foreign key.
To add custom user fields, add new columns to your `qwc_config.user_infos` table and set your `USER_INFO_FIELDS` accordingly (see [below](#service-configurations)).


### Service configurations

The QWC Services are generally configured using environment variables.
These can be set when running the services locally or in `docker-compose.yml` when using Docker.

See READMEs of services for details.


#### [Map Viewer](https://github.com/qwc-services/qwc-map-viewer#configuration)

ENV                                     | default value                         | description
----------------------------------------|---------------------------------------|---------
`JWT_SECRET_KEY`                        | `********`                            | secret key for JWT token (same for all services) 
`CONFIG_SERVICE_URL`                    | `http://localhost:5010/`              | QWC Config service URL
`OGC_SERVICE_URL`                       | `http://localhost:5013/`              | QWC OGC service URL or QGIS server URL
`DATA_SERVICE_URL`                      | `http://localhost:5012/`              | QWC Data service URL


ENV (optional)                          | default value                         | description
----------------------------------------|---------------------------------------|---------
`QWC2_PATH`                             | `qwc2/`                               | QWC2 files path
`QWC2_CONFIG`                           | `$QWC2_PATH/config.json`              | QWC2 `config.json` path
`QWC2_VIEWERS_PATH`                     | `$QWC2_PATH/viewers/`                 | QWC2 custom viewers path
`CONFIG_CHECK_INTERVAL`                 | `60`s                                 | check if config cache is valid every x seconds
`DEFAULT_CONFIG_CACHE_DURATION`         | `86400`s (24h)                        | time in seconds until config cache expiry
`ORIGIN_CONFIG`                         | `{"host": {"_intern_": "^127.0.0.1(:\\\\d+)?$"}}` | origin detection rules
`AUTH_SERVICES_CONFIG`                  | `{}`                                  | auth service lookups
`AUTH_SERVICE_URL`                      | from `config.json`                    | QWC Authorization service URL
`DOCUMENT_SERVICE_URL`                  | from `config.json`                    | QWC Document service URL
`ELEVATION_SERVICE_URL`                 | from `config.json`                    | QWC Elevation service URL
`INFO_SERVICE_URL`                      | from `config.json`                    | QWC Feature Info proxy service URL
`LEGEND_SERVICE_URL`                    | from `config.json`                    | QWC Data service URL
`MAPINFO_SERVICE_URL`                   | from `config.json`                    | QWC Map Info service URL
`PERMALINK_SERVICE_URL`                 | from `config.json`                    | QWC Permalink service URL
`PRINT_SERVICE_URL`                     | from `config.json`                    | QWC Print service URL
`SEARCH_SERVICE_URL`                    | from `config.json`                    | QWC Search service URL


Custom viewer configurations can be added by placing a `<viewer>.json` and/or `<viewer>.html` for each custom viewer into the `$QWC2_VIEWERS_PATH` directory. The custom viewers can be opened by appending the viewer name to the base URL: `http://localhost:8088/<viewer>/`.


#### [Admin GUI](https://github.com/qwc-services/qwc-admin-gui#configuration)

ENV                                     | default value                         | description
----------------------------------------|---------------------------------------|---------
`JWT_SECRET_KEY`                        | `********`                            | secret key for JWT token (same for all services) 


ENV (optional)                          | default value                         | description
----------------------------------------|---------------------------------------|---------
`USER_INFO_FIELDS`                      | `[]`                                  | custom user info fields JSON 


#### [Config service](https://github.com/qwc-services/qwc-config-service#configuration)

ENV                                     | default value                         | description
----------------------------------------|---------------------------------------|---------
`QGIS_SERVER_URL`                       | `http://localhost:8001/ows/`          | QGIS server URL
`QGIS_RESOURCES_PATH`                   | `qgs/`                                | QGIS project files path
`QWC2_PATH`                             | `qwc2/`                               | QWC2 files path
`QWC2_THEMES_CONFIG`                    | `$QWC2_PATH/themesConfig.json`        | QWC2 `themesConfig.json` path
`DEFAULT_ALLOW`                         | `True`                                | set whether some resources are permitted or restricted by default


#### [OGC service](https://github.com/qwc-services/qwc-ogc-service#usage)

ENV                                     | default value                         | description
----------------------------------------|---------------------------------------|---------
`JWT_SECRET_KEY`                        | `********`                            | secret key for JWT token (same for all services) 
`QGIS_SERVER_URL`                       | `http://localhost:8001/ows/`          | QGIS server URL
`CONFIG_SERVICE_URL`                    | `http://localhost:5010/`              | QWC Config service URL


ENV (optional)                          | default value                         | description
----------------------------------------|---------------------------------------|---------
`CONFIG_CHECK_INTERVAL`                 | `60`s                                 | check if config cache is valid every x seconds
`DEFAULT_CONFIG_CACHE_DURATION`         | `86400`s (24h)                        | time in seconds until config cache expiry


#### [Data service](https://github.com/qwc-services/qwc-data-service#usage)

ENV                                     | default value                         | description
----------------------------------------|---------------------------------------|---------
`JWT_SECRET_KEY`                        | `********`                            | secret key for JWT token (same for all services) 
`CONFIG_SERVICE_URL`                    | `http://localhost:5010/`              | QWC Config service URL


ENV (optional)                          | default value                         | description
----------------------------------------|---------------------------------------|---------
`CONFIG_CHECK_INTERVAL`                 | `60`s                                 | check if config cache is valid every x seconds
`DEFAULT_CONFIG_CACHE_DURATION`         | `86400`s (24h)                        | time in seconds until config cache expiry


#### [Authentication service with local user database](https://github.com/qwc-services/qwc-db-auth#configuration)

ENV                                     | default value                         | description
----------------------------------------|---------------------------------------|---------
`JWT_SECRET_KEY`                        | `********`                            | secret key for JWT token (same for all services) 


ENV (optional)                          | default value                         | description
----------------------------------------|---------------------------------------|---------
`MAX_LOGIN_ATTEMPTS`                    | `20`                                  | maximum number of 
failed login attempts before sign in is blocked for an user
`POST_PARAM_LOGIN`                      | `False`                               | activate (insecure) plain POST login
`MAIL_SERVER`                           | `localhost`                           | [Flask-Mail](https://pythonhosted.org/Flask-Mail/) options (for sending password recovery instructions)
`MAIL_PORT`                             | `25`                                  | "
`MAIL_USE_TLS`                          | `False`                               | "
`MAIL_USE_SSL`                          | `False`                               | "
`MAIL_DEBUG`                            | `app.debug`                           | "
`MAIL_USERNAME`                         | `None`                                | "
`MAIL_PASSWORD`                         | `None`                                | "
`MAIL_DEFAULT_SENDER`                   | `None`                                | "
`MAIL_MAX_EMAILS`                       | `None`                                | "
`MAIL_SUPPRESS_SEND`                    | `app.testing`                         | "
`MAIL_ASCII_ATTACHMENTS`                | `False`                               | "


Development
-----------

Create a QWC services dir:

    mkdir qwc-services
    cd qwc-services/

Clone [QWC Config DB](https://github.com/qwc-services/qwc-config-db):

    git clone https://github.com/qwc-services/qwc-config-db.git

Clone [QWC Config service](https://github.com/qwc-services/qwc-config-service):

    git clone https://github.com/qwc-services/qwc-config-service.git

Clone [QWC OGC service](https://github.com/qwc-services/qwc-ogc-service):

    git clone https://github.com/qwc-services/qwc-ogc-service.git

Clone [QWC Data service](https://github.com/qwc-services/qwc-data-service):

    git clone https://github.com/qwc-services/qwc-data-service.git

Clone [QWC Map Viewer](https://github.com/qwc-services/qwc-map-viewer):

    git clone https://github.com/qwc-services/qwc-map-viewer.git

Clone [QWC Admin GUI](https://github.com/qwc-services/qwc-admin-gui):

    git clone https://github.com/qwc-services/qwc-admin-gui.git

See READMEs of each service for their setup.

Setup your ConfigDB and run migrations (see [QWC Config DB](https://github.com/qwc-services/qwc-config-db)). 

Run local services (set `$QGIS_SERVER_URL` to your QGIS server and `$QWC2_PATH` to your QWC2 files):

    cd qwc-config-service/
    QGIS_SERVER_URL=http://localhost:8001/ows/ QWC2_PATH=qwc2/ python server.py

    cd qwc-ogc-service/
    QGIS_SERVER_URL=http://localhost:8001/ows/ CONFIG_SERVICE_URL=http://localhost:5010/ python server.py

    cd qwc-data-service/
    CONFIG_SERVICE_URL=http://localhost:5010/ python server.py

    cd qwc-map-viewer/
    OGC_SERVICE_URL=http://localhost:5013/ CONFIG_SERVICE_URL=http://localhost:5010/ QWC2_PATH=qwc2/ python server.py

    cd qwc-admin-gui/
    python server.py

Sample requests:

    curl 'http://localhost:5010/ogc?ows_type=WMS&ows_name=qwc_demo'
    curl 'http://localhost:5010/qwc'
    curl 'http://localhost:5013/qwc_demo?VERSION=1.1.1&SERVICE=WMS&REQUEST=GetCapabilities'
    curl 'http://localhost:5012/qwc_demo.edit_points/'
    curl 'http://localhost:5030/themes.json'
    curl 'http://localhost:5031'

To use a local version of QWC Services Core for development, replace the
`qwc-services-core` module URL in `requirements.txt` of each service with an URL
pointing to the local files:

    # git+git://github.com/qwc-services/qwc-services-core.git#egg=qwc-services-core
    file:../qwc-services-core/#egg=qwc-services-core
