from flask import Flask, jsonify, request
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask_cors import CORS
from bson import ObjectId
from bson import Timestamp
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
app = Flask(__name__)
CORS(app)

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USER = 'hack.binary.potatoes@gmail.com' 
EMAIL_PASSWORD = 'ggfz qcnu deex rviq'  


db = None

def dbconnection():
    global db
    url = ""  # connection string here

    client = MongoClient(url, server_api=ServerApi('1'))

    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        db = client['cluster0']

    except Exception as e:
        print(e)

dbconnection()
def fetch_data(station_id):
    try:
        collection = db['ports']
        cursor = collection.find({'station_id': station_id})

        documents = []
        for document in cursor:
            document.pop('_id', None)
            for key, value in document.items():
                if isinstance(value, ObjectId):
                    document[key] = str(value)
                elif isinstance(value, Timestamp):
                    document[key] = datetime.datetime.fromtimestamp(value.time).strftime('%Y-%m-%d %H:%M:%S')
            documents.append(document)

        if documents:
            return jsonify(documents), 200
        else:
            return jsonify({'error': 'Data not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def find_email(station_id, port_id):
    try:
        collection = db['issues']
        document = collection.find_one({'station_id': station_id, 'port_id': port_id})
        if document:
            return document.get('email')
        else:
            return None
    except Exception as e:
         print(e)
    return None

def delete_issue(station_id, port_id):
    try:
        collection = db['issues']
        collection.delete_one({'station_id': station_id, 'port_id': port_id})
    except Exception as e:
        print(e)
    return None

@app.route('/')
def hello():
    return 'Binary Potatoes !!'

@app.post('/new')
def get_keys():
    print(request.method)  
    try:
        data = request.get_json()  
        id = data.get('id')  

        
        print(id)

        collection = db['ports']
        all_documents = collection.find()
        all_documents_with_keys_values = []
        for doc in all_documents:

            doc['_id'] = str(doc['_id']) if '_id' in doc else None
            for key, value in doc.items():
                if isinstance(value, ObjectId):
                    doc[key] = str(value)
                elif isinstance(value, Timestamp):
 
                    doc[key] = datetime.datetime.fromtimestamp(value.time).strftime('%Y-%m-%d %H:%M:%S')
            
            all_documents_with_keys_values.append(doc)

        return jsonify(all_documents_with_keys_values), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.post('/station')
def get_station():
    try:
        data = request.get_json()
        station_id = data.get('station_id')

        collection = db['ports']
        document = collection.find_one({'station_id': station_id})

        if document:
            document['_id'] = str(document['_id']) if '_id' in document else None
            for key, value in document.items():
                if isinstance(value, ObjectId):
                    document[key] = str(value)
                elif isinstance(value, Timestamp):
                    document[key] = datetime.datetime.fromtimestamp(value.time).strftime('%Y-%m-%d %H:%M:%S')

            return jsonify(document), 200
        else:
            return jsonify({'error': 'Station not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.post('/update_ratings')
def update_ratings():
    try:
        data = request.get_json()
        station_id = data.get('station_id')
        ratings = data.get('ratings')
        feedback_content = data.get('feedback_content')
        collection = db['station']
        document = collection.find_one({'station_id': station_id})

        if document:
            no_of_ratings = document.get('no_of_ratings', 0)
            overall_ratings = document.get('overall_ratings', 0)

            calc_overall_ratings = ((overall_ratings * no_of_ratings) + ratings) / (no_of_ratings + 1)
            calc_overall_ratings = float(f'{calc_overall_ratings:.1f}')
            fb = document.get('feedback_content', [])
            fb.append(feedback_content)
            no_of_ratings += 1
            collection.update_one({'station_id': station_id}, {'$set': {'overall_ratings': calc_overall_ratings, 'feedback_content': fb, 'no_of_ratings': no_of_ratings}})

            return jsonify({'message': 'Ratings updated successfully'}), 200
        else:
            return jsonify({'error': 'Station not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.post('/ports_id')
def ports_id():
    try:
        data = request.get_json()
        station_id = data.get('station_id')
        collection_station = db['station']
        documents_station = collection_station.find({'station_id': station_id})
        
        station_documents = []
        for doc in documents_station:
            no_of_ports = doc.get('no_of_ports')  
            station_documents.append(no_of_ports)  
        
        collection_ports = db['ports']
        documents_ports = collection_ports.find({'station_id': station_id})
        
        port_documents = []
        for doc in documents_ports:
            doc.pop('_id', None)
            
            for key, value in doc.items():
                if isinstance(value, ObjectId):
                    doc[key] = str(value)
                elif isinstance(value, Timestamp):
                    doc[key] = datetime.datetime.fromtimestamp(value.time).strftime('%Y-%m-%d %H:%M:%S')
            
            port_documents.append(doc)
        
        return jsonify({'station_documents': station_documents, 'port_documents': port_documents}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.post('/update_issue')
def update_issue():
            try:
                data = request.get_json()
                station_id = data.get('station_id')
                condition = data.get('condition')
                port_id = data.get('port_id')

                if condition == "working" and find_email(station_id, port_id):
                    receiver_email = find_email(station_id, port_id)
                    subject = "subject"
                    message = '''Dear Customer,

We hope this message finds you well. We wanted to take a moment to update you on some significant improvements we've made to address recent challenges you may have experienced during your EV charging sessions.

After carefully reviewing your feedback and concerns, we're pleased to inform you that we've taken immediate action to resolve port damages , slow charging and all connectivity related issues and enhanced our overall service quality.

We're dedicated to continually improving our service quality to meet and exceed your expectations. Your satisfaction remains our utmost priority, and we're grateful for your ongoing support.

Best regards,
Team Electroad'''

                    msg = MIMEMultipart()
                    msg['From'] = EMAIL_USER
                    msg['To'] = receiver_email
                    msg['Subject'] = subject

                    msg.attach(MIMEText(message, 'plain'))
                    server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
                    server.starttls()
                    server.login(EMAIL_USER, EMAIL_PASSWORD)
                    server.sendmail(EMAIL_USER, receiver_email, msg.as_string())
                    server.quit()
                    collection = db['ports']
                    collection.update_many({'port_id': port_id , 'station_id': station_id}, {'$set': {'issue.port damage': 0, 'issue.slow charging': 0, 'condition': 'working', 'issue.not connecting': 0, 'issue.connecting but not charging': 0}})
                    delete_issue(station_id, port_id)
                elif condition == "working":
                    collection = db['ports']
                    collection.update_many({'port_id': port_id , 'station_id': station_id}, {'$set': {'issue.port damage': 0, 'issue.slow charging': 0, 'condition': 'working', 'issue.not connecting': 0, 'issue.connecting but not charging': 0}})

                elif condition == "disable":
                     collection = db['ports']
                     collection.update_many({'port_id': port_id , 'station_id': station_id}, {'$set': {'condition': 'disable'}})
                documents_station = collection.find({'station_id': station_id,'port_id': port_id})
                station_documents = []
                for doc in documents_station:
                    no_of_ports = doc.get('no_of_ports')  
                    station_documents.append(no_of_ports)  
                return fetch_data(station_id)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
            
@app.post('/add_issue')
def add_issue():
                try:
                    
                    data = request.get_json()
                    station_id = data.get('station_id')
                    port_id = data.get('port_id')
                    issue_type = data.get('issue_type')
                    email = data.get('email')

                    collection = db['issues']
                    document = {
                        'station_id': station_id,
                        'port_id': port_id,
                        'issue_type': issue_type,
                        'email': email,
                    }
                    collection.insert_one(document)

                    return jsonify({'message': 'Issue added successfully'}), 200
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
                
@app.post('/send_email')
def send_email():
    try:
        data = request.get_json()
        receiver_email = data.get('receiver_email')
        subject = data.get('subject')
        message = data.get('message')

        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = receiver_email
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)

        server.sendmail(EMAIL_USER, receiver_email, msg.as_string())
        server.quit()

        return jsonify({'message': 'Email sent successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.post('/get_station_details')
def get_station_details():
    try:
        data = request.get_json()
        station_id = data.get('station_id')

        collection = db['station']
        cursor = collection.find({'station_id': station_id})

        documents = []
        for document in cursor:
            document.pop('_id', None)
            documents.append(document)

        return jsonify(documents), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
if __name__ == '__main__':
    app.run(debug=True)