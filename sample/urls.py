from django.conf.urls.defaults import patterns, include, url

from django.views.generic.simple import redirect_to

urlpatterns = patterns('',
    url(r'^$', redirect_to, {'url': '/index.html'}, name='home'),
    url(r'^index.html$', 'views.index'),
    
    # Django's logout view
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'template_name':'logout.html'}, name='logout'),

    # TFA-Login views
    url(r'^login/$', 
        'twofactor.views.login_view', 
        {'template_name':'login.html'}, 
        name='login'),
    url(r'^login/tfa$', 
        'twofactor.views.login_twofactor', 
        {'template_name':'login_twofactor.html'}, 
        name='login_twofactor'),
    url(r'^login/tfa/enable$', 
        'twofactor.views.twofactor_enable', 
        {}, 
        name='login_twofactor_enable'),

)
