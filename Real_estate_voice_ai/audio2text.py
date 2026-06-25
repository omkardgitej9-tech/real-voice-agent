MASTER_CONTEXT = [

    # ========================
    # PROPERTIES
    # ========================

    {
        "type": "property",
        "id": "V001",
        "property_type": "villa",
        "bhk": 4,
        "price": "2.5 Crore",
        "location": "Andheri East, Mumbai",
        "area": "2500 sq.ft.",
        "furnishing": "semi-furnished",
        "parking": "2 covered",
        "flooring": "Italian marble",
        "age_of_property": "2 years",
        "rera_approved": True,
        "amenities": ["swimming pool", "private garden", "parking", "security", "home theater"],
        "description": "Luxurious 4BHK villa with modern amenities",
        "status": "ready to move"
    },

    {
        "type": "property",
        "id": "V002",
        "property_type": "villa",
        "bhk": 3,
        "price": "1.8 Crore",
        "location": "Powai, Mumbai",
        "area": "1800 sq.ft.",
        "furnishing": "fully furnished",
        "parking": "1 covered",
        "age_of_property": "1 year",
        "rera_approved": True,
        "amenities": ["garden", "parking", "club house", "gym"],
        "description": "Beautiful 3BHK villa in prime location",
        "status": "ready to move"
    },

    {
        "type": "property",
        "id": "F002",
        "property_type": "flat",
        "bhk": 3,
        "price": "1.45 Crore",
        "location": "Malad East, Mumbai",
        "area": "1200 sq.ft.",
        "floor": "12th floor",
        "total_floors": 22,
        "furnishing": "unfurnished",
        "rera_approved": True,
        "amenities": ["gym", "park", "security", "shopping center nearby"],
        "description": "Spacious 3BHK flat with excellent ventilation",
        "status": "ready to move"
    },

    {
        "type": "property",
        "id": "PH001",
        "property_type": "penthouse",
        "bhk": 4,
        "price": "5.5 Crore",
        "location": "Worli, Mumbai",
        "area": "3500 sq.ft.",
        "furnishing": "luxury furnished",
        "view": "sea view",
        "rera_approved": True,
        "amenities": ["private terrace", "jacuzzi", "panoramic view", "private elevator"],
        "description": "Luxury penthouse with 360-degree view",
        "status": "ready to move"
    },

    {
        "type": "property",
        "id": "LX001",
        "property_type": "sea-facing villa",
        "bhk": 6,
        "price": "12.5 Crore",
        "location": "Juhu, Mumbai",
        "area": "6500 sq.ft.",
        "land_area": "9000 sq.ft.",
        "private_security": True,
        "amenities": ["private beach access", "helipad", "infinity pool", "wine cellar"],
        "description": "Celebrity-style sea-facing mansion",
        "status": "ready to move"
    },

    {
        "type": "property",
        "id": "C001",
        "property_type": "commercial office",
        "price": "2.2 Crore",
        "location": "Bandra Kurla Complex, Mumbai",
        "area": "1500 sq.ft.",
        "furnishing": "fully furnished",
        "rental_yield": "6-8%",
        "status": "ready to move"
    },

    {
        "type": "property",
        "id": "UL001",
        "property_type": "under construction flat",
        "bhk": 2,
        "price": "1.05 Crore",
        "location": "Kharghar, Navi Mumbai",
        "area": "980 sq.ft.",
        "expected_possession": "Dec 2027",
        "pre_launch_offer": True,
        "rera_approved": True,
        "status": "under construction"
    },

    # ========================
    # COMPANY PROFILE
    # ========================

    {
        "type": "company_profile",
        "name": "Wifi Estates India",
        "established": 2005,
        "founder": "Shri Ram Lal Chaturvedi Bedi",
        "head_office": "Bandra Kurla Complex, Mumbai",
        "branch_offices": ["Andheri", "Powai", "Thane", "Navi Mumbai", "Pune"],
        "employees": 240,
        "certifications": ["RERA Registered", "ISO 9001:2015 Certified"],
        "total_deals_closed": "12,500+",
        "portfolio_value": "₹8,500 Crore",
        "customer_rating": "4.8/5",
        "vision": "To simplify property buying through transparency and technology.",
        "mission": "Deliver trusted advisory-driven real estate services."
    },

    # ========================
    # SERVICES
    # ========================

    {
        "type": "services",
        "home_buying": True,
        "home_selling": True,
        "rental_management": True,
        "property_valuation": True,
        "nri_services": True,
        "corporate_bulk_deals": True,
        "legal_documentation_support": True,
        "site_visit_arrangement": True,
        "virtual_tour_available": True,
        "after_sales_support": True
    },

    # ========================
    # LOAN & FINANCE
    # ========================

    {
        "type": "loan_info",
        "banks": [
            {"name": "SBI", "rate": "8.5%", "max_tenure": "30 years"},
            {"name": "HDFC", "rate": "8.65%", "max_tenure": "30 years"},
            {"name": "ICICI", "rate": "8.7%", "max_tenure": "30 years"},
            {"name": "Axis", "rate": "8.75%", "max_tenure": "30 years"}
        ],
        "max_loan_percentage": "80-90%",
        "processing_time": "7-10 working days",
        "emi_formula": "EMI = [P x R x (1+R)^N] / [(1+R)^N - 1]",
        "tax_benefits": ["Section 24(b)", "Section 80C"]
    },

    # ========================
    # INVESTMENT INSIGHTS
    # ========================

    {
        "type": "market_insights",
        "mumbai_growth_rate": "12-16% annually in premium zones",
        "best_for_rental_yield": ["Powai", "BKC", "Worli"],
        "best_for_long_term_appreciation": ["Juhu", "Bandra", "Worli"],
        "emerging_hotspots": [
            "Kharghar - 18% projected growth",
            "Kalyan - 15% projected growth",
            "Hinjewadi - 20% growth due to IT expansion"
        ]
    },

    # ========================
    # DISCOUNT & OFFERS
    # ========================

    {
        "type": "discount_policy",
        "ready_property_discount": "5-10%",
        "full_payment_discount": "2-3%",
        "festival_offers": {
            "Diwali": "5%",
            "New Year": "3%"
        },
        "corporate_discount_available": True,
        "referral_bonus": "₹50,000"
    },

    # ========================
    # CUSTOMER JOURNEY
    # ========================

    {
        "type": "sales_process",
        "steps": [
            "Requirement analysis",
            "Property shortlisting",
            "Site visit scheduling",
            "Price negotiation",
            "Loan assistance",
            "Legal verification",
            "Registration",
            "After-sales support"
        ]
    },

    # ========================
# LEGAL & COMPLIANCE
# ========================

{
    "type": "legal_compliance",
    "documents_required_buyer": [
        "PAN Card",
        "Aadhaar Card",
        "Address Proof",
        "Passport Size Photos",
        "Income Proof (ITR/Form 16)",
        "Bank Statements (6 months)"
    ],
    "documents_required_property": [
        "Sale Deed",
        "Title Deed",
        "Encumbrance Certificate",
        "Occupancy Certificate (OC)",
        "Completion Certificate (CC)",
        "RERA Registration Certificate"
    ],
    "stamp_duty_mumbai": "5-6% approx",
    "registration_charges": "1% of property value",
    "gst_under_construction": "5%",
    "capital_gains_tax_rules": "Applicable on resale as per holding period"
},

# ========================
# RENTAL SERVICES
# ========================

{
    "type": "rental_services",
    "tenant_verification": True,
    "rental_agreement_assistance": True,
    "property_management": True,
    "average_rental_yield_mumbai": "3-5%",
    "prime_rental_locations": ["Powai", "Worli", "BKC", "Andheri East"]
},

# ========================
# BUILDER PARTNERSHIPS
# ========================

{
    "type": "builder_partnerships",
    "top_builders": [
        "Lodha Group",
        "Hiranandani Developers",
        "Godrej Properties",
        "Runwal Group",
        "Kalpataru Group"
    ],
    "exclusive_inventory_available": True,
    "pre_launch_access": True,
    "bulk_deal_negotiation_power": "High"
},

# ========================
# INVESTMENT CALCULATIONS
# ========================

{
    "type": "investment_metrics",
    "roi_formula": "ROI = (Net Profit / Investment Cost) x 100",
    "rental_yield_formula": "Rental Yield = (Annual Rent / Property Price) x 100",
    "ideal_hold_period": "5-8 years for appreciation",
    "luxury_appreciation_zones": ["Worli", "Juhu", "Bandra"],
    "mid_segment_growth_zones": ["Powai", "Andheri", "Borivali"]
},

# ========================
# CUSTOMER TYPES
# ========================

{
    "type": "customer_profiles",
    "first_time_buyer": {
        "budget_range": "50L - 1.5 Cr",
        "priority": "EMI affordability, safety, schools nearby"
    },
    "investor": {
        "priority": "Rental yield, appreciation, resale value"
    },
    "luxury_buyer": {
        "budget_range": "5 Cr+",
        "priority": "Privacy, exclusivity, sea view, premium amenities"
    },
    "nri_buyer": {
        "priority": "Legal transparency, rental management, long-term appreciation"
    }
},

# ========================
# OBJECTION HANDLING
# ========================

{
    "type": "objection_handling",
    "price_high": "Explain appreciation potential and negotiation margin.",
    "need_time": "Offer price lock-in and limited inventory urgency.",
    "checking_other_options": "Highlight exclusive benefits and compare ROI.",
    "loan_confusion": "Provide EMI breakdown and bank tie-up support."
},

# ========================
# NEGOTIATION RULES
# ========================

{
    "type": "negotiation_policy",
    "max_discount_ready": "Up to 10%",
    "extra_discount_full_payment": "3%",
    "festival_stack_allowed": True,
    "corporate_bulk_discount": "Case to case",
    "minimum_margin_threshold": "5%"
},

# ========================
# SITE VISIT LOGIC
# ========================

{
    "type": "site_visit_process",
    "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    "time_slots": ["10 AM", "12 PM", "2 PM", "4 PM", "6 PM"],
    "pickup_service_available": True,
    "virtual_site_tour": True,
    "follow_up_within_hours": 24
},

# ========================
# INTERNAL SALES RULES
# ========================

{
    "type": "sales_intelligence",
    "hot_lead_definition": "Budget confirmed + site visit completed",
    "warm_lead_definition": "Budget discussed but no visit",
    "cold_lead_definition": "Just inquiry without commitment",
    "follow_up_frequency_hot": "Every 2 days",
    "follow_up_frequency_warm": "Weekly",
    "follow_up_frequency_cold": "Bi-weekly"
},

# ========================
# AFTER SALES SUPPORT
# ========================

{
    "type": "after_sales",
    "registration_assistance": True,
    "interior_design_support": True,
    "home_inspection_service": True,
    "resale_assistance": True,
    "rental_listing_support": True
},

# ========================
# BRAND POSITIONING
# ========================

{
    "type": "brand_identity",
    "tagline": "Turning Properties into Prosperity",
    "core_values": ["Transparency", "Trust", "Customer First", "Data-Driven Advice"],
    "unique_selling_point": "Advisory-based selling instead of aggressive sales",
    "average_closure_time": "21 days"
}

]