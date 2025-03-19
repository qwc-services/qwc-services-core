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
| `POOL_SIZE`                  | `5`                         | Maximum number of possible data base connections.                                   |
| `MAX_OVERFLOW`               | `10`                        | Additional connections beyond pool_size during peak load.                           |
| `POOL_TIMEOUT`               | `30`                        | Time (in seconds) to wait for a connection to become available.                     |
| `POOL_RECYCLE`               | `-1`                        | Time (in seconds) after idle connections will be resetted.                          |

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

QWC unified permissions
=======================

A unified and simplified permissions format is also supported, if there is only a single WMS/WFS resource and resource permissions are identical in all QWC Services.
This may be used as an alternative to the full QWC permission file ([JSON schema](https://github.com/qwc-services/qwc-services-core/blob/master/schemas/qwc-services-permissions.json))


## Structure

* [JSON schema](https://github.com/qwc-services/qwc-services-core/blob/master/schemas/qwc-services-unified-permissions.json)
* File location: `$CONFIG_PATH/<tenant>/permissions.json`

`all_services`: resources permitted for a role
* top-level dataproducts below WMS root layer or WFS layers
* additional restricted layers
* additional layers with write permissions (`"writable": true`)
* document templates

`wms_name`: Name of WMS service and its root layer

`wfs_name`: WFS service name

`dataproducts`: nested details for dataproducts referenced from `all_services` and `sublayers`

`common_resources`: additional resources with no restrictions
* internal print layers
* background layers
* print templates
* default Solr facets


## Example

Example unified permissions for the following resources:

WMS layer tree:
```
* demo_wms (WMS root layer)
  * single_layer
  * group_layer
    * facade_layer (facade layer)
      * sublayer_a
      * sublayer_b
    * edit_layer
    * restricted_layer
  * osm_bg (internal print layer for 'osm' background layer)
```

WFS layers (potential, not all have to actually be present in the WFS project file):
```
* single_layer
* sublayer_a
* sublayer_b
* edit_layer
* restricted_layer
```

Background layer: `osm`

Print template: `A4 Landscape`

Document template: `demo_doc`

Unified `permissions.json`:
```jsonc
{
  "schema": "https://github.com/qwc-services/qwc-services-core/raw/master/schemas/qwc-services-unified-permissions.json",
  "users": [
    {
      "name": "demo",
      "groups": ["demo"],
      "roles": []
    }
  ],
  "groups": [
    {
      "name": "demo",
      "roles": ["edit_demo"]
    }
  ],
  "roles": [
    {
      "role": "public",
      "permissions": {
        "all_services": {
          // top-level dataproducts: references to "dataproducts"
          "single_layer": {},
          "group_layer": {},
          "facade_layer": {},
          // document templates
          "demo_doc": {}
        }
      }
    },
    {
      "role": "edit_demo",
      "permissions": {
        "all_services": {
          // additional restricted layers
          "restricted_layer": {},
          // additional layers with write permissions (default: writable=false)
          "edit_layer": {
            "writable": true
          }
        }
      }
    }
  ],
  // WMS name for wms_services
  "wms_name": "demo_wms",
  // WFS name for wfs_services
  "wfs_name": "demo_wfs",
  // details for dataproducts referenced from "all_services" and "sublayers"
  "dataproducts": [
    // single layer
    {
      "name": "single_layer",
      "attributes": [
        // permitted attributes, excluding "geometry"
        "name", "number", "description"
      ]
    },
    // group layer
    {
      "name": "group_layer",
      "sublayers": [
        // references to other "dataproducts"
        "facade_layer",
        "edit_layer"
      ]
    },
    // facade layer
    {
      "name": "facade_layer",
      "sublayers": [
        "sublayer_a",
        "sublayer_b"
      ]
    },
    // facade sublayers
    {
      "name": "sublayer_a",
      "attributes": [
        "name", "number", "a"
      ]
    },
    {
      "name": "sublayer_b",
      "attributes": [
        "name", "number", "b"
      ]
    },
    // sublayers
    {
      "name": "edit_layer",
      "attributes": [
        "name", "description"
      ]
    },
    {
      "name": "restricted_layer",
      "attributes": [
        "name", "number", "description"
      ]
    }
  ],
  // additional resources with no restrictions
  "common_resources": [
    // internal print layers
    "osm_bg",
    // background layers
    "osm",
    // print templates
    "A4 Landscape",
    // default Solr facets
    "foreground",
    "background"
  ]
}
```

Full internal resource permissions expanded from unified permissions:

**NOTE:** This generates more permissions than there are actual resources in a specific service. Any surplus permissions will be ignored.

<details>
  <summary>Expanded internal permissions</summary>

**NOTE:** The internal permissions dict below has a slightly different structure than a full JSON permissions file.

```jsonc
{
  "users": {
    "demo": [
      "edit_demo"
    ]
  },
  "groups": {
    "demo": [
      "edit_demo"
    ]
  },
  "roles": {
    // public permissions
    "public": {
      "wms_services": [
        {
          "name": "demo_wms",
          "layers": [
            {
              "name": "demo_wms"
            },
            {
              "name": "group_layer"
            },
            {
              "name": "facade_layer"
            },
            {
              "name": "sublayer_a",
              "attributes": [
                "name", "number", "a", "geometry"
              ],
              "info_template": true
            },
            {
              "name": "sublayer_b",
              "attributes": [
                "name", "number", "b", "geometry"
              ],
              "info_template": true
            },
            {
              "name": "edit_layer",
              "attributes": [
                "name", "description", "geometry"
              ],
              "info_template": true
            },
            {
              "name": "single_layer",
              "attributes": [
                "name", "number", "description", "geometry"
              ],
              "info_template": true
            },
            {
              "name": "demo_doc"
            },
            {
              "name": "osm_bg"
            },
            {
              "name": "osm"
            },
            {
              "name": "A4 Landscape"
            },
            {
              "name": "foreground"
            },
            {
              "name": "background"
            }
          ],
          "print_templates": [
            "osm_bg",
            "osm",
            "A4 Landscape",
            "foreground",
            "background"
          ]
        }
      ],
      "wfs_services": [
        {
          "name": "demo_wfs",
          "layers": [
            {
              "name": "sublayer_a",
              "attributes": [
                "name", "number", "a", "geometry"
              ]
            },
            {
              "name": "sublayer_b",
              "attributes": [
                "name", "number", "b", "geometry"
              ]
            },
            {
              "name": "edit_layer",
              "attributes": [
                "name", "description", "geometry"
              ]
            },
            {
              "name": "single_layer",
              "attributes": [
                "name", "number", "description", "geometry"
              ]
            }
          ]
        }
      ],
      "background_layers": [
        "osm_bg",
        "osm",
        "A4 Landscape",
        "foreground",
        "background"
      ],
      "data_datasets": [
        {
          "name": "sublayer_a",
          "attributes": [
            "name", "number", "a"
          ],
          "writable": false,
          "readable": true
        },
        {
          "name": "sublayer_b",
          "attributes": [
            "name", "number", "b"
          ],
          "writable": false,
          "readable": true
        },
        {
          "name": "edit_layer",
          "attributes": [
            "name", "description"
          ],
          "writable": false,
          "readable": true
        },
        {
          "name": "single_layer",
          "attributes": [
            "name", "number", "description"
          ],
          "writable": false,
          "readable": true
        }
      ],
      "dataproducts": [
        "demo_wms",
        "group_layer",
        "facade_layer",
        "sublayer_a",
        "sublayer_b",
        "edit_layer",
        "single_layer",
        "demo_doc"
      ],
      "document_templates": [
        "demo_doc"
      ],
      "print_templates": [],
      "solr_facets": [
        "sublayer_a",
        "sublayer_b",
        "edit_layer",
        "single_layer",
        "osm_bg",
        "osm",
        "A4 Landscape",
        "foreground",
        "background"
      ]
    },
    // additional permissions for role edit_demo
    "edit_demo": {
      "wms_services": [
        {
          "name": "demo_wms",
          "layers": [
            {
              "name": "demo_wms"
            },
            {
              "name": "restricted_layer",
              "attributes": [
                "name", "number", "description", "geometry"
              ],
              "info_template": true
            },
            {
              "name": "edit_layer",
              "attributes": [
                "name", "description", "geometry"
              ],
              "info_template": true
            },
            {
              "name": "osm_bg"
            },
            {
              "name": "osm"
            },
            {
              "name": "A4 Landscape"
            },
            {
              "name": "foreground"
            },
            {
              "name": "background"
            }
          ],
          "print_templates": [
            "osm_bg",
            "osm",
            "A4 Landscape",
            "foreground",
            "background"
          ]
        }
      ],
      "wfs_services": [
        {
          "name": "demo_wfs",
          "layers": [
            {
              "name": "restricted_layer",
              "attributes": [
                "name", "number", "description", "geometry"
              ]
            },
            {
              "name": "edit_layer",
              "attributes": [
                "name", "description", "geometry"
              ]
            }
          ]
        }
      ],
      "background_layers": [
        "osm_bg",
        "osm",
        "A4 Landscape",
        "foreground",
        "background"
      ],
      "data_datasets": [
        {
          "name": "restricted_layer",
          "attributes": [
            "name",
            "number",
            "description"
          ],
          "writable": false,
          "readable": true
        },
        {
          "name": "edit_layer",
          "attributes": [
            "name",
            "description"
          ],
          "writable": true,
          "readable": true
        }
      ],
      "dataproducts": [
        "demo_wms",
        "restricted_layer",
        "edit_layer"
      ],
      "document_templates": [],
      "print_templates": [],
      "solr_facets": [
        "restricted_layer",
        "edit_layer",
        "osm_bg",
        "osm",
        "A4 Landscape",
        "foreground",
        "background"
      ]
    }
  }
}
```
</details>
