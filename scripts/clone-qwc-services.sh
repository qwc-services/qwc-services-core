GITBASE=https://github.com/qwc-services
#GITBASE=git@github.com:qwc-services
REPOS="qwc-config-service 
       qwc-docker
       qwc-ogc-service
       qwc-services-core
       qwc-map-viewer
       qwc-config-db
       qwc-legend-service
       qwc-admin-gui
       qwc-db-auth
       qwc-data-service
       qwc-permalink-service
       qwc-print-service
       qwc-elevation-service
       qwc-fulltext-search-service
       qwc-ldap-auth
       qwc-registration-gui"

for repo in $REPOS; do
    if [ ! -d "${repo}" ]; then
        git clone $GITBASE/$repo.git
    fi
done
