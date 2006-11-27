#!/usr/bin/env python2.4
import httplib2
import apptools
from elementtree.ElementTree import fromstring, tostring
import cPickle
import md5
import feedvalidator
from feedvalidator import compatibility
import cStringIO
from ErrorReporting import *

# Called as logger_cb(uri, resp, content, method, body, headers, redirections)
logger_cb = None

# Called with a ErrorReporting.Reportable
# e.g. error_reporting_cb(EntryCreationMustReturn201())
error_reporting_cb = None


# Monkey patch httplib2 to enable logging/validation
#
httplib2.Http.request_not_instrumented = httplib2.Http.request

def instrumented_request(self, uri, method="GET", body=None, headers=None, redirections=httplib2.DEFAULT_MAX_REDIRECTS):
    (resp, content) = httplib2.Http.request_not_instrumented(self, uri, method, body, headers, redirections)
    # trigger a validation callback with the request and response info
    if logger_cb:
        logger_cb(uri, resp, content, method, body, headers, redirections)
    return (resp, content)

httplib2.Http.request = instrumented_request

ENTRY_ELEMENTS = ["title", "title__type", "summary", "summary__type", "content", "content__type"]
DEFAULT_ENTRY = """<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom">
  <title type="text"></title>
  <id>http://bitworking.org/foo/app/main/third</id>
  <author>
     <name>anonymous</name>
  </author>
  <updated>2006-08-04T15:52:00-05:00</updated>
  <summary type="html"></summary>
  <content type="xhtml">
    <div xmlns="http://www.w3.org/1999/xhtml">
    </div>
  </content>
</entry>

"""

def report(reportable):
    if error_reporting_cb:
        error_reporting_cb(reportable)

def validate_atom(content, baseuri):
    try:
        events = feedvalidator.validateStream(cStringIO.StringIO(content), firstOccurrenceOnly=1,base=baseuri)['loggedEvents']
    except feedvalidator.logging.ValidationFailure, vf:
        events = [vf.event]

    filterFunc = getattr(compatibility, "AA")
    events = filterFunc(events)
    if len(events):
        from feedvalidator.formatter.text_plain import Formatter
        output = Formatter(events)
        report(MustUseValidAtom("\n".join(output)))

class Entry(object):
    def __init__(self, h, edit, title="", title__type="text", updated="", published=""):
        self.h = h
        self.member_uri = edit 

        # Will be filled in with an ElementTree of the entry
        # once self.get() is called.
        self.element = None

        self._values = {
            "title" : title,
            "title__type" : title__type,
            "updated" : updated,
            "published" : published,
            "summary": "",
            "summary__type": "text",
            "content": "",
            "content__type": "text"
        }

    # def get/set text element (takes both text and it's type)
    # def get/set link (rel and optional type).

    def __getitem__(self, name):
        return self._values.get(name, name.endswith("__type") and 'text' or '')

    def __setitem__(self, name, value):
        if name in self._values:
            self._values[name] = value
        else:
            raise IndexError, "index '%s' not found" % name

    def get(self):
        if self.member_uri:
            (resp, content) = self.h.request(self.member_uri)
        else:
            content = DEFAULT_ENTRY
        validate_atom(content, self.member_uri)
        self.element = fromstring(content) 
        d = apptools.parse_atom_entry(self.element)
        self._values.update(d)

    def put(self):
        # loop over the values in sef._values, update self.element
        # then serialize the element into a PUT
        self.h.request(self.member_uri, method="PUT", body=self.tostring(), headers={
                'content-type': 'application/atom+xml'
                }
            )

    def delete(self):
        self.h.request(self.member_uri, method="DELETE")

    def tostring(self):
        apptools.unparse_atom_entry(self.element, self._values)
        return tostring(self.element)


class Collection:
    def __init__(self, name, password, href, title, workspace, accept):
        self.h = httplib2.Http(".cache")
        self.entry_info_cache = httplib2.FileCache(".cache/collections/") # For keys use md5.new(defrag_uri).hexdigest()
        self.h.add_credentials(name, password)
        self.href = href 
        self.title = title 
        self.workspace = workspace 
        self.accept = accept 

        self.cachekey = md5.new(self.href).hexdigest()
        cached_entry_info_raw = self.entry_info_cache.get(self.cachekey)

        self.entry_info =  {
            'next': None,
            'entries': []
        }
 
        if cached_entry_info_raw:
            try:
                self.entry_info = cPickle.load(cached_entry_info_raw)
            except:
                pass
        
        # Does a collection save and restore itself or does it merely serialize and someone else saves/restores?

        # Store in .cache but use a prefix 
        
        # Really this needs to keep a list of all the entries, (their id's and their
        # 'updated' values). Sync up at startup by recursing through the collection
        # documents until you hit the end, or a match.

        # The file will just be a pickle with atom:id, atom:updated, atom:link@href[@rel="edit"], atom:title, and atom:title@type in RCO (Reverse Chronological Order)
        # The data will be a list of dictionaries, sorted by atom:updated
        
        # So we need to look up this stored info based on self.href

        # Need a way to detect deletions, unless there is a 'trash' collection.
        

    def post(self, entry):
        (resp, content) = self.h.request(self.href, method="POST", body=entry.tostring(), headers={
                'content-type': 'application/atom+xml'
                }
            )

    def entries(self):
        (resp, content) = self.h.request(self.href)
        retval = [Entry(self.h, "", "(new...)")]
        if resp['status'] == 304 and self.entry_info:
            return (self.entry_info['entries'], self.entry_info['next'])
        elif resp.status < 300:
            validate_atom(content, self.href)
            (self.entry_info['entries'], self.entry_info['next']) = apptools.parse_collection_feed(content)
            retval.extend([Entry(self.h, **e) for e in self.entry_info['entries']])
            self.entry_info_cache.set(self.cachekey, cPickle.dumps(self.entry_info))
            return (retval,  self.entry_info['next'])
        else:
            return (retval, None)

# Need to save and restore service URIs along with
# names and passwords.
# Store them as space separated values in a text file for now

class Model:
    def __init__(self):
        self.service_list = []
        self.load_service_list()
        self.current_collection = None
        self.h = httplib2.Http(".cache")

    def load_service_list(self):
        self.service_list = []
        for line in file("service.dat", "r"):
            (service, name, password) = line.split()
            self.service_list.append((service, name, password))

    def save_service_list(self):
        f = file("service.dat", "w")
        f.write(
                "\n".join([" ".join(service) for service in self.service_list])
            )
        f.close()
    
    def all_collections(self):
        coll = []
        for (service, name, password) in self.service_list:
            self.h.add_credentials(name, password)
            (resp, content) = self.h.request(service)
            if resp.status == 200:
                for d in apptools.parse_service(content):
                    coll.append(Collection(name, password, **d))    
        return coll     



