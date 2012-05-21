import ldap

# IEM access configuration
HOLMES_URL="localhost:8080"
HOLMES_USERNAME="admin"
HOLMES_PASSWORD="admin"

# LDAP access configuration
LDAP_SERVER   = "ldap.intelie.net"
LDAP_USERNAME = "uid=auth,ou=People,dc=intelie,dc=net"
LDAP_PASSWORD = "auth"

# LDAP search configuration
LDAP_BASE_DN             = "ou=People,dc=intelie,dc=net"
LDAP_SEARCH_FILTER       = "(givenName=*)"
LDAP_SEARCH_SCOPE        = ldap.SCOPE_ONELEVEL
LDAP_RETRIEVE_ATTRIBUTES = None

# E-mail configuration
EMAIL_DOMAIN="intelie.com.br"

