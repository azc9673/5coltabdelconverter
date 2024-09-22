import sys
from Bio import SeqIO

def load_allowed_features_and_qualifiers(file_path):
    allowed_features = set()
    allowed_qualifiers = set()
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        
        if line.startswith("Feature Key"):
            feature_key = line.split("Feature Key")[1].strip()
            allowed_features.add(feature_key)
        
        elif line.startswith("Qualifier"):
            qualifier_key = line.split("Qualifier")[1].strip().lstrip("/").split("=")[0]
            allowed_qualifiers.add(qualifier_key)
    
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

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python genbank_to_tab.py <input_genbank_file> <output_tab_file> <allowed_features_qualifiers_file>")
        sys.exit(1)

    input_genbank_file = sys.argv[1]
    output_tab_file = sys.argv[2]
    allowed_features_qualifiers_file = sys.argv[3]
    
    allowed_features, allowed_qualifiers = load_allowed_features_and_qualifiers(allowed_features_qualifiers_file)
    parse_genbank_to_tab(input_genbank_file, output_tab_file, allowed_features, allowed_qualifiers)
    print(f"Conversion complete. Output written to {output_tab_file}")
