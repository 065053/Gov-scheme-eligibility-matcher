from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

def load_data(filepath='schemes_db.json'):
    # Use absolute path to ensure file is found regardless of where server is run from
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, filepath)
    
    if not os.path.exists(full_path):
        return []
    try:
        with open(full_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading database: {e}")
        return []

def filter_schemes(schemes, age, gender, occupation, income):
    matched = []
    occ_lower = occupation.lower()
    gender_lower = gender.lower()
    
    for s in schemes:
        try:
            age_valid = s['age_range']['min'] <= age <= s['age_range']['max']
            income_valid = s['max_income_limit'] >= income
            
            target_occs = [o.lower() for o in s['target_occupation']]
            occ_valid = ('all' in target_occs) or any(occ_lower in t or t in occ_lower for t in target_occs)
            
            target_gender = s.get('target_gender', 'all').lower()
            gender_valid = (target_gender == 'all' or target_gender == gender_lower)
            
            if age_valid and income_valid and occ_valid and gender_valid:
                matched.append(s)
        except KeyError as e:
            print(f"Skipping scheme due to missing field {e}: {s.get('scheme_name')}")
            continue
            
    return matched

@app.route('/api/schemes', methods=['POST'])
def match_schemes():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "Invalid JSON data"}), 400
        
    age = int(data.get('age', 22))
    gender = data.get('gender', 'Male')
    occupation = data.get('occupation', 'Student')
    income = int(data.get('income', 0))
    
    schemes = load_data()
    matches = filter_schemes(schemes, age, gender, occupation, income)
    
    return jsonify({
        "status": "success",
        "matches": matches
    })

# Serve Static Files
@app.route('/')
@app.route('/<path:path>')
def serve(path=''):
    # Prevent direct access to sensitive python/json files if served as static
    if path.endswith('.py') or path.endswith('.json'):
        return "Access Forbidden", 403
        
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    # Using a standard port like 5000 or 8000 is common, but keeping 8501 if user expects it
    print("Starting Welfare Matching Portal on http://127.0.0.1:8501")
    app.run(debug=True, port=8501)
