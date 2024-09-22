import argparse

def parse_genbank(genbank_file):
    features = []
    current_feature = None
    current_qualifiers = {}
    in_features_section = False  # Initialize the variable here

    with open(genbank_file, 'r') as gb_file:
        for line in gb_file:
            line = line.strip()
            
            # Detect start of a feature
            if line.startswith("FEATURES"):
                in_features_section = True
                continue

            if line.startswith("ORIGIN"):
                in_features_section = False
                continue
            
            if not in_features_section:
                continue

            # Debug print statement to trace features section processing
            print(f"Processing line: {line}")

            # Process each feature and its qualifiers
            if line.startswith("     ") and not line.startswith("                     "):
                if current_feature:
                    features.append(current_feature)
                    print(f"Added feature: {current_feature}")

                parts = line.split()
                if len(parts) >= 2:
                    feature_type = parts[0]
                    location = ' '.join(parts[1:])
                    current_feature = {
                        'type': feature_type,
                        'location': location,
                        'qualifiers': {}
                    }
                    current_qualifiers = {}
                    print(f"New feature detected: {current_feature}")
            elif current_feature:
                parts = line.split("=", 1)
                if len(parts) == 2:
                    qualifier_key = parts[0].strip().lstrip('/')
                    qualifier_value = parts[1].strip().strip('"')
                    if qualifier_key not in current_qualifiers:
                        current_qualifiers[qualifier_key] = []
                    current_qualifiers[qualifier_key].append(qualifier_value)
                    current_feature['qualifiers'] = current_qualifiers
                    print(f"Qualifier added: {qualifier_key} = {qualifier_value}")
    
    if current_feature:
        features.append(current_feature)
        print(f"Added last feature: {current_feature}")
    
    print(f"Total features parsed: {len(features)}")
    return features

def convert_location(location):
    complement = False
    if location.startswith("complement"):
        complement = True
        location = location[len("complement("):-1]
    if "join" in location:
        location = location[len("join("):-1]
    intervals = [tuple(map(int, loc.split(".."))) for loc in location.split(",")]
    return intervals, complement

def convert_genbank_to_tab(genbank_file, output_file):
    features = parse_genbank(genbank_file)

    with open(output_file, 'w') as out_file:
        # Write the feature table header
        out_file.write(f">Feature {genbank_file}\n")
        print(f"Header written: >Feature {genbank_file}")

        for feature in features:
            intervals, complement = convert_location(feature['location'])
            for start, end in intervals:
                start, end = (end, start) if complement else (start, end)
                out_file.write(f"{start}\t{end}\t{feature['type']}\n")
                print(f"Feature line written: {start}\t{end}\t{feature['type']}")

                for qualifier_key, qualifier_values in feature['qualifiers'].items():
                    for value in qualifier_values:
                        out_file.write(f"\t\t{qualifier_key}\t{value}\n")
                        print(f"Qualifier line written: \t\t{qualifier_key}\t{value}")

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description='Convert GenBank file to 5-column tab-delimited format.')
    
    # Add arguments
    parser.add_argument('input_file', help='Input GenBank file path')
    parser.add_argument('output_file', help='Output tab-delimited file path')
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Call the conversion function with the provided arguments
    convert_genbank_to_tab(args.input_file, args.output_file)

if __name__ == '__main__':
    main()