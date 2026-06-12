
import json
import random
import csv

random.seed(42)
SECTORS = ["IT Services", "Construction", "Logistics", "Healthcare IT",
           "Telecom", "Education", "Energy", "Public Sector"]

CERT_POOL = ["ISO 9001", "ISO 27001", "ISO 14001", "CMMI Level 3",
              "PMP Certified Team", "PEC Registered", "OHSAS 18001",
              "Microsoft Gold Partner", "AWS Advanced Tier Partner"]

CLIENT_TYPES = ["Government", "Private Enterprise", "NGO / Donor-funded",
                "Multinational Corporation", "SME"]

PROJECT_TEMPLATES = [
    ("Enterprise ERP Implementation", "IT Services",
     "Designed and deployed a cloud-based ERP covering finance, HR and procurement modules for a {client} client, including data migration and staff training."),
    ("Network Infrastructure Upgrade", "IT Services",
     "Upgraded core network infrastructure including routers, switches and a redundant fibre backbone across {n} regional offices for a {client} client."),
    ("Custom Web Portal Development", "IT Services",
     "Built a citizen/customer-facing web portal with role-based access, payment gateway integration and analytics dashboard for a {client} client."),
    ("Highway Rehabilitation Project", "Construction",
     "Executed rehabilitation of a {n} km highway segment including asphalt overlay, drainage works and road safety signage for a {client} client."),
    ("Commercial Building Construction", "Construction",
     "Delivered turnkey construction of a {n}-storey commercial building including civil works, electromechanical fit-out and HVAC for a {client} client."),
    ("Water Supply Scheme", "Construction",
     "Constructed a water supply scheme covering {n} households including overhead tanks, distribution network and filtration plant for a {client} client."),
    ("Fleet Management & Logistics Optimization", "Logistics",
     "Implemented a fleet tracking and route optimization system covering {n} vehicles, reducing fuel costs and delivery times for a {client} client."),
    ("Warehouse Automation Rollout", "Logistics",
     "Rolled out barcode-based inventory and warehouse management automation across {n} warehouses for a {client} client."),
    ("Last-Mile Delivery Network Setup", "Logistics",
     "Established a last-mile delivery network covering {n} cities including hub setup and rider onboarding for a {client} client."),
    ("Hospital Information System Deployment", "Healthcare IT",
     "Deployed an integrated Hospital Information System (HIS) including EMR, lab and pharmacy modules across {n} facilities for a {client} client."),
    ("Telemedicine Platform Development", "Healthcare IT",
     "Developed a telemedicine platform supporting video consultations and e-prescriptions, scaled to {n} registered doctors for a {client} client."),
    ("4G/LTE Network Rollout Support", "Telecom",
     "Provided site acquisition, civil works and equipment installation support for a {n}-site 4G/LTE rollout for a {client} client."),
    ("OSS/BSS Integration", "Telecom",
     "Integrated OSS/BSS systems enabling automated billing and provisioning for {n} subscribers for a {client} client."),
    ("Learning Management System Rollout", "Education",
     "Implemented a Learning Management System (LMS) for {n} institutions including content migration and faculty training for a {client} client."),
    ("School Digitization Programme", "Education",
     "Digitized administrative and academic records for {n} schools, including biometric attendance and a parent-facing mobile app for a {client} client."),
    ("Solar Power Plant Installation", "Energy",
     "Installed a {n} MW solar power plant including grid synchronization and a 12-month O&M contract for a {client} client."),
    ("Energy Audit & Efficiency Programme", "Energy",
     "Conducted an energy audit across {n} facilities and implemented efficiency retrofits reducing consumption for a {client} client."),
    ("Digital Tax Collection System", "Public Sector",
     "Built a digital tax assessment and collection system covering {n} municipal units, including online payment integration for a {client} client."),
    ("Citizen Grievance Redressal Portal", "Public Sector",
     "Developed an online grievance redressal and case-tracking portal handling over {n} cases annually for a {client} client."),
    ("Cybersecurity Assessment & Hardening", "IT Services",
     "Performed a cybersecurity risk assessment and hardened infrastructure for {n} critical systems, aligned with ISO 27001 for a {client} client."),
]

capability_library = []
for i in range(50):
    template = PROJECT_TEMPLATES[i % len(PROJECT_TEMPLATES)]
    title, sector, desc_template = template
    n = random.choice([3, 5, 8, 10, 12, 15, 20, 25, 30, 50])
    client_type = random.choice(CLIENT_TYPES)
    desc = desc_template.format(n=n, client=client_type)
    year = random.choice([2019, 2020, 2021, 2022, 2023, 2024, 2025])
    contract_value_pkr = random.choice(
        [5_000_000, 12_000_000, 25_000_000, 40_000_000, 75_000_000,
         120_000_000, 250_000_000, 500_000_000, 800_000_000]
    )
    duration_months = random.choice([2, 3, 4, 6, 9, 12, 18, 24])
    certs = random.sample(CERT_POOL, k=random.choice([1, 2, 3]))
    capability_library.append({
        "id": f"CAP-{i+1:03d}",
        "title": f"{title} #{i+1}",
        "sector": sector,
        "description": desc,
        "certifications": certs,
        "year_completed": year,
        "contract_value_pkr": contract_value_pkr,
        "duration_months": duration_months,
        "client_type": client_type,
        "tags": [sector.lower(), client_type.lower()] + [c.lower() for c in certs],
    })

with open("capability_library.json", "w", encoding="utf-8") as f:
    json.dump(capability_library, f, indent=2, ensure_ascii=False)

eval_criteria_taxonomy = [
    {"criterion": "Technical Methodology", "sector": "IT Services", "typical_weight_pct": 30,
     "description": "Soundness and clarity of the proposed technical approach."},
    {"criterion": "Team Experience & CVs", "sector": "All", "typical_weight_pct": 15,
     "description": "Relevant qualifications and past experience of key personnel."},
    {"criterion": "Past Performance / Track Record", "sector": "All", "typical_weight_pct": 15,
     "description": "Evidence of successfully delivered similar projects."},
    {"criterion": "Financial Proposal / Cost", "sector": "All", "typical_weight_pct": 30,
     "description": "Competitiveness and realism of the price quoted."},
    {"criterion": "Compliance with Specifications", "sector": "Construction", "typical_weight_pct": 25,
     "description": "Adherence to technical specifications and standards (e.g. PEC)."},
    {"criterion": "Project Management Plan", "sector": "All", "typical_weight_pct": 10,
     "description": "Quality of work plan, schedule, and risk management approach."},
    {"criterion": "Local Presence / Resources", "sector": "Logistics", "typical_weight_pct": 10,
     "description": "Availability of local offices, fleet, or warehousing."},
    {"criterion": "Certifications & Quality Standards", "sector": "All", "typical_weight_pct": 10,
     "description": "Possession of relevant ISO / industry certifications."},
    {"criterion": "Sustainability / HSE Plan", "sector": "Construction", "typical_weight_pct": 10,
     "description": "Health, safety, environment, and sustainability commitments."},
    {"criterion": "Innovation / Value-add", "sector": "IT Services", "typical_weight_pct": 10,
     "description": "Additional value, automation, or innovation beyond minimum scope."},
    {"criterion": "Data Security & Privacy", "sector": "Healthcare IT", "typical_weight_pct": 15,
     "description": "Approach to securing sensitive data and regulatory compliance."},
    {"criterion": "Scalability", "sector": "Telecom", "typical_weight_pct": 10,
     "description": "Ability of the proposed solution to scale with future demand."},
    {"criterion": "Training & Knowledge Transfer", "sector": "Education", "typical_weight_pct": 10,
     "description": "Plan for transferring skills and knowledge to client staff."},
    {"criterion": "Maintenance & Support (SLA)", "sector": "IT Services", "typical_weight_pct": 10,
     "description": "Quality and responsiveness of post-deployment support commitments."},
    {"criterion": "Local Content / SME Participation", "sector": "Public Sector", "typical_weight_pct": 10,
     "description": "Extent of local sourcing, employment or SME sub-contracting."},
]

with open("eval_criteria_taxonomy.json", "w", encoding="utf-8") as f:
    json.dump(eval_criteria_taxonomy, f, indent=2, ensure_ascii=False)

columns = [
    "bid_id", "sector", "client_type", "region", "contract_value_pkr",
    "our_bid_value_pkr", "estimated_competitor_count", "past_relationship",
    "certifications_match_pct", "requirements_total", "requirements_matched_pct",
    "compliance_gap_count", "submission_on_time", "budget_alignment_score",
    "technical_score_pct", "financial_score_pct", "evaluation_weight_technical_pct",
    "outcome"
]

REGIONS = ["Punjab", "Sindh", "KPK", "Balochistan", "Islamabad", "AJK"]

rows = []
for i in range(120):
    sector = random.choice(SECTORS)
    client_type = random.choice(CLIENT_TYPES)
    region = random.choice(REGIONS)
    contract_value = random.choice(
        [8_000_000, 20_000_000, 35_000_000, 60_000_000, 100_000_000,
         200_000_000, 350_000_000, 600_000_000]
    )
    bid_value = int(contract_value * random.uniform(0.85, 1.10))
    competitor_count = random.randint(2, 9)
    past_relationship = random.choice([0, 1])
    cert_match = random.randint(20, 100)
    req_total = random.randint(15, 80)
    req_matched_pct = random.randint(30, 100)
    gap_count = max(0, int(req_total * (100 - req_matched_pct) / 100))
    on_time = 1 if random.random() > 0.05 else 0
    budget_alignment = round(random.uniform(0.5, 1.0), 2)
    tech_score = random.randint(40, 100)
    fin_score = random.randint(40, 100)
    eval_weight_tech = random.choice([20, 30, 40, 50, 60, 70])

    score = (
        0.30 * (cert_match / 100) +
        0.30 * (req_matched_pct / 100) +
        0.15 * past_relationship +
        0.10 * budget_alignment +
        0.10 * (tech_score / 100) +
        0.05 * (1 - (competitor_count - 2) / 7)
    )
    score -= 0.05 * (gap_count / max(req_total, 1))
    if on_time == 0:
        score -= 0.25
    outcome = 1 if (score + random.uniform(-0.12, 0.12)) > 0.55 else 0

    rows.append([
        f"BID-{i+1:04d}", sector, client_type, region, contract_value, bid_value,
        competitor_count, past_relationship, cert_match, req_total, req_matched_pct,
        gap_count, on_time, budget_alignment, tech_score, fin_score,
        eval_weight_tech, "win" if outcome == 1 else "loss"
    ])

with open("historical_bids.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(columns)
    writer.writerows(rows)

print(f"Generated {len(capability_library)} capability records")
print(f"Generated {len(eval_criteria_taxonomy)} eval criteria entries")
print(f"Generated {len(rows)} historical bid rows x {len(columns)} cols")
