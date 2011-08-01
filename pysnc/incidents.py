""" A Python Library to query and update the Service Now console """

import logging
import copy
import urllib
import urllib2
import simplejson as json

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
        
        
