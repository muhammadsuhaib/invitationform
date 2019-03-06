# encoding=utf-8
# We need the currently logged in user in the models.py::create_activity_log, so we just do this:
# http://stackoverflow.com/questions/4721771/get-current-user-log-in-signal-in-django
#
#
import logging

from concertinvitation.settings import DEBUG_LOGGER
log = logging.getLogger(DEBUG_LOGGER)


class Singleton(type):
    '''
        Singleton pattern requires for GetUser class
    '''
    def __init__(cls, name, bases, dicts):
        cls.instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.instance


class NotLoggedInUserException(Exception):
    '''
    '''
    def __init__(self, val='No users have been logged in'):
        self.val = val
        super(NotLoggedInUserException, self).__init__()

    def __str__(self):
        return self.val


class LoggedInUser(object):
    __metaclass__ = Singleton

    user = None

    def set_user(self, request):
        if request.user.is_authenticated():
            self.user = request.user

    def force_logout(self):
        self.user = None

    @property
    def current_user(self):
        '''
            Return current user or raise Exception
        '''
        if self.user is None:
            raise NotLoggedInUserException()
        return self.user

    @property
    def have_user(self):
        return self.user is not None


class LoggedInUserMiddleware(object):
    '''
        Insert this middleware after django.contrib.auth.middleware.AuthenticationMiddleware
    '''
    def process_request(self, request):
        '''
            Returned None for continue request
        '''
        logged_in_user = LoggedInUser()
        logged_in_user.set_user(request)
        return None
