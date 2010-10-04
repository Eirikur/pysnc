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
        ret = []
        for i in j['records']:
            ret.append(SNCIncident(snc_instance=self, log=self.log, data=i))
        return ret

    def getIncident(self, *args, **kwargs):

        self.log.debug("Querying incident table with params %s" % kwargs)

        url = self._get_incident_url(kwargs)
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
                

class SNCIncident:
    def __init__(self, snc_instance, log, data):
        self.data = data
        self.log = log
        self.snc_instance = snc_instance
        for k in self.data.keys():
            self.__dict__[k] = data[k]

    def save(self):
        self.log.debug("Saving incident to SNC")

        data = copy.copy(self.__dict__)
        # Clean up __dict__ a little...
        del data['snc_instance']
        del data['log']

        MANDATORY_ATTRS = [ 'short_description', 'caller', 'company', 'location' ]
        
        for attr in MANDATORY_ATTRS:
            if attr not in data.keys() or not data[attr]:
                raise PySNCError('''%s is a mandatory attribute''' % attr)

        self.log.debug("Incident has all the mandatory attributes required")
        
        # Are we creating a new item or updating an existing one? Check the presence of
        # number attribute TODO: This isn't bulletproof, what if the user created a new
        # incident and then assigned their own number???
        if 'number' in self.__dict__.keys():
            data['sysparm_action'] = 'update'
            self.log.debug("This is an existing incident to update")
        else:
            data['sysparm_action'] = 'insert'
            self.log.debug("This is a new incident to create")
        
        url = 'https://%s.service-now.com/incident.do?JSON' % self.snc_instance.instance
        post_data = json.dumps(data)
        self.log.debug('POST data %s' % post_data)
        req = urllib2.Request(url, post_data)
        response = urllib2.urlopen(req)

        new_data = json.loads(response.read())
        self.log.debug('JSON response from SNC %s' % new_data)
        for k in new_data['records'][0].keys():
            self.__dict__[k] = new_data['records'][0][k]
        
        
