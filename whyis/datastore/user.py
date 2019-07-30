from flask_security import UserMixin
from flask_security.utils import verify_and_update_password

from whyis.namespace import dc, auth, foaf, prov

from .single import single
from .multiple import multiple
from .mapped_resource import MappedResource


class User(MappedResource, UserMixin):
    rdf_type = prov.Agent

    key = 'id'

    id = single(dc.identifier)
    active = single(auth.active)
    confirmed_at = single(auth.confirmed)
    email = single(auth.email)
    current_login_at = single(auth.hadCurrentLogin)
    current_login_ip = single( auth.hadCurrentLoginIP)
    last_login_at = single( auth.hadLastLogin)
    last_login_ip = single( auth.hadLastLoginIP)
    login_count = single( auth.hadLoginCount)
    roles = multiple( auth.hasRole)
    password = single( auth.passwd)
    familyName = single(foaf.familyName)
    givenName = single(foaf.givenName)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def verify_and_update_password(self, password):
        return verify_and_update_password(password, self)
