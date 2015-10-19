A library to manage Incidents, Service Requests, CMDB Items in the Service Now database

A quick overview of the project here http://blog.beerandspeech.org/blog/2011/06/25/introducing-pysnc

Quick and data data out of Service Now
http://blog.beerandspeech.org/blog/2011/07/18/quick-and-dirty-data-out-of-service-now

Quick example

```
sm@sm-Lenovo-IdeaPad-S10-2:~/code/pysnc-read-only$ python
Python 2.7.1+ (r271:86832, Apr 11 2011, 18:05:24) 
[GCC 4.5.2] on linux2
Type "help", "copyright", "credits" or "license" for more information.

>>> import sys
>>> sys.path.append('/home/sm/code/pysnc-read-only')

# Import the library
>>> import pysnc
>>>

# The class requires a username, password and Service Now instance name
# optionally, you can also pass 'debug': True to enable debugging
>>> config = {'username': 'api_user',
'password': 'XXXXXXX',
'instance': 'your_instance'}
>>>

# Create an instance of the PySNC class
>>> p = pysnc.PySNC(**config)
>>>

# getIncident() fetches a single Incident from Service Now
>>> incident = p.getIncident(number='INC1234567')

# With the variable you can now access data through it's attributes
>>> 
>>> incident.contact_type
'self-service'
>>> 
>>> incident.urgency
'2'
>>> 
>>> incident.opened_at
'2011-06-24 18:10:21'
>>> 
>>>

# Or you can see all the attributes using the standard __dict__ object
>>> for k in incident.__dict__.keys():
...    '''%s => %s''' % ( k, incident.__dict__[k] )
... 
'sla_due => '
'follow_up => '
'knowledge => false'
'u_itil_watch_list => '
'location => 8a8022200a0a3c7e018b3b649ca7fbd7'
'work_start => '
'due_date => '
'sys_updated_on => 2011-06-24 18:10:22'
'service_offering => '
# etc etc
```