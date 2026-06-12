from docx import Document
from docx.shared import Pt

doc = Document()

doc.add_heading("Request for Proposal (RFP)", level=0)
doc.add_paragraph("RFP Reference No: PITB/IT-SVCS/2026/0147")
doc.add_paragraph("Issuing Authority: Provincial IT Board (PITB)")
doc.add_paragraph(
    "Subject: Design, Development, Deployment and Maintenance of an "
    "Integrated Case Management System (ICMS) for District Offices"
)

doc.add_heading("1. Introduction and Background", level=1)
doc.add_paragraph(
    "The Provincial IT Board (PITB) intends to engage a qualified firm "
    "(\"the Bidder\") for the design, development, deployment, and "
    "three-year maintenance of an Integrated Case Management System "
    "(ICMS) to be rolled out across 25 district offices. The system "
    "will digitize citizen case filing, tracking, and resolution "
    "workflows currently managed manually."
)

doc.add_heading("2. Submission Deadline and Key Dates", level=1)
doc.add_paragraph(
    "Bidders must submit both technical and financial proposals in "
    "separate sealed envelopes no later than 17:00 hours on "
    "25th August 2026. Proposals received after the deadline shall "
    "not be considered under any circumstances."
)
doc.add_paragraph(
    "A pre-bid query session will be held on 10th August 2026. "
    "Written clarification requests must be received by 5th August 2026."
)

doc.add_heading("3. Estimated Budget", level=1)
doc.add_paragraph(
    "The total estimated budget for this engagement, inclusive of "
    "development, deployment, and three years of maintenance, is "
    "PKR 180,000,000 (One Hundred Eighty Million Pakistani Rupees). "
    "Bids exceeding this ceiling by more than 10% may be declared "
    "non-responsive."
)

doc.add_heading("4. Mandatory Eligibility and Compliance Requirements", level=1)
mandatory = [
    "The Bidder must be registered with the Securities and Exchange "
    "Commission of Pakistan (SECP) for a minimum of five (5) years.",
    "The Bidder shall hold a valid ISO 9001 certification at the time "
    "of bid submission.",
    "The Bidder must hold a valid ISO 27001 certification covering "
    "information security management.",
    "The Bidder shall demonstrate at least three (3) completed projects "
    "of similar nature and scale (minimum contract value of PKR "
    "50,000,000 each) within the last five years.",
    "The Bidder must provide CVs of key personnel including a Project "
    "Manager (minimum PMP certified, 8 years experience) and a Lead "
    "Solution Architect (minimum 10 years experience).",
    "The proposed solution shall be web-based, accessible via modern "
    "browsers, and must support role-based access control (RBAC).",
    "The Bidder shall provide a disaster recovery (DR) site with a "
    "Recovery Time Objective (RTO) of not more than 4 hours.",
    "The system must support bilingual interfaces (English and Urdu).",
    "The Bidder must provide on-site technical support for a minimum "
    "of 12 months post go-live, with a Service Level Agreement (SLA) "
    "guaranteeing 99.5% uptime.",
    "The Bidder shall comply with the Provincial Data Protection "
    "Guidelines 2024 for all citizen data handled by the system.",
    "The Bidder must submit an affidavit confirming no conflict of "
    "interest with PITB officials.",
    "The proposed team shall include at least two (2) certified data "
    "security professionals (CISSP or equivalent).",
]
for item in mandatory:
    doc.add_paragraph(item, style="List Bullet")

doc.add_heading("5. Scope of Work", level=1)
scope_items = [
    "Requirements gathering workshops with PITB and district offices.",
    "Design and development of the ICMS web application and mobile-"
    "responsive citizen portal.",
    "Integration with the existing PITB Single Sign-On (SSO) system.",
    "Data migration from legacy spreadsheets used by district offices.",
    "User acceptance testing (UAT) and training for up to 500 government staff.",
    "Phased rollout across 25 district offices over 9 months.",
    "Three years of maintenance, bug-fixing, and minor enhancements.",
]
for item in scope_items:
    doc.add_paragraph(item, style="List Number")

doc.add_heading("6. Evaluation Criteria", level=1)
doc.add_paragraph(
    "Technical and financial proposals will be evaluated using the "
    "following weighted criteria. A minimum technical score of 70% "
    "is required to qualify for financial evaluation."
)
eval_table_text = [
    "Technical Methodology and Solution Architecture - 30%",
    "Team Experience and CVs of Key Personnel - 15%",
    "Past Performance and Track Record on Similar Projects - 15%",
    "Project Management Plan and Implementation Timeline - 10%",
    "Certifications and Quality Standards (ISO 9001 / ISO 27001) - 10%",
    "Data Security and Privacy Approach - 10%",
    "Innovation and Value-Added Services - 10%",
    "Financial Proposal - 30% (evaluated separately as per PPRA rules)",
]
for item in eval_table_text:
    doc.add_paragraph(item, style="List Bullet")

doc.add_heading("7. Questions and Answers Section", level=1)
doc.add_paragraph(
    "Q1: Describe your organization's experience in implementing "
    "similar case management or workflow automation systems for "
    "government clients in Pakistan."
)
doc.add_paragraph(
    "Q2: Provide details of your proposed technical architecture, "
    "including technology stack, hosting environment, and security "
    "measures to be implemented."
)
doc.add_paragraph(
    "Q3: Describe your approach to data migration from the existing "
    "manual / spreadsheet-based systems used by district offices, "
    "including data cleansing and validation steps."
)
doc.add_paragraph(
    "Q4: Detail your proposed training plan for government staff, "
    "including the number of sessions, training materials, and "
    "post-training support."
)
doc.add_paragraph(
    "Q5: Explain your maintenance and support model for the three-year "
    "post-deployment period, including your SLA commitments and "
    "escalation procedures."
)

doc.add_heading("8. Submission Instructions", level=1)
doc.add_paragraph(
    "Proposals must be submitted in three (3) hard copies and one (1) "
    "soft copy on USB drive, addressed to the Procurement Committee, "
    "Provincial IT Board, Lahore. Bids submitted via email will not "
    "be accepted."
)

doc.save("/home/claude/bidengine/sample_rfps/PITB_ICMS_RFP_2026.docx")
print("Sample RFP generated.")
