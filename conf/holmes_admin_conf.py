import ldap

# IEM access configuration
HOLMES_URL="localhost:8080"
HOLMES_USERNAME="admin"
HOLMES_PASSWORD="admin"

# LDAP access configuration
LDAP_SERVER_URI = "ldap://ldap.intelie.net:389"
LDAP_USERNAME   = "uid=auth,ou=People,dc=intelie,dc=net"
LDAP_PASSWORD   = "auth"

# LDAP search configuration
LDAP_BASE_DN             = "ou=People,dc=intelie,dc=net"
LDAP_SEARCH_FILTERS      = ["(givenName=*)"]
LDAP_SEARCH_SCOPE        = ldap.SCOPE_ONELEVEL
LDAP_RETRIEVE_ATTRIBUTES = None
LDAP_PAGE_SEARCH_PAGE_SIZE = 3
LDAP_USER_FACTORY = lambda g: {
    "username":g('uid'), 
    "name":g('givenName') + ' ' + g('sn'),
    "email": g('uid') + "@intelie.com.br",
    "xmpp_user":"",
}

LDAP_USER_GROUPS = lambda g: g('objectClass')

# E-mail configuration
EMAIL_DOMAIN="intelie.com.br"

