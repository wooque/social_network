from celery import shared_task
from wall.models import User
from wall.serializers import UserSerializer
from django.conf import settings
import clearbit


clearbit.key = settings.CLEARBIT_API_KEY


@shared_task
def load_additional_user_data(email):
    """
        Use ClearBit Enrichment for getting additional data
        API docs: https://dashboard.clearbit.com/docs?python#enrichment-api-combined-api
    """
    person = clearbit.Enrichment.find(email=email, stream=True)
    if person is None:
        return
    u = User.objects.filter(email=email).get()
    us = UserSerializer(u, data=dict(
        facebook=person['facebook']['handle'],
        twitter=person['twitter']['handle']
    ), partial=True)

    if us.is_valid():
        us.save()
