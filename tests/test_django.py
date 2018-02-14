import pathlib
import os
import shutil
import unittest

from fabric.api import local, lcd

from fab_support import set_stages, copy_null
from fabfile import remove_tree


class TestBasicFabSupport(unittest.TestCase):

    def setUp(self):
        # bodge to get .git file delete keeps giving a PermissionError after testing about a git file
        try:
            with lcd('demo_django'):
                local('del /F /S /Q /A .git')
        except FileNotFoundError:
            pass
        try:
            shutil.rmtree('demo_django')
        except FileNotFoundError:
            pass
        local('django-admin startproject demo_django')
        # TODO convert paths to windows and linux
        local('copy template_files\\demo_django_fabfile.py demo_django\\fabfile.py')
        local('copy template_files\\demo_django.env demo_django\\.env')  # Need to have an environment for secrets
        local('copy template_files\\demo_django_Procfile demo_django\\Procfile')  #  Need to a Procfile to tell
        # heroku what types of workers you need
        local('copy template_files\\demo_requirements.txt demo_django\\requirements.txt') # Need to tell Heroku that
        # this is a python project and what is needed in production
        local('copy template_files\\demo_django_settings.py demo_django\\demo_django\\settings.py /Y')  # Need to customise
        # for collect statics (alternative would be to ignore collect static)
        local('git init demo_django')
        with lcd('demo_django'):
            local('mkdir static')  # Heroku needs a place to put static files in collectstatic and won't create it.
            local('copy ..\\template_files\\demo_django_fabfile.py static\\fabfile.py') # To make git recognise it
            local('git add .')
            print(local('dir', capture=True))
            local("git commit -m 'start'")

    def tearDown(self):
        pass

    def test_set_stages(self):
        # Can you call it
        # Definition of different environments to deploy to
        set_stages(globals(), {
            'testhost': {
                'comment': 'stage: Local build and serving from output directory',
                'config_file': 'local_conf.py',
                'destination': '',
                'copy_method': copy_null,
                'SITEURL': 'http://localhost:8000',
                'PORT': 8000,
            },
        })
        # Now actually create a test environment and see if actually working
        remove_tree(('demo_testhost486',))
        pathlib.Path("demo_testhost486").mkdir(exist_ok=True)
        local('copy template_files\\demo_testhost486_fabfile.py demo_testhost486\\fabfile.py')  # TODO convert to windows and linux
        with lcd('demo_testhost486'):
            result = local('fab --list', capture=True)
        print(result)
        self.assertRegex(result, 'test486', 'Using test486 fabfile should have set up demo using set_stages')
        self.assertRegex(result, 'test486_fab_file', 'The fabfile has defined a new task.')

    def test_got_heroku_and_build(self):
        """After running this the directory is kept available.  You can test the server locally by:
        - running the deve enrionment
        - switching to tests\demo_django
        - run `python manage.py runserver`
        - open localhost:8000

        This should be made into another functional test.  It is running from a sqllite database.
        The Heroku test version that is spun up is a test version at zero cost.
        The Django version is meant to be as simple as possible.
        """
        with lcd('demo_django'):
            # Check staging and fabfile are correct
            result = local('fab --list', capture=True)
            self.assertRegex(result, 'demo', 'demo stage')
            self.assertRegex(result, 'test_demo_django_fab_file', 'The fabfile has defined a new task.')
            try:
                local('fab demo fab_support.django.kill_app')  # Remove any existing run time
            except SystemExit:
                pass
            local('fab demo fab_support.django.create_newbuild')  # Build database from scratch
            # local('fab demo fab_support.django.kill_app')  # By default don't let it run after test

    def test_got_local_fabfile(self):
        with lcd('demo_django'):
            result = local('fab --list', capture=True)
        print(result)
        self.assertNotRegex(result, 'test_fab_file', 'Should not be using test fabfile')
        self.assertRegex(result, 'test_demo_django_fab_file', 'Testing local django fab')  # should be using local fab file

    # This was an experiment but couldn't make wsl run from local
    # def test_got_wsl(self):
    #     """Check that have wsl version of heroku and is logged in."""
    #     result = local('bash ls', capture=True)
    #     self.assertRegex(result, 'Apps\:', 'Make sure have heroku working and logged in')
    #
    # def test_got_wsl_heroku(self):
    #     """Check that have wsl version of heroku and is logged in."""
    #     result = local('bash /usr/bin/heroku status', capture=True)
    #     self.assertRegex(result, 'Apps\:', 'Make sure have heroku working and logged in')


"""
: (security.W004) You have not set a value for the SECURE_HSTS_SECONDS setting. If your entire site is served only over SSL, you may want to consider s
etting a value and enabling HTTP Strict Transport Security. Be sure to read the documentation first; enabling HSTS carelessly can cause serious, irrever
sible problems.
?: (security.W006) Your SECURE_CONTENT_TYPE_NOSNIFF setting is not set to True, so your pages will not be served with an 'x-content-type-options: nosnif
f' header. You should consider enabling this header to prevent the browser from identifying content types incorrectly.
?: (security.W007) Your SECURE_BROWSER_XSS_FILTER setting is not set to True, so your pages will not be served with an 'x-xss-protection: 1; mode=block'
 header. You should consider enabling this header to activate the browser's XSS filtering and help prevent XSS attacks.
?: (security.W008) Your SECURE_SSL_REDIRECT setting is not set to True. Unless your site should be available over both SSL and non-SSL connections, you
may want to either set this setting True or configure a load balancer or reverse-proxy server to redirect all connections to HTTPS.
?: (security.W012) SESSION_COOKIE_SECURE is not set to True. Using a secure-only session cookie makes it more difficult for network traffic sniffers to
hijack user sessions.
?: (security.W016) You have 'django.middleware.csrf.CsrfViewMiddleware' in your MIDDLEWARE, but you have not set CSRF_COOKIE_SECURE to True. Using a sec
ure-only CSRF cookie makes it more difficult for network traffic sniffers to steal the CSRF token.
?: (security.W018) You should not have DEBUG set to True in deployment.
?: (security.W019) You have 'django.middleware.clickjacking.XFrameOptionsMiddleware' in your MIDDLEWARE, but X_FRAME_OPTIONS is not set to 'DENY'. The d
efault is 'SAMEORIGIN', but unless there is a good reason for your site to serve other parts of itself in a frame, you should change it to 'DENY'.
?: (security.W020) ALLOWED_HOSTS must not be empty in deployment.
"""
