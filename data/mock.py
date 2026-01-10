"""
data/mock.py - Mock data for Justicia Ex Machina
"""

JUROR_PERSONAS = {
    "Marcus": {"occupation": "Construction Foreman"},
    "Elena": {"occupation": "High School Teacher"},
    "Raymond": {"occupation": "Retired Accountant"},
    "Destiny": {"occupation": "Emergency Room Nurse"},
    "Chen": {"occupation": "Software Engineer"},
    "Patricia": {"occupation": "Former Judge"},
}

MOCK_PLAINTIFF_MESSAGES = [
    {"agent_type": "plaintiff", "agent_name": "Plaintiff Counsel", "timestamp": "09:15:32",
     "content": "Your Honor, members of the jury, the evidence will show a clear pattern of negligence that resulted in catastrophic damages to my client."},
    {"agent_type": "plaintiff", "agent_name": "Plaintiff Counsel", "timestamp": "09:18:45",
     "content": "Exhibit A demonstrates that the defendant was explicitly warned about these risks three times before the incident occurred."},
]

MOCK_DEFENSE_MESSAGES = [
    {"agent_type": "defense", "agent_name": "Defense Counsel", "timestamp": "09:16:08",
     "content": "Your Honor, the plaintiff's case rests on circumstantial evidence and emotional appeals rather than established facts."},
    {"agent_type": "defense", "agent_name": "Defense Counsel", "timestamp": "09:19:55",
     "content": "My client followed every protocol mandated by industry standards. The so-called warnings were routine compliance notices."},
]

MOCK_CASE_FACTS = """SUPREME COURT OF THE STATE OF NEW YORK
COUNTY OF NASSAU

JOHN JONES,
    Plaintiff,
        v.
GEORGE SMITH,
    Defendant.

Index No. 2024-0130

COMPLAINT

Plaintiff John Jones, by and through his attorneys, alleges as follows:

1. Plaintiff is a resident of Nassau County, New York.
2. Defendant is a corporation organized under the laws of the State of New York.
3. At all times relevant hereto, Defendant owed a duty of care to Plaintiff..."""

MOCK_JUROR_DATA = [
    {"name": "Marcus", "score": 45, "thought": "The defense seems unprepared..."},
    {"name": "Elena", "score": 62, "thought": "Those documents are damning."},
    {"name": "Raymond", "score": 38, "thought": "I need to see the numbers myself."},
    {"name": "Destiny", "score": 55, "thought": "Both sides make valid points."},
    {"name": "Chen", "score": 48, "thought": "The timeline doesn't add up."},
    {"name": "Patricia", "score": 52, "thought": "Counsel is grandstanding again."},
]
