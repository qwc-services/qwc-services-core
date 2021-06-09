[![PyPI version](https://img.shields.io/pypi/v/qwc-services-core)](https://pypi.org/project/qwc-services-core)


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
      - [Database migrations](#database_migrations)
    - [Service configurations](#service-configurations)
- [Resources and Permissions](#resources-and-permissions)
    - [Resources](#resources)
    - [Permissions](#permissions)
- [Group registration](#group_registration)
- [Development](#development)


Overview
--------

The QWC Services are a collection of microservices providing configurations for and authorized access to different QWC Map Viewer components.

![qwc-services-arch](doc/qwc-services-arch.png)

QWC Services
------------

Applications:
* [Map Viewer](https://github.com/qwc-services/qwc-map-viewer)
* [QWC configuration backend](https://github.com/qwc-services/qwc-admin-gui)
* [Registration GUI](https://github.com/qwc-services/qwc-registration-gui)

REST services:
* [Authentication service with local user database](https://github.com/qwc-services/qwc-db-auth)
* [OGC service](https://github.com/qwc-services/qwc-ogc-service)
* [Data service](https://github.com/qwc-services/qwc-data-service)
* [Permalink service](https://github.com/qwc-services/qwc-permalink-service)
* [Elevation service](https://github.com/qwc-services/qwc-elevation-service)
* [Mapinfo service](https://github.com/qwc-services/qwc-mapinfo-service)
* [Document service](https://github.com/qwc-services/qwc-document-service)
* [Print service](https://github.com/qwc-services/qwc-print-service)
* [Fulltext search service](https://github.com/qwc-services/qwc-fulltext-search-service)

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

Create a secret key:

    python3 -c 'import secrets; print("JWT_SECRET_KEY=\"%s\"" % secrets.token_hex(48))' >.env

Set permissions for writable volumes:

    sudo chown -R www-data:www-data volumes/qgs-resources
    sudo chown -R www-data:www-data demo-config
    sudo chown -R www-data:www-data volumes/qwc2/assets

    sudo chown 8983:8983 volumes/solr/data

### Run containers

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

### Add a QGIS project

Setup PostgreSQL connection service file `~/.pg_service.conf`
for DB connections from the host machine to PostGIS container:

```
cat >>~/.pg_service.conf <<EOS
[qwc_geodb]
host=localhost
port=5439
dbname=qwc_demo
user=qwc_service
password=qwc_service
sslmode=disable
EOS
```

* Open project `demo-projects/natural-earth-countries.qgz` with QGIS and save as `volumes/config-in/default/qgis_projects/natural-earth-countries.qgs`
* Update configuration in Admin GUI

### Add an editable layer

* Add `edit_polygon` layer in QGIS project
* Add map and data resources with permissions
* Update configuration in Admin GUI

### Add a custom edit form

Adapt edit form with Drag and Drop Designer:
* Change attribute form type to `Drag and Drop Designer`.
* Change form layout
* Update configuration in Admin GUI

Use the previously generated edit form in `volumes/qwc2/assets/forms/autogen/` as a template.

Edit and save the form with QT Designer.

Copy the form into the volumes:

    sudo cp natural-earth-countries_edit_polygons.ui volumes/config-in/default/qgis_projects/
    sudo cp natural-earth-countries_edit_polygons.ui volumes/qgs-resources/

Change attribute form type to `Provide ui-file`.

Select `natural-earth-countries_edit_polygons.ui` as `Edit UI`.

Update configuration in Admin GUI.

### Customize QWC2 Viewer

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
    cp -r translations $DSTDIR/qwc2/ && \
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

    cp volumes/qwc2/themesConfig-example.json volumes/qwc2/themesConfig.json


Configuration
-------------

### Configuration database

The [Configuration database](https://github.com/qwc-services/qwc-config-db) (ConfigDB) contains the database schema `qwc_config` for configurations and permissions of QWC services.

This database uses the PostgreSQL connection service `qwc_configdb` by default, which can be setup for the corresponding database in the PostgreSQL connection service file `pg_service.conf`. This default can be overridden by setting the environment variable `CONFIGDB_URL` to a custom DB connection string (see [below](#service-configurations)).

Additional user fields are saved in the table `qwc_config.user_infos` with a a one-to-one relation to `qwc_config.users` via the `user_id` foreign key.
To add custom user fields, add new columns to your `qwc_config.user_infos` table and set your `USER_INFO_FIELDS` accordingly (see [below](#service-configurations)).


#### Database migrations

An existing ConfigDB can be updated to the latest schema by running the database migrations from the `qwc-config-db` directory:

    cd qwc-config-db/
    git pull
    alembic upgrade head


### Service configurations

The QWC Services are generally configured using environment variables.
These can be set when running the services locally or in `docker-compose.yml` when using Docker.

Common configuration:

ENV                   | default value      | description
----------------------|--------------------|---------
`CONFIG_PATH`         | .                  | Base path for service configuration files
`JWT_SECRET_KEY`      | `********`         | secret key for JWT token
`TENANT_URL_RE`       | None               | Regex for tenant extraction from base URL. Example: ^https?://.+?/(.+?)/
`TENANT_HEADER`       | None               | Tenant Header name. Example: Tenant


See READMEs of services for details.


Resources and Permissions
-------------------------

Permissions and configurations are based on different resources with assigned permissions in the [configuration database](https://github.com/qwc-services/qwc-config-db).
These can be managed in the [QWC configuration backend](https://github.com/qwc-services/qwc-admin-gui).


### Resources

The following resource types are available:

* `map`: WMS corresponding to a QGIS Project
    * `layer`: layer of a map
        * `attribute`: attribute of a map layer
    * `print_template`: print composer template of a QGIS Project
    * `data`: Data layer for editing
        * `attribute`: attribute of a data layer
    * `data_create`: Data layer for creating features
    * `data_read`: Data layer for reading features
    * `data_update`: Data layer for updating features
    * `data_delete`: Data layer for deleting features
* `viewer`: custom map viewer configuration
* `viewer_task`: permittable viewer tasks

The resource `name` corresponds to the technical name of its resource (e.g. WMS layer name).

The resource types can be extended by inserting new types into the `qwc_config.resource_types` table.
These can be queried, e.g. in a custom service, by using `PermissionClient::resource_permissions()` or 
`PermissionClient::resource_restrictions()` from [QWC Services Core](https://github.com/qwc-services/qwc-services-core).

Available `map`, `layer`, `attribute` and `print_template` resources are collected from WMS `GetProjectSettings` and the QGIS projects.

`data` and their `attribute` resources define a data layer for the [Data service](https://github.com/qwc-services/qwc-data-service).
Database connections and attribute metadata are collected from the QGIS projects.

For more detailed CRUD permissions `data_create`, `data_read`, `data_update` and `data_delete` can be used instead of `data` 
(`data` and `write=False` is equivalent to `data_read`; `data` and `write=True` is equivalent to all CRUD resources combined).

The `viewer` resource defines a custom viewer configuration for the map viewer (see [Custom viewer configurations](https://github.com/qwc-services/qwc-map-viewer#custom-viewer-configurations)).

The `viewer_task` resource defines viewer functionalities (e.g. printing or raster export) that can be restricted or permitted.
Their `name` (e.g. `RasterExport`) corresponds to the `key` in `menuItems` and `toolbarItems` in the QWC2 `config.json`. Restricted viewer task items are then removed from the menu and toolbar in the map viewer. Viewer tasks not explicitly added as resources are kept unchanged from the `config.json`.


### Permissions

Permissions are based on roles. Roles can be assigned to groups or users, and users can be members of groups.
A special role is `public`, which is always included, whether a user is signed in or not.

Each role can be assigned a permission for a resource.
The `write` flag is only used for `data` resources and sets whether a data layer is read-only.

Based on the user's identity (user name and/or group name), all corresponding roles and their permissions and restrictions are collected.
The service configurations are then modified according to these permissions and restrictions.

Using the `DEFAULT_ALLOW` environment variable, some resources can be set to be permitted or restricted by default if no permissions are set (default: `False`). Affected resources are `map`, `layer`, `print_template` and `viewer_task`.

e.g. `DEFAULT_ALLOW=True`: all maps and layers are permitted by default
e.g. `DEFAULT_ALLOW=False`: maps and layers are only available if their resources and permissions are explicitly configured


Group registration
------------------

Using the optional [Registration GUI](https://github.com/qwc-services/qwc-registration-gui) allows users to request membership or unsubscribe from registrable groups. These requests can then be accepted or rejected in the [Admin GUI](https://github.com/qwc-services/qwc-admin-gui).

Workflow:
* Admin GUI
  * admin user creates new groups with assigned roles and permissions on resources
  * admin user configures registrable groups
* Registration GUI
  * user select desired groups from registrable groups and submits application form
  * admin users are notified of new registration requests
* Admin GUI
  * admin user selects entry from list of pending registration requests
  * admin user accepts or rejects registration requests for a user
  * user is added to or removed from accepted groups
  * user is notified of registration request updates
* Map Viewer
  * user permissions are updated for new groups


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
