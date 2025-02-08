[![PyPI version](https://img.shields.io/pypi/v/qwc-services-core)](https://pypi.org/project/qwc-services-core)


QWC Services Core
=================

The QWC Services are a collection of microservices providing configurations for and authorized access to different QWC Map Viewer components.

See [QWC Docker](https://github.com/qwc-services/qwc-docker/) for using QWC Services with Docker.

This repository contains the shared modules for QWC services.


Environment variables
=====================

| Name                         | Default                     | Description                                                                         |
|------------------------------|-----------------------------|-------------------------------------------------------------------------------------|
| `JWT_SECRET_KEY`             | `<random>`                  | Secret key used to encode and decode JWTs.                                          |
| `JWT_COOKIE_CSRF_PROTECT`    | `True`                      | Controls whether CSRF is enabled in JWT cookies.                                    |
| `JWT_ACCESS_COOKIE_NAME`     | `access_token_cookie`       | Name of the JWT access cookie.                                                      |
| `QWC_SERVICE_PREFIX`         | ``                          | URL path prefix for all QWC services for single-tenant setups.                      |
| `OVERRIDE_ACCESS_COOKIE_PATH`| `<service_prefix>`          | Path for which the access cookie is valid.                                          |
| `TENANT_HEADER`              | `<empty>`                   | The name of the HTTP header which contains the tenant name for multi-tenant setups. |
| `TENANT_PATH_PREFIX`         | `@service_prefix@/@tenant@` | URL path prefix for all QWC services for multi-tenant setups.                       |
| `TENANT_ACCESS_COOKIE_PATH`  | `<tenant_path_prefix>`      | Path for which the access cookie is valid for multi-tenant setups.                  |

Development
===========

This repository contains a [justfile](https://just.systems/man/en/) with various helper tasks for releasing etc.
Add a symlink to it in the parent directory of the qwc-services repositories:

    ln -s qwc-services-core/scripts/justfile ..

To use a local version of QWC Services Core for development, replace the
`qwc-services-core` module URL in `requirements.txt` of each service with an URL
pointing to the local files:

    # git+git://github.com/qwc-services/qwc-services-core.git#egg=qwc-services-core
    file:../qwc-services-core/#egg=qwc-services-core
