# encoding=utf-8
"""concertinvitation URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.views.generic import RedirectView

from invitationform import views
# admin.site.index_title = "Welcome to ACCENTURE NEW YEAR CONCERT INVITATION FORMS"
admin.site.site_header = "Accenture NYC 2019 Administration"
admin.site.site_title = "Accenture NYC 2019"
admin.site.index_title = "Welcome to Accenture NYC 2019 Management"

urlpatterns = [
    url(r'^favicon.ico$', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
    url(r'^robots.txt$', RedirectView.as_view(url='/static/robots.txt', permanent=True)),

    url(r'^$', views.home, name="home"),
    url(r'^bouncer/$', views.bouncer, name="bouncer"),
    url(r'^event/$', views.bouncer, name="event"),

    url(r'^registration/$', views.registration_redirect, name="registration_redirect"),
    url(r'^registration/(?P<event_id>\d+)/$', views.registration, name="registration"),
    url(r'^registration/process/$', views.registration_process, name="registration_process"),
    url(r'^registration/confirm/$', views.registration_confirm, name="registration_confirm"),
    url(r'^registration/confirm/process/$', views.registration_confirm_process, name="registration_confirm_process"),
    url(r'^registration/thankyou/$', views.registration_thankyou, name="registration_thankyou"),
    url(r'^registration/exist/$', views.registration_exist, name="registration_exist"),

    url(r'^overview/$', views.overview, name="overview"),
    url(r'^overview/process/(?P<eventform_id>\d+)/$', views.overview_process, name="overview_process"),
    url(r'^overview/change/(?P<eventform_id>\d+)/$', views.overview_change, name="overview_change"),
    url(r'^overview/change/(?P<eventform_id>\d+)/process/$', views.overview_change_process, name="overview_change_process"),
    url(r'^overview/confirm/(?P<eventform_id>\d+)/$', views.overview_confirm, name="overview_confirm"),
    url(r'^overview/confirm/(?P<eventform_id>\d+)/process/$', views.overview_confirm_process, name="overview_confirm_process"),
    url(r'^overview/thankyou/(?P<eventform_id>\d+)/$', views.overview_thankyou, name="overview_thankyou"),


    url(r'^privacy/$', views.privacy_statement, name="privacy_statement"),
    url(r'^privacy/process/$', views.privacy_statement_process, name="privacy_statement_process"),
    url(r'^password_set_done/$', views.password_set_done, name="password_set_done"),
    url(r'^password_reset_done/$', views.password_reset_done, name="password_reset_done"),

    url(r'^logout/$', views.accounts_logout, name="logout"),
    url(r'^login/$', views.accounts_login, name="login"),
    url(r'^login/process/$', views.accounts_login_process, name="login_process"),
    url(r'^accounts/resetpassword/$', views.accounts_reset_password, name="accounts_reset_password"),
    url(r'^accounts/resetpassword/code/(?P<code>\w+)/$', views.accounts_reset_password_code, name="accounts_reset_password_code"),
    url(r'^accounts/resetpassword/confirm/$', views.accounts_confirm_password, name="accounts_confirm_password"),
    url(r'^accounts/login/$', views.accounts_login, name="accounts_login"),
    url(r'^accounts/logout/$', views.accounts_logout, name="accounts_logout"),
    url(r'^accounts/setup/$', views.accounts_setup),
    url(r'^accounts/setup/(?P<code>\w+)/$', views.accounts_setup, name="accounts_setup"),

    url(r'^admin/', admin.site.urls),
]
