import os
import dotenv

ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

DEBUG = True
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = '-05sgp9!deq=q1nltm@^^2cc+v29i(tyybv3v2t77qi66czazj'
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
<<<<<<< Updated upstream
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.twitter',
=======
<<<<<<< Updated upstream
=======
    # 'allauth.socialaccount.providers.google',
    # 'allauth.socialaccount.providers.facebook',
>>>>>>> Stashed changes
>>>>>>> Stashed changes
    'stripe',

    'crispy_forms',
    'django_countries',
    'core',
    'social_django',
]

<<<<<<< Updated upstream
SOCIALACCOUNT_PROVIDERS = {
    'github': {},
    'google': {},
    'twitter': {}
}

=======
<<<<<<< Updated upstream
=======
SOCIALACCOUNT_PROVIDERS = {
    # 'facebook': {
    #     'METHOD': 'oauth2',
    #     'SCOPE': ['email', 'public_profile', 'user_friends'],
    #     'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
    #     'INIT_PARAMS': {'cookie': True},
    #     'FIELDS': [
    #         'id',
    #         'email',
    #         'name',
    #         'first_name',
    #         'last_name',
    #         'verified',
    #         'locale',
    #         'timezone',
    #         'link',
    #         'gender',
    #         'updated_time',
    #     ],
    #     'EXCHANGE_TOKEN': True,
    #     'LOCALE_FUNC': 'path.to.callable',
    #     'VERIFIED_EMAIL': False,
    #     'VERSION': 'v2.12',
    # },
    # 'google': {
    #     'SCOPE': [
    #         'profile',
    #         'email',
    #     ],
    #     'AUTH_PARAMS': {
    #         'access_type': 'online',
    #     }
    # }
}

>>>>>>> Stashed changes
>>>>>>> Stashed changes
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
]

ROOT_URLCONF = 'djecommerce.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static_in_env')]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_root')

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, 'db.sqlite3')
    }
}

if ENVIRONMENT == 'production':
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    SESSION_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_REDIRECT_EXEMPT = []
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Auth

<<<<<<< Updated upstream
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 7
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 180
=======
AUTHENTICATION_BACKENDS = [

<<<<<<< Updated upstream
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',

]
=======
# ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 7
# ACCOUNT_EMAIL_REQUIRED = True
# ACCOUNT_EMAIL_VERIFICATION = "mandatory"
# ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
# ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 180
>>>>>>> Stashed changes
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
ACCOUNT_FORMS = {
    'signup': 'djecommerce.forms.CustomSignupForm',
}
<<<<<<< Updated upstream
=======
# SOCIALACCOUNT_QUERY_EMAIL = ACCOUNT_EMAIL_REQUIRED
# SOCIALACCOUNT_EMAIL_REQUIRED = ACCOUNT_EMAIL_REQUIRED
# SOCIALACCOUNT_STORE_TOKENS = False

>>>>>>> Stashed changes
>>>>>>> Stashed changes

SITE_ID = 1

# CRISPY FORMS
CRISPY_TEMPLATE_PACK = "bootstrap4"

# STRIPE Settings

dotenv_file = os.path.join(BASE_DIR, ".env")
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)

STRIPE_PUBLISHABLE_KEY = os.environ['STRIPE_PUBLISHABLE_KEY']
STRIPE_SECRET_KEY = os.environ['STRIPE_SECRET_KEY']
