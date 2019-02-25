from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import psycopg2


app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/postgres'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://etfohmzbucvaxx:38507ab589412477b07a4a8faf45cdc71e3b0dc845c6b19a981df7206ce77d3a@ec2-54-235-160-57.compute-1.amazonaws.com:5432/d6knq59g0agg8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    email = db.Column(db.String(), primary_key=True, nullable=False)

    def __repr__(self):
        return self.email


# def save_to_database(new_email):
#     # Connect to an existing database
#     conn = psycopg2.connect(dbname="postgres", user="postgres", password="postgres")
#     # Open a cursor to perform database operations
#     cur = conn.cursor()
#     # Execute a command: this creates a new table
#     cur.execute(
#         """
#         INSERT INTO email_addresses
#         (email) VALUES (%s)
#         """,
#         [new_email]
#     )
#     # Make the changes to the database persistent
#     conn.commit()
#     # Close communication with the database
#     cur.close()
#     conn.close()
#     return


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/email_submitted', methods=["POST"])
def email_submitted():
    new_email = request.form['email']
    contact = User.query.filter_by(email=new_email).first()
    if contact is None:
        new_user = User(email=new_email)
        db.session.add(new_user)
        db.session.commit()
        db.session.close()
    # save_to_database(new_email)
    return render_template('thank_you.html')


@app.route('/contact_us', methods=["POST"])
def contact_us():
    return redirect("mailto:waterloodevs@gmail.com")


if __name__ == "__main__":
    app.run(debug=True)
