from django.conf.urls import url
from . import views

urlpatterns = [
    url('index', views.index, name='index'),
    # url('get_access_token', views.get_access_token),
    # url('accounts', views.accounts),
    # url('item', views.item),
    # url('transactions', views.transactions),
    # url('create_public_token', views.create_public_token)
]
