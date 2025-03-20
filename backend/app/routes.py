from flask import jsonify, request
from .models import db, User, RuoloEnum, Prenotazione, DettagliPrenotazione, Piatto, Menu, MenuSezione, MenuSezioneRel, MenuItem
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
        admin_email = os.getenv('ADMIN_EMAIL', 'Gabrielcuter27@gmail.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'Gabicu27')

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

        access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=1))

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
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
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

    # --- Endpoint per prenotazioni ---

    @app.route('/api/prenotazioni', methods=['POST'])
    @jwt_required()
    def crea_prenotazione():
        user_id = get_jwt_identity()
        data = request.get_json()
        if not data or 'data_prenotata' not in data or 'numero_posti' not in data:
            return jsonify({"message": "Dati mancanti per la prenotazione"}), 400
        try:
            nuova_prenotazione = Prenotazione(
                data_prenotata=datetime.fromisoformat(data['data_prenotata']),
                stato="attiva",
                id_utente=user_id,
                data_creazione=datetime.utcnow(),
                note_aggiuntive=data.get('note_aggiuntive', ''),
                numero_posti=data['numero_posti']
            )
            db.session.add(nuova_prenotazione)
            db.session.commit()
            return jsonify({
                "message": "Prenotazione creata",
                "prenotazione_id": nuova_prenotazione.id_prenotazione
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Errore server: {str(e)}"}), 500

    @app.route('/api/prenotazioni/menu', methods=['POST'])
    @jwt_required()
    def crea_prenotazione_con_menu():
        user_id = get_jwt_identity()
        data = request.get_json()
        if not data or 'data_prenotata' not in data or 'numero_posti' not in data or 'piatti' not in data:
            return jsonify({"message": "Dati mancanti per la prenotazione con menu"}), 400
        try:
            prenotazione = Prenotazione(
                data_prenotata=datetime.fromisoformat(data['data_prenotata']),
                stato="attiva",
                id_utente=user_id,
                data_creazione=datetime.utcnow(),
                note_aggiuntive=data.get('note_aggiuntive', ''),
                numero_posti=data['numero_posti']
            )
            db.session.add(prenotazione)
            db.session.flush()  # Per ottenere l'id della prenotazione

            for item in data['piatti']:
                dettaglio = DettagliPrenotazione(
                    fk_prenotazione=prenotazione.id_prenotazione,
                    fk_piatto=item['fk_piatto'],
                    quantita=item['quantita']
                )
                db.session.add(dettaglio)
            db.session.commit()
            return jsonify({
                "message": "Prenotazione con menu creata",
                "prenotazione_id": prenotazione.id_prenotazione
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Errore server: {str(e)}"}), 500

    @app.route('/api/prenotazioni/storico/<int:user_id>', methods=['GET'])
    @jwt_required()
    def storico_prenotazioni(user_id):
        prenotazioni = Prenotazione.query.filter_by(id_utente=user_id).all()
        prenotazioni_data = []
        for p in prenotazioni:
            prenotazioni_data.append({
                "id_prenotazione": p.id_prenotazione,
                "data_prenotata": p.data_prenotata.isoformat(),
                "stato": p.stato,
                "data_creazione": p.data_creazione.isoformat(),
                "numero_posti": p.numero_posti,
                "note_aggiuntive": p.note_aggiuntive
            })
        return jsonify(prenotazioni_data), 200

    @app.route('/api/prenotazioni/calendario', methods=['GET'])
    @jwt_required()
    def prenotazioni_calendario():
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.ruolo != RuoloEnum.admin:
            return jsonify({"message": "Accesso negato"}), 403

        prenotazioni = Prenotazione.query.all()
        prenotazioni_data = []
        for p in prenotazioni:
            prenotazioni_data.append({
                "id_prenotazione": p.id_prenotazione,
                "data_prenotata": p.data_prenotata.isoformat(),
                "stato": p.stato,
                "data_creazione": p.data_creazione.isoformat(),
                "numero_posti": p.numero_posti,
                "note_aggiuntive": p.note_aggiuntive
            })
        return jsonify(prenotazioni_data), 200

    # --- Endpoint per la gestione dei menù ---

    # Ottieni la lista dei piatti disponibili (usato per il menù)
    @app.route('/api/menu', methods=['GET'])
    def get_piatti():
        piatti = Piatto.query.all()
        piatti_data = [{
            "id_piatto": p.id_piatto,
            "nome": p.nome,
            "prezzo": p.prezzo,
            "descrizione": p.descrizione
        } for p in piatti]
        return jsonify(piatti_data), 200

    # Salva un nuovo menù (solo admin)
    @app.route('/api/menu', methods=['POST'])
    @jwt_required()
    def save_menu():
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.ruolo != RuoloEnum.admin:
            return jsonify({"message": "Accesso negato"}), 403

        data = request.get_json()
        if not data or 'titolo' not in data or 'sezioni' not in data:
            return jsonify({"message": "Dati mancanti per il menù"}), 400

        try:
            nuovo_menu = Menu(titolo=data['titolo'])
            db.session.add(nuovo_menu)
            db.session.flush()  # per ottenere nuovo_menu.id_menu

            sezioni_data = data['sezioni']  # es. {"Antipasto": [ { "id_piatto": 1 }, ... ], "Primo": [...] }
            for nome_sezione, items in sezioni_data.items():
                # Trova o crea la sezione
                sezione = MenuSezione.query.filter_by(nome_sezione=nome_sezione).first()
                if not sezione:
                    sezione = MenuSezione(nome_sezione=nome_sezione)
                    db.session.add(sezione)
                    db.session.flush()
                # Crea la relazione per questo menù e la sezione
                rel = MenuSezioneRel(id_menu=nuovo_menu.id_menu, id_sezione=sezione.id_sezione)
                db.session.add(rel)
                db.session.flush()
                # Aggiungi gli item per questa sezione
                for item in items:
                    mi = MenuItem(id_menu_sezione=rel.id_menu_sezione, id_piatto=item['id_piatto'])
                    db.session.add(mi)

            db.session.commit()
            return jsonify({
                "message": "Menù salvato",
                "menu": {
                    "id_menu": nuovo_menu.id_menu,
                    "titolo": nuovo_menu.titolo,
                    "data_creazione": nuovo_menu.data_creazione.isoformat()
                }
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Errore nel salvataggio del menù: {str(e)}"}), 500

    # Ottieni tutti i menù salvati
    @app.route('/api/menu/saved', methods=['GET'])
    @jwt_required()
    def get_saved_menus():
        try:
            menus = Menu.query.all()
            result = []
            for m in menus:
                sezioni_list = []
                for rel in m.sezioni:
                    sezione_obj = MenuSezione.query.get(rel.id_sezione)
                    items = []
                    for mi in rel.items:
                        piatto = Piatto.query.get(mi.id_piatto)
                        items.append({
                            "id_piatto": piatto.id_piatto,
                            "nome": piatto.nome,
                            "prezzo": piatto.prezzo,
                            "descrizione": piatto.descrizione
                        })
                    sezioni_list.append({
                        "nome_sezione": sezione_obj.nome_sezione,
                        "piatti": items
                    })
                result.append({
                    "id_menu": m.id_menu,
                    "titolo": m.titolo,
                    "data_creazione": m.data_creazione.isoformat(),
                    "sezioni": sezioni_list
                })
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"message": f"Errore nel recupero dei menù: {str(e)}"}), 500
