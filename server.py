from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os

app = Flask(__name__, static_folder='frontend')
CORS(app)

def load_data(filepath='schemes_db.json'):
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []

def filter_schemes(schemes, age, occupation, income):
    matched = []
    occ_lower = occupation.lower()
    
    for s in schemes:
        age_valid = s['age_range']['min'] <= age <= s['age_range']['max']
        income_valid = s['max_income_limit'] >= income
        
        target_occs = [o.lower() for o in s['target_occupation']]
        occ_valid = ('all' in target_occs) or (occ_lower in target_occs)
        
        if age_valid and income_valid and occ_valid:
            matched.append(s)
            
    return matched

@app.route('/api/schemes', methods=['POST'])
def match_schemes():
    data = request.json
    age = data.get('age', 22)
    occupation = data.get('occupation', 'Student')
    income = data.get('income', 0)
    
    schemes = load_data()
    matches = filter_schemes(schemes, age, occupation, income)
    
    return jsonify({
        "status": "success",
        "matches": matches
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    # Render requires binding to 0.0.0.0 and using PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
