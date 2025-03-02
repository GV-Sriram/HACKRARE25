import json
from collections import Counter

# Define file paths
hp_json_path = r"C:\Users\gvsri\Downloads\hpo_disease_diagnosis\hp.json"
hpoa_path = r"C:\Users\gvsri\Downloads\hpo_disease_diagnosis\phenotype.hpoa"

# Load the HPO ontology JSON file
def load_hpo_json(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)  # Load JSON as dictionary

# Parse phenotype.hpoa to map HPO terms to diseases
def parse_hpoa(file_path):
    disease_map = {}  # Maps HPO terms to diseases
    disease_to_hpo = {}  # Maps diseases to their associated HPO terms
    
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):  # Skip comments
                continue
            fields = line.strip().split("\t")
            if len(fields) < 5:
                continue  # Skip invalid lines
            
            disease_id = fields[0]  # Disease ID (e.g., OMIM:305400)
            hpo_term = fields[3].replace("HP:", "HP_")  # Normalize HPO term format
            disease_name = fields[1]  # Disease Name
            
            # Map HPO terms to diseases
            if hpo_term not in disease_map:
                disease_map[hpo_term] = []
            disease_map[hpo_term].append((disease_id, disease_name))
            
            # Map diseases to HPO terms
            disease_key = (disease_id, disease_name)
            if disease_key not in disease_to_hpo:
                disease_to_hpo[disease_key] = []
            disease_to_hpo[disease_key].append(hpo_term)
    
    print("✅ First 5 HPO mappings from phenotype.hpoa:")
    for key, value in list(disease_map.items())[:5]:  # Print first 5 mappings
        print(f"{key}: {value}")
    
    return disease_map, disease_to_hpo

# Search diseases based on input HPO terms
def find_diseases_by_phenotype(hpo_terms, disease_map):
    # Track disease matches and counts
    disease_match_count = {}
    matched_diseases = {}

    # Count how many symptoms match each disease
    for term in hpo_terms:
        if term in disease_map:
            for disease_id, disease_name in disease_map[term]:
                disease_key = (disease_id, disease_name)
                if disease_key not in disease_match_count:
                    disease_match_count[disease_key] = 0
                    matched_diseases[disease_key] = disease_name
                disease_match_count[disease_key] += 1
    
    # Sort diseases by number of matching symptoms (descending)
    sorted_diseases = [
        (disease_id, disease_name, count)
        for (disease_id, disease_name), count in disease_match_count.items()
    ]
    sorted_diseases.sort(key=lambda x: x[2], reverse=True)
    
    return sorted_diseases

# Map symptom names to HPO terms
def map_symptoms_to_hpo_terms(symptom_names, hpo_data):
    hpo_terms = []
    hpo_term_to_name = {}  # Maps HPO terms to their human-readable names
    
    for symptom in symptom_names:
        symptom = symptom.strip()  # Trim leading/trailing spaces
        if not symptom:  # Skip empty strings
            continue
            
        symptom_lower = symptom.lower()  # Case-insensitive comparison
        found = False
        for term in hpo_data["graphs"][0]["nodes"]:
            # Check if the symptom matches the label
            if "lbl" in term and term["lbl"].lower() == symptom_lower:
                hpo_id = term["id"].replace("http://purl.obolibrary.org/obo/", "").replace(":", "_")
                hpo_terms.append(hpo_id)
                hpo_term_to_name[hpo_id] = term["lbl"]
                found = True
                break
            # Check synonyms
            if "meta" in term and "synonyms" in term["meta"]:
                for synonym in term["meta"]["synonyms"]:
                    if "val" in synonym and synonym["val"].lower() == symptom_lower:
                        hpo_id = term["id"].replace("http://purl.obolibrary.org/obo/", "").replace(":", "_")
                        hpo_terms.append(hpo_id)
                        hpo_term_to_name[hpo_id] = term["lbl"]
                        found = True
                        break
                if found:
                    break
        if not found:
            print(f"⚠️ Warning: Symptom '{symptom}' not found in HPO ontology.")
    
    # Build a comprehensive term-to-name dictionary for all HPO terms
    all_hpo_term_to_name = {}
    for term in hpo_data["graphs"][0]["nodes"]:
        if "id" in term and "lbl" in term:
            hpo_id = term["id"].replace("http://purl.obolibrary.org/obo/", "").replace(":", "_")
            all_hpo_term_to_name[hpo_id] = term["lbl"]
    
    return hpo_terms, hpo_term_to_name, all_hpo_term_to_name

# Generate follow-up questions based on potential diseases
def generate_follow_up_questions(possible_diseases, confirmed_hpo_terms, disease_to_hpo, all_hpo_term_to_name, max_questions=5):
    if not possible_diseases:
        return []
        
    # Only consider top 50 diseases to avoid overwhelming with questions
    top_diseases = possible_diseases[:50]
    
    # Collect all HPO terms associated with the possible diseases
    disease_hpo_terms = []
    for disease_id, disease_name, _ in top_diseases:
        disease_key = (disease_id, disease_name)
        if disease_key in disease_to_hpo:
            disease_hpo_terms.extend(disease_to_hpo[disease_key])
    
    # Count frequency of each HPO term across diseases
    term_counter = Counter(disease_hpo_terms)
    
    # Remove already confirmed HPO terms
    for term in confirmed_hpo_terms:
        if term in term_counter:
            del term_counter[term]
    
    # Get the most common HPO terms (these will help differentiate diseases)
    common_terms = term_counter.most_common(max_questions)
    
    # Generate questions for these terms
    questions = []
    for hpo_term, count in common_terms:
        # Get human-readable name for the HPO term
        term_name = all_hpo_term_to_name.get(hpo_term, hpo_term)
        questions.append((hpo_term, f"Do you experience {term_name}?"))
    
    return questions

# Interactive diagnosis function
def interactive_diagnosis():
    # Load data
    print("\n📌 Loading HPO JSON...")
    hpo_data = load_hpo_json(hp_json_path)

    print("\n📌 Parsing phenotype.hpoa...")
    disease_map, disease_to_hpo = parse_hpoa(hpoa_path)
    
    # Initial symptoms from user
    user_symptoms = input("\n🔍 Enter your initial symptoms separated by commas: ").split(",")
    
    # Map symptom names to HPO terms
    hpo_terms, hpo_term_to_name, all_hpo_term_to_name = map_symptoms_to_hpo_terms(user_symptoms, hpo_data)
    print(f"\n🧬 Mapped HPO terms: {[f'{term} ({hpo_term_to_name.get(term, term)})' for term in hpo_terms]}")
    
    if not hpo_terms:
        print("❌ No valid symptoms were identified. Please try again with different wording.")
        return
    
    # Find initial list of possible diseases
    possible_diseases = find_diseases_by_phenotype(hpo_terms, disease_map)
    
    # Display initial results
    print("\n🔎 **Initial Results**:")
    if possible_diseases:
        print(f"Found {len(possible_diseases)} potential diseases based on your symptoms:")
        for i, (disease_id, disease_name, match_count) in enumerate(possible_diseases[:10], 1):
            print(f"{i}. 🦠 {disease_id}: {disease_name} (matched {match_count} symptoms)")
        if len(possible_diseases) > 10:
            print(f"...and {len(possible_diseases) - 10} more")
    else:
        print("❌ No diseases found for the given symptoms.")
        return
    
    # Interactive follow-up questions
    confirmed_hpo_terms = hpo_terms.copy()
    max_rounds = 5  # Limit the number of question rounds
    
    for round_num in range(max_rounds):
        # If we've narrowed down to 3 or fewer diseases, stop asking questions
        if len(possible_diseases) <= 3:
            break
            
        print("\n🔍 Let's narrow down the possibilities with some follow-up questions...")
        questions = generate_follow_up_questions(
            possible_diseases, 
            confirmed_hpo_terms, 
            disease_to_hpo, 
            all_hpo_term_to_name,
            max_questions=3  # Ask 3 questions per round
        )
        
        if not questions:
            print("No more differentiating questions available.")
            break
            
        # Ask follow-up questions
        additional_hpo_terms = []
        for hpo_term, question in questions:
            print(f"\n➡️ {question} (y/n)")
            answer = input("Your answer: ").strip().lower()
            
            if answer.startswith('y'):
                additional_hpo_terms.append(hpo_term)
                confirmed_hpo_terms.append(hpo_term)
                print(f"✅ Added {all_hpo_term_to_name.get(hpo_term, hpo_term)} to your symptoms")
        
        # Update possible diseases based on new symptoms
        if additional_hpo_terms:
            # Find diseases that match all confirmed symptoms (more restrictive)
            all_diseases = find_diseases_by_phenotype(confirmed_hpo_terms, disease_map)
            
            # Filter to only include diseases that match all symptoms
            # This helps narrow down the list substantially
            possible_diseases = []
            for disease_id, disease_name, match_count in all_diseases:
                if match_count >= len(confirmed_hpo_terms) * 0.7:  # At least 70% match
                    possible_diseases.append((disease_id, disease_name, match_count))
            
            print("\n🔄 **Updated Results**:")
            if possible_diseases:
                print(f"Found {len(possible_diseases)} potential diseases matching most of your symptoms:")
                for i, (disease_id, disease_name, match_count) in enumerate(possible_diseases[:10], 1):
                    match_percent = (match_count / len(confirmed_hpo_terms)) * 100
                    print(f"{i}. 🦠 {disease_id}: {disease_name} (matched {match_count}/{len(confirmed_hpo_terms)} symptoms - {match_percent:.1f}%)")
                if len(possible_diseases) > 10:
                    print(f"...and {len(possible_diseases) - 10} more")
            else:
                print("❌ No diseases match your combination of symptoms.")
                possible_diseases = all_diseases[:50]  # Revert to using all diseases
                print(f"Showing top {len(possible_diseases)} partial matches instead:")
                for i, (disease_id, disease_name, match_count) in enumerate(possible_diseases[:10], 1):
                    match_percent = (match_count / len(confirmed_hpo_terms)) * 100
                    print(f"{i}. 🦠 {disease_id}: {disease_name} (matched {match_count}/{len(confirmed_hpo_terms)} symptoms - {match_percent:.1f}%)")
        else:
            print("No new symptoms confirmed. Continuing with current list of diseases.")
    
    # Final diagnosis
    print("\n🏥 **Final Diagnosis**:")
    if possible_diseases:
        print("Based on your symptoms, the most likely diagnoses are:")
        for i, (disease_id, disease_name, match_count) in enumerate(possible_diseases[:5], 1):
            confidence = (match_count / len(confirmed_hpo_terms)) * 100
            print(f"{i}. 🦠 {disease_id}: {disease_name}")
            print(f"   Confidence: {confidence:.1f}% ({match_count}/{len(confirmed_hpo_terms)} symptoms matched)")
            
            # Show matched symptoms for top diagnosis
            if i == 1:
                disease_key = (disease_id, disease_name)
                if disease_key in disease_to_hpo:
                    disease_hpo_terms = set(disease_to_hpo[disease_key])
                    matched_terms = disease_hpo_terms.intersection(set(confirmed_hpo_terms))
                    print("   Matched symptoms:")
                    for term in matched_terms:
                        print(f"   ✓ {all_hpo_term_to_name.get(term, term)}")
        
        print("\n⚠️ Note: This is not a substitute for professional medical advice. Please consult a healthcare provider for proper diagnosis and treatment.")
    else:
        print("❌ No diseases match your combination of symptoms.")

# Start the interactive diagnosis process
if __name__ == "__main__":
    interactive_diagnosis()