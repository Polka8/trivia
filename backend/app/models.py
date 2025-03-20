from datetime import datetime
from . import db
import enum
from werkzeug.security import generate_password_hash, check_password_hash

class RuoloEnum(enum.Enum):
    admin = "admin"
    cliente = "cliente"

class User(db.Model):
    __tablename__ = 'utente'
    id = db.Column('id_utente', db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    cognome = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column('psw', db.String(200), nullable=False)
    ruolo = db.Column(db.Enum(RuoloEnum), nullable=False, default=RuoloEnum.cliente)
    creato_il = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Prenotazione(db.Model):
    __tablename__ = 'prenotazione'
    id_prenotazione = db.Column(db.Integer, primary_key=True)
    data_prenotata = db.Column(db.DateTime, nullable=False)
    stato = db.Column(db.String(50), nullable=False)
    id_utente = db.Column(db.Integer, db.ForeignKey('utente.id_utente'), nullable=False)
    data_annullamento = db.Column(db.DateTime)
    data_creazione = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    note_aggiuntive = db.Column(db.Text)
    numero_posti = db.Column(db.Integer, nullable=False)
    dettagli = db.relationship('DettagliPrenotazione', backref='prenotazione', lazy=True)

class Piatto(db.Model):
    __tablename__ = 'piatto'
    id_piatto = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    prezzo = db.Column(db.Float, nullable=False)
    descrizione = db.Column(db.Text)

class DettagliPrenotazione(db.Model):
    __tablename__ = 'dettagli_prenotazione'
    id_dettaglio = db.Column(db.Integer, primary_key=True)
    fk_prenotazione = db.Column(db.Integer, db.ForeignKey('prenotazione.id_prenotazione'), nullable=False)
    fk_piatto = db.Column(db.Integer, db.ForeignKey('piatto.id_piatto'), nullable=False)
    quantita = db.Column(db.Integer, nullable=False)

# Nuovi modelli per la gestione dei menù

class Menu(db.Model):
    __tablename__ = 'menu'
    id_menu = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titolo = db.Column(db.String(255), nullable=False)
    data_creazione = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # Relazione con le sezioni del menù
    sezioni = db.relationship('MenuSezioneRel', backref='menu', lazy=True)

class MenuSezione(db.Model):
    __tablename__ = 'menu_sezione'
    id_sezione = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_sezione = db.Column(db.String(255), nullable=False)

class MenuSezioneRel(db.Model):
    __tablename__ = 'menu_sezione_rel'
    id_menu_sezione = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_menu = db.Column(db.Integer, db.ForeignKey('menu.id_menu'), nullable=False)
    id_sezione = db.Column(db.Integer, db.ForeignKey('menu_sezione.id_sezione'), nullable=False)
    # Relazione con gli item del menù
    items = db.relationship('MenuItem', backref='menu_sezione_rel', lazy=True)

class MenuItem(db.Model):
    __tablename__ = 'menu_item'
    id_item = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_menu_sezione = db.Column(db.Integer, db.ForeignKey('menu_sezione_rel.id_menu_sezione'), nullable=False)
    id_piatto = db.Column(db.Integer, db.ForeignKey('piatto.id_piatto'), nullable=False)
