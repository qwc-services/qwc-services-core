QWC Services Core
=================

Shared modules for QWC services and documentation for setup.


Table of Contents
-----------------

- [Overview](#overview)
- [QWC Services](#qwc-services)
- [Quick start](#quick-start)
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
