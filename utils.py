# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# from django.utils import timezone
from django.core.mail import mail_admins, send_mail  # , EmailMultiAlternatives

import logging
from invitationform.models import *

from concertinvitation.settings import DEBUG_LOGGER, FROM_EMAIL, HOST_URL
log = logging.getLogger(DEBUG_LOGGER)

from django.core.mail import EmailMessage


def email_registration_done(request, eventform2019):
   
    code = eventform2019.password_setup_code or "???"
    login_url = "%s/accounts/login" % (HOST_URL)
    password_url = "%s/accounts/setup/%s" % (HOST_URL, code)

    print(login_url)
    print(password_url)

    to = eventform2019.user.email
    subject = u"【ご登録完了】%s" % (eventform2019.event.title)
    text = u"""
%(last)s %(first)s　様

この度は、 %(title)s へのご出欠の登録をいただきましてありがとうございます。
ご登録情報の確認/変更が生じた場合は、下記のURLよりパスワードを設定の上、確認/修正を行ってください。

Thank you very much for your registration for %(title)s.
If you wish to change your registered information, please set up your password from the link below  and login to change.

■パスワード設定用URL

　%(password_url)s

■登録情報確認/修正用URL

　%(login_url)s

■ お客様ID

　登録されたメールアドレス

ご不明点等はアクセンチュア ニューイヤー・コンサート事務局へお問い合わせください。
For any questions and inquiries, please contact Accenture New Year Concert Office:
TEL:03-5657-0700 (受付時間：平日10:00～18:00 土・日・祝日と12/29～1/3は休み)
Email:nyc-jimukyoku2019@jtbcom.co.jp


※本メールは送信専用となりますため、こちらのメールに返信いただいいてもご返答できませんので、ご了承ください。
""" % {
        "password_url": password_url,
        "login_url": login_url,
        "last": eventform2019.last_name,
        "first": eventform2019.first_name,
        "title": eventform2019.event.title,
    }

    try:
        # send_mail(subject, text, FROM_EMAIL, [to], fail_silently=EMAIL_FAIL_SILENTLY, html_message=html)

        email = EmailMessage(
            subject,
            text.strip(),
            FROM_EMAIL,
            [to],
            ['jimukyoku2019@acn-nyc.com', 'nyc-jimukyoku2019@jtbcom.co.jp', 'shinsuke.shinozaki@t-mark.co.jp']
        )
        email.send()

        #send_mail(subject, text.strip(), FROM_EMAIL, [to], fail_silently=False)
        #log.info(u"Sent email with subject [%s] to %s" % (subject, to))
        #mail_admins(subject, text.strip(), fail_silently=True)
    except Exception as ex:
        log.error(u"Could not send email with subject [%s] to %s, because: %s" % (subject, to, unicode(ex)))
        print(u"Could not send email with subject [%s] to %s, because: %s" % (subject, to, unicode(ex)))
        return False
    else:
        return True


def email_password_setup_done(request, eventform2019):

    login_url = "%s/accounts/login" % (HOST_URL)

    to = eventform2019.user.email
    subject = u"【パスワード設定完了】%s" % (eventform2019.event.title)
    text = u"""
%(last)s %(first)s　様

パスワードを設定致しました。
パスワードの内容は、お客さまご自身にしか分かりませんので、必ずメモをとるなどしてお控ください。
ご登録情報の確認/変更が生じた場合は、設定いただきましたパスワードで確認/修正を行ってください。

You have created your own password.
Your password is unique to yourself. If you changed, please take a note of it.
You will be required to enter this password to confirm and change your registered information.

■登録情報確認/修正用URL

　%(login_url)s

■ お客様ID

　登録されたメールアドレス


ご不明点等はアクセンチュア ニューイヤー・コンサート事務局へお問い合わせください。
For any questions and inquiries, please contact Accenture New Year Concert Office:
TEL:03-5657-0700 (受付時間：平日10:00～18:00 土・日・祝日と12/29～1/3は休み)
Email:nyc-jimukyoku2019@jtbcom.co.jp


※本メールは送信専用となりますため、こちらのメールに返信いただいいてもご返答できませんので、ご了承ください。
""" % {
        "login_url": login_url,
        "last": eventform2019.last_name,
        "first": eventform2019.first_name,
    }

    try:

        email = EmailMessage(
            subject,
            text.strip(),
            FROM_EMAIL,
            [to],
            ['jimukyoku2019@acn-nyc.com', 'nyc-jimukyoku2019@jtbcom.co.jp', 'shinsuke.shinozaki@t-mark.co.jp']
        )
        email.send()

    except Exception as ex:
        log.error(u"Could not send email with subject [%s] to %s, because: %s" % (subject, to, unicode(ex)))
        return False
    else:
        return True


def email_account_info_updated(request, eventform2019):

    login_url = "%s/accounts/login" % (HOST_URL)

    to = eventform2019.user.email
    subject = u"【ご変更完了】%s" % (eventform2019.event.title)
    text = u"""
%(last)s %(first)s　様


登録情報の変更を受付けました。
ご登録情報の確認/変更が生じた場合は、設定いただきましたパスワードで確認/修正を行ってください


We have updated your registered information.
You will be required to enter this password to confirm and change your registered information.


■登録情報確認/修正用URL

　%(login_url)s

■ お客様ID

　登録されたメールアドレス


ご不明点等はアクセンチュア ニューイヤー・コンサート事務局へお問い合わせください。
For any questions and inquiries, please contact Accenture New Year Concert Office:
TEL:03-5657-0700 (受付時間：平日10:00～18:00 土・日・祝日と12/29～1/3は休み)
Email:nyc-jimukyoku2019@jtbcom.co.jp


※本メールは送信専用となりますため、こちらのメールに返信いただいいてもご返答できませんので、ご了承ください。
""" % {
        "login_url": login_url,
        "last": eventform2019.last_name,
        "first": eventform2019.first_name,
    }

    try:

        email = EmailMessage(
            subject,
            text.strip(),
            FROM_EMAIL,
            [to],
            ['nyc-jimukyoku2019@acn-nyc.com', 'nyc-jimukyoku2019@jtbcom.co.jp', 'shinsuke.shinozaki@t-mark.co.jp']
        )
        email.send()

    except Exception as ex:
        log.error(u"Could not send email with subject [%s] to %s, because: %s" % (subject, to, unicode(ex)))
        return False
    else:
        return True


def email_password_reset_requested(request, eventform2019):

    reset_code = eventform2019.password_reset_code
    pwd_reset_confirm = "%s/accounts/resetpassword/code/%s" % (HOST_URL, reset_code)

    to = eventform2019.user.email
    subject = u"【パスワード再発行】%s" % (eventform2019.event.title)
    text = u"""
%(last)s %(first)s　様

下記のURLよりパスワードの再設定をお願い致します。
Please set up your new password from the link below.

■再パスワード設定用URL

　%(pwd_reset_confirm)s


ご不明点等はアクセンチュア ニューイヤー・コンサート事務局へお問い合わせください。
For any questions and inquiries, please contact Accenture New Year Concert Office:
TEL:03-5657-0700 (受付時間：平日10:00～18:00 土・日・祝日と12/29～1/3は休み)
Email:nyc-jimukyoku2019@jtbcom.co.jp


※本メールは送信専用となりますため、こちらのメールに返信いただいいてもご返答できませんので、ご了承ください。
""" % {
        "pwd_reset_confirm": pwd_reset_confirm,
        "last": eventform2019.last_name,
        "first": eventform2019.first_name,
        "reset_code": reset_code,
    }

    try:

        email = EmailMessage(
            subject,
            text.strip(),
            FROM_EMAIL,
            [to],
            ['nyc-jimukyoku2019@acn-nyc.com', 'nyc-jimukyoku2019@jtbcom.co.jp', 'shinsuke.shinozaki@t-mark.co.jp']
        )
        email.send()

    except Exception as ex:
        log.error(u"Could not send email with subject [%s] to %s, because: %s" % (subject, to, unicode(ex)))
        return False
    else:
        return True
