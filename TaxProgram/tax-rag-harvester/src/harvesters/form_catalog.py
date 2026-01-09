"""
IRS Form Catalog

Contains metadata about IRS forms, schedules, and publications
for intelligent harvesting and categorization.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class FormInfo:
    """Information about an IRS form."""
    form_id: str
    title: str
    category: str
    description: str
    related_forms: list[str]
    related_pubs: list[str]
    schedules: list[str]
    priority: int = 5  # 1-10, higher = more important


# Core individual tax forms
INDIVIDUAL_FORMS = {
    "1040": FormInfo(
        form_id="1040",
        title="U.S. Individual Income Tax Return",
        category="individual",
        description="Main form for individual federal income tax returns",
        related_forms=["W-2", "1099-INT", "1099-DIV", "1099-G"],
        related_pubs=["17", "501"],
        schedules=["1", "2", "3", "A", "B", "C", "D", "E", "SE"],
        priority=10
    ),
    "1040sr": FormInfo(
        form_id="1040sr",
        title="U.S. Tax Return for Seniors",
        category="individual",
        description="Simplified form for taxpayers 65 and older",
        related_forms=["1040"],
        related_pubs=["17", "554"],
        schedules=["1", "2", "3"],
        priority=7
    ),
}

# Schedules (attached to 1040)
SCHEDULES = {
    "1040sa": FormInfo(
        form_id="1040sa",
        title="Schedule A - Itemized Deductions",
        category="schedule",
        description="Itemized deductions including medical, taxes, interest, charity",
        related_forms=["1040"],
        related_pubs=["17", "502", "526", "936"],
        schedules=[],
        priority=9
    ),
    "1040sb": FormInfo(
        form_id="1040sb",
        title="Schedule B - Interest and Ordinary Dividends",
        category="schedule",
        description="Report interest and dividends over $1,500",
        related_forms=["1040", "1099-INT", "1099-DIV"],
        related_pubs=["17", "550"],
        schedules=[],
        priority=8
    ),
    "1040sc": FormInfo(
        form_id="1040sc",
        title="Schedule C - Profit or Loss From Business",
        category="schedule",
        description="Report income/expenses from sole proprietorship",
        related_forms=["1040", "1099-NEC", "1099-MISC"],
        related_pubs=["334", "535", "587"],
        schedules=["SE"],
        priority=9
    ),
    "1040sd": FormInfo(
        form_id="1040sd",
        title="Schedule D - Capital Gains and Losses",
        category="schedule",
        description="Report sales of stocks, bonds, real estate",
        related_forms=["1040", "8949", "1099-B"],
        related_pubs=["544", "550"],
        schedules=[],
        priority=8
    ),
    "1040se": FormInfo(
        form_id="1040se",
        title="Schedule E - Supplemental Income and Loss",
        category="schedule",
        description="Rental real estate, royalties, partnerships, S corps",
        related_forms=["1040", "K-1"],
        related_pubs=["527", "925"],
        schedules=[],
        priority=7
    ),
    "1040sse": FormInfo(
        form_id="1040sse",
        title="Schedule SE - Self-Employment Tax",
        category="schedule",
        description="Calculate Social Security and Medicare tax for self-employed",
        related_forms=["1040", "1040sc"],
        related_pubs=["334", "505"],
        schedules=[],
        priority=8
    ),
}

# Healthcare forms
HEALTHCARE_FORMS = {
    "8889": FormInfo(
        form_id="8889",
        title="Health Savings Accounts (HSAs)",
        category="healthcare",
        description="Report HSA contributions, distributions, and deductions",
        related_forms=["1040", "1099-SA", "5498-SA"],
        related_pubs=["969"],
        schedules=[],
        priority=8
    ),
    "8962": FormInfo(
        form_id="8962",
        title="Premium Tax Credit",
        category="healthcare",
        description="Calculate premium tax credit for marketplace insurance",
        related_forms=["1040", "1095-A"],
        related_pubs=["974"],
        schedules=[],
        priority=6
    ),
}

# Retirement forms
RETIREMENT_FORMS = {
    "8606": FormInfo(
        form_id="8606",
        title="Nondeductible IRAs",
        category="retirement",
        description="Track nondeductible IRA contributions and conversions",
        related_forms=["1040", "1099-R"],
        related_pubs=["590a", "590b"],
        schedules=[],
        priority=7
    ),
    "5329": FormInfo(
        form_id="5329",
        title="Additional Taxes on Qualified Plans",
        category="retirement",
        description="Early distribution penalties, excess contributions",
        related_forms=["1040", "1099-R"],
        related_pubs=["590a", "590b", "575"],
        schedules=[],
        priority=6
    ),
}

# Credit forms
CREDIT_FORMS = {
    "8863": FormInfo(
        form_id="8863",
        title="Education Credits",
        category="credits",
        description="American Opportunity and Lifetime Learning Credits",
        related_forms=["1040", "1098-T"],
        related_pubs=["970"],
        schedules=[],
        priority=7
    ),
    "2441": FormInfo(
        form_id="2441",
        title="Child and Dependent Care Expenses",
        category="credits",
        description="Credit for child care while working",
        related_forms=["1040"],
        related_pubs=["503"],
        schedules=[],
        priority=7
    ),
    "5695": FormInfo(
        form_id="5695",
        title="Residential Energy Credits",
        category="credits",
        description="Credits for solar, energy efficiency improvements",
        related_forms=["1040"],
        related_pubs=["17"],
        schedules=[],
        priority=6
    ),
    "8812": FormInfo(
        form_id="8812",
        title="Credits for Qualifying Children",
        category="credits",
        description="Child tax credit and additional child tax credit",
        related_forms=["1040"],
        related_pubs=["972"],
        schedules=[],
        priority=8
    ),
}

# Key publications
PUBLICATIONS = {
    "17": {
        "title": "Your Federal Income Tax",
        "description": "Comprehensive guide for individual taxpayers",
        "category": "general",
        "priority": 10
    },
    "501": {
        "title": "Dependents, Standard Deduction, and Filing Information",
        "description": "Who qualifies as dependent, filing requirements",
        "category": "general",
        "priority": 9
    },
    "502": {
        "title": "Medical and Dental Expenses",
        "description": "What medical expenses are deductible",
        "category": "deductions",
        "priority": 7
    },
    "503": {
        "title": "Child and Dependent Care Expenses",
        "description": "Credit for child care expenses",
        "category": "credits",
        "priority": 7
    },
    "505": {
        "title": "Tax Withholding and Estimated Tax",
        "description": "How to adjust withholding and pay estimated taxes",
        "category": "general",
        "priority": 7
    },
    "525": {
        "title": "Taxable and Nontaxable Income",
        "description": "What income is taxable",
        "category": "income",
        "priority": 8
    },
    "526": {
        "title": "Charitable Contributions",
        "description": "Deducting donations to charity",
        "category": "deductions",
        "priority": 7
    },
    "527": {
        "title": "Residential Rental Property",
        "description": "Tax rules for rental income and expenses",
        "category": "income",
        "priority": 6
    },
    "334": {
        "title": "Tax Guide for Small Business",
        "description": "Tax info for sole proprietors and small businesses",
        "category": "business",
        "priority": 8
    },
    "535": {
        "title": "Business Expenses",
        "description": "What business expenses are deductible",
        "category": "business",
        "priority": 7
    },
    "550": {
        "title": "Investment Income and Expenses",
        "description": "Tax treatment of investment income",
        "category": "investments",
        "priority": 7
    },
    "587": {
        "title": "Business Use of Your Home",
        "description": "Home office deduction rules",
        "category": "business",
        "priority": 7
    },
    "590a": {
        "title": "Contributions to IRAs",
        "description": "IRA contribution rules and deductions",
        "category": "retirement",
        "priority": 8
    },
    "590b": {
        "title": "Distributions from IRAs",
        "description": "IRA distribution rules and taxation",
        "category": "retirement",
        "priority": 8
    },
    "969": {
        "title": "HSAs and Other Tax-Favored Health Plans",
        "description": "Health Savings Account rules",
        "category": "healthcare",
        "priority": 8
    },
    "970": {
        "title": "Tax Benefits for Education",
        "description": "Education credits and deductions",
        "category": "credits",
        "priority": 7
    },
}


def get_all_forms() -> dict:
    """Get all form definitions."""
    all_forms = {}
    all_forms.update(INDIVIDUAL_FORMS)
    all_forms.update(SCHEDULES)
    all_forms.update(HEALTHCARE_FORMS)
    all_forms.update(RETIREMENT_FORMS)
    all_forms.update(CREDIT_FORMS)
    return all_forms


def get_forms_by_priority(min_priority: int = 7) -> list[str]:
    """Get form IDs above a certain priority."""
    all_forms = get_all_forms()
    return [
        f.form_id for f in all_forms.values() 
        if f.priority >= min_priority
    ]


def get_related_forms(form_id: str) -> list[str]:
    """Get all forms related to a given form."""
    all_forms = get_all_forms()
    
    if form_id not in all_forms:
        return []
    
    form = all_forms[form_id]
    related = set(form.related_forms)
    related.update(f"1040s{s.lower()}" for s in form.schedules)
    
    return list(related)


def get_publications_for_topic(topic: str) -> list[str]:
    """Get publications relevant to a topic."""
    return [
        pub_id for pub_id, info in PUBLICATIONS.items()
        if topic.lower() in info['category'].lower() or 
           topic.lower() in info['description'].lower()
    ]
