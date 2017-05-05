Default config (override with config.ini):

[conf]
api=http://127.0.0.1:8080
users=5
posts=3
likes=2

Run bot with:

python bot.py


NOTE:
it's advised to run Django with test settings (export DJANGO_SETTINGS_MODULE=social_network.settings.test)
because email_checker is disabled