from flask import jsonify, request
from .models import db, User, RuoloEnum,Risposte,Domande,Punteggio,StatoEnum
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta, datetime
import os
import re
import json

def init_routes(app):

    @app.route('/api/register', methods=['POST'])
    def register():
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"message": "Dati mancanti"}), 400

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, data['email']):
            return jsonify({"message": "Formato email non valido"}), 400

        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({"message": "Email già registrata"}), 409

        try:
            new_user = User(
                email=data['email'],
                nome=data.get('nome', ''),
                cognome=data.get('cognome', ''),
                ruolo=RuoloEnum.cliente
            )
            new_user.set_password(data['password'])
            db.session.add(new_user)
            db.session.commit()

            access_token = create_access_token(identity=new_user.id, expires_delta=timedelta(days=1))
            return jsonify({
                "message": "Registrazione completata",
                "token": access_token,
                "user": {
                    "nome": new_user.nome,
                    "cognome": new_user.cognome,
                    "email": new_user.email,
                    "ruolo": new_user.ruolo.value,
                    "creato_il": new_user.creato_il.isoformat()
                }
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Errore server: {str(e)}"}), 500

    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"message": "Dati mancanti"}), 400

        user = User.query.filter_by(email=data['email']).first()
        if not user or not user.check_password(data['password']):
            return jsonify({"message": "Credenziali non valide"}), 401

        # Imposta le credenziali admin dai parametri d'ambiente o di default
        admin_email = os.getenv('ADMIN_EMAIL', 'Admin@gmail.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'Admin123')

        print("Admin email:", admin_email)
        print("Admin password:", admin_password)
        print("Input email:", data['email'])
        print("Input password:", data['password'])

        if data['email'] == admin_email and data['password'] == admin_password:
            user.ruolo = RuoloEnum.admin
            print("Ruolo impostato a admin")
        else:
            user.ruolo = RuoloEnum.cliente
            print("Ruolo impostato a cliente")

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Errore di aggiornamento ruolo: {str(e)}"}), 500

        access_token = create_access_token(identity=user.email, expires_delta=timedelta(days=1))

        return jsonify({
            "message": "Login riuscito",
            "token": access_token,
            "user": {
                "nome": user.nome,
                "cognome": user.cognome,
                "ruolo": user.ruolo.value,
                "email": user.email,
                "creato_il": user.creato_il.isoformat()
            }
        }), 200

    @app.route('/api/profilo', methods=['GET'])
    @jwt_required()
    def get_profile():
        user_email = get_jwt_identity()
        user = User.query.filter_by(email=user_email).first()
        if not user:
            return jsonify({"message": "Utente non trovato"}), 404

        return jsonify({
            "id": user.id,
            "email": user.email,
            "nome": user.nome,
            "cognome": user.cognome,
            "ruolo": user.ruolo.value,
            "creato_il": user.creato_il.isoformat()
        }), 200

    @app.route('/api/domande', methods=['GET'])
    @jwt_required()
    def get_domande():
        try:
            domande = Domande.query.all()
            result = []
            for domanda in domande:
                risposte = Risposte.query.filter_by(id_domanda=domanda.id_domanda).all()
                risposte_data = [{
                    "id_risposta": r.id_risposta,
                    "descrizione": r.descrizione,
                    "stato": r.stato.value
                } for r in risposte]
                result.append({
                    "id_domanda": domanda.id_domanda,
                    "descrizione": domanda.descrizione,
                    "risposte": risposte_data
                })
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"message": f"Errore: {str(e)}"}), 500
        
    @app.route('/api/punteggio', methods=['POST'])
    @jwt_required()
    def save_punteggio():
        user_email = get_jwt_identity()
        data = request.get_json()
        if not data or 'valore' not in data:
            return jsonify({"message": "Dati mancanti"}), 400
        try:
            nuovo_punteggio = Punteggio(
                valore=data['valore'],
                email=user_email,
                data_creazione=datetime.utcnow()
            )
            db.session.add(nuovo_punteggio)
            db.session.commit()
            return jsonify({"message": "Punteggio salvato"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Errore: {str(e)}"}), 500


