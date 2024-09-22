from flask import Flask, render_template, request, redirect, send_file
import os
import uuid
from Bio import SeqIO
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads/'
PROCESSED_FOLDER = 'processed/'

# Ensure upload and processed folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def fetch_allowed_features_and_qualifiers(url):
    allowed_features = set()
    allowed_qualifiers = set()

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch webpage: {response.status_code}")
        sys.exit(1)

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the start of the Feature Keys section
    feature_keys_section = soup.find(string=lambda text: text and "7.2 Appendix II: Feature keys reference" in text)
    if feature_keys_section:
        print("Found Feature Keys section")
        current_element = feature_keys_section.find_next('pre')
        while current_element:
            text = current_element.get_text().strip()
            if "7.3" in text:
                break
            lines = text.splitlines()
            for line in lines:
                line = line.strip()
                if line.startswith("Feature Key"):
                    feature_key = line.split("Feature Key")[1].strip()
                    print(f"Found Feature Key: {feature_key}")
                    allowed_features.add(feature_key)
            current_element = current_element.find_next_sibling('pre')
    else:
        print("Feature keys section not found")

    # Find the start of the Qualifiers section
    qualifiers_section = soup.find(string=lambda text: text and "7.3.1 Qualifier List" in text)
    if qualifiers_section:
        print("Found Qualifiers section")
        current_element = qualifiers_section.find_next('pre')
        while current_element:
            text = current_element.get_text().strip()
            if "7.4" in text:
                break
            lines = text.splitlines()
            for line in lines:
                line = line.strip()
                if line.startswith("Qualifier"):
                    qualifier_key = line.split("Qualifier")[1].strip().lstrip("/").split("=")[0]
                    print(f"Found Qualifier: {qualifier_key}")
                    allowed_qualifiers.add(qualifier_key)
            current_element = current_element.find_next_sibling('pre')
    else:
        print("Qualifiers section not found")

    print("Allowed features:", allowed_features)
    print("Allowed qualifiers:", allowed_qualifiers)
    return allowed_features, allowed_qualifiers

def format_location(location):
    start = location.start + 1
    end = location.end
    strand = location.strand
    
    if isinstance(location.start, int) and isinstance(location.end, int):
        return f"{start}\t{end}"
    else:
        start_str = f"<{start}" if location.start_is_partial else f"{start}"
        end_str = f">{end}" if location.end_is_partial else f"{end}"
        return f"{start_str}\t{end_str}"

def parse_genbank_to_tab(input_file, output_file, allowed_features, allowed_qualifiers):
    with open(output_file, 'w') as out_f:
        for record in SeqIO.parse(input_file, "genbank"):
            seq_id = record.id
            out_f.write(f">Feature {seq_id}\n")
            
            for feature in record.features:
                if feature.type not in allowed_features:
                    continue
                
                # Handle feature locations
                if len(feature.location.parts) > 1:
                    for i, part in enumerate(feature.location.parts):
                        if i == 0:
                            out_f.write(f"{format_location(part)}\t{feature.type}\t\t\n")
                        else:
                            out_f.write(f"{format_location(part)}\t\t\t\t\n")
                else:
                    out_f.write(f"{format_location(feature.location)}\t{feature.type}\t\t\n")

                # Write the qualifiers
                for qualifier_key, qualifier_value in feature.qualifiers.items():
                    if qualifier_key not in allowed_qualifiers:
                        continue
                    if isinstance(qualifier_value, list):
                        for value in qualifier_value:
                            out_f.write(f"\t\t\t{qualifier_key}\t{value}\n")
                    else:
                        out_f.write(f"\t\t\t{qualifier_key}\t{qualifier_value}\n")

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            return redirect(request.url)

        if file:
            # Save the uploaded file
            filename = str(uuid.uuid4()) + ".gbk"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Fetch allowed features and qualifiers
            url = "https://www.insdc.org/submitting-standards/feature-table/"
            allowed_features, allowed_qualifiers = fetch_allowed_features_and_qualifiers(url)
            
            if not allowed_features and not allowed_qualifiers:
                return "No allowed features or qualifiers found."
            
            # Process the GenBank file
            output_filename = filename.replace(".gbk", ".tab")
            output_filepath = os.path.join(PROCESSED_FOLDER, output_filename)
            parse_genbank_to_tab(filepath, output_filepath, allowed_features, allowed_qualifiers)

            # Send the processed file to the user
            return send_file(output_filepath, as_attachment=True)

    return '''
    <!doctype html>
    <title>Upload GenBank File</title>
    <h1>Upload GenBank File to Convert</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)