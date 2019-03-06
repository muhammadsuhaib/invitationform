# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db                  import models
from django.contrib.auth.models import User  # , Group
# from django.core.exceptions     import ValidationError
# from django.utils.encoding      import force_unicode  # smart_str, smart_unicode,
# from django.utils.functional    import lazy
# from django.db.models           import Q
from django.db.models.signals   import post_save
# from django.utils.safestring    import mark_safe
from django.utils import timezone
# TODO(dkg): translate model names and attributes
# https://stackoverflow.com/questions/2938692/django-internationalization-for-admin-pages-translate-model-name-and-attribute
from django.utils.translation import ugettext_lazy as _

from invitationform.middleware import LoggedInUser

import logging
import os
import re

from concertinvitation.settings import DEBUG_LOGGER
log = logging.getLogger(DEBUG_LOGGER)


CHOICE_NONE = u"u"
CHOICE_YES = u"y"
CHOICE_NO = u"n"
CHOICES = (
    (CHOICE_NONE, u"not set"),
    (CHOICE_YES, u"はい"),
    (CHOICE_NO, u"いいえ"),
)

AGREE_NONE = u"n/a"
AGREE_NO = u"no"
AGREE_YES = u"yes"
AGREE_STATUS = (
    (AGREE_NONE, u"not set"),
    (AGREE_NO, u"X"),
    (AGREE_YES, u"〇"),
)

TIER_LEVEL_NONE = u"0"
TIER_LEVEL_ONE = u"1"
TIER_LEVEL_TWO = u"2"
TIER_LEVEL_THREE = u"3"
TIER_LEVELS = (
    (TIER_LEVEL_NONE, u"not set"),
    (TIER_LEVEL_ONE, u"1"),
    (TIER_LEVEL_TWO, u"2"),
    (TIER_LEVEL_THREE, u"3"),
)

INVITATION_TYPE_NONE = u"none"
INVITATION_TYPE_CARD = u"card"
INVITATION_TYPE_LETTER = u"letter"
INVITATION_TYPES = (
    (INVITATION_TYPE_NONE, u"not set"),
    (INVITATION_TYPE_CARD, u"招待状"),
    (INVITATION_TYPE_LETTER, u"推薦状"),
)

DELIVERY_TYPE_NONE = u"none"
DELIVERY_TYPE_MAIL = u"mail"
DELIVERY_TYPE_PERSONAL = u"hand"
DELIVERY_TYPES = (
    (DELIVERY_TYPE_NONE, u"not set"),
    (DELIVERY_TYPE_MAIL, u"郵送"),
    (DELIVERY_TYPE_PERSONAL, u"手渡"),
)

ATTEND_NONE = "u"
ATTEND_YES = "y"
ATTEND_NO = "n"
ATTEND_TYPES = (
    (ATTEND_NONE, _("not set")),
    (ATTEND_YES, _("出席")),
    (ATTEND_NO, _("欠席")),
)

CONTACT_ADDRESS_TYPE_NOTSET = u"none"
CONTACT_ADDRESS_TYPE_HONNIN = u"hon"
CONTACT_ADDRESS_TYPE_SECRETARY = u"sec"
CONTACT_ADDRESS_TYPES = (
    (CONTACT_ADDRESS_TYPE_NOTSET, u"not set"),
    (CONTACT_ADDRESS_TYPE_HONNIN, u"ご本人"),
    (CONTACT_ADDRESS_TYPE_SECRETARY, u"秘書様"),
)

ADDRESS_TYPE_NOTSET = u"none"
ADDRESS_TYPE_HOME = u"home"
ADDRESS_TYPE_COMPANY = u"company"
ADDRESS_TYPES = (
    (ADDRESS_TYPE_NOTSET, u"not set"),
    (ADDRESS_TYPE_HOME, u"自宅"),
    (ADDRESS_TYPE_COMPANY, u"会社"),
)

BRING_TYPE_NONE = u"none"
BRING_TYPE_MAIL = u"mail"
BRING_TYPE_PERSONAL = u"hand"
BRING_TYPES = (
    (BRING_TYPE_NONE, u"not set"),
    (BRING_TYPE_MAIL, u"郵送"),
    (BRING_TYPE_PERSONAL, u"当日持参"),
)

TRANSPORTATION_TYPE_NONE = u"none"
# TRANSPORTATION_TYPE_TRAIN = u"train"
TRANSPORTATION_TYPE_HI_TRAIN = u"speed"
TRANSPORTATION_TYPE_CAR = u"car"
TRANSPORTATION_TYPES = (
    (TRANSPORTATION_TYPE_NONE, u"not set"),
    # (TRANSPORTATION_TYPE_TRAIN, u"列車"),
    (TRANSPORTATION_TYPE_HI_TRAIN, u"新幹線"),
    (TRANSPORTATION_TYPE_CAR, u"お車"),
)

GREETING_TYPE_NONE = u"none"
GREETING_TYPE_MAIL = u"mail"
GREETING_TYPE_PERSONAL = u"hand"
GREETING_TYPES = (
    (GREETING_TYPE_NONE, u"not set"),
    (GREETING_TYPE_MAIL, u"郵送"),
    (GREETING_TYPE_PERSONAL, u"手渡し"),
)

CSG_TYPE_NONE = "n/a"
CSG_TYPE_HPS = "hps"
CSG_TYPE_PRD = "prd"
CSG_TYPE_FS = "fs"
CSG_TYPE_CMT = "cmt"
CSG_TYPE_RES = "res"
CSG_TYPES = (
    (CSG_TYPE_NONE, "not set"),
    (CSG_TYPE_HPS, "H&PS"),
    (CSG_TYPE_PRD, "PRD"),
    (CSG_TYPE_FS, "FS"),
    (CSG_TYPE_CMT, "CMT"),
    (CSG_TYPE_RES, "RES"),
)

GP_TYPE_NONE = "n/a"
GP_TYPE_STRATEGY = "strategy"
GP_TYPE_DIGITAL = "digital"
GP_TYPE_TECH = "tech"
GP_TYPE_OPE = "ope"
GP_TYPES = (
    (GP_TYPE_NONE, "not set"),
    (GP_TYPE_STRATEGY, "strategy"),
    (GP_TYPE_DIGITAL, "digital"),
    (GP_TYPE_TECH, "tech"),
    (GP_TYPE_OPE, "ope"),
)


class CKEditorField(models.TextField):
    pass


class CommonColumns(models.Model):

    created_by = models.ForeignKey(User, related_name="+", blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name="+", blank=True, null=True)
    created_at = models.DateTimeField(u"受付日", auto_now_add=True)
    updated_at = models.DateTimeField(u"編集日", auto_now=True)
    # they insist on these extra distinctions .... ugh
    # 編集日
    user_changed = models.DateTimeField(u"編集日", blank=True, null=True)
    # アドミン編集日
    admin_changed = models.DateTimeField(u"アドミン編集日", blank=True, null=True)

    def save(self, *args, **kwargs):
        try:
            logged_in = LoggedInUser()
        except Exception:
            logged_in = None

        if logged_in is not None and logged_in.user is not None:
            if self.created_by is None:
                self.created_by = logged_in.user
            self.updated_by = logged_in.user

        super(CommonColumns, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class CommonColumnsExtra(CommonColumns):
    # TODO(dkg): Put Japanese column names as first parameter for each field.
    title = models.CharField("Title", max_length=255)
    description = CKEditorField("Description", blank=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.title or u""

# Problem: The PO wants to re-use this system year after year, each year
# for a new event. However, the registration data should persists, but still
# allow for the same company to "sign up" again for that new particular event.
#
# How to do this in a sane manner, that doesn't require a lot of admin interaction
# to change settings etc within this CMS?
#


class Event(CommonColumnsExtra):

    class Meta:
        verbose_name = 'ダウンロードページ'
        verbose_name_plural = 'ダウンロードページ'
        

    EVENT_TYPE_NONE = "none"
    EVENT_TYPE_NYC = "nyc"
    EVENT_TYPE_NYC2019 = "nyc2019"
    EVENT_TYPE_CXO = "cxo"
    EVENT_TYPES = (
        (EVENT_TYPE_NONE, u"not set"),
        (EVENT_TYPE_NYC, u"NYC"),
        (EVENT_TYPE_NYC2019, u"NYC2019"),
        (EVENT_TYPE_CXO, u"CXO"),
    )

    # TODO(dkg): Put Japanese column names as first parameter for each field.
    # date for registration to be open/available to users
    date_open = models.DateField("Open Registration Date", help_text="Date for registration to be open/available to users.")
    # date of the event
    date_event = models.DateField("Event Date", help_text="Date of the Event.")
    # date when registration closes / is not possible any longer
    date_close = models.DateField("Close Registration Date", help_text="Date when registration closes / is not possible any longer.")
    # Users will be mailed (via postcard!) this code, and they have to enter it in order to be able to register for the event
    entry_code = models.CharField("Registration Code", max_length=25, help_text="Users will be mailed (via postcard!) this code, and they have to enter it in order to be able to register for the event")
    # Determines what elements/items/questions are displayed on the actual form
    event_type = models.CharField("Event Type", max_length=20, choices=EVENT_TYPES, default=EVENT_TYPE_NONE)

    # def save(self, *args, **kwargs):
    #     log.debug("Event(%s)::save()" % (self))
    #
    #     # TODO(dkg): Or should we allow multiple events to be open for registration.
    #     #            Make sure that only one event at a time is open for registration?!
    #     super(Event, self).save(*args, **kwargs)
    #     log.debug("Event(%s)::save() super.save() called" % (self))



    def get_form_fields(self):

        if self.event_type not in [Event.EVENT_TYPE_NYC, Event.EVENT_TYPE_NYC2019, Event.EVENT_TYPE_CXO]:
            raise Exception("Please set the event type on Event %s" % (self))
        if self.event_type == Event.EVENT_TYPE_CXO:
            return list(set(REQUIRED_FIELDS_CXO + EVENT_FIELDS_CXO_ONLY + POSSIBLE_REQUIRED_FIELDS))
        if self.event_type == Event.EVENT_TYPE_NYC:
            return list(set(REQUIRED_FIELDS_NYC + EVENT_FIELDS_NYC_ONLY + POSSIBLE_REQUIRED_FIELDS))
        if self.event_type == Event.EVENT_TYPE_NYC2019:
            return list(set(REQUIRED_FIELDS_NYC2019 + EVENT_FIELDS_NYC2019_ONLY + POSSIBLE_REQUIRED_FIELDS))
            
        return []

    def get_form_fields_as_string(self):
        return ",".join(self.get_form_fields())

    def get_required_form_fields(self):

        if self.event_type not in [Event.EVENT_TYPE_NYC, Event.EVENT_TYPE_NYC2019, Event.EVENT_TYPE_CXO]:
            raise Exception("Please set the event type on Event %s" % (self))
        if self.event_type == Event.EVENT_TYPE_CXO:
            return list(set(REQUIRED_FIELDS_CXO + POSSIBLE_REQUIRED_FIELDS))
        if self.event_type == Event.EVENT_TYPE_NYC:
            return list(set(REQUIRED_FIELDS_NYC))
        if self.event_type == Event.EVENT_TYPE_NYC2019:
            return list(set(REQUIRED_FIELDS_NYC2019))
        return []

    def get_required_form_fields_as_string(self):
        return ",".join(self.get_required_form_fields())



# TODO(dkg): maybe have a model that let's the admins assign which questions etc.
#            are supposed to go where on the form, and which should be not on the
#            form at all. But since they are only paying ¥1,000,000 (or even less)
#            I am hestitant to put that much work into this right now. Certainly
#            something to keep in mind for a phase 2 or so.

# Each form has it's own set of fields. Assumption: all other fields are shared/on both forms.
EVENT_FIELDS_CXO_ONLY = [
    "company_name_furigana",
    "ws",
    "party_attendance",
    "stay_night",
    "golf",
    "golf_hc",
    "golf_bag",
    "transportation",
    "shinkansen_to",
    "shinkansen_from",
    "car_license_plate",
    "notes",
    "allergies",
    "golf_visitor_zip",
    "golf_visitor_address",
]

EVENT_FIELDS_NYC_ONLY = [
    "honnin_attending",
    "companion_attending",
    "secretary_attending",
    "honnin_attending_reception",
    "companion_attending_reception",
    "secretary_attending_reception",
]

EVENT_FIELDS_NYC2019_ONLY = [
    "honnin_attending",
    "companion_attending",
    "secretary_attending",
    "honnin_attending_reception",
    "companion_attending_reception",
    "secretary_attending_reception",
]

REQUIRED_FIELDS_CXO = [
    "company_name",
    "compliance",
    "company_name_furigana",
    "position",
    "last_name",
    "last_name_furigana",
    "first_name",
    "first_name_furigana",
    "address_type",
    "zipcode",
    "prefecture",
    "address",
    "address_2",
    "honnin_attending",
    "companion_attending",
    "secretary_attending",
    "secretary_department",
    "secretary_last_name",
    "secretary_first_name",
    "secretary_last_name_furigana",
    "secretary_first_name_furigana",
    "contact_address_type",
    "phone_number",
    "email",
    "ws",
    "party_attendance",
    "stay_night",
    "golf",
    "transportation",
]

REQUIRED_FIELDS_NYC = [
    "company_name",
    "position",
    "last_name",
    "last_name_furigana",
    "first_name",
    "first_name_furigana",
    "address_type",
    "zipcode",
    "prefecture",
    "address",
    "address_2",
    "honnin_attending",
    "companion_attending",
    "secretary_attending",
    "honnin_attending_reception",
    "contact_address_type",
    "phone_number",
    "email",
]

REQUIRED_FIELDS_NYC2019 = [
    "company_name",
    "position",
    "last_name",
    "last_name_furigana",
    "first_name",
    "first_name_furigana",
    "address_type",
    "zipcode",
    "prefecture",
    "address",
    "address_2",
    "honnin_attending",
    "companion_attending",
    "secretary_attending",
    "honnin_attending_reception",
    "contact_address_type",
    "phone_number",
    "email",
]

# depends on "secretary_attending" field
POSSIBLE_REQUIRED_FIELDS = [
    "secretary_department",
    "secretary_last_name",
    "secretary_first_name",
    "secretary_last_name_furigana",
    "secretary_first_name_furigana",
]

CHARACTER_FIELDS = [
    'contact_id',
    'lk_id',
    'csg',
    'gp',
    'industry',
    'company_name',
    'company_name_furigana',
    'cal',
    'compliance',
    'position',
    'last_name',
    'last_name_furigana',
    'first_name',
    'first_name_furigana',
    'tier',
    'invitation_type',
    'delivery_type',
    'circulation_destionation',
    'zipcode',
    "prefecture",
    "address",
    "address_2",
    'address_type',
    'invitation_status',
    'honnin_attending',
    'companion_attending',
    'secretary_attending',
    'secretary_department',
    'secretary_last_name',
    'secretary_last_name_furigana',
    'secretary_first_name',
    'secretary_first_name_furigana',
    'honnin_attending_reception',
    'companion_attending_reception',
    'secretary_attending_reception',
    'contact_address_type',
    'phone_number',
    "extension",
    'email',
    'comment',
    'attendee_md',
    'attendee_md_ea',
    'ws',
    'party_attendance',
    'stay_night',
    'golf',
    'golf_hc',
    'golf_bag',
    'transportation',
    'shinkansen_to',
    'shinkansen_from',
    'car_license_plate',
    'notes',
    'allergies',
    'golf_visitor_zip',
    'golf_visitor_address',
    'greetings',
    'greetings_status'
]

def numz2h(z2hstr):
    z2hstr = z2hstr.replace('０', "0")
    z2hstr = z2hstr.replace('１', "1")
    z2hstr = z2hstr.replace('２', "2")
    z2hstr = z2hstr.replace('３', "3")
    z2hstr = z2hstr.replace('４', "4")
    z2hstr = z2hstr.replace('５', "5")
    z2hstr = z2hstr.replace('６', "6")
    z2hstr = z2hstr.replace('７', "7")
    z2hstr = z2hstr.replace('８', "8")
    z2hstr = z2hstr.replace('９', "9")
    #z2hstr = z2hstr.replace('－', "-")
    return z2hstr



def get_app_list(self, request):
    """
    Return a sorted list of all the installed apps that have been
    registered in this site.
    """
    app_dict = self._build_app_dict(request)

    # Sort the apps alphabetically.
    app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

    # Sort the models alphabetically within each app.
    for app in app_list:
        app['models'].sort(key=lambda x: x['name'])

    return app_list




# This was supposed to be a 1:1 relationship with User, but due to the whole "we want to be able to re-use this cms"
# (see comment at top), this has to be a 1:n relationship, as the company is supposed to sign-up anew for each event.
class EventForm2019(CommonColumns):
    class Meta:
       
        verbose_name_plural = 'EventForms(2019)'
       

    # user = models.OneToOneField(User)
    user = models.ForeignKey(User, null=True)
    # The event this user/company wants to register for
    event = models.ForeignKey(Event, null=True)

    # TODO(dkg): Put Japanese column names as first parameter for each field.
    # TODO(dkg): Furigana are expected to be in Katakana - need to implement validation for that!

    # 受信日
    signup_date = models.DateTimeField(u"受信日", auto_now_add=True)

    # Contact ID
    contact_id = models.CharField(u"Contact ID", max_length=50, blank=True, null=True)
    # LKID
    lk_id = models.CharField(u"LKID", max_length=50, blank=True, null=True)
    # CSG
    csg = models.CharField(u"CSG", max_length=10, choices=CSG_TYPES, default=CSG_TYPE_NONE, blank=True, null=True)
    # CSG
    gp = models.CharField(u"GP", max_length=10, choices=GP_TYPES, default=GP_TYPE_NONE, blank=True, null=True)
    # インダストリー
    industry = models.CharField(u"インダストリー", max_length=200, blank=True, null=True)

    # 会社名
    company_name = models.CharField(u"会社名", max_length=250, null=True, blank=True)
    # 会社名カナ（全角カナ）
    company_name_furigana = models.CharField(u"会社名カナ（全角カナ）", max_length=250, null=True, blank=True)

    # CAL/担当者（フルネーム漢字）
    cal = models.CharField(u"CAL/担当者（フルネーム漢字）", max_length=100, blank=True, null=True)
    # 自社のコンプライアンス規定と照らして参加可能か？
    compliance = models.CharField(u"自社のコンプライアンス規定と照らして参加可能か？", max_length=4, choices=CHOICES, default=CHOICE_NONE, blank=True, null=True)

    # 役職
    position = models.CharField(u"役職", max_length=50, blank=True, null=True)
    # 役職確認日（要正確）
    position_verified_date = models.DateField(u"役職確認日（要正確）", blank=True, null=True)

    # 姓
    last_name = models.CharField(u"姓", max_length=50)
    # 姓カナ（全角）
    last_name_furigana = models.CharField(u"姓カナ（全角）", max_length=50)
    # 名
    first_name = models.CharField(u"名", max_length=50)
    # 名カナ（全角）
    first_name_furigana = models.CharField(u"名カナ（全角）", max_length=50)

    # Tier
    tier = models.CharField(u"Tier", max_length=2, choices=TIER_LEVELS, default=TIER_LEVEL_NONE, blank=True, null=True)
    # 招待状 or 推薦状
    invitation_type = models.CharField(u"招待状 or 推薦状", max_length=6, choices=INVITATION_TYPES, default=INVITATION_TYPE_NONE, blank=True, null=True)
    # 郵送 or 手渡
    delivery_type = models.CharField(u"郵送 or 手渡", max_length=4, choices=DELIVERY_TYPES, default=DELIVERY_TYPE_NONE, blank=True, null=True)
    # 手渡しの場合のサーキュレーション先
    circulation_destionation = models.CharField(u"手渡しの場合のサーキュレーション先", max_length=40, null=True, blank=True)
    # 〒
    zipcode = models.CharField(u"〒", max_length=8, null=True, blank=True)

    # 県
    prefecture = models.CharField(u"県", max_length=250, null=True, blank=True)

    # 住所
    address = models.CharField(u"住所", max_length=250, null=True, blank=True)

    # 住所 #2
    address_2 = models.CharField(u"住所 #2", max_length=250, null=True, blank=True)

    # 自宅/会社
    address_type = models.CharField(u"自宅/会社", max_length=10, choices=ADDRESS_TYPES, default=ADDRESS_TYPE_NOTSET, blank=True, null=True)
    # 招待状のステータス
    invitation_status = models.CharField(u"招待状のステータス", max_length=100, blank=True, null=True)

    # ご本人出欠
    honnin_attending = models.CharField(u"ご本人出欠", max_length=2, choices=ATTEND_TYPES, default=ATTEND_NONE, blank=True, null=True)
    # 同伴者出欠
    companion_attending = models.CharField(u"同伴者出欠", max_length=4, choices=ATTEND_TYPES, default=ATTEND_NONE, blank=True, null=True)
    # 秘書出欠
    secretary_attending = models.CharField(u"秘書出欠", max_length=4, choices=ATTEND_TYPES, default=ATTEND_NONE, blank=True, null=True)

    # 秘書所属部署名
    secretary_department = models.CharField(u"秘書所属部署名", max_length=50, blank=True, null=True)
    # 秘書姓
    secretary_last_name = models.CharField(u"秘書姓", max_length=50, blank=True, null=True)
    # 秘書 姓カナ（全角）
    secretary_last_name_furigana = models.CharField(u"秘書 姓カナ（全角）", max_length=50, blank=True, null=True)
    # 秘書名
    secretary_first_name = models.CharField(u"秘書名", max_length=50, blank=True, null=True)
    # 秘書 名カナ（全角）
    secretary_first_name_furigana = models.CharField(u"秘書 名カナ（全角）", max_length=50, blank=True, null=True)

    # レセプション本人出欠
    honnin_attending_reception = models.CharField(u"レセプション本人出欠", max_length=2, choices=ATTEND_TYPES, default=ATTEND_NONE, blank=True, null=True)
    # レセプション同伴者出欠
    companion_attending_reception = models.CharField(u"レセプション同伴者出欠", max_length=2, choices=ATTEND_TYPES, default=ATTEND_NONE, blank=True, null=True)
    # レセプション秘書出欠
    secretary_attending_reception = models.CharField(u"レセプション秘書出欠", max_length=2, choices=ATTEND_TYPES, default=ATTEND_NONE, blank=True, null=True)

    # 今後の連絡先
    contact_address_type = models.CharField(u"今後の連絡先", max_length=10, choices=CONTACT_ADDRESS_TYPES, default=CONTACT_ADDRESS_TYPE_NOTSET, blank=True, null=True)

    # 電話番号
    phone_number = models.CharField(u"電話番号", max_length=50)

    # 内線
    extension = models.CharField(u"内線", max_length=50, blank=True, null=True)

    # メールアドレス
    email = models.CharField(u"メールアドレス", max_length=255)
    # コメント
    comment = models.TextField(u"コメント", blank=True, null=True)

    # アテンドMD
    attendee_md = models.CharField(u"アテンドMD", max_length=40, blank=True, null=True)
    # アテンドMDのEA
    attendee_md_ea = models.CharField(u"アテンドMDのEA", max_length=40, blank=True, null=True)

    # ワークショップ
    ws = models.CharField(u"ワークショップ", max_length=4, choices=AGREE_STATUS, default=AGREE_NONE, blank=True, null=True)

    # 懇親会
    party_attendance = models.CharField(u"懇親会", max_length=4, choices=AGREE_STATUS, default=AGREE_NONE, blank=True, null=True)
    # 宿泊
    stay_night = models.CharField(u"宿泊", max_length=4, choices=AGREE_STATUS, default=AGREE_NONE, blank=True, null=True)

    # ゴルフ
    golf = models.CharField(u"ゴルフ", max_length=4, choices=AGREE_STATUS, default=AGREE_NONE, blank=True, null=True)
    # ゴルフ ハンディキャップ
    golf_hc = models.CharField(u"ゴルフ ハンディキャップ", max_length=10, blank=True, null=True)
    # ゴルフバッグ
    golf_bag = models.CharField(u"ゴルフバッグ", max_length=16, choices=BRING_TYPES, default=BRING_TYPE_NONE, blank=True, null=True)

    # 交通手段
    transportation = models.CharField(u"交通手段", max_length=6, choices=TRANSPORTATION_TYPES, default=TRANSPORTATION_TYPE_NONE, blank=True, null=True)
    # 新幹線（行き）
    shinkansen_to = models.CharField(u"新幹線（行き）", max_length=250, blank=True, null=True)
    # 新幹線（帰り）
    shinkansen_from = models.CharField(u"新幹線（帰り）", max_length=250, blank=True, null=True)
    # お車ナンバー
    car_license_plate = models.CharField(u"お車ナンバー", max_length=25, blank=True, null=True)

    # その他備考欄
    notes = models.CharField(u"その他備考欄", max_length=250, blank=True, null=True)
    # 食べ物アレルギー
    allergies = models.CharField(u"食べ物アレルギー", max_length=250, blank=True, null=True)

    # ゴルフ　ビジター登録用　ご自宅郵便番号
    golf_visitor_zip = models.CharField(u"ゴルフ　ビジター登録用　ご自宅郵便番号", max_length=10, blank=True, null=True)
    # ゴルフ　ビジター登録用　ご自宅住所
    golf_visitor_address = models.CharField(u"ゴルフ　ビジター登録用　ご自宅住所", max_length=250, blank=True, null=True)

    # お礼状
    greetings = models.CharField(u"お礼状", max_length=6, choices=GREETING_TYPES, default=GREETING_TYPE_NONE, blank=True, null=True)
    # お礼状ステータス
    greetings_status = models.CharField(u"お礼状ステータス", max_length=80, blank=True, null=True)

    # prefecture = models.CharField("Prefecture", max_length=50, null=True, blank=True)

    accepted_privacy_statement = models.CharField(max_length=5, choices=AGREE_STATUS, default=AGREE_NONE, blank=True, null=True)
    registration_done = models.BooleanField(default=False)

    password_setup_code = models.CharField(max_length=100, null=True, blank=True)
    password_setup_time = models.DateTimeField(null=True, blank=True)
    password_setup_done = models.BooleanField(default=False)
    password_setup_done_time = models.DateTimeField(null=True, blank=True)

    password_reset_code = models.CharField(max_length=100, null=True, blank=True)
    password_reset_time = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        for field in CHARACTER_FIELDS:
            try:
                val = numz2h(getattr(self, field))
                setattr(self, field, val)
            except:
                pass
        self.phone_number = self.phone_number.replace('－', "-")

        self.address_2 = re.sub(r'([0-9]+)(ー|ー|－)([0-9]+)(ー|ー|－)([0-9]+)', r"\1-\3-\5", self.address_2)
        self.address_2 = re.sub(r'([0-9]+)(ー|ー|－)([0-9]+)', r"\1-\3", self.address_2)

        super(EventForm2019, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'Company: %s [%s]' % (self.company_name, self.email or self.user)







# This was supposed to be a 1:1 relationship with User, but due to the whole "we want to be able to re-use this cms"
# (see comment at top), this has to be a 1:n relationship, as the company is supposed to sign-up anew for each event.

class EventForm(CommonColumns):
    class Meta:        
         
            verbose_name_plural = "EventForms(2018)"


    # user = models.OneToOneField(User)
    user = models.ForeignKey(User, null=True)
    # The event this user/company wants to register for
    event = models.ForeignKey(Event, null=True)

    # TODO(dkg): Put Japanese column names as first parameter for each field.
    # TODO(dkg): Furigana are expected to be in Katakana - need to implement validation for that!

    # 受信日
    signup_date = models.DateTimeField(u"受信日", auto_now_add=True)

    # Contact ID
    contact_id = models.CharField(u"Contact ID", max_length=50, blank=True, null=True)
    # LKID
    lk_id = models.CharField(u"LKID", max_length=50, blank=True, null=True)
    # CSG
    csg = models.CharField(u"CSG", max_length=10, choices=CSG_TYPES, default=CSG_TYPE_NONE, blank=True, null=True)
    # CSG
    gp = models.CharField(u"GP", max_length=10, choices=GP_TYPES, default=GP_TYPE_NONE, blank=True, null=True)
    # インダストリー
    industry = models.CharField(u"インダストリー", max_length=200, blank=True, null=True)

    # 会社名
    company_name = models.CharField(u"会社名", max_length=250, null=True, blank=True)
    # 会社名カナ（全角カナ）
    company_name_furigana = models.CharField(u"会社名カナ（全角カナ）", max_length=250, null=True, blank=True)

    # CAL/担当者（フルネーム漢字）
    cal = models.CharField(u"CAL/担当者（フルネーム漢字）", max_length=100, blank=True, null=True)
    # 自社のコンプライアンス規定と照らして参加可能か？
    compliance = models.CharField(u"自社のコンプライアンス規定と照らして参加可能か？", max_length=4, choices=CHOICES, default=CHOICE_NONE, blank=True, null=True)

    # 役職
    position = models.CharField(u"役職", max_length=50, blank=True, null=True)
    # 役職確認日（要正確）
    position_verified_date = models.DateField(u"役職確認日（要正確）", blank=True, null=True)

    # 姓
    last_name = models.CharField(u"姓", max_length=50)
    # 姓カナ（全角）
    last_name_furigana = models.CharField(u"姓カナ（全角）", max_length=50)
    # 名
    first_name = models.CharField(u"名", max_length=50)
    # 名カナ（全角）
    first_name_furigana = models.CharField(u"名カナ（全角）", max_length=50)

    # Tier
    tier = models.CharField(u"Tier", max_length=2, choices=TIER_LEVELS, default=TIER_LEVEL_NONE, blank=True, null=True)
    # 招待状 or 推薦状
    invitation_type = models.CharField(u"招待状 or 推薦状", max_length=6, choices=INVITATION_TYPES, default=INVITATION_TYPE_NONE, blank=True, null=True)
    # 郵送 or 手渡
    delivery_type = models.CharField(u"郵送 or 手渡", max_length=4, choices=DELIVERY_TYPES, default=DELIVERY_TYPE_NONE, blank=True, null=True)
    # 手渡しの場合のサーキュレーション先
    circulation_destionation = models.CharField(u"手渡しの場合のサーキュレーション先", max_length=40, null=True, blank=True)
    # 〒
    zipcode = models.CharField(u"〒", max_length=8, null=True, blank=True)

    # 県
    prefecture = models.CharField(u"県", max_length=250, null=True, blank=True)

    # 住所
    address = models.CharField(u"住所", max_length=250, null=True, blank=True)

    # 住所 #2
    address_2 = models.CharField(u"住所 #2", max_length=250, null=True, blank=True)

    # 自宅/会社
    address_type = models.CharField(u"自宅/会社", max_length=10, choices=ADDRESS_TYPES, default=ADDRESS_TYPE_NOTSET, blank=True, null=True)
    # 招待状のステータス
    invitation_status = models.CharField(u"招待状のステータス", max_length=100, blank=True, null=True)

    # ご本人出欠
    honnin_attending = models.CharField(u"ご本人出欠", max_length=2, choices=ATTEND_TYPES, default=ATTEND_NONE, blank=True, null=True)
    # 同伴者出欠
    companion_attending = models.CharField(u"同伴者出欠", max_length=4, choices=ATTEND_TYPES, default=ATTEND_NONE, blank=True, null=True)
    # 秘書出欠
    secretary_attending = models.CharField(u"秘書出欠", max_length=4, choices=ATTEND_TYPES, default=ATTEND_NONE, blank=True, null=True)

    # 秘書所属部署名
    secretary_department = models.CharField(u"秘書所属部署名", max_length=50, blank=True, null=True)
    # 秘書姓
    secretary_last_name = models.CharField(u"秘書姓", max_length=50, blank=True, null=True)
    # 秘書 姓カナ（全角）
    secretary_last_name_furigana = models.CharField(u"秘書 姓カナ（全角）", max_length=50, blank=True, null=True)
    # 秘書名
    secretary_first_name = models.CharField(u"秘書名", max_length=50, blank=True, null=True)
    # 秘書 名カナ（全角）
    secretary_first_name_furigana = models.CharField(u"秘書 名カナ（全角）", max_length=50, blank=True, null=True)

    # レセプション本人出欠
    honnin_attending_reception = models.CharField(u"レセプション本人出欠", max_length=2, choices=ATTEND_TYPES, default=ATTEND_NONE, blank=True, null=True)
    # レセプション同伴者出欠
    companion_attending_reception = models.CharField(u"レセプション同伴者出欠", max_length=2, choices=ATTEND_TYPES, default=ATTEND_NONE, blank=True, null=True)
    # レセプション秘書出欠
    secretary_attending_reception = models.CharField(u"レセプション秘書出欠", max_length=2, choices=ATTEND_TYPES, default=ATTEND_NONE, blank=True, null=True)

    # 今後の連絡先
    contact_address_type = models.CharField(u"今後の連絡先", max_length=10, choices=CONTACT_ADDRESS_TYPES, default=CONTACT_ADDRESS_TYPE_NOTSET, blank=True, null=True)

    # 電話番号
    phone_number = models.CharField(u"電話番号", max_length=50)

    # 内線
    extension = models.CharField(u"内線", max_length=50, blank=True, null=True)

    # メールアドレス
    email = models.CharField(u"メールアドレス", max_length=255)
    # コメント
    comment = models.TextField(u"コメント", blank=True, null=True)

    # アテンドMD
    attendee_md = models.CharField(u"アテンドMD", max_length=40, blank=True, null=True)
    # アテンドMDのEA
    attendee_md_ea = models.CharField(u"アテンドMDのEA", max_length=40, blank=True, null=True)

    # ワークショップ
    ws = models.CharField(u"ワークショップ", max_length=4, choices=AGREE_STATUS, default=AGREE_NONE, blank=True, null=True)

    # 懇親会
    party_attendance = models.CharField(u"懇親会", max_length=4, choices=AGREE_STATUS, default=AGREE_NONE, blank=True, null=True)
    # 宿泊
    stay_night = models.CharField(u"宿泊", max_length=4, choices=AGREE_STATUS, default=AGREE_NONE, blank=True, null=True)

    # ゴルフ
    golf = models.CharField(u"ゴルフ", max_length=4, choices=AGREE_STATUS, default=AGREE_NONE, blank=True, null=True)
    # ゴルフ ハンディキャップ
    golf_hc = models.CharField(u"ゴルフ ハンディキャップ", max_length=10, blank=True, null=True)
    # ゴルフバッグ
    golf_bag = models.CharField(u"ゴルフバッグ", max_length=16, choices=BRING_TYPES, default=BRING_TYPE_NONE, blank=True, null=True)

    # 交通手段
    transportation = models.CharField(u"交通手段", max_length=6, choices=TRANSPORTATION_TYPES, default=TRANSPORTATION_TYPE_NONE, blank=True, null=True)
    # 新幹線（行き）
    shinkansen_to = models.CharField(u"新幹線（行き）", max_length=250, blank=True, null=True)
    # 新幹線（帰り）
    shinkansen_from = models.CharField(u"新幹線（帰り）", max_length=250, blank=True, null=True)
    # お車ナンバー
    car_license_plate = models.CharField(u"お車ナンバー", max_length=25, blank=True, null=True)

    # その他備考欄
    notes = models.CharField(u"その他備考欄", max_length=250, blank=True, null=True)
    # 食べ物アレルギー
    allergies = models.CharField(u"食べ物アレルギー", max_length=250, blank=True, null=True)

    # ゴルフ　ビジター登録用　ご自宅郵便番号
    golf_visitor_zip = models.CharField(u"ゴルフ　ビジター登録用　ご自宅郵便番号", max_length=10, blank=True, null=True)
    # ゴルフ　ビジター登録用　ご自宅住所
    golf_visitor_address = models.CharField(u"ゴルフ　ビジター登録用　ご自宅住所", max_length=250, blank=True, null=True)

    # お礼状
    greetings = models.CharField(u"お礼状", max_length=6, choices=GREETING_TYPES, default=GREETING_TYPE_NONE, blank=True, null=True)
    # お礼状ステータス
    greetings_status = models.CharField(u"お礼状ステータス", max_length=80, blank=True, null=True)

    # prefecture = models.CharField("Prefecture", max_length=50, null=True, blank=True)

    accepted_privacy_statement = models.CharField(max_length=5, choices=AGREE_STATUS, default=AGREE_NONE, blank=True, null=True)
    registration_done = models.BooleanField(default=False)

    password_setup_code = models.CharField(max_length=100, null=True, blank=True)
    password_setup_time = models.DateTimeField(null=True, blank=True)
    password_setup_done = models.BooleanField(default=False)
    password_setup_done_time = models.DateTimeField(null=True, blank=True)

    password_reset_code = models.CharField(max_length=100, null=True, blank=True)
    password_reset_time = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        for field in CHARACTER_FIELDS:
            try:
                val = numz2h(getattr(self, field))
                setattr(self, field, val)
            except:
                pass
        self.phone_number = self.phone_number.replace('－', "-")

        self.address_2 = re.sub(r'([0-9]+)(ー|ー|－)([0-9]+)(ー|ー|－)([0-9]+)', r"\1-\3-\5", self.address_2)
        self.address_2 = re.sub(r'([0-9]+)(ー|ー|－)([0-9]+)', r"\1-\3", self.address_2)

        super(EventForm, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'Company: %s [%s]' % (self.company_name, self.email or self.user)



# # TODO(dkg): not sure if this will ever be used...
# class NotificationEmail(CommonColumns):

#     MAIL_SENT = "s"
#     MAIL_ERROR = "e"
#     MAIL_UNKNOWN = "u"

#     MAIL_STATUS = (
#         (MAIL_SENT, _("sent")),
#         (MAIL_ERROR, _("error")),
#         (MAIL_UNKNOWN, _("not set")),
#     )

#     # TODO(dkg): Put Japanese column names as first parameter for each field.
#     email = models.CharField("Email", max_length=255)
#     email_sent = models.CharField("Email sent?", max_length=2, choices=MAIL_STATUS, default=MAIL_UNKNOWN)
#     email_error = models.TextField("Error Message", blank=True, null=True)

#     def __unicode__(self):
#         return u'%s [%s]' % (self.user, self.get_email_sent_display())


# # custom signals
# def user_post_save(sender, instance, created, **kwargs):

#     try:
#         form_count = instance.eventform_set.count()
#     except:
#         form_count = 0
#     if created or form_count == 0:
#         EventForm.objects.create(user=instance)

# # attach the post save signal to User
# post_save.connect(user_post_save, User)
