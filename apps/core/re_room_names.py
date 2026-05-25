#!/usr/bin/env python3
#this belongs in apps/core/re_room_names.py - Version: 1
# X-Seti - May22 2026 - ResBio-Evil-Workshop - Room Name Database
"""
Room name lookup for RE1, RE2 and RE3.
Key format: "SRR" where S=stage hex, RR=room hex (3 chars total).
e.g. "11C" = stage 1, room 0x1C

RE2 room IDs end in a scenario digit (0=Leon, 1=Claire) which is
stripped before lookup.
"""

from typing import Optional

##Methods list -
# get_room_name
# get_game_from_room_id

# --- RE1 (Biohazard / Resident Evil 1) ---
RE1_ROOM_NAMES = {
    # Stage 0 - Spencer Mansion 1F
    "000": "Outside / Garden",
    "001": "Main Hall",
    "002": "Dining Room",
    "003": "West Corridor",
    "004": "Staircase West",
    "005": "Art Room",
    "006": "Push-Block Room",
    "007": "East Corridor",
    "008": "Changing Room",
    "009": "Library",
    "00A": "Bathroom",
    "00B": "Master Bedroom",
    "00C": "Closet",
    "00D": "Mansion Corridor",
    "00E": "Dark Courtyard",
    "00F": "East Stairs",
    # Stage 1 - Spencer Mansion 2F
    "100": "Main Hall 2F",
    "101": "2F West Corridor",
    "102": "Lounge",
    "103": "Trevor's Room",
    "104": "Plant Room",
    "105": "2F East Corridor",
    "106": "Small Gallery",
    "107": "2F East Room",
    "108": "2F Storage",
    "109": "2F Back Corridor",
    "10A": "Small Storage",
    # Stage 2 - Guardhouse
    "200": "Guardhouse Hall",
    "201": "Aqua Corridor",
    "202": "Aqua Ring",
    "203": "Neptune Tank",
    "204": "Chemical Room",
    "205": "Dormitory",
    "206": "Cafeteria",
    "207": "Bar / Rec Room",
    "208": "Guardhouse Back",
    "209": "Emergency Stairs",
    # Stage 3 - Mansion Basement
    "300": "B1 Main Corridor",
    "301": "Shark Pool",
    "302": "B1 East Hall",
    "303": "Generator Room",
    "304": "B2 Stairwell",
    "305": "Lab Passage",
    "306": "Tyrant Room",
    # Stage 4 - Laboratory
    "400": "Lab Entrance Hall",
    "401": "Break Room",
    "402": "Research Corridor",
    "403": "Experiment Room",
    "404": "Serum Storage",
    "405": "Helipad",
    "406": "Control Room",
    "407": "Waste Processing",
}

# --- RE2 (Biohazard 2 / Resident Evil 2) ---
RE2_ROOM_NAMES = {
    # Stage 0 - Raccoon City Exterior
    "000": "Raccoon City Street",
    "001": "Gas Station",
    "002": "Alley",
    "003": "Gun Shop",
    "004": "Side Street",
    # Stage 1 - Police Station
    "100": "Police Station Front",
    "101": "East Corridor 1F",
    "102": "Darkroom",
    "103": "Break Room",
    "104": "Press Room",
    "105": "Roof Access",
    "106": "West Corridor 1F",
    "107": "Women's Locker",
    "108": "Men's Locker",
    "109": "S.T.A.R.S. Office",
    "10A": "Captain's Office",
    "10B": "Evidence Room",
    "10C": "Clock Tower Room",
    "10D": "Night-Duty Room",
    "10E": "Interrogation Room",
    "10F": "Roof",
    "110": "East Balcony",
    "111": "Library 2F",
    "112": "Art Room 2F",
    "113": "Waiting Room",
    "114": "Safety Deposit Room",
    "115": "Main Hall",
    "116": "East Stairwell",
    "117": "Storage Closet",
    "118": "West Corridor 2F",
    "119": "Chief's Anteroom",
    "11A": "Chief's Office",
    "11B": "Parking Lot",
    "11C": "Parking Garage",
    "11D": "Sewage Control",
    "11E": "East Stairwell 2F",
    "11F": "West Stairwell",
    "120": "East Corridor 3F",
    "121": "Balcony East",
    "122": "Observation Deck",
    # Stage 2 - Sewers
    "200": "Sewer Entrance",
    "201": "Sewer Main Passage",
    "202": "Monitor Room",
    "203": "Pump Room",
    "204": "Sewage Control Room",
    "205": "Underground Stairs",
    "206": "Treatment Pool",
    "207": "Sewer East",
    "208": "Cable Car Platform",
    "209": "Junction",
    # Stage 3 - Laboratory (Umbrella)
    "300": "Lab Main Corridor",
    "301": "Power Room",
    "302": "Culture Experiment Room",
    "303": "Neonatal Unit",
    "304": "Presentation Room",
    "305": "Lab Lobby",
    "306": "Hallway",
    "307": "Security Room",
    "308": "Lift",
    "309": "Tyrant Capsule Room",
    "30A": "Emergency Ladder",
    "30B": "Escape Route",
    "30C": "Train Platform",
}

# --- RE3 (Biohazard 3: Last Escape / Nemesis) ---
RE3_ROOM_NAMES = {
    # Stage 0 - Raccoon City Downtown
    "000": "Raccoon City Streets",
    "001": "J's Bar",
    "002": "Downtown Alley",
    "003": "Downtown East",
    "004": "Grill 13",
    "005": "Gas Station Exterior",
    "006": "Trolley",
    "007": "Pharmacy",
    "008": "Restaurant",
    # Stage 1 - Uptown
    "100": "Uptown Streets",
    "101": "Warehouse",
    "102": "Uptown Alley",
    "103": "Dead Factory Exterior",
    # Stage 2 - Park
    "200": "Raccoon Park",
    "201": "Fountain Area",
    "202": "Statue Puzzle",
    "203": "Park Entrance",
    # Stage 3 - Clocktower
    "300": "Clocktower Entrance",
    "301": "Clocktower Bell Room",
    "302": "Clocktower Courtyard",
    "303": "Bell Tower",
    "304": "Clocktower Interior",
    # Stage 4 - Hospital
    "400": "Hospital Reception",
    "401": "Nurse Station",
    "402": "Operations Room",
    "403": "Aqua Cure Lab",
    "404": "Hospital Rooftop",
    "405": "Hospital Corridor",
    "406": "Storage",
    # Stage 5 - Sewers
    "500": "Sewer Main",
    "501": "Pump Room",
    "502": "Drain Decontamination",
    "503": "Sewer Junction",
    # Stage 6 - Dead Factory / Lab
    "600": "Factory Entrance",
    "601": "Research Corridor",
    "602": "Nemesis Room",
    "603": "Helipad",
    "604": "Factory Floor",
    "605": "Waste Disposal",
}

# Combined lookup
ALL_ROOM_NAMES = {
    **RE1_ROOM_NAMES,
    **RE2_ROOM_NAMES,
    **RE3_ROOM_NAMES,
}


def _extract_key(room_id: str) -> str: #vers 2
    """Extract the 3-char lookup key from a room_id string.
    Handles RE1 (ROOM000), RE2 (ROOM11C0/ROOM11C1), RE3 (ROOM0XX0).
    """
    name = room_id.upper().strip()
    if '.' in name:
        name = name.rsplit('.', 1)[0]
    digits = name[4:] if name.startswith('ROOM') else name
    # Strip trailing scenario digit for RE2/RE3 (4+ char stems ending in 0/1)
    if len(digits) >= 4 and digits[-1] in ('0', '1'):
        digits = digits[:-1]
    return digits[-3:] if len(digits) >= 3 else digits.zfill(3)


def get_room_name(room_id: str) -> Optional[str]: #vers 1
    """Return human-readable name for a room ID. Returns None if unknown."""
    key = _extract_key(room_id)
    return ALL_ROOM_NAMES.get(key.upper())


def get_room_name_or_id(room_id: str) -> str: #vers 1
    """Return human-readable name, falling back to room_id if unknown."""
    return get_room_name(room_id) or room_id


def get_game_from_room_id(room_id: str) -> str: #vers 1
    """Guess which game a room ID belongs to from naming patterns.
    Returns 're1', 're2', 're3' or 'unknown'.
    """
    name = room_id.upper()
    if name.startswith('ROOM'):
        digits = name[4:]
        # RE2: 4 char stem ending in 0 or 1
        if len(digits) >= 4 and digits[-1] in ('0', '1'):
            key = digits[:-1][-3:]
            if key in RE2_ROOM_NAMES:
                return 're2'
        key = digits[-3:]
        if key in RE3_ROOM_NAMES:
            return 're3'
        if key in RE1_ROOM_NAMES:
            return 're1'
    return 'unknown'
