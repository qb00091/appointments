import secrets

from flask import Flask, render_template, request, flash, redirect, url_for, sessions
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, IntegerField, DecimalField, BooleanField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import DataRequired, Email, Length

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from datetime import datetime, date, timedelta

import subprocess
import os

UPLOAD_FOLDER = '/uploads/'
PICTURE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
app = Flask(__name__)      
app.secret_key = 'My very first predatory hawk scooped their prey off the palm tree in my garden yesterday morning at 10AM sharp.'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://appointments:123@localhost/appointments"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

class Users(db.Model, UserMixin):
    uid = db.Column('uid', db.Integer, primary_key = True)
    email = db.Column('email', db.String(50), unique=True, nullable=False)
    name = db.Column('name', db.String(50))
    salt = db.Column('salt', db.String(32), nullable=False)
    hashed = db.Column('hash', db.String(256), nullable=False)

    def __init__(self, email, name, password):
        self.email = email
        self.name = name
        self.salt = secrets.token_urlsafe(32) # Columns are too large for hash and salt?
        self.set_password(password)

    def set_password(self, password):
        self.hashed = generate_password_hash(password + self.salt)

    def check_password(self, password):
        return check_password_hash(self.hashed, password + self.salt)

    def get_id(self):
        return self.uid

    def __repr__(self):
        return '<User "{}">'.format(self.email)

class Appointments(db.Model):
    aid = db.Column('aid', db.Integer, primary_key = True)
    uid = db.Column('uid', db.Integer, primary_key = True)
    eid = db.Column('eid', db.Integer, primary_key = True)
    description = db.Column('description', db.String(100))
    datetime_start = db.Column('datetime_start', db.DateTime, nullable=False)
    datetime_end = db.Column('datetime_end', db.DateTime, nullable=False)

    def __init__(self, uid, eid, description, datetime_start, datetime_end):
        self.uid = uid
        self.eid = eid
        self.description = description
        self.datetime_start = datetime_start
        self.datetime_end = datetime_end

    def __repr__(self):
        return '<Appointment "{}: {}">'.format(self.aid, self.description)

class Managers(db.Model):
    uid = db.Column('uid', db.Integer, db.ForeignKey('users.uid'), primary_key = True)

    def __init__(self, uid, rid):
        self.uid = uid

    def __repr__(self):
        return '<Manager ({})>'.format(self.uid)

class Entities(db.Model):
    eid = db.Column('eid', db.Integer, primary_key = True)
    name = db.Column('name', db.String(50))
    location = db.Column('location', db.String(100))
    title = db.Column('title', db.String(50))
    picture_filename = db.Column('picture_filename', db.String(100))

    def __init__(self, name, location, title, picture_filename):
        self.name = name
        self.location = location
        self.title = title
        self.picture_filename = picture_filename

    def __repr__(self):
        return '<Entity ({} => {})>'.format(self.eid, self.name)

class AppointmentCreateForm(FlaskForm):
    entity = SelectField('Entity',
            choices = [(e.eid, e.name) for e in Entities.query.all()]
    )
    date_start = DateField('Start Date:', format='%Y-%m-%d', default=datetime.today, validators=[DataRequired()])
    time_start = TimeField('Start Time:', format='%H:%M:%S', default=datetime.utcnow, validators=[DataRequired()])
    date_end = DateField('End Date:', format='%Y-%m-%d', default=datetime.today, validators=[DataRequired()])
    time_end = TimeField('End Time:', format='%H:%M:%S', default=datetime.utcnow, validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired(), Length(4, 200)])
    submit = SubmitField('Create')

class AppointmentSearchForm(FlaskForm):
    entity = SelectField('Entity',
            choices = [(e.eid, e.name) for e in Entities.query.all()]
    )
    date_start = DateField('Start Date:', format='%Y-%m-%d', default = datetime.utcnow() - timedelta(weeks=4))
    time_start = TimeField('Start Time:', format='%H:%M:%S', default=datetime.utcnow)
    date_end = DateField('End Date:', format='%Y-%m-%d', default=datetime.utcnow() + timedelta(weeks = 4))
    time_end = TimeField('End Time:', format='%H:%M:%S', default=datetime.utcnow)
    description = TextAreaField('Description', validators=[Length(0, 200)])
    submit = SubmitField('Search')

class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email(), Length(4, 50)])
    password = PasswordField('password', validators=[DataRequired(), Length(6, 50)])
    login = SubmitField()

class SignupForm(FlaskForm): # TODO When a form goes bad, it doesn't tell you what field is wrong.
    email = StringField('email', validators=[DataRequired(), Email(), Length(4, 50)])
    name = StringField('name', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('password', validators=[DataRequired(), Length(6, 50)])
    signup = SubmitField()

class EntityCreateForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(1, 20)])
    picture = FileField('picture')
    create = SubmitField()

class BackupForm(FlaskForm):
     backup = SubmitField('Backup')

class RestoreForm(FlaskForm):
    local_password = PasswordField('password', validators=[DataRequired()])
    checkbox = BooleanField(validators=[DataRequired()])
    restore_file = FileField(validators=[DataRequired()])
    restore = SubmitField('Restore')

def priv():
    privs = dict()
    if current_user.is_anonymous:
        privs['email'] = 'Anonymous'
        privs['authed'] = False
        privs['manager'] = False
    else:
        privs['email'] = current_user.email
        privs['authed'] = current_user.is_authenticated
        privs['manager'] = Managers.query.filter_by(uid=current_user.get_id()).first() is not None
    return privs

@login_manager.user_loader
def load_user(uid):
    return Users.query.get(int(uid))

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('search'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('search'))

    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        cuid = current_user.get_id()
        #current_user.is_manager = \
        #    Managers.query.filter_by(uid=cuid).first() is not None
        return redirect(url_for('home'))
    else:
        return render_template('login.html', form=form, priv=priv())

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/entity/create', methods=['GET', 'POST'])
def entity_create():
    if not priv()['manager']:
        return redirect(url_for('login'))
    form = EntityCreateForm()
    if form.validate_on_submit():
        name = form.name.data
        if form.picture.data is None:
            filename = "Anonymous.png"
        else: 
            filename = form.picture.data.filename

        filename = secure_filename(filename)
        # TODO if Entities.query.filter_by()...  for unique entities, make them users.
        # TODO Allows weird edge cases. The form should handle this maybe
        if not os.path.exists(os.path.join(UPLOAD_FOLDER, filename)) \
            and form.picture.data is not None: 
            form.picture.data.save(os.path.join(UPLOAD_FOLDER, filename))
        db.session.add(Entities(name=name, picture_filename=filename))
        db.session.commit()
        flash('Successfully created.')

    return render_template('entity/create.html', form=form, priv=priv())

@app.route('/entity/view/<eid>')
def entity_view(eid = None):
    if eid is None:
        return redirect(url_for('search'))

    entity = Entities.query.filter_by(eid=eid).first()
    if entity is None:
        return redirect(url_for('search'))
    picture = entity.picture_filename

    return render_template('/entity/view.html', picture=picture, priv=priv(), entity=entity)

@app.route('/appointment/view/<aid>')
def appointment_view(aid = None):
    if aid is None:
        return redirect(url_for('search'))

    appointment = Appointments.query.filter_by(aid=aid).first()
    if appointment is None:
        return redirect(url_for('search'))
    entity = Entities.query.filter_by(eid=appointment.eid).first()
    if entity is None:
        return redirect(url_for('search'))

    return render_template('/appointment/view.html', priv=priv(), appointment=appointment, entity=entity)

@app.route('/backup', methods=['GET', 'POST'])
def backup():
    if not priv()['manager']:
        return redirect(url_for('login'))

    backup_form = BackupForm()
    restore_form = RestoreForm()

    if backup_form.validate_on_submit() and backup_form.backup.data:
        print(str(subprocess.run(['./backup'], capture_output=True, cwd='bin/').stdout))
        print('yeah')
    elif restore_form.validate_on_submit() and restore_form.checkbox.data:
        print('got hit')
        print('got restore hit ', restore_form.restore_file.data)

    return render_template('backup/main.html', backup_form=backup_form, restore_form=restore_form, priv=priv())

@app.route('/appointment/create/', methods=['GET', 'POST'])
def appointment_create():
    def are_overlapping(start1, end1, start2, end2):
        return False

    if current_user.is_anonymous:
        return redirect(url_for('login'))

    form = AppointmentCreateForm()
    privs = priv()

    if form.validate_on_submit():
        eid = form.entity.data

        date_start = form.date_start.data
        time_start = form.time_start.data
        date_end = form.date_end.data
        time_end = form.time_end.data
        datetime_start = datetime.combine(date_start, time_start)
        datetime_end = datetime.combine(date_end, time_end)

        description = form.description.data

        appointments = Appointments.query.filter_by(eid=eid)
        success = True
        for a in appointments:
            if (are_overlapping(datetime_start, datetime_end, a.datetime_start, a.datetime_end)):
                success = False
                break
        if success:
            flash('Successfully created.')
            db.session.add(Appointments(eid=eid, uid=current_user.uid,
                datetime_start=datetime_start, datetime_end=datetime_end, description=description)
            )
            db.session.commit()
        else:
            flash('Creation unsuccessful. Appointment may already be booked.')

    return render_template('appointment/create.html', form=form, priv=priv(), appointments=[])

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('search'))

    form = SignupForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            flash('This email is already taken.')
            return redirect(url_for('signup'))
        new_user = Users(form.email.data, form.name.data, form.password.data)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('search'))
    return render_template('signup.html', form=form, priv=priv())


@app.route('/search', methods=['GET', 'POST'])
def search():
    if not current_user.is_authenticated:
        return redirect(url_for('signup'))
    form = AppointmentSearchForm()

    matches = []
    if form.validate_on_submit():
        eid = int(form.entity.data)
        timestamp_start = datetime.combine(form.date_start.data, form.time_start.data)
        timestamp_end = datetime.combine(form.date_end.data, form.time_end.data)
        description = form.description.data

        appointments = Appointments.query.filter_by(uid=current_user.uid)
        for a in appointments:
            if timestamp_start <= a.datetime_start and timestamp_end >= a.datetime_end and description in a.description and eid == a.eid:
                matches.append(a)

    return render_template('search.html', form=form, appointments=matches, priv=priv()) 

if __name__ == '__main__':
    app.run(debug=True)
