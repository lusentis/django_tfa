import random
import string

from django.db import models
from django.contrib.auth.models import User

import settings

class Secret(models.Model):
    """ Store Secrets for each user """

    user = models.ForeignKey(User)
    _secret = models.CharField(max_length=16)

    def set_secret(self, secret):
        self._secret = secret

    def get_secret(self):
        return self._secret

    def __unicode__(self):
        return 'Secret for user {0}'.format(self.user)

    @staticmethod
    def get_user_secret(user):
        if not Secret.user_has_otp(user):
            return False
        else:
            return Secret.objects.get(user=user).get_secret()

    @staticmethod
    def user_has_otp(user):
        if Secret.objects.filter(user=user):
            return True
        else:
            return False
    
    @staticmethod
    def build_secret():
        chars = list('ABCDEFGHJKMNPQRSTUVZXW234567')
        length = getattr(settings, 'TWOFACTOR_TOKEN_LENGTH', 32)
        return ''.join([random.choice(chars) for i in range(length)]) 

    @staticmethod
    def user_enable_otp(user):
        if Secret.user_has_otp(user):
            raise ValueError('Specified user has OTP already enabled')
        else:
            otp_secret = Secret.build_secret()
            s = Secret()
            s.user = user
            s.set_secret(otp_secret)
            s.save()
            return otp_secret


class OneTimeToken(models.Model):
    """ Stores used OTTs """

    user = models.ForeignKey(User)
    token = models.CharField(max_length=20)
    date = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return 'Token #{1} for user {0}'.format(self.user, self.pk)
    
    @staticmethod
    def use(user, token):
        """

        Returns True iff token has not yet been used for the given user.
        The token is always consumed.

        """
        tt = OneTimeToken.objects.filter(user=user, token=token)

        if not tt:
            tt = OneTimeToken()
            tt.user = user
            tt.token = token
            tt.save()
            return True

        else:
            return False

