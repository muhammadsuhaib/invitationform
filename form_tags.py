# encoding=utf-8

from django import template

from invitationform.models import *

import logging
from concertinvitation.settings import DEBUG_LOGGER
log = logging.getLogger(DEBUG_LOGGER)

register = template.Library()


@register.filter
def is_required_field(event, fieldname):
    if fieldname is None or fieldname == "":
        raise Exception("Please provide a valid fieldname as argument.")
    if event is None:
        raise Exception("Please provide a valid Event object.")
    if event.event_type not in [Event.EVENT_TYPE_NYC, Event.EVENT_TYPE_NYC2019, Event.EVENT_TYPE_CXO]:
        raise Exception("Please set the event type on Event %s" % (event))

    return fieldname in event.get_required_form_fields()


@register.filter
def is_visible_field(event, fieldname):
    if fieldname is None or fieldname == "":
        raise Exception("Please provide a valid fieldname as argument.")
    if event is None:
        raise Exception("Please provide a valid Event object.")
    if event.event_type not in [Event.EVENT_TYPE_NYC, Event.EVENT_TYPE_NYC2019, Event.EVENT_TYPE_CXO]:
        raise Exception("Please set the event type on Event %s" % (event))

    return fieldname in event.get_form_fields()


@register.filter
def selected_choice(form, fieldname):
    # log.debug(u"fieldname: %s " % fieldname)
    if form is None:
        return ""
    if fieldname not in form.fields:
        return ""
    # log.debug(form.fields[fieldname])
    # log.debug(form.data[fieldname])
    return dict(form.fields[fieldname].choices)[form.data[fieldname]]
    # try:
    #     return dict(form.fields[fieldname].choices)[form.data[fieldname]]
    # except Exception as ex:
    #     log.error(u"selected_choice(%s): %s" % (fieldname, str(ex)))
    #     return ""


@register.filter
def max_length(form, fieldname):
    # log.debug(u"fieldname: %s " % fieldname)
    if form is None:
        return 255
    if fieldname not in form.fields:
        return 255
    # log.debug(form.fields[fieldname])
    # log.debug(form.data[fieldname])
    return form.fields[fieldname].max_length or 255
