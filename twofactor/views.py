import datetime

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseServerError
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from twofactor.models import Secret, OneTimeToken
import settings

@csrf_exempt
def twofactor_enable(request, template_name='login_twofactor_enable.html', template_name_confirm='login_twofactor_enable_confirm.html'):
    if not request.session.get('logging_user') or not request.session.get('logging_user_auth') or not request.session.get('logging_datetime') or datetime.datetime.now() - request.session['logging_datetime'] > datetime.timedelta(seconds=5*60):
            return HttpResponse(_('Sorry, your request is invalid or expired.'));

    user = User.objects.get(pk=request.session['logging_user'])
    user_auth = request.session['logging_user_auth']

    if request.method == 'POST':
        otp_secret = Secret.user_enable_otp(user)
        return render_to_response(template_name, {'otp_secret': otp_secret}, context_instance=RequestContext(request))
    else:
        return render_to_response(template_name_confirm, {'user': user}, context_instance=RequestContext(request))

def _session_setup(request, user):
    request.session['username'] = request.POST['username']
    request.session['password'] = request.POST['password']
    request.session['logging_user'] = user.pk
    request.session['logging_user_auth'] = user
    request.session['logging_datetime'] = datetime.datetime.now()
    request.session.save()


@csrf_exempt
def login_view(request, template_name='login.html'):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                if Secret.user_has_otp(user):
                    _session_setup(request, user)
                    return HttpResponseRedirect(reverse('twofactor.views.login_twofactor', current_app='twofactor'))
                else:
                    from twofactor.callbacks import everyone_must_have_otp
                    enabled_callback = getattr(settings, 'TWOFACTOR_ENABLED_CALLBACK', everyone_must_have_otp)

                    if enabled_callback(user):
                        if settings.TWOFACTOR_ENABLE_AT_FIRST_LOGIN:
                            _session_setup(request, user)
                            return HttpResponseRedirect(reverse('login_twofactor_enable'))
                        else:
                            raise ValueError('Sorry, Two-factor is required but not enabled for your account. Additionally, TWOFACTOR_ENABLE_AT_FIRST_LOGIN False.')

                    else:
                        login(request, user)
                        return HttpResponseRedirect(reverse('home'))
            else:
                return render_to_response(template_name, {'error':_('Your account is not active')}, context_insance=RequestContext(request))
        else:
            return render_to_response(template_name, {'error':_('Invalid username or password')}, context_instance=RequestContext(request))

    else:
        return render_to_response(template_name, context_instance=RequestContext(request))


@csrf_exempt
def login_twofactor(request, template_name='login_twofactor.html'):
    if not request.session.get('logging_user') or not request.session.get('logging_user_auth') or not request.session.get('logging_datetime') or datetime.datetime.now() - request.session['logging_datetime'] > datetime.timedelta(seconds=5*60):
            return HttpResponse(_('Sorry, your request is invalid or expired.'));

    else:
        user = User.objects.get(pk=request.session['logging_user'])
        user_auth = request.session['logging_user_auth']

        if not user:
            return HttpResponseServerError(_('Invalid request: user does not exists'))

        else:
            if request.method == 'POST':
                from twofactor.otp import valid_totp, get_totp

                secret = Secret.get_user_secret(user)

                try:
                    valid_secret = valid_totp(token=request.POST.get('token'), secret=secret)
                except TypeError, e:
                    valid_secret = False
                
                if valid_secret and OneTimeToken.use(user=user, token=request.POST.get('token')):
                    """ django require us to authenticate again (see https://docs.djangoproject.com/en/dev/topics/auth/#django.contrib.auth.login) """
                    aa = authenticate(username=request.session['username'], password=request.session['password'])
                    if aa is None:
                        raise ValueError("User cannot be authenticated anymore. Using: {0}/{1}".format(request.session['username'],request.session['password']))
                    
                    login(request, aa)
                    request.session.save()
                    return HttpResponseRedirect(reverse('home'))

                else:
                    del request.session['logging_user']
                    request.session.save()

                    return HttpResponse(_('The login token you entered ({0}) is not valid or has been already used.').format(request.POST.get('token'),))

            else:
                return render_to_response(template_name, {'user': user}, context_instance=RequestContext(request))


