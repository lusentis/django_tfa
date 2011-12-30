from django.conf.urls.defaults import patterns, include, url

from django.views.generic.simple import redirect_to

urlpatterns = patterns('',
    url(r'^$', redirect_to, {'url': '/index.html'}, name='home'),

    url(r'^login/$', 'twofactor.views.login', {'template_name':'login.html'}, name='login'),
    url(r'^login/tfa$', 'twofactor.views.login_twofactor', {'template_name':'login_twofactor.html'}, name='login_twofactor'),

    url(r'^logout/$', 'django.contrib.auth.views.logout', {'template_name':'logout.html'}, name='logout'),
)
