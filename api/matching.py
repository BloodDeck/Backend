# import re
# import random
# from django.utils import timezone
# from datetime import timedelta
# from django.db.models import Count, Q
# from .models import User, Donation

# # Clinical Blood Compatibility Chart (Recipient -> Compatible Donors)
# COMPATIBILITY = {
#     'O-': ['O-'],
#     'O+': ['O+', 'O-'],
#     'A-': ['A-', 'O-'],
#     'A+': ['A+', 'A-', 'O+', 'O-'],
#     'B-': ['B-', 'O-'],
#     'B+': ['B+', 'B-', 'O+', 'O-'],
#     'AB-': ['AB-', 'A-', 'B-', 'O-'],
#     'AB+': ['AB+', 'AB-', 'A+', 'A-', 'B+', 'B-', 'O+', 'O-'],
# }

# def extract_request_info(details_str):
#     """Parses the frontend details string to extract clinical data."""
#     if not details_str:
#         return {'blood_type': None, 'is_emergency': False}
        
#     blood_match = re.search(r"Blood Type:\s*([A-Z]{1,2}[+-])", details_str, re.IGNORECASE)
#     urgency_match = re.search(r"Urgency:\s*([a-zA-Z]+)", details_str, re.IGNORECASE)
    
#     return {
#         'blood_type': blood_match.group(1).upper() if blood_match else None,
#         'is_emergency': urgency_match.group(1).lower() == 'emergency' if urgency_match else False
#     }

# def knn_randmax_hybrid_matching(application, gamma=0.3, k_donors=4):
#     """
#     PEAK ALGORITHM: 
#     Combines K-Nearest Neighbors (KNN) for clinical/geospatial precision 
#     with RandMax Policy for donor fatigue management & fairness.
#     """
#     # 1. Parse Request Data
#     req_info = extract_request_info(application.details)
#     req_blood = req_info.get('blood_type')
#     is_emergency = req_info.get('is_emergency')

#     # 2. Hard Constraints (56-Day Deferral Rule)
#     cutoff_date = timezone.now().date() - timedelta(days=56)
#     recent_donors = Donation.objects.filter(
#         status='completed', 
#         donation_date__gte=cutoff_date
#     ).values_list('donor_id', flat=True)

#     # Base query: Active donors + Annotate their historical reliability
#     eligible_donors = User.objects.filter(
#         role='donor', 
#         is_active=True
#     ).exclude(id__in=recent_donors).annotate(
#         successful_donations=Count('donations', filter=Q(donations__status='completed'))
#     )

#     scored_donors = []
#     request_city = application.user.city

#     # 3. K-Nearest Neighbor (KNN) Scoring Phase
#     for donor in eligible_donors:
#         # Infer donor's blood type from their past donations
#         past_donation = Donation.objects.filter(donor=donor).first()
#         inferred_blood_type = past_donation.blood_group if past_donation else None

#         # STRICT CLINICAL FILTER: If we know their type, ensure compatibility
#         if req_blood and inferred_blood_type:
#             if inferred_blood_type not in COMPATIBILITY.get(req_blood, []):
#                 continue # Incompatible! Skip this donor entirely.

#         score = 0.0
        
#         # Feature 1: Spatial/Distance Weight (City Match)
#         if request_city and donor.city and request_city.lower() == donor.city.lower():
#             score += 0.50  # Exact location match is heavily weighted
        
#         # Feature 2: Historical Reliability (KNN weight)
#         # More successful past donations = higher reliability score (capped at 0.3)
#         reliability = min(donor.successful_donations * 0.1, 0.3)
#         score += reliability

#         # Feature 3: Urgency Adaptation
#         days_on_platform = (timezone.now() - donor.date_joined).days
#         if is_emergency:
#             # For emergencies, prioritize newer users who might be more actively monitoring the app
#             if days_on_platform < 90:
#                 score += 0.20
#         else:
#             # For standard, prioritize retaining older users
#             if days_on_platform > 180:
#                 score += 0.20

#         # Feature 4: Universal Donor Bonus
#         if inferred_blood_type == 'O-':
#             score += 0.10

#         scored_donors.append({'donor': donor, 'score': score})

#     # 4. RandMax Selection Phase
#     matched_donors = []
    
#     while len(matched_donors) < k_donors and scored_donors:
#         # Flip a weighted coin using Gamma (e.g., 30% chance for random exploration)
#         if random.random() < gamma:
#             selected = random.choice(scored_donors)
#             policy = "Rand (Fatigue Prevention)"
#         else:
#             # KNN/Max Policy: Pick the statistically closest/best donor
#             scored_donors.sort(key=lambda x: x['score'], reverse=True)
#             selected = scored_donors[0]
#             policy = f"KNN/Max Optimized"

#         matched_donors.append({
#             "id": selected['donor'].id,
#             "name": selected['donor'].get_full_name() or selected['donor'].email,
#             "city": selected['donor'].city or "Unknown",
#             "score": round(selected['score'] * 100),
#             "match_policy": policy
#         })
#         scored_donors.remove(selected)

#     return matched_donors



import os
import re
import random
import joblib
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.db.models import Count, Q, Max, Min
from .models import User, Donation

# -----------------------------------------------------------------------------
# 1. MACHINE LEARNING MODEL INITIALIZATION
# -----------------------------------------------------------------------------
MODEL_PATH = os.path.join(settings.BASE_DIR, 'donor_prediction_model.pkl')
try:
    ml_model = joblib.load(MODEL_PATH)
except Exception as e:
    print(f"Warning: Could not load ML model from {MODEL_PATH}. Error: {e}")
    ml_model = None


# -----------------------------------------------------------------------------
# 2. CLINICAL CONSTANTS & HELPERS
# -----------------------------------------------------------------------------
# Clinical Blood Compatibility Chart (Recipient -> Compatible Donors)
COMPATIBILITY = {
    'O-': ['O-'],
    'O+': ['O+', 'O-'],
    'A-': ['A-', 'O-'],
    'A+': ['A+', 'A-', 'O+', 'O-'],
    'B-': ['B-', 'O-'],
    'B+': ['B+', 'B-', 'O+', 'O-'],
    'AB-': ['AB-', 'A-', 'B-', 'O-'],
    'AB+': ['AB+', 'AB-', 'A+', 'A-', 'B+', 'B-', 'O+', 'O-'],
}

def extract_request_info(details_str):
    """Parses the frontend details string to extract clinical data."""
    if not details_str:
        return {'blood_type': None, 'is_emergency': False}
        
    blood_match = re.search(r"Blood Type:\s*([A-Z]{1,2}[+-])", details_str, re.IGNORECASE)
    urgency_match = re.search(r"Urgency:\s*([a-zA-Z]+)", details_str, re.IGNORECASE)
    
    return {
        'blood_type': blood_match.group(1).upper() if blood_match else None,
        'is_emergency': urgency_match.group(1).lower() == 'emergency' if urgency_match else False
    }

def calculate_months_between(date1, date2):
    """Helper to calculate months between two dates for RFMT features."""
    if not date1 or not date2:
        return 0
    return (date1.year - date2.year) * 12 + (date1.month - date2.month)


# -----------------------------------------------------------------------------
# 3. CORE ALGORITHM
# -----------------------------------------------------------------------------
def knn_randmax_hybrid_matching(application, gamma=0.3, k_donors=4):
    """
    PEAK ALGORITHM (ML-ENHANCED): 
    Combines Random Forest Predictions, K-Nearest Neighbors (KNN) for 
    clinical/geospatial precision, and RandMax Policy for donor fatigue management.
    """
    # 1. Parse Request Data
    req_info = extract_request_info(application.details)
    req_blood = req_info.get('blood_type')
    is_emergency = req_info.get('is_emergency')

    # 2. Hard Constraints (56-Day Deferral Rule)
    now = timezone.now()
    current_date = now.date()
    cutoff_date = current_date - timedelta(days=56)
    
    recent_donors = Donation.objects.filter(
        status='completed', 
        donation_date__gte=cutoff_date
    ).values_list('donor_id', flat=True)

    # Base query: Active donors + Annotate their RFMT data in one DB query!
    eligible_donors = User.objects.filter(
        role='donor', 
        is_active=True
    ).exclude(id__in=recent_donors).annotate(
        # RFMT Features gathered directly from SQL
        frequency=Count('donations', filter=Q(donations__status='completed')),
        last_donation_date=Max('donations__donation_date', filter=Q(donations__status='completed')),
        first_donation_date=Min('donations__donation_date', filter=Q(donations__status='completed'))
    )

    scored_donors = []
    request_city = application.user.city

    # 3. Scoring Phase
    for donor in eligible_donors:
        # Infer donor's blood type from their past donations
        past_donation = Donation.objects.filter(donor=donor).first()
        inferred_blood_type = past_donation.blood_group if past_donation else getattr(donor, 'blood_group', None)

        # STRICT CLINICAL FILTER: Ensure compatibility
        if req_blood and inferred_blood_type:
            if inferred_blood_type not in COMPATIBILITY.get(req_blood, []):
                continue # Incompatible! Skip this donor entirely.
            # Only apply the strict skip block for compatible types check
            elif inferred_blood_type not in COMPATIBILITY.get(req_blood, []):
                pass # Already handled above, just keeping logic clear

        score = 0.0
        
        # Feature 1: Spatial/Distance Weight (City Match)
        if request_city and donor.city and request_city.lower() == donor.city.lower():
            score += 0.50  # Exact location match is heavily weighted
        
        # Feature 2: Historical Reliability (Heuristic weight)
        reliability = min(donor.frequency * 0.1, 0.3)
        score += reliability

        # Feature 3: Urgency Adaptation
        days_on_platform = (now - donor.date_joined).days
        if is_emergency:
            if days_on_platform < 90:
                score += 0.20
        else:
            if days_on_platform > 180:
                score += 0.20

        # Feature 4: Machine Learning Predictor (RFMT Integration)
        if ml_model:
            # Calculate dynamic RFMT data
            time_joined_months = calculate_months_between(current_date, donor.date_joined.date())
            
            # Recency: Months since last donation (fallback to time since joined)
            if donor.last_donation_date:
                recency = calculate_months_between(current_date, donor.last_donation_date)
            else:
                recency = time_joined_months
                
            # Time: Months since first donation (fallback to time since joined)
            if donor.first_donation_date:
                time_feat = calculate_months_between(current_date, donor.first_donation_date)
            else:
                time_feat = time_joined_months

            # Frequency & Monetary (The dataset uses freq * 250cc typically)
            frequency = donor.frequency
            monetary = frequency * 250
            
            # Format exactly as model expects: [[Recency, Frequency, Monetary, Time]]
            features = [[recency, frequency, monetary, time_feat]]
            
            # predict_proba returns [[prob_0, prob_1]]. We extract the likelihood of donating
            ml_prob = ml_model.predict_proba(features)[0][1]
            
            # Weigh the ML probability (contributes heavily to the final score)
            score += (ml_prob * 0.40)
        else:
            # Baseline addition if ML isn't running so scores don't skew
            score += 0.20

        # Feature 5: Universal Donor Bonus
        if inferred_blood_type == 'O-':
            score += 0.10

        scored_donors.append({'donor': donor, 'score': score})

    # 4. RandMax Selection Phase
    matched_donors = []
    
    while len(matched_donors) < k_donors and scored_donors:
        # Flip a weighted coin using Gamma (e.g., 30% chance for random exploration)
        if random.random() < gamma:
            selected = random.choice(scored_donors)
            policy = "Rand (Fatigue Prevention)"
        else:
            # KNN/Max/ML Policy: Pick the statistically closest/best donor
            scored_donors.sort(key=lambda x: x['score'], reverse=True)
            selected = scored_donors[0]
            policy = "KNN/ML Optimized"

        matched_donors.append({
            "id": selected['donor'].id,
            "name": selected['donor'].get_full_name() or selected['donor'].email,
            "city": selected['donor'].city or "Unknown",
            "score": round(selected['score'] * 100),
            "match_policy": policy
        })
        scored_donors.remove(selected)

    return matched_donors