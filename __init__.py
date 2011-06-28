""" A Python Library to query and update the Service Now console """

import logging
import copy
import urllib
import urllib2
import simplejson as json

from incidents import SNCIncident

# A base SNC Exception class
class PySNCError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class PySNCConfigError(PySNCError):
    pass


class PySNC:
    """ The Service Now Console helper class """

    def __init__(self, *args, **kwargs):
        self.username = kwargs.get('username')
        if not self.username: raise PySNCConfigError("Missing username parameter")

        self.password = kwargs.get('password')
        if not self.password: raise PySNCConfigError("Missing password parameter")

        self.instance = kwargs.get('instance')
        if not self.instance: raise PySNCConfigError("Missing instance parameter")

        self.log = logging.getLogger('pysnc')
        if kwargs.has_key('debug') and kwargs['debug']:
            self.log.setLevel(logging.DEBUG)
            h = logging.StreamHandler()
            f = logging.Formatter("%(levelname)s %(asctime)s fn=%(funcName)s() line=%(lineno)d msg=%(message)s")
            h.setFormatter(f)
            self.log.addHandler(h)
        else:
            self.log.setLevel(logging.NOTSET)

        self._login()



    def _login(self):
        """ Log into SNC and set the correct credentials"""

        base_url = 'https://%s.service-now.com/' % self.instance
        pass_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        pass_manager.add_password(None,base_url,self.username,self.password) 
        authhandler = urllib2.HTTPBasicAuthHandler(pass_manager)

        opener = urllib2.build_opener(authhandler)
        urllib2.install_opener(opener)
        self.log.debug('''Logged into Service Now and authenticated as %s''' % self.username)


    def _get_query_url(self, table, **params):
        """ Return the correct URL for querying the Service Now console database table """

        str = ''
        for k in params.keys():
            str += '''%s=%s^''' % ( k, params[k])
        str = str[:-1]
        str = '''sysparm_action=getRecords&sysparm_query=%s''' % str
        url = '''https://%s.service-now.com/%s?JSON&%s''' % ( self.instance, table, str )
        self.log.debug("Query URL %s" % url)
        return url


    def filterIncidents(self, *args, **kwargs):

        self.log.debug("Querying incident table with params %s" % kwargs)

        url = self._get_query_url('incident.do', **kwargs)
        r = urllib2.urlopen(url)
        j = json.loads(r.read())
        ret = []
        for i in j['records']:
            ret.append(SNCIncident(snc_instance=self, log=self.log, data=i))
        return ret

    def getIncident(self, *args, **kwargs):

        self.log.debug("Querying incident table with params %s" % kwargs)

        url = self._get_query_url('incident.do' **kwargs)
        r = urllib2.urlopen(url)
        j = json.loads(r.read())
        if len(j['records']) == 0:
            raise PySNCError("No records were returned")
        elif len(j['records']) > 1:
            raise PySNCError("Multiple records were returned")
        else:
            return SNCIncident(snc_instance=self, log=self.log, data=j['records'][0])


    def addIncident(self, *args, **kwargs):
        """ Return a SNCIncident instance that is not committed to the Service
        Now database yet.

        The user should call save() on this instance to actually create the
        incident
        """

        self.log.debug("Adding a new instance with kwargs %s" % kwargs)
        return SNCIncident(snc_instance=self, log=self.log, data=kwargs)

    def resolveAttribute(self, name, table_name):
        """ Return a sys_id for an attribute given it's name.

        Return None if the attribute is not found"""

        name = urllib.urlencode({'sysparm_query': 'name=%s' % name})

        url = '''https://%s.service-now.com/%s?JSON&sysparm_action=getRecords&%s''' % ( self.instance, table_name, name)
        self.log.debug('Query URL %s' % url)
        r = urllib2.urlopen(url)
        j = json.loads(r.read())
        if not j['records']:
            self.log.debug('Returning None')
            return None
        self.log.debug('Returned result %s' % j)
        return j['records'][0]['sys_id']

                

        