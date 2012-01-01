# Two factor authentication for Django projects #

Django\_tfa (twofactor) is a Django app that implements Two-Factor authentication based on Django's `contrib.auth`.

## Prerequisites ##
- Django 1.3+
- South (optional), install with `easy\_install south`

## Installation ##

Devel:

    git clone git://github.com/lusentis/django_tfa.git
    sudo python setup.py install

Stable:

    sudo easy_install django_tfa

## Setup ##

1. Add `twofactor` to your `INSTALLED_APPS` list.
 
    INSTALLED_APPS = (
        ...
        'twofactor'
        ...
    )

2. Sync database (optional: use south)

```bash
    \# no south:
    ./manage.py syncdb

    \# south (recomended):
    ./manage.py schemamigration --initial twofactor
    ./manage.py syncdb
    ./manage.py migrate
``

3. Add some settings (optional, defaults are shown)

```python
    from twofactor.callbacks import everyone_must_have_otp
    TWOFACTOR_ENABLED_CALLBACK = everyone_must_have_otp
    TWOFACTOR_ENABLE_AT_FIRST_LOGIN = True
    TWOFACTOR_TOKEN_LENGTH = 32
```

4. Add login and logout templates (the same you use with `contrib.auth`)

5. Add twofactor urls to your root urls.py


    url(r'^login/$', 'twofactor.views.login_view', {'template_name':'login.html'}, 
        name='login'),
    url(r'^login/tfa$', 'twofactor.views.login_twofactor', {'template_name':'login_twofactor.html'}, 
        name='login_twofactor'),
    url(r'^login/tfa/enable$', 'twofactor.views.twofactor_enable', 
        name='login_twofactor_enable'),

    You need to replace your existing /login/ url from `django.contrib.auth`.

6. Add some users from Django admin or ./manage.py shell


## Bugs ##

- Post-login redirect is not handled correctly, so you should have a urlpattern named "home" that is where you want to be reidrected after the login.

- Putting twofactor's urls in a separate file (eg: twofactor.urls) breaks the urlconf `reverse` function... why?

## Sample ##
Clone this repo and run:
    
    ./manage.py syncdb
    ./manage.py runserver

and point your browser to `http://localhost:8000` 

