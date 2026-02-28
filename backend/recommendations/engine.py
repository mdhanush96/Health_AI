"""
Personalized health recommendation engine.
Maps symptom categories to diet, exercise, lifestyle, OTC medications, and specialist recommendations.
"""
from typing import Dict, List

# Recommendation database keyed by symptom category
RECOMMENDATIONS_DB = {
    'cardiovascular': {
        'diet': [
            'Low sodium diet (< 2300mg/day)',
            'High fiber foods (oats, legumes, whole grains)',
            'Omega-3 rich foods (fatty fish, flaxseed)',
            'Avoid saturated and trans fats',
            'Limit processed foods and red meat',
            'Increase fruits and vegetables',
            'Mediterranean diet pattern',
        ],
        'exercise': [
            '30 minutes of moderate aerobic exercise daily',
            'Brisk walking 5 days per week',
            'Cycling or swimming for low-impact cardio',
            'Avoid intense exercise without medical clearance',
            'Yoga or tai chi for stress reduction',
        ],
        'lifestyle': [
            'Quit smoking immediately',
            'Limit alcohol to 1-2 drinks per day',
            'Monitor blood pressure daily',
            'Manage stress with relaxation techniques',
            'Maintain healthy weight (BMI 18.5–24.9)',
            'Get 7–9 hours of sleep nightly',
        ],
        'medicines': [
            'Aspirin (81mg) - consult doctor',
            'Statins for elevated cholesterol (prescription)',
            'ACE inhibitors for hypertension (prescription)',
            'Nitroglycerin for angina (prescription)',
        ],
        'specialist': 'Cardiologist',
    },
    'respiratory': {
        'diet': [
            'Anti-inflammatory foods (berries, turmeric, ginger)',
            'Warm fluids (herbal tea, warm water with honey)',
            'Avoid dairy if mucus production increases',
            'Vitamin C rich foods (citrus, bell peppers)',
            'Adequate hydration (8-10 glasses water/day)',
        ],
        'exercise': [
            'Breathing exercises (diaphragmatic breathing)',
            'Pursed lip breathing for COPD',
            'Light walking in clean air environments',
            'Avoid exercise during acute episodes',
            'Pulmonary rehabilitation program (if prescribed)',
        ],
        'lifestyle': [
            'Avoid smoking and secondhand smoke',
            'Use air purifiers at home',
            'Avoid allergens and triggers',
            'Monitor peak flow daily (for asthma)',
            'Stay up to date on flu and pneumonia vaccines',
            'Maintain home humidity at 30–50%',
        ],
        'medicines': [
            'Salbutamol inhaler for acute asthma (prescription)',
            'Steam inhalation for congestion',
            'OTC decongestants for mild symptoms',
            'Antihistamines for allergic rhinitis',
        ],
        'specialist': 'Pulmonologist',
    },
    'neurological': {
        'diet': [
            'Brain-healthy foods (blueberries, walnuts, salmon)',
            'Magnesium-rich foods (spinach, nuts, seeds)',
            'Limit caffeine and alcohol',
            'Stay well hydrated',
            'Avoid skipping meals (hypoglycemia can worsen symptoms)',
        ],
        'exercise': [
            'Regular aerobic exercise (improves cerebral blood flow)',
            'Yoga and meditation for stress-related headaches',
            'Neck stretches for tension headaches',
            'Balance exercises for vertigo',
            'Avoid overexertion',
        ],
        'lifestyle': [
            'Maintain consistent sleep schedule',
            'Manage stress with CBT or mindfulness',
            'Avoid bright lights and loud sounds during migraine',
            'Keep a headache diary to identify triggers',
            'Limit screen time and take regular breaks',
        ],
        'medicines': [
            'Acetaminophen or ibuprofen for mild headaches',
            'Sumatriptan for migraines (prescription)',
            'Anti-vertigo medications (prescription)',
            'Avoid overuse of analgesics (rebound headache risk)',
        ],
        'specialist': 'Neurologist',
    },
    'gastrointestinal': {
        'diet': [
            'High fiber diet for constipation',
            'Bland BRAT diet (bananas, rice, applesauce, toast) for diarrhea',
            'Avoid trigger foods (spicy, fatty, acidic)',
            'Small, frequent meals',
            'Probiotics (yogurt, kefir, fermented foods)',
            'Avoid carbonated beverages',
        ],
        'exercise': [
            'Light walking after meals',
            '30 minutes moderate exercise daily',
            'Avoid high-impact exercise with active symptoms',
            'Abdominal strengthening exercises',
        ],
        'lifestyle': [
            'Eat slowly and chew thoroughly',
            'Avoid lying down after meals',
            'Elevate head of bed for GERD',
            'Reduce stress (gut-brain axis)',
            'Limit NSAIDs use',
            'Maintain healthy weight',
        ],
        'medicines': [
            'Antacids (calcium carbonate) for heartburn',
            'H2 blockers or PPIs for GERD (prescription)',
            'OTC anti-diarrheal (loperamide)',
            'Fiber supplements for constipation',
        ],
        'specialist': 'Gastroenterologist',
    },
    'musculoskeletal': {
        'diet': [
            'Calcium-rich foods (dairy, leafy greens, fortified foods)',
            'Vitamin D from sunlight and supplements',
            'Anti-inflammatory foods (turmeric, ginger, omega-3)',
            'Adequate protein for muscle repair',
            'Collagen-boosting foods (bone broth, citrus)',
        ],
        'exercise': [
            'Low-impact exercise (swimming, cycling)',
            'Stretching and flexibility exercises',
            'Strengthening exercises for supporting muscles',
            'Physical therapy as directed',
            'RICE protocol (Rest, Ice, Compression, Elevation) for acute injuries',
        ],
        'lifestyle': [
            'Maintain healthy weight to reduce joint stress',
            'Ergonomic workstation setup',
            'Avoid prolonged sitting or standing',
            'Use proper lifting techniques',
            'Apply heat/ice therapy',
        ],
        'medicines': [
            'NSAIDs (ibuprofen, naproxen) for pain and inflammation',
            'Topical analgesics (diclofenac gel)',
            'Acetaminophen for pain relief',
            'Glucosamine/chondroitin supplements',
        ],
        'specialist': 'Orthopedist / Rheumatologist',
    },
    'endocrine': {
        'diet': [
            'Low glycemic index foods',
            'Limit refined carbohydrates and sugars',
            'High fiber diet',
            'Lean proteins and healthy fats',
            'Iodine-rich foods for thyroid health (seafood, dairy)',
            'Chromium-rich foods (broccoli, whole grains)',
        ],
        'exercise': [
            '150 minutes moderate aerobic exercise per week',
            'Resistance training 2-3 times per week',
            'Exercise after meals to regulate blood sugar',
            'Monitor blood glucose before/after exercise (diabetes)',
        ],
        'lifestyle': [
            'Monitor blood glucose regularly',
            'Take medications as prescribed',
            'Foot care for diabetics',
            'Regular HbA1c testing (every 3 months for diabetes)',
            'Manage stress (cortisol affects blood sugar)',
            'Regular thyroid function tests',
        ],
        'medicines': [
            'Metformin for type 2 diabetes (prescription)',
            'Insulin therapy if required (prescription)',
            'Thyroid hormone replacement (prescription)',
            'Berberine supplement (natural blood sugar support)',
        ],
        'specialist': 'Endocrinologist',
    },
    'dermatological': {
        'diet': [
            'Antioxidant-rich foods (berries, dark leafy greens)',
            'Omega-3 fatty acids for skin health',
            'Avoid foods that trigger flare-ups',
            'Stay well hydrated',
            'Zinc-rich foods (pumpkin seeds, beef, chickpeas)',
        ],
        'exercise': [
            'Regular exercise improves circulation and skin health',
            'Shower immediately after exercise',
            'Avoid excessive heat if eczema/rosacea prone',
        ],
        'lifestyle': [
            'Use gentle, fragrance-free skin products',
            'Moisturize twice daily for dry skin/eczema',
            'Apply SPF 30+ sunscreen daily',
            'Avoid scratching affected areas',
            'Wear breathable, loose-fitting clothing',
            'Avoid known allergens',
        ],
        'medicines': [
            'Topical hydrocortisone for mild eczema/rash',
            'Oral antihistamines for allergic reactions',
            'Topical antifungals for fungal infections',
            'Calamine lotion for itching',
        ],
        'specialist': 'Dermatologist',
    },
    'infectious': {
        'diet': [
            'Increased fluid intake (water, broths, herbal teas)',
            'Vitamin C rich foods and supplements',
            'Zinc-rich foods for immune support',
            'Honey and ginger for throat soothing',
            'Avoid alcohol (immunosuppressive)',
        ],
        'exercise': [
            'Rest during acute illness',
            'Light walking only when fever-free for 24+ hours',
            'Gradual return to normal activity',
        ],
        'lifestyle': [
            'Adequate rest and sleep',
            'Isolate to prevent spreading infection',
            'Frequent hand washing',
            'Stay up to date on vaccinations',
            'Use N95 mask if respiratory symptoms',
        ],
        'medicines': [
            'Acetaminophen or ibuprofen for fever/pain',
            'Zinc lozenges for cold duration reduction',
            'OTC throat lozenges',
            'Saline nasal rinse for congestion',
            'Antibiotics if bacterial (prescription required)',
        ],
        'specialist': 'General Physician / Infectious Disease Specialist',
    },
    'psychiatric': {
        'diet': [
            'Omega-3 rich foods (salmon, walnuts)',
            'Tryptophan-rich foods (turkey, eggs, dairy)',
            'Magnesium-rich foods (dark chocolate, avocado)',
            'Limit caffeine and alcohol',
            'Stable blood sugar through regular meals',
        ],
        'exercise': [
            '30 minutes aerobic exercise 5 days/week',
            'Yoga and mindfulness movement',
            'Outdoor exercise for mood benefits',
            'Exercise with a partner for motivation',
        ],
        'lifestyle': [
            'Cognitive Behavioral Therapy (CBT)',
            'Mindfulness and meditation practice',
            'Regular sleep schedule',
            'Social support and connection',
            'Journaling for emotional processing',
            'Limit social media and news exposure',
            'Crisis hotline: 988 (US Suicide & Crisis Lifeline)',
        ],
        'medicines': [
            'SSRIs/SNRIs for depression/anxiety (prescription)',
            'Melatonin for sleep (OTC, low dose)',
            'Magnesium glycinate for anxiety (supplement)',
            'St. Johns Wort (consult doctor - drug interactions)',
        ],
        'specialist': 'Psychiatrist / Psychologist',
    },
    'general': {
        'diet': [
            'Balanced diet with all food groups',
            'Plenty of fruits and vegetables (5-9 servings/day)',
            'Adequate protein intake',
            'Limit processed foods and added sugars',
            'Stay well hydrated',
        ],
        'exercise': [
            '150 minutes moderate exercise per week',
            '75 minutes vigorous exercise per week',
            'Strength training 2 days per week',
            'Reduce sedentary time',
        ],
        'lifestyle': [
            'Get 7-9 hours of sleep per night',
            'Manage stress effectively',
            'Regular health check-ups',
            'Avoid tobacco and limit alcohol',
            'Stay socially connected',
        ],
        'medicines': [
            'Multivitamin supplement',
            'Vitamin D (if deficient)',
            'Consult a doctor for specific medications',
        ],
        'specialist': 'General Physician',
    },
}


def get_recommendations(symptom_category: str, risk_level: str) -> Dict:
    """
    Get personalized recommendations based on symptom category and risk level.
    """
    recs = RECOMMENDATIONS_DB.get(symptom_category, RECOMMENDATIONS_DB['general'])

    # Add urgent note for critical/high risk
    notes = ''
    if risk_level == 'CRITICAL':
        notes = (
            '⚠️ URGENT: Your symptoms may indicate a medical emergency. '
            'Call 911 or go to the nearest emergency room immediately.'
        )
    elif risk_level == 'HIGH':
        notes = (
            '⚠️ HIGH PRIORITY: Please consult a doctor within 24–48 hours. '
            'Do not delay seeking medical attention.'
        )

    return {
        'diet': recs['diet'],
        'exercise': recs['exercise'],
        'lifestyle': recs['lifestyle'],
        'medicines': recs['medicines'],
        'specialist': recs['specialist'],
        'notes': notes,
    }
