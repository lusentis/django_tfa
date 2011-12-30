import datetime

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseServerError
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from twofactor.models import Secret, OneTimeToken


@csrf_exempt
def login(request, template_name='login.html'):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                if Secret.user_has_otp(user):
                    request.session['logging_user']=user.pk
                    request.session['logging_user_auth']=user
                    request.session['logging_datetime']=datetime.datetime.now()
                    request.session.save()
                    return HttpResponseRedirect(reverse('login_twofactor'))
                else:
                    auth_login(request, user)
                    return HttpResponseRedirect(reverse('home'))
            else:
                return render_to_response(template_name, {'error':_('Your account is not active')}, context_insance=RequestContext(request))
        else:
            return render_to_response(template_name, {'error':_('Invalid username or password')}, context_instance=RequestContext(request))

    else:
        return render_to_response(template_name)


@csrf_exempt
def login_twofactor(request, template_name='login_twofactor.html'):
    if not request.session.get('logging_user') or not request.session.get('logging_user_auth') or not request.session.get('logging_datetime') or datetime.datetime.now() - request.session['logging_datetime'] > datetime.timedelta(seconds=5*60):
            return HttpResponse(_('Sorry, your request is invalid or expired.'));

    else:
        user = User.objects.get(pk=request.session['logging_user'])
        user_auth = request.session['logging_user_auth']

        if not user:
            return HttpResponseServerError('Invalid request: user does not exists')

        else:
            if request.method == 'POST':
                from twofactor.otp import valid_totp, get_totp

                secret = Secret.get_user_secret(user)
                print "Secret is {0}".format(secret)

                if valid_totp(token=request.POST.get('token'), secret=secret):
                    OneTimeToken.use(user=user, token=request.POST.get('token'))
                    auth_login(request, user_auth)
                    return HttpResponseRedirect(reverse('home'))

                else:
                    del request.session['logging_user']
                    request.session.save()

                    return HttpResponse(_('The login token you entered ({0}) is not valid. Try {1}.').format(
                        request.POST.get('token'),
                        get_totp(secret, as_string=True)))
                    #return HttpResponseRedirect(reverse('login'))

            else:
                return render_to_response(template_name, {'user': user}, context_instance=RequestContext(request))



