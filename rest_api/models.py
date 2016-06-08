"""
    SQL tables.
    This is a typical declarative usage of sqlalchemy,
    It has no dependency on flask or eve itself. Pure sqlalchemy.
"""
from app import db, app

from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from passlib.apps import custom_app_context as pwd_context
from flask.ext.login import LoginManager, UserMixin, login_required
from flask import request

from sqlalchemy.engine import reflection
from sqlalchemy.engine.reflection import Inspector

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import inspect, join
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, column_property
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext import hybrid
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Table
from sqlalchemy import func
from sqlalchemy import (
    Column,
    Boolean,
    String,
    Integer,
    Float,
    ForeignKey,
    DateTime,
    Enum)

Base = declarative_base()
Base.metadata.bind = db.engine


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))
 #   person_id = Column(Integer, ForeignKey('person.id'))
 #   person = relationship("Person", backref=backref("user", uselist=False))
 #   roles = relationship("Role", secondary=lambda: user_roles, backref="user")

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration = 3600): # set expiration to 1 hour
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({ 'id': self.id })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        return user

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def __repr__(self):
        return '<User %r>' % (self.username)


class DataType(db.Model):
    __tablename__ = 'data_type'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80))
    attribute = relationship("Attribute", backref=backref("project", uselist=False))
    clinical_data = relationship("ClinicalData", backref=backref("data_type", uselist=False))
    phi_data = relationship("PhiData", backref=backref("data_type", uselist=False))

class Memoize(db.Model):
    __tablename__ = 'memoize'
    id = Column(Integer, primary_key=True, autoincrement=True)
    atom = Column(String(800))
    results = Column(String(255))

    def __init__(self, atom, results):
        self.atom = atom
        self.results = results

class Project(db.Model):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80))
    tb_project_id = Column(Integer)
    tb_phi_project_id = Column(Integer)
    date_project_added = Column(DateTime)
    clinical_data = relationship("ClinicalData", backref=backref("project", uselist=False))
    phi_data = relationship("PhiData", backref=backref("project", uselist=False))


class Attribute(db.Model): # Ontology
    __tablename__ = 'attribute'
    id = Column(Integer, primary_key=True, autoincrement=True)
    attribute_value = Column(String(80))
    attribute_description = Column(String(80))
    data_type_id = Column(Integer, ForeignKey('data_type.id'))
    num_parents = Column(Integer)
    num_children = Column(Integer)
    project_id = Column(Integer, ForeignKey('project.id'))
    clinical_data = relationship("ClinicalData", backref=backref("attribute", uselist=False))
    phi_data = relationship("PhiData", backref=backref("attribute", uselist=False))


class ClinicalData(db.Model):
    __tablename__ = 'clinical_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer)
    patient_sid  = Column(Integer)
    string_value = Column(String(255))
    double_value = Column(Float)
    data_type_id = Column(Integer, ForeignKey('data_type.id'))
    event_date = Column(DateTime)
    ontology_id = Column(Integer)
    attribute_id = Column(Integer, ForeignKey('attribute.id'))
    project_id = Column(Integer, ForeignKey('project.id'))
    replaced_by_id = Column(Integer)
    date_record_added = Column(DateTime)
    parent = Column(Integer)
    num_children = Column(Integer)
    lft = Column(Integer)
    rgt = Column(Integer)


class PhiData(db.Model):
    __tablename__ = 'phi_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    mrn = Column(String(80))
    patient_sid  = Column(Integer)
    string_value = Column(String(255))
    date_value = Column(DateTime)
    data_type_id = Column(Integer, ForeignKey('data_type.id'))
    attribute_id = Column(Integer, ForeignKey('attribute.id'))
    ontology_id = Column(Integer)
    project_id = Column(Integer, ForeignKey('project.id'))
    replaced_by_id = Column(Integer)
    date_record_added = Column(DateTime)
    parent = Column(Integer)
    num_children = Column(Integer)
    lft = Column(Integer)
    rgt = Column(Integer)


class Query(db.Model):
    __tablename__ = 'cc_query'
    id = Column(Integer, primary_key=True, autoincrement=True)
    query_name = Column(String(80))
    molecule = Column(String(2048))
    criteria = Column(String(2048))
    remote_user = Column(String(80))


class Results(db.Model):
    __tablename__ = 'results'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sid = Column(Integer)
    attribute = Column(String(2048))
    value_s = Column(String(2048))
    value_d = Column(Float)
    user = Column(String(48), default=lambda: request.remote_user)

# see http://stackoverflow.com/questions/4896104/creating-a-tree-from-self-referential-tables-in-sqlalchemy

# SQL view representation of coerced adjacency list
class Meds_Menu(db.Model):
    __tablename__ = 'meds_menu'
    id = Column(Integer, primary_key=True)
    type = Column(String(64))
    name = Column(String(64))
    parent_id = Column(Integer, ForeignKey('meds_menu.id'))
    code = Column(String(64))
    iconCls = Column(String(64))
    leaf = Column(Boolean, default =False)
    children = relationship('Meds_Menu',

                        # cascade deletions
                        cascade="all",

                        # many to one + adjacency list - remote_side
                        # is required to reference the 'remote'
                        # column in the join condition.
                        backref=backref("parent", remote_side='Meds_Menu.id'),

                        # children will be represented as a dictionary
                        # on the "name" attribute.
                        #collection_class=attribute_mapped_collection('name')

                    )

    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent

    def append(self, nodename):
        self.children[nodename] = Meds_Menu(nodename, parent=self)

    def __repr__(self):
        return "Meds_Menu(name=%r, id=%r, parent_id=%r, type=%r, iconCls=%r, leaf=%r)" % (
                    self.name,
                    self.id,
                    self.parent_id,
                    self.type,
                    self.iconCls,
                    self.leaf
                )
