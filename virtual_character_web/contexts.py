from django.conf import settings


def lang(request):
    return {'ENV_NAME': settings.ENV_NAME}
