import os
import datetime
import plaid
import json
import psycopg2
import psycopg2.extras
from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON

app = Flask(__name__)

PLAID_CLIENT_ID = '5b7508b160197b001323a0b5'
PLAID_SECRET = '2feff03a82f23275ba2a6382d876ac'
PLAID_PUBLIC_KEY = 'afd6281ce2dc49712d9cc5cb1ac82a'
PLAID_ENV = 'sandbox'

# # Fill in your Plaid API keys - https://dashboard.plaid.com/account/keys
# PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
# PLAID_SECRET = os.getenv('PLAID_SECRET')
# PLAID_PUBLIC_KEY = os.getenv('PLAID_PUBLIC_KEY')
# # Use 'sandbox' to test with Plaid's Sandbox environment (username: user_good,
# # password: pass_good)
# # Use `development` to test with live users and credentials and `production`
# # to go live
# PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')


client = plaid.Client(client_id=PLAID_CLIENT_ID, secret=PLAID_SECRET,
                      public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV)

DATABASE_URL = 'postgresql://postgres:postgres@localhost:5432/postgres'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['POSTGRES_DATABASE_CHARSET'] = 'utf8mb4'
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'Users'
    uid = db.Column(db.String(), primary_key=True, nullable=False)
    access_token = db.Column(db.String())
    item_id = db.Column(db.String())
    transactions = db.Column(JSON)
    kin = db.Column(db.Numeric())

    def __repr__(self):
        return "(uid: {}, access_token: {}, item_id: {}, transactions={}, kin={})"\
            .format(self.uid, self.access_token, self.item_id, self.transactions, self.kin)


@app.route('/')
def hello_world():
    return 'Welcome to Kino!'


@app.route("/register_user", methods=['POST'])
def register_user():
    # Get firebase's user UID
    uid = request.get_json()['uid']
    # Save the token
    conn = psycopg2.connect(DATABASE_URL, sslmode='allow')
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(
        """
        INSERT INTO \"Users\"
            (uid, kin)
        VALUES
            (%s, %s)
        """,
        [uid, 0]
    )
    conn.commit()
    conn.close()
    cur.close()
    # new_user = User(uid=uid, transaction=json.dumps({}), kin=0)
    # db.session.add(new_user)
    # db.session.commit()
    # db.session.close()
    return ""


@app.route("/link_card", methods=['POST'])
def link_card():
    # Get firebase's id token for the user
    # Verify the token and get user's uid
    #fb_id_token = request.form['fb_id_token']
    # uid = verify_user(fb_id_token)
    # Get the public token
    # Exchange the public token for access token and item id
    uid = request.get_json()['uid']
    public_token = request.get_json()['public_token']
    access_token, item_id = exchange_public_token(public_token)
    # Save the access token for this user
    # Save the item id for this user
    conn = psycopg2.connect(DATABASE_URL, sslmode='allow')
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(
        """
        UPDATE \"Users\"
        SET
            access_token = %s,
            item_id = %s,
            transactions = %s
        WHERE
            uid = %s
        """,
        [access_token, item_id, json.dumps({}), uid]
    )
    conn.commit()
    conn.close()
    cur.close()
    # user = User.query.filter_by(uid=uid).first()
    # user.access_token = access_token
    # user.item_id = item_id
    # db.session.commit()
    # db.session.close()
    return ""


@app.route("/webhook", methods=['POST'])
def webhook():
    payload = request.get_json()
    webhook_code = payload['webhook_code']
    if webhook_code == 'DEFAULT_UPDATE':
        new_transactions(payload)
    return ""


def new_transactions(payload):
    # webhook json payload
    item_id = payload['item_id']
    num_of_new_transactions = payload['new_transactions']
    # find the user associated with this item_id
    conn = psycopg2.connect(DATABASE_URL, sslmode='allow')
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(
        """
        SELECT
            *
        FROM \"Users\"
        WHERE item_id=%s
        """,
        [item_id]
    )
    user = cur.fetchone()
    conn.close()
    cur.close()
    # user = User.query.filter_by(item_id=item_id).first()
    # Fetch transactions for the past 5 days (plaid hopefully updates more regularly than this)
    start_date = "{:%Y-%m-%d}".format(datetime.datetime.now() + datetime.timedelta(-20))
    end_date = "{:%Y-%m-%d}".format(datetime.datetime.now())
    response = client.Transactions.get(user['access_token'],
                                       start_date, end_date,
                                       count=num_of_new_transactions)
    new_transactions = response['transactions']
    existing_transactions = user['transactions']
    for new in new_transactions:
        if new['transaction_id'] not in existing_transactions:
            # It is indeed a new transaction
            # Reward Kin (this will send a signal to the app associated with this item_id,
            # then updates the Kin rewarded in the database)
            # reward_kin(item_id, new)
            # Append new transaction to existing transactions
            conn = psycopg2.connect(DATABASE_URL, sslmode='allow')
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(
                """
                SELECT transactions FROM \"Users\" WHERE uid = 'fakeuid'
                """
            )
            x = cur.fetchone()['transactions']
            x.update({new['transaction_id']: new})
            cur.execute(
                """
                UPDATE \"Users\"
                SET
                    transactions = %s
                WHERE
                    item_id = %s
                """,
                [json.dumps(x), item_id]
            )
            conn.commit()
            conn.close()
            cur.close()
        else:
            # Already existed
            # Move on to the next
            pass
    return ""


def reward_kin(user, transaction):
    return ""

#
# def verify_user(fb_id_token):
#     decoded_token = auth.verify_id_token(fb_id_token)
#     uid = decoded_token['uid']
#     return uid


def exchange_public_token(public_token):
    exchange_response = client.Item.public_token.exchange(public_token)
    access_token = exchange_response['access_token']
    item_id = exchange_response['item_id']
    return access_token, item_id


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

# @app.route("/")
# def index():
#     return render_template('index.ejs', plaid_public_key=PLAID_PUBLIC_KEY, plaid_environment=PLAID_ENV)
#
#
# access_token = None
# public_token = None
#
#
# @app.route("/get_access_token", methods=['POST'])
# def get_access_token():
#     global access_token
#     public_token = request.form['public_token']
#     exchange_response = client.Item.public_token.exchange(public_token)
#     print('public token: ' + public_token)
#     print('access token: ' + exchange_response['access_token'])
#     print('item ID: ' + exchange_response['item_id'])
#
#     access_token = exchange_response['access_token']
#
#     return jsonify(exchange_response)
#
#
# @app.route("/accounts", methods=['GET'])
# def accounts():
#     global access_token
#     accounts = client.Auth.get(access_token)
#     return jsonify(accounts)
#
#
# @app.route("/item", methods=['GET', 'POST'])
# def item():
#     global access_token
#     item_response = client.Item.get(access_token)
#     institution_response = client.Institutions.get_by_id(item_response['item']['institution_id'])
#     return jsonify({'item': item_response['item'], 'institution': institution_response['institution']})
#
#
# @app.route("/transactions", methods=['GET', 'POST'])
# def transactions():
#     global access_token
#     # Pull transactions for the last 30 days
#     start_date = "{:%Y-%m-%d}".format(datetime.datetime.now() + datetime.timedelta(-30))
#     end_date = "{:%Y-%m-%d}".format(datetime.datetime.now())
#
#     try:
#         response = client.Transactions.get(access_token, start_date, end_date, count=2)
#         return jsonify(response)
#     except plaid.errors.PlaidError as e:
#         return jsonify({'error': {'error_code': e.code, 'error_message': str(e)}})
#
#
# @app.route("/create_public_token", methods=['GET'])
# def create_public_token():
#     global access_token
#     # Create a one-time use public_token for the Item. This public_token can be used to
#     # initialize Link in update mode for the user.
#     response = client.Item.public_token.create(access_token)
#     return jsonify(response)
#
#
# if __name__ == "__main__":
#     app.run(port=os.getenv('PORT', 5000))
