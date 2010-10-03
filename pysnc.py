""" A Python Library to query and update the Service Now console """

import logging
import copy
import urllib
import urllib2
import simplejson as json

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


    def _get_incident_url(self, params):
        """ Return the correct URL for querying the Service Now console Incident table """
        str = ''
        for k in params.keys():
            str += '''%s=%s^''' % ( k, params[k])
        str = str[:-1]
        str = '''sysparm_action=getRecords&sysparm_query=%s''' % str
        url = '''https://%s.service-now.com/incident.do?JSON&%s''' % ( self.instance, str )
        self.log.debug("Query URL %s" % url)
        return url


    def filterIncidents(self, *args, **kwargs):

        self.log.debug("Querying incident table with params %s" % kwargs)

        url = self._get_incident_url(kwargs)
        r = urllib2.urlopen(url)
        j = json.loads(r.read())
        if self.debug: logging.debug(j)
        ret = []
        for i in j['records']:
            ret.append(PySNCIncident(snc_instance=self, data=i))
        return ret
                

class PySNCIncident:
    def __init__(self, snc_instance, data):
        self.data = data
        self.snc_instance = snc_instance
        for k in self.data.keys():
            self.__dict__[k] = data[k]
            
        
