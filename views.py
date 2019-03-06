# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect  # , get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import login, authenticate, logout
from django.forms.models import model_to_dict

import logging

import uuid

# from invitationform.jsonencoder import JSONSerializer
from invitationform.models import *
from invitationform.forms import EventFormForm
from invitationform.forms import EventFormForm2019
from invitationform.utils import email_registration_done, email_password_setup_done, email_account_info_updated, email_password_reset_requested

from concertinvitation.settings import DEBUG_LOGGER, HOST
log = logging.getLogger(DEBUG_LOGGER)


def logout_user(request):
    messages_delete(request)
    session_delete_extra_data(request)
    logout(request)


def render_template(request, template_name, template_path='', data={}):

    if 'error' in request.session:
        data['error'] = request.session['error']
    if 'field' in request.session:
        data['field'] = request.session['field']
    if 'for_id' in request.session:
        data['for_id'] = request.session['for_id']
    if 'form_input' in request.session:
        data['form_input'] = request.session['form_input']
    if 'form_errors' in request.session:
        data['form_errors'] = request.session['form_errors']

    data["is_local"] = "localhost" in HOST.lower()

    return render(request, '%s%s.html' % (template_path, template_name), data)


def messages_delete(request):
    # clear the messages from the storage that may have piled up due to user's being users... sigh
    storage = messages.get_messages(request)
    storage.used = True
    list(messages.get_messages(request))


def session_delete_extra_data(request):
    try:
        del request.session['event']
    except:
        pass
    try:
        del request.session['warning']
    except:
        pass
    try:
        del request.session['field']
    except:
        pass
    try:
        del request.session['for_id']
    except:
        pass
    try:
        del request.session['agreed']
    except:
        pass
    try:
        del request.session['form_input']
    except:
        pass
    try:
        del request.session['form_errors']
    except:
        pass
    try:
        del request.session['form_instance']
    except:
        pass


def issue_warning(request, warning, field=None, for_id=None):
    messages.warning(request, warning)
    request.session['error'] = warning
    request.session['field'] = field
    request.session['for_id'] = for_id


def home(request):
    log.debug("home")

    user = request.user

    # They want to show the title of the event that is open for registration on the initial page
    # right away. Soooo, this is why we do this open events thingy.
    curdate = timezone.now().date()
    open_events = Event.objects.filter(date_open__lte=curdate, date_close__gt=curdate)
    future_events = Event.objects.filter(date_open__gt=curdate)
    title = "Home" if len(open_events) == 0 else open_events[0].title or "Home"

    context = {
        "title": title,
        "open_events": open_events,
        "future_events": future_events,
    }

    if user.is_anonymous():
        return render_template(request, "home", data=context)

    # Has the user a company? If not, it is likely an admin
    if user.eventform_set.count() is None:
        issue_warning(request, 'Your account has no company assigned to it. If you are an administrator, please use the admin login page.')
        return render_template(request, "home", data=context)

    event_id = request.session['event'] if 'event' in request.session else 0
    if event_id == 0:
        return render_template(request, "home", data=context)

    try:
        event = Event.objects.get(id=event_id)
    except:
        session_delete_extra_data(request)
        issue_warning(request, 'The selected event could not be found.')
        return render_template(request, "home", data=context)

    try:
        company = user.company_set.get(event=event)
    except:
        session_delete_extra_data(request)
        issue_warning(request, 'The selected event has no company assigned to it.')
        return render_template(request, "home", data=context)

    # check if user is agreed to terms and conditions
    if company.accepted_privacy_statement != AGREE_YES:
        issue_warning(request, 'Please agree to our Privacy Statement first.')
        return redirect("privacy_statement")

    # check if user is already done with registration process
    if not company.registration_done:
        issue_warning(request, 'Please complete your registration first.')
        return redirect("registration")

    # Show the form in read-only mode
    return redirect("overview")


def bouncer(request):
    log.debug("bouncer")

    if request.method != "POST":
        issue_warning(request, 'Do not call this page directly.')
        session_delete_extra_data(request)
        return redirect('home')

    # check if the input code is matching any event, if so, go ahead and display the registration page for
    # that event
    event_id = request.POST.get("event", "").strip()
    code = request.POST.get("code", "").strip()

    log.debug(u"bouncer: code: %s" % code)

    if len(code) == 0:
        session_delete_extra_data(request)
        issue_warning(request, 'Please enter a valid code.', field="code", for_id=event_id)
        return redirect('home')

    try:
        event = Event.objects.get(id=int(event_id))
    except:
        session_delete_extra_data(request)
        issue_warning(request, 'The selected event could not be found.', field="code", for_id=event.id)
        return redirect('home')

    if code != event.entry_code:
        session_delete_extra_data(request)
        issue_warning(request, '認証コードが間違っています。<br>The access code is incorrect. Please try again.', field="code", for_id=event_id)
        return redirect('home')


    # TODO: make this more user friendly, by for example showing a "event not open for registration yet"
    #       or a "event registration is already closed"
    curdate = timezone.now().date()
    if curdate < event.date_open or curdate > event.date_close:
        session_delete_extra_data(request)
        issue_warning(request, 'The event is not open for registration.', field="code", for_id=event_id)
        return redirect('home')

    session_delete_extra_data(request)

    request.session['event'] = event.id

    return redirect('privacy_statement')


def privacy_statement(request):
    log.debug("privacy_statement")

    curdate = timezone.now().date()
    try:
        event_id = int(request.session['event'])
    except:
        session_delete_extra_data(request)
        issue_warning(request, 'No event was selected for registration.')
        return redirect('home')

    try:
        # event = Event.objects.get(id=event_id, date_open__lte=curdate, date_close__gt=curdate)
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        session_delete_extra_data(request)
        issue_warning(request, 'The selected event is not available.')
        return redirect('home')

    if curdate < event.date_open:
        session_delete_extra_data(request)
        issue_warning(request, 'The selected event is not open for registration yet.')
        return redirect('home')

    if curdate > event.date_close:
        session_delete_extra_data(request)
        issue_warning(request, 'The selected event is closed for registration.')
        return redirect('home')

    request.session['event'] = event.id

    return render_template(request, "privacy_statement")


def privacy_statement_process(request):
    log.debug("privacy_statement_process")

    if request.method != "POST":
        issue_warning(request, 'Do not call this page directly.')
        session_delete_extra_data(request)
        return redirect('home')

    agreed = request.POST.get("agree", "").lower() == "agree"

    if not agreed:
        event_id = request.session['event'] if 'event' in request.session else None
        issue_warning(request, 'You need to agree to our Privacy statement.', field="agree", for_id=event_id)
        session_delete_extra_data(request)
        return redirect('home')

    request.session['agreed'] = True

    return redirect('registration', event_id=int(request.session['event']))


def registration(request, event_id):
    log.debug("registration")

    try:
        event = Event.objects.get(id=event_id)
    except:
        session_delete_extra_data(request)
        issue_warning(request, 'The selected event is not available.')
        return redirect('home')

    curdate = timezone.now().date()

    if curdate < event.date_open:
        session_delete_extra_data(request)
        issue_warning(request, 'The selected event is not open for registration yet.')
        return redirect('home')

    if curdate > event.date_close:
        session_delete_extra_data(request)
        issue_warning(request, 'The selected event is closed for registration.')
        return redirect('home')

    agreed = request.session['agreed'] if 'agreed' in request.session else False
    if not agreed:
        issue_warning(request, 'You need to agree to our Privacy statement.', field="agree", for_id=event.id)
        session_delete_extra_data(request)
        return redirect('home')

    previous_input = request.session['form_input'] if 'form_input' in request.session else None
    log.debug(u"has data: %s" % unicode(previous_input))

    context = {
        "event": event,
        "form": EventFormForm2019(previous_input) if previous_input is not None else EventFormForm2019(),
    }

    return render_template(request, "registration", data=context)


def registration_process(request):
    log.debug("registration_process")

    if request.method != "POST":
        issue_warning(request, 'Do not call this page directly.')
        session_delete_extra_data(request)
        return redirect('home')

    event_id = request.session['event'] if 'event' in request.session else request.POST.get("event", 0)
    try:
        event = Event.objects.get(id=event_id)
    except:
        session_delete_extra_data(request)
        issue_warning(request, 'The selected event is not available.')
        return redirect('home')

    curdate = timezone.now().date()

    if curdate < event.date_open:
        session_delete_extra_data(request)
        issue_warning(request, 'The selected event is not open for registration yet.')
        return redirect('home')

    if curdate > event.date_close:
        session_delete_extra_data(request)
        issue_warning(request, 'The selected event is closed for registration.')
        return redirect('home')

    agreed = request.session['agreed'] if 'agreed' in request.session else False
    if not agreed:
        issue_warning(request, 'You need to agree to our Privacy statement.', field="agree", for_id=event.id)
        session_delete_extra_data(request)
        return redirect('home')

    # TODO(dkg): should we double check the DB here if a EventForm entry already exists
    #            for this user??? If so, we should not allow them to sign up again.
    # Also, we should probably check eventform.registration_done if there is an EventForm
    # entry, and if it is False, then continue the registration process, otherwise sent
    # them to the password reset page.

    # log.debug(unicode(request.POST))

    form = EventFormForm2019(request.POST)
    if not form.is_valid():
        log.debug(u"form not valid %s" % unicode(form.errors))
        request.session['form_input'] = form.cleaned_data
        request.session['form_errors'] = form.errors
        return redirect('registration', event_id=event_id)

    log.debug("form is valid")
    form_instance = form.save(commit=False)  # no saving in db yet
    form_instance.event = event

    def set_value_if_none(form_dict, fieldname, empty="", alt=""):
        val = form_dict[fieldname] if fieldname in form_dict else None
        if val is None or len(val) == "" or val == empty:
            form_dict[fieldname] = alt
            setattr(form_instance, fieldname, alt)

    set_value_if_none(form.cleaned_data, "honnin_attending", empty=ATTEND_NONE, alt=ATTEND_NO)
    set_value_if_none(form.cleaned_data, "companion_attending", empty=ATTEND_NONE, alt=ATTEND_NO)
    set_value_if_none(form.cleaned_data, "secretary_attending", empty=ATTEND_NONE, alt=ATTEND_NO)
    set_value_if_none(form.cleaned_data, "honnin_attending_reception", empty=ATTEND_NONE, alt=ATTEND_NO)
    set_value_if_none(form.cleaned_data, "companion_attending_reception", empty=ATTEND_NONE, alt=ATTEND_NO)
    set_value_if_none(form.cleaned_data, "secretary_attending_reception", empty=ATTEND_NONE, alt=ATTEND_NO)

    #We loop

    # form_instance.user = request.user

    request.session['form_input'] = form.cleaned_data
    # request.session['form_instance'] = JSONSerializer().serialize(form_instance)

    log.debug(u"form_instance: %s" % unicode(form_instance))

    # error message if required fields are not filled in
    # ※未入力があります
    # Please complete all required fields.

    return redirect('registration_confirm')


def registration_confirm(request):
    log.debug("registration_confirm")
    event_id = request.session['event'] if 'event' in request.session else request.POST.get("event", 0)

    try:
        event = Event.objects.get(id=event_id)
    except:
        session_delete_extra_data(request)
        issue_warning(request, 'The selected event is not available.')
        return redirect('home')

    curdate = timezone.now().date()

    if curdate < event.date_open:
        session_delete_extra_data(request)
        issue_warning(request, 'The selected event is not open for registration yet.')
        return redirect('home')

    if curdate > event.date_close:
        session_delete_extra_data(request)
        issue_warning(request, 'The selected event is closed for registration.')
        return redirect('home')

    agreed = request.session['agreed'] if 'agreed' in request.session else False
    if not agreed:
        issue_warning(request, 'You need to agree to our Privacy statement.', field="agree", for_id=event.id)
        session_delete_extra_data(request)
        return redirect('home')

    form_input = request.session['form_input'] if 'form_input' in request.session else None
    if form_input is None:
        issue_warning(request, 'Please fill out the registration form first.', for_id=event.id)
        session_delete_extra_data(request)
        return redirect('home')

    context = {
        "event": event,
        "form": EventFormForm2019(form_input) if form_input is not None else EventFormForm2019(),
        # "input": form_input,
    }

    return render_template(request, "registration_confirm", data=context)


def registration_confirm_process(request):
    log.debug("registration_confirm_process")

    if request.method != "POST":
        issue_warning(request, 'Do not call this page directly.')
        session_delete_extra_data(request)
        return redirect('home')

    event_id = request.session['event'] if 'event' in request.session else request.POST.get("event", 0)
    try:
        event = Event.objects.get(id=event_id)
    except:
        issue_warning(request, 'The selected event is not available.')
        session_delete_extra_data(request)
        return redirect('home')

    curdate = timezone.now().date()

    if curdate < event.date_open:
        issue_warning(request, 'The selected event is not open for registration yet.')
        session_delete_extra_data(request)
        return redirect('home')

    if curdate > event.date_close:
        issue_warning(request, 'The selected event is closed for registration.')
        session_delete_extra_data(request)
        return redirect('home')

    agreed = request.session['agreed'] if 'agreed' in request.session else False
    if not agreed:
        session_delete_extra_data(request)
        issue_warning(request, 'You need to agree to our Privacy statement.', field="agree", for_id=event.id)
        return redirect('home')

    form_input = request.session['form_input'] if 'form_input' in request.session else None
    if form_input is None:
        session_delete_extra_data(request)
        issue_warning(request, 'Please fill out the registration form first.', for_id=event.id)
        return redirect('home')

    form_object = EventFormForm2019(form_input)
    form_instance = form_object.save(commit=False)

    log.debug(unicode(request.POST))

    if 'change-button' in request.POST:
        log.debug("change!")
        return redirect('registration', event_id=event.id)
    if 'submit-button' not in request.POST:
        session_delete_extra_data(request)
        issue_warning(request, 'Internal data error. The admin needs to investigate.')
        return redirect('home')

    # Check if the user is already existing in the database, if so
    # send them to the proper login page
    email_username = form_instance.email[:30]  # django's auth_user.username is limited to 30 chars
    try:
        other_user = User.objects.get(username=email_username)
    except:
        other_user = None

    # TODO(dkg): Check if the company name is already registered for this event
    # company_name
    check = False
    if other_user is None:
        user, created = User.objects.get_or_create(username=email_username, defaults={
            "first_name": form_instance.first_name,
            "last_name": form_instance.last_name,
            "email": form_instance.email,
        })
        if not created:
            check = True
            other_user = user
    else:
        # there is already an existing user, double check the events that user has
        # registered against - maybe they didn't find/see the proper link to the login page
        check = True
        user = other_user

    if check:
        # they may have clicked "change" on the 'confirm registration' page or something
        try:
            event_form = EventForm2019.objects.get(event=event, user=other_user)
        except:
            event_form = None

        if event_form is None:
            # So for whatever reason, there is a user already existing, but no eventform, which
            # is strange, since both go hand-in-hand
            # However this use-case is where we really have to think:
            #
            # User registered for event A.
            # EventForm for Event A exists. AuthUser exists.
            # User wants to register for event B.
            # EventForm for Event B does not exist. AuthUser exists.
            #
            # This should be possible!!!
            log.warn(u"User (%s) with username %s already exists, but no eventform entry found for event %s" % (str(other_user.id), email_username, str(event.id)))
            pass  # all clear
        else:
            log.warn(u"User (%s) with username %s already exists, and eventform entry found for event %s (event_form: %s)" % (str(other_user.id), email_username, str(event.id), str(event_form.id)))
            return redirect('registration_exist')

    if user is None:
        log.warn("no user selected/created for registration!!!!")
        raise Exception("no user created for registration")

    form_instance.event = event
    form_instance.user = user
    #form_instance.user_changed = curdate
    form_instance.accepted_privacy_statement = AGREE_YES
    form_instance.registration_done = False  # set to True after user set initial password
    form_instance.password_setup_code = uuid.uuid4().hex.upper()
    form_instance.password_setup_time = timezone.now()
    form_instance.save()

    log.debug(u"EventForm entry saved %s for user %s (%s)" % (form_instance.id, user, str(user.id)))

    user.is_active = True
    user.is_staff = False
    user.is_superuser = False
    user.set_unusable_password()
    user.save()

    # TODO(dkg): send email to user

    # log.debug(u"login: login(request, %s, %s)" % (user, str(user.id)))
    # user.backend = settings.AUTHENTICATION_BACKENDS[0]
    # login(request, user)

    email_registration_done(request, form_instance)

    return redirect('registration_thankyou')


def registration_exist(request):
    log.debug("registration_exist")
    event_id = request.session['event'] if 'event' in request.session else request.POST.get("event", 0)

    try:
        event = Event.objects.get(id=event_id)
    except:
        session_delete_extra_data(request)
        issue_warning(request, 'The selected event is not available.')
        return redirect('home')

    context = {
        "event": event,
    }

    session_delete_extra_data(request)

    return render_template(request, "registration_exist", data=context)


def registration_thankyou(request):
    log.debug("registration_thankyou")
    event_id = request.session['event'] if 'event' in request.session else request.POST.get("event", 0)

    try:
        event = Event.objects.get(id=event_id)
    except:
        session_delete_extra_data(request)
        issue_warning(request, 'The selected event is not available.')
        return redirect('home')

    context = {
        "event": event,
    }

    session_delete_extra_data(request)
    messages_delete(request)

    return render_template(request, "registration_thankyou", data=context)


def registration_redirect(request):
    log.debug("registration_redirect")
    return redirect('home')


@login_required
def overview(request):
    log.debug("overview")
    # figure out which eventform we need to load, as there might be older ones that are already done,
    # and we don't need those...

    curdate = timezone.now().date()

    eventforms = EventForm2019.objects.filter(user=request.user, event__date_open__lte=curdate, event__date_close__gt=curdate)

    title = "Home" if len(eventforms) == 0 else eventforms[0].event.title or "Home"
    context = {
        "is_overview": True,
        "title": title,
    }

    if len(eventforms) == 0:
        issue_warning(request, "Your account is not subscribed to any open/future events.")
        session_delete_extra_data(request)
        return render_template(request, "overview", data=context)

    eventform = eventforms[0]
    form = EventFormForm(model_to_dict(eventform))
    form.is_valid()

    context["eventform"] = eventform
    context["event"] = eventform.event
    context["form_input"] = form.cleaned_data
    context["form"] = form

    return render_template(request, "registration_confirm", data=context)


@login_required
def overview_process(request, eventform_id):
    log.debug("overview_process")

    if request.method != "POST":
        session_delete_extra_data(request)
        redirect('logout')

    do_close = 'close-button' in request.POST
    do_change = 'change-button' in request.POST

    log.debug(request.POST)

    if do_close:
        log.debug("close-button")
        logout_user(request)
        return redirect('accounts_login')

    if not do_change:
        log.debug(u"wrong choice or parameter not set")
        session_delete_extra_data(request)
        return redirect('logout')

    return redirect('overview_change', eventform_id=request.POST.get("eventform_id", eventform_id))


@login_required
def overview_change_process(request, eventform_id):
    log.debug("overview_change_process")

    try:
        eventform = EventForm2019.objects.get(id=eventform_id, user=request.user)
    except:
        session_delete_extra_data(request)
        issue_warning(request, 'EventForm %s not found.' % str(eventform_id))
        return redirect('overview')

    if request.method != "POST":
        session_delete_extra_data(request)
        redirect('logout')

    # log.debug(request.POST)

    do_close = 'close-button' in request.POST
    do_change = 'change-button' in request.POST or 'submit-button' in request.POST

    if do_close:
        log.debug("close-button")
        return aedirect('logout')

    if not do_change:
        log.debug(u"wrong choice or parameter not set")
        session_delete_extra_data(request)
        return redirect('logout')

    form = EventFormForm2019(request.POST, instance=eventform)
    if not form.is_valid():
        log.debug(u"form not valid %s" % unicode(form.errors))
        request.session['form_input'] = form.cleaned_data
        request.session['form_errors'] = form.errors
        return redirect('registration', event_id=event_id)

    log.debug("form is valid")
    form_instance = form.save(commit=False)  # no saving in db yet

    def set_value_if_none(form_dict, fieldname, empty="", alt=""):
        val = form_dict[fieldname] if fieldname in form_dict else None
        if val is None or len(val) == "" or val == empty:
            form_dict[fieldname] = alt
            setattr(form_instance, fieldname, alt)

    set_value_if_none(form.cleaned_data, "honnin_attending", empty=ATTEND_NONE, alt=ATTEND_NO)
    set_value_if_none(form.cleaned_data, "companion_attending", empty=ATTEND_NONE, alt=ATTEND_NO)
    set_value_if_none(form.cleaned_data, "secretary_attending", empty=ATTEND_NONE, alt=ATTEND_NO)
    set_value_if_none(form.cleaned_data, "honnin_attending_reception", empty=ATTEND_NONE, alt=ATTEND_NO)
    set_value_if_none(form.cleaned_data, "companion_attending_reception", empty=ATTEND_NONE, alt=ATTEND_NO)
    set_value_if_none(form.cleaned_data, "secretary_attending_reception", empty=ATTEND_NONE, alt=ATTEND_NO)

    # form_instance.user = request.user

    request.session['form_input'] = form.cleaned_data

    return redirect('overview_confirm', eventform_id=request.POST.get('eventform_id'))


@login_required
def overview_change(request, eventform_id):
    log.debug("overview_change")

    try:
        eventform = EventForm2019.objects.get(id=eventform_id, user=request.user)
    except:
        session_delete_extra_data(request)
        issue_warning(request, 'EventForm %s not found.' % str(eventform_id))
        return redirect('overview')

    # TODO: should the event and the event dates be checked here as well?
    form_input = request.session['form_input'] if 'form_input' in request.session else None
    if form_input is None:
        log.debug("overview_change: no form_input, using model instance")
        form = EventFormForm(model_to_dict(eventform), instance=eventform)
    else:
        log.debug("overview_change: form_input will be used")
        form = EventFormForm(form_input, instance=eventform)
    form.is_valid()

    form.cleaned_data["email_type_again"] = form.cleaned_data["email"]

    title = eventform.event.title
    context = {
        "is_overview": True,
        "title": title,
        "eventform": eventform,
        "event": eventform.event,
        "form_input": form.cleaned_data,
        "form": form,
    }

    return render_template(request, "overview_change", data=context)


@login_required
def overview_confirm(request, eventform_id):
    log.debug("overview_confirm")

    try:
        eventform = EventForm2019.objects.get(id=eventform_id, user=request.user)
    except:
        session_delete_extra_data(request)
        issue_warning(request, 'EventForm %s not found.' % str(eventform_id))
        return redirect('overview')

    form_input = request.session['form_input'] if 'form_input' in request.session else None
    if form_input is None:
        issue_warning(request, 'Please fill out the registration form first.', for_id=event.id)
        session_delete_extra_data(request)
        return redirect('home')

    context = {
        "is_overview_confirm": True,
        "event": eventform.event,
        "eventform": eventform,
        "form": EventFormForm(form_input, instance=eventform) if form_input is not None else EventFormForm(instance=eventform),
        # "input": form_input,
    }

    return render_template(request, "overview_confirm", data=context)


@login_required
def overview_confirm_process(request, eventform_id):
    log.debug("overview_confirm_process")
    try:
        eventform = EventForm2019.objects.get(id=eventform_id, user=request.user)
    except:
        session_delete_extra_data(request)
        issue_warning(request, 'EventForm %s not found.' % str(eventform_id))
        return redirect('overview')

    form_input = request.session['form_input'] if 'form_input' in request.session else None
    if form_input is None:
        session_delete_extra_data(request)
        issue_warning(request, 'Please fill out the registration form first.', for_id=event.id)
        return redirect('home')

    form_object = EventFormForm(form_input, instance=eventform)
    form_instance = form_object.save(commit=False)

    #We need to update the email in the user account too.
    eventform.user.username = form_input['email'][:30]
    eventform.user.email = form_input['email']
    eventform.user.save()

    log.debug(unicode(request.POST))

    if 'change-button' in request.POST:
        log.debug("change!")
        return redirect('overview_change', eventform_id=eventform_id)
    if 'submit-button' not in request.POST:
        session_delete_extra_data(request)
        issue_warning(request, 'Internal data error 2. The admin needs to investigate.')
        return redirect('logout')

    curdate = timezone.now()
    # TODO(dkg): should this be set at this stage?
    form_instance.user_changed = curdate
    form_instance.save()

    log.debug(u"EventForm entry saved %s for user %s (%s)" % (form_instance.id, request.user, str(request.user.id)))

    email_account_info_updated(request, form_instance)

    session_delete_extra_data(request)
    messages_delete(request)

    return redirect('overview_thankyou', eventform_id=eventform_id)


@login_required
def overview_thankyou(request, eventform_id):
    log.debug("overview_thankyou")
    try:
        eventform = EventForm2019.objects.get(id=eventform_id, user=request.user)
    except:
        session_delete_extra_data(request)
        issue_warning(request, 'EventForm %s not found.' % str(eventform_id))
        return redirect('overview')

    messages_delete(request)

    context = {
        "event": eventform.event,
        "eventform": eventform,
    }

    return render_template(request, "overview_thankyou", data=context)


def accounts_reset_password(request):
    log.debug("accounts_reset_password")

    session_delete_extra_data(request)
    messages_delete(request)

    curdate = timezone.now().date()

    open_events = Event.objects.filter(date_open__lte=curdate, date_close__gt=curdate)
    # They want that as title on the page, even though at this stage we don't know what event
    # they will login to....
    event_title = open_events[0].title if len(open_events) > 0 else "10th Accenture New Year Concert"
    # ... maybe the solution is to have the event_id in the URL and as parameter here, so we
    # can load the right one... but then you wouldn't be able to have a generic login page
    # and you would need some kind of event dropdown selection or something on it.

    context = {
        "event_title": event_title,
    }

    if request.method == "POST":
        messages_delete(request)
        eventforms = []
        email = request.POST.get("email", "").strip()
        email_username = email[:30]
        try:
            user = User.objects.get(username=email_username)
        except:
            session_delete_extra_data(request)
            context["email_not_found_error"] = 'The provided email address was not found.'
        else:
            eventforms = EventForm2019.objects.filter(user=user, event__date_open__lte=curdate, event__date_close__gt=curdate)

            if len(eventforms) > 0:

                eventform = eventforms[0]
                context = {
                    "event_title": eventform.event.title,
                    "event": eventform.event,
                }

                eventform.password_reset_code = uuid.uuid4().hex.upper()
                eventform.password_reset_time = timezone.now()
                #eventform.user_changed = timezone.now()
                eventform.save()

                # log.debug(u"accounts_reset_password: for %s (%s)(%s): %s" % (user, str(user.id), str(eventform.id), eventform.password_reset_code))

                success = email_password_reset_requested(request, eventform)

                if success:
                    context["success"] = True
                else:
                    context["email_error"] = "Could not sent email."

            else:
                context["error"] = 'The provided email address has not been registered to any open events. Please register first.'

    log.debug(context)
    return render_template(request, "accounts_reset_password", data=context)


def accounts_reset_password_code(request, code):
    log.debug("accounts_reset_password_code")

    curdate = timezone.now().date()

    # Actually, to make this really safe, there should be also a test to see if the code is too old already
    # and if the user's email addresses match, but the PM/PO didn't want that, cause of reasons like
    # "We already changed the flow too much, the PO wouldn't like this.".
    # Therefore, this is a security hole of kinds that isn't closed.
    eventforms = EventForm2019.objects.filter(event__date_open__lte=curdate, event__date_close__gt=curdate, password_reset_code=code)

    if len(eventforms) == 0:
        session_delete_extra_data(request)
        issue_warning(request, "The code did not match.")
        context = {
            "code_not_matching_error": "The code did not match.",
            "code": code or "wrongcode",
        }
        # return render_template(request, "accounts_reset_password_code", data=context)
        return redirect('accounts_reset_password')

    eventform = eventforms[0]

    context = {
        "event_title": eventform.event.title,
        "event": eventform.event,
        "code": code or request.POST.get("code", "wrongcode"),
    }

    user = eventform.user

    if request.method == "POST":

        pwd1 = request.POST.get("pwd1", "").strip()
        pwd2 = request.POST.get("pwd2", "").strip()

        # todo: password rule validation (also done client side already)
        if len(pwd1) == 0 or len(pwd2) == 0:
            session_delete_extra_data(request)
            issue_warning(request, "Please provide a valid password.", field="pwd1")
            log.error(u"User %s password reset: Please provide a valid password." % (user))
            return render_template(request, "accounts_reset_password_code", data=context)

        if pwd1 != pwd2:
            session_delete_extra_data(request)
            issue_warning(request, "Passwords do not match.", field="pwd1")
            log.error(u"User %s password reset: Passwords do not match." % (user))
            return render_template(request, "accounts_reset_password_code", data=context)

        user = eventform.user

        #eventform.user_changed = curdate
        eventform.password_reset_code = None
        eventform.password_reset_time = None
        eventform.save()

        user.set_password(pwd1)
        user.save()

        try:
            login_user(request, user.username, pwd1)
        except Exception as ex:
            session_delete_extra_data(request)
            issue_warning(request, str(ex), field=field)
            return redirect('accounts_login')
        else:
            messages_delete(request)
            email_password_setup_done(request, eventform)
            return redirect('password_reset_done')

    return render_template(request, "accounts_reset_password_code", data=context)

def accounts_confirm_password(request):
    log.debug("accounts_confirm_password")
    return render_template(request, "accounts_confirm_password")

def password_reset_done(request):
    return render_template(request, "password_reset_done")

def password_set_done(request):
    return render_template(request, "password_set_done")


def accounts_login(request):
    log.debug("accounts_login")

    session_delete_extra_data(request)

    curdate = timezone.now().date()

    open_events = Event.objects.filter(date_open__lte=curdate, date_close__gt=curdate)
    # They want that as title on the page, even though at this stage we don't know what event
    # they will login to....
    event_title = open_events[0].title if len(open_events) > 0 else "10th Accenture New Year Concert"
    # ... maybe the solution is to have the event_id in the URL and as parameter here, so we
    # can load the right one... but then you wouldn't be able to have a generic login page
    # and you would need some kind of event dropdown selection or something on it.

    context = {
        "event_title": event_title,
    }

    return render_template(request, "accounts_login", data=context)


def accounts_login_process(request):
    log.debug("accounts_login_process")

    messages_delete(request)

    if request.method != "POST":
        issue_warning(request, 'Do not call this page directly.')
        session_delete_extra_data(request)
        return redirect('home')

    email = request.POST.get('email', "").strip()
    password = request.POST.get('password', "").strip()

    log.debug("")

    if len(email) == 0 or len(password) == 0:
        field = 'email' if len(email) == 0 else 'password'
        session_delete_extra_data(request)
        issue_warning(request, "Please provide your email address and your password.", field=field)
        return redirect('accounts_login')

    email_username = email[:30]  # django's auth_user.username is limited to 30 chars
    try:
        User.objects.get(username=email_username)
    except:
        field = 'email'
        session_delete_extra_data(request)
        issue_warning(request, "Your email address wasn't found.", field=field)
        return redirect('accounts_login')

    try:
        login_user(request, email_username, password)
    except Exception as ex:
        field = 'email'
        session_delete_extra_data(request)
        issue_warning(request, str(ex), field=field)
        return redirect('accounts_login')

    messages_delete(request)

    return redirect('overview')


def login_user(request, username, password):

    log.debug(u"login? %s, %s", username or "???", "<not shown>" or "???")

    try:
        user = authenticate(username=username, password=password)
        log.debug(u"login: %s" % user)

        if user is not None and user.is_active:
            log.debug(u"login: login(request, user)")
            login(request, user)
        else:
            log.debug(u"auth failed for username: %s" % username)
            user = None
    except Exception as ex:
        log.debug(u"auth failed for username %s with error %s" % (username, unicode(ex)))
        user = None

    if user is None:
        log.warn(u"auth failed for username %s with error %s" % (username, unicode("no user - user is none")))
        raise Exception(u"Email or password wrong.")

    if not user.is_active:
        log.warn(u"auth failed for username %s with error %s" % (username, unicode("user account is not active")))
        raise Exception(u"Your user is disabled. Please contact support.")

    return user


def accounts_logout(request):
    logout_user(request)
    return redirect('home')


def accounts_setup(request, code=None):
    log.debug("accounts_setup")

    if code is not None:
        try:
            eventform = EventForm2019.objects.get(password_setup_code=code)
        except:
            issue_warning(request, 'The code is not available.')
            session_delete_extra_data(request)
            return redirect('accounts_login')

        event = eventform.event
        code = eventform.password_setup_code

        if eventform.registration_done or eventform.password_setup_done:
            issue_warning(request, 'Your initial password was already set by you. Please use the password reset function instead.')
            session_delete_extra_data(request)
            return redirect('accounts_login')

        if not eventform.user.is_active:
            issue_warning(request, 'Your user account is disabled.')
            session_delete_extra_data(request)
            return redirect('home')

    else:
        # event = None
        # eventform = None
        # code = None
        issue_warning(request, 'No code supplied.')
        session_delete_extra_data(request)
        return redirect('home')

    curdate = timezone.now()

    context = {
        "eventform": eventform,
        "event": event,
        "event_title": event.title if event is not None else "10th Accenture New Year Concert",
        "code": code,
    }

    if request.method == "POST":
        pwd1 = request.POST.get("pwd1", "").strip()
        pwd2 = request.POST.get("pwd2", "").strip()

        # todo: password rule validation (also done client side already)
        if len(pwd1) == 0 or len(pwd2) == 0:
            context["error"] = "Please provide a valid password."
            return render_template(request, "accounts_set_password", data=context)

        user = eventform.user

        eventform.accepted_privacy_statement = AGREE_YES
        eventform.registration_done = True
        eventform.password_setup_code = None
        eventform.password_setup_done = True
        eventform.password_setup_done_time = curdate
        #eventform.user_changed = curdate
        eventform.save()

        user.set_password(pwd1)
        user.save()

        try:
            login_user(request, user.username, pwd1)
        except Exception as ex:
            session_delete_extra_data(request)
            issue_warning(request, str(ex), field=field)
            return redirect('accounts_login')
        else:
            email_password_setup_done(request, eventform)

        return redirect('password_set_done')

    return render_template(request, "accounts_set_password", data=context)
