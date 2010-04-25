# -*- coding: utf-8 -*-
from django.db import models
#from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.safestring import mark_safe
from django.conf import settings

from django.db.models import permalink, signals
from google.appengine.ext import db
from ragendja.dbutils import *

import datetime
import time

from time import strftime


class User(db.Model):
    name        = db.StringProperty( default = "NEW CREATED USER") 

class Room(db.Model):
    """Conversations can take place in one of many rooms.

    >>> l = Room(name='Test room')
    >>> l.save()
    >>> l
    <Room: Test room>

    Note that updating 'description' auto-updates 'description_modified' when saving:

    >>> l.description_modified

    >>> l.description = 'A description'

    Note that we need to always set the 'user' attribute as a system message is generated for each change.
    >>> l.user = User.objects.get(id=1)
    >>> l.save()

    # description_modified is a unix timestamp.
    >>> m = l.description_modified
    >>> m > 0
    True

    """
    
    name        = db.StringProperty( default = "Name of the room") 
    created     = db.DateTimeProperty( required = False);
    description = db.StringProperty( default = "Description of the room") 
    description_modified    = db.IntegerProperty( default=0 ); #timestamp in seconds when room was created
    last_activity           = db.IntegerProperty( default=0 ); #timestamp of last activity
    object_id               = db.IntegerProperty( default=0 );


    def __unicode__(self):
        return u'%s' % (self.name)

    #class Meta:
    #   ordering = ['created']

    def __init__(self, *args, **kw):
        super(Room, self).__init__(*args, **kw)
        self._init_description = self.description

    def save(self, **kw):
        # If description modified, update the timestamp field.
        if self._init_description != self.description:
            self.description_modified = int(time.time())
        # if last_activity is null (i.e. we are creating the room) set it to now.
        if not self.last_activity:
            self.last_activity = int(time.time())
        if not self.created:
            self.created = datetime.datetime.now()
        self.put();

    @property
    def last_activity_formatted(self):
        """Return Unix timestamp, then express it as a time."""
        return display_timestamp(self.last_activity)

    @property
    def last_activity_datetime(self):
        """Convert last_activity into a datetime object (used to feed into timesince
        filter tag, ideally I should send a patch to Django to accept Unix times)"""
        return datetime.datetime.fromtimestamp(self.last_activity)

# The list of events can be customised for each project.
try:
    EVENT_CHOICES = settings.JQCHAT_EVENT_CHOICES
except:
    # Use default event list.
    EVENT_CHOICES = (
                  (1, "has changed the room's description."),
                  (2, "has joined the room."),
                  (3, "has left the room."),
                 )
class messageManager():
    
    def create_message(self, user, room, msg):
        """Create a message for the given user."""
        m = db_create(Message, user=user, room=room,text='<strong>%s</strong> %s<br />' % (user, msg) );
        return m

    def create_event(self, user, room, event_id):
        """Create an event for the given user."""
        m = db_create(Message, user=user, room=room, event=event_id, 
                               text='<strong>%s</strong> %s<br />' % (user, m.get_event_display()) );
        return m

class Message(db.Model):
    """Messages displayed in the chat client.

    Note that we have 2 categories of messages:
    - a text typed in by the user.
    - an event carried out in the room ("user X has left the room.").

    New messages should be created through the supplied manager methods, as all 
    messages get preformatted (added markup) for display in the chat window.
    For example:
    
    Messages:
    >>> user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
    >>> room = Room.objects.create(name='Test room')
    >>> m = Message.objects.create_message(user, room, 'hello there')
    >>> m.text
    '<strong>john</strong> hello there<br />'

    Events:
    >>> m1 = Message.objects.create_event(user, room, 1)
    >>> u'<strong>john</strong> <em>has changed' in m1.text
    True

    Note that there are 2 timestamp fields:
    - a unix timestamp.
    - a datetime timestamp.
    The reason: the unix timestamp is higher performance when sending data to the browser (easier
    and faster to handle INTs instead of datetimes. The 'created' is used for displaying the date
    of messages; I could calculate it from the unix timestamp, but I'm guessing that I will get
    higher performance by storing it in the database.

    """

    user  = db.ReferenceProperty( User, required=True);             #jqchat message
    room  = db.ReferenceProperty( Room, required=True );            #this message is going to be posted in the room
    event = db.IntegerProperty(   default=-1 );                     #an action performed in this room
    text  = db.StringProperty(    default = "" , multiline = True); #message generateed by use or system
    unix_timestamp = db.IntegerProperty( required = False);        #timestamp when this record is inserted into db
    created = db.DateTimeProperty( required = False);

    def __unicode__(self):
        return u'%s, %s' % (self.user, self.unix_timestamp)

    def save(self, **kw):
        if not self.unix_timestamp:
            self.unix_timestamp = int(time.time())
            self.created = datetime.datetime.fromtimestamp(self.unix_timestamp)
        self.put();
        self.room.last_activity = int(time.time())
        self.room.put()
    def get_json(self):
        DATE_FORMAT = "%H:%M:%S"
        return "%s %s"%( self.created.strftime(DATE_FORMAT), self.text);
        

    class Meta:
        ordering = ['unix_timestamp']

    objects = messageManager()

def display_timestamp(t):
        """Takes a Unix timestamp as a an arg, returns a text string with
        '<unix timestamp> (<equivalent time>)'."""
        return '%s (%s)' % (t, time.strftime('%d/%m/%Y %H:%M', time.gmtime(t)))


