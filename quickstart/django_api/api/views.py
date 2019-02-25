# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
import json
import os
import datetime
import plaid
from django.shortcuts import render

PLAID_CLIENT_ID = '5b7508b160197b001323a0b5'
PLAID_SECRET = '2feff03a82f23275ba2a6382d876ac'
PLAID_PUBLIC_KEY = 'afd6281ce2dc49712d9cc5cb1ac82a'
PLAID_ENV = 'sandbox'

client = plaid.Client(client_id=PLAID_CLIENT_ID, secret=PLAID_SECRET,
                      public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV)


def index(request):
    return render(request, 'index.html')


# access_token = None
# public_token = None
#
#
# def get_access_token(request):
#     if request.method == 'POST':
#         global access_token
#         public_token = request.form['public_token']
#         exchange_response = client.Item.public_token.exchange(public_token)
#         print('public token: ' + public_token)
#         print('access token: ' + exchange_response['access_token'])
#         print('item ID: ' + exchange_response['item_id'])
#         access_token = exchange_response['access_token']
#         return HttpResponse(json.dumps(exchange_response), content_type="application/json")
#
#
# def accounts(request):
#     global access_token
#     accounts = client.Auth.get(access_token)
#     return HttpResponse(json.dumps(accounts), content_type="application/json")
#
#
# def item(request):
#     global access_token
#     item_response = client.Item.get(access_token)
#     institution_response = client.Institutions.get_by_id(item_response['item']['institution_id'])
#     return HttpResponse(json.dumps({'item': item_response['item'], 'institution': institution_response['institution']}), content_type="application/json")
#
#
# def transactions(request):
#     global access_token
#     # Pull transactions for the last 30 days
#     start_date = "{:%Y-%m-%d}".format(datetime.datetime.now() + datetime.timedelta(-30))
#     end_date = "{:%Y-%m-%d}".format(datetime.datetime.now())
#
#     try:
#         response = client.Transactions.get(access_token, start_date, end_date)
#         return HttpResponse(json.dumps(response), content_type="application/json")
#     except plaid.errors.PlaidError as e:
#         return HttpResponse(json.dumps({'error': {'error_code': e.code, 'error_message': str(e)}}), content_type="application/json")
#
#
# def create_public_token(request):
#     global access_token
#     # Create a one-time use public_token for the Item. This public_token can be used to
#     # initialize Link in update mode for the user.
#     response = client.Item.public_token.create(access_token)
#     return HttpResponse(json.dumps(response), content_type="application/json")