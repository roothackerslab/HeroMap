import json
import os
import sys
import webbrowser
import platform
import datetime
import hashlib
import random

# =============================================================
#  CONFIG LOADER
# =============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_json(filename, default=None):
    path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(path):
        return default if default is not None else {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return json.loads(content) if content else (default or {})
    except FileNotFoundError:
        print(f"\n  [!] File not found: {filename}")
        print(f"  Make sure '{filename}' exists in the same folder as main.py\n")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"\n  [!] Broken JSON in {filename}: {e}\n")
        sys.exit(1)

config     = load_json("config.json",     {"version": "2.1.0", "author": "ZeroTraceX"})
progress   = load_json("progress.json",   {})
bookmarks  = load_json("bookmarks.json",  {})
settings   = load_json("settings.json",   {})
badges     = load_json("badges.json",     {})
ctf_data   = load_json("challenges.json", {"challenges": []})
ctf_scores = load_json("ctf_scores.json", {})
profile    = load_json("profile.json",    {})
facts_data = load_json("facts.json",      {"facts": []})

_villain_runtime = False  # session-only flag, never saved

# =============================================================
#  ANSI COLOR CODES
# =============================================================
class _A:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    BLACK   = "\033[30m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    LGRAY   = "\033[37m"
    DGRAY   = "\033[90m"

# =============================================================
#  THEME SYSTEM
# =============================================================
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

THEMES = {
    "dark": {
        "primary":   _A.GREEN,
        "secondary": _A.CYAN,
        "highlight": _A.YELLOW,
        "danger":    _A.RED,
        "accent":    _A.MAGENTA,
        "info":      _A.BLUE,
        "muted":     _A.DGRAY,
        "text":      _A.WHITE,
        "banner":    _A.GREEN,
        "divider":   _A.DGRAY,
        "label":     "DARK  \U0001f319",
    },
    "light": {
        "primary":   _A.BLUE,
        "secondary": _A.MAGENTA,
        "highlight": _A.CYAN,
        "danger":    _A.RED,
        "accent":    _A.BLUE,
        "info":      _A.GREEN,
        "muted":     _A.LGRAY,
        "text":      _A.BLACK,
        "banner":    _A.BLUE,
        "divider":   _A.LGRAY,
        "label":     "LIGHT \u2600\ufe0f",
    },
    "villain": {
        "primary":   _A.RED,
        "secondary": _A.MAGENTA,
        "highlight": _A.RED,
        "danger":    _A.RED,
        "accent":    _A.MAGENTA,
        "info":      _A.MAGENTA,
        "muted":     _A.DGRAY,
        "text":      _A.WHITE,
        "banner":    _A.RED,
        "divider":   _A.DGRAY,
        "label":     "VILLAIN \U0001f608",
    },
}

def save_settings():
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)

def get_theme():
    return settings.get("theme", "dark")

def set_theme(name):
    settings["theme"] = name
    save_settings()

class C:
    RESET = _A.RESET
    BOLD  = _A.BOLD

    @classmethod
    def _t(cls, role):
        return THEMES.get(get_theme(), THEMES["dark"]).get(role, "")

    @classmethod
    def primary(cls):     return cls._t("primary")
    @classmethod
    def secondary(cls):   return cls._t("secondary")
    @classmethod
    def highlight(cls):   return cls._t("highlight")
    @classmethod
    def danger(cls):      return cls._t("danger")
    @classmethod
    def accent(cls):      return cls._t("accent")
    @classmethod
    def info(cls):        return cls._t("info")
    @classmethod
    def muted(cls):       return cls._t("muted")
    @classmethod
    def banner_c(cls):    return cls._t("banner")
    @classmethod
    def divider_c(cls):   return cls._t("divider")
    @classmethod
    def theme_label(cls): return THEMES.get(get_theme(), THEMES["dark"]).get("label", "")

# =============================================================
#  FILE PATHS
# =============================================================
PROGRESS_FILE   = os.path.join(BASE_DIR, "progress.json")
BOOKMARK_FILE   = os.path.join(BASE_DIR, "bookmarks.json")
BADGE_FILE      = os.path.join(BASE_DIR, "badges.json")
CTF_SCORES_FILE = os.path.join(BASE_DIR, "ctf_scores.json")
PROFILE_FILE    = os.path.join(BASE_DIR, "profile.json")

# =============================================================
#  OS DETECTION
# =============================================================
def get_os():
    s = platform.system().lower()
    if "linux"   in s: return "linux"
    if "windows" in s: return "windows"
    if "darwin"  in s: return "macos"
    return "unknown"

CURRENT_OS = get_os()

def os_label():
    labels = {
        "linux":   C.highlight() + "Linux"      + C.RESET,
        "windows": C.secondary() + "Windows"    + C.RESET,
        "macos":   C.accent()    + "macOS"      + C.RESET,
        "unknown": C.danger()    + "Unknown OS" + C.RESET,
    }
    return labels.get(CURRENT_OS, CURRENT_OS)

# =============================================================
#  UTILITY HELPERS
# =============================================================
def clear():
    os.system("cls" if os.name == "nt" else "clear")

def pause(msg="Press Enter to continue..."):
    input("\n" + C.highlight() + msg + C.RESET)

def divider(char="\u2500", length=52):
    print(C.divider_c() + char * length + C.RESET)

def banner():
    bc = C.banner_c() + C.BOLD
    print(bc + """
\u2588\u2588\u2557  \u2588\u2588\u2557\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2557\u2588\u2588\u2588\u2588\u2588\u2588\u2557  \u2588\u2588\u2588\u2588\u2588\u2588\u2557     \u2588\u2588\u2588\u2557   \u2588\u2588\u2588\u2557 \u2588\u2588\u2588\u2588\u2588\u2557 \u2588\u2588\u2588\u2588\u2588\u2588\u2557
\u2588\u2588\u2551  \u2588\u2588\u2551\u2588\u2588\u2554\u2550\u2550\u2550\u2550\u255d\u2588\u2588\u2554\u2550\u2550\u2588\u2588\u2557\u2588\u2588\u2554\u2550\u2550\u2550\u2588\u2588\u2557    \u2588\u2588\u2588\u2588\u2557 \u2588\u2588\u2588\u2588\u2551\u2588\u2588\u2554\u2550\u2550\u2588\u2588\u2557\u2588\u2588\u2554\u2550\u2550\u2588\u2588\u2557
\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2551\u2588\u2588\u2588\u2588\u2588\u2557  \u2588\u2588\u2588\u2588\u2588\u2588\u2554\u255d\u2588\u2588\u2551   \u2588\u2588\u2551    \u2588\u2588\u2554\u2588\u2588\u2588\u2588\u2554\u2588\u2588\u2551\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2551\u2588\u2588\u2588\u2588\u2588\u2588\u2554\u255d
\u2588\u2588\u2554\u2550\u2550\u2588\u2588\u2551\u2588\u2588\u2554\u2550\u2550\u255d  \u2588\u2588\u2554\u2550\u2550\u2588\u2588\u2557\u2588\u2588\u2551   \u2588\u2588\u2551    \u2588\u2588\u2551\u255a\u2588\u2588\u2554\u255d\u2588\u2588\u2551\u2588\u2588\u2554\u2550\u2550\u2588\u2588\u2551\u2588\u2588\u2554\u2550\u2550\u2550\u255d
\u2588\u2588\u2551  \u2588\u2588\u2551\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2557\u2588\u2588\u2551  \u2588\u2588\u2551\u255a\u2588\u2588\u2588\u2588\u2588\u2588\u2554\u255d    \u2588\u2588\u2551 \u255a\u2550\u255d \u2588\u2588\u2551\u2588\u2588\u2551  \u2588\u2588\u2551\u2588\u2588\u2551
\u255a\u2550\u255d  \u255a\u2550\u255d\u255a\u2550\u2550\u2550\u2550\u2550\u2550\u255d\u255a\u2550\u255d  \u255a\u2550\u255d \u255a\u2550\u2550\u2550\u2550\u2550\u255d     \u255a\u2550\u255d     \u255a\u2550\u255d\u255a\u2550\u255d  \u255a\u2550\u255d\u255a\u2550\u255d""" + C.RESET)

    version = config.get("version", "2.1.0")
    author  = config.get("author",  "ZeroTraceX")
    print(C.secondary() + C.BOLD + "        Powered by RootHackersLab" + C.RESET +
          "   " + C.muted() + "v" + version + C.RESET)
    print(C.highlight() + "        developed by " + author + C.RESET)
    print("        OS: " + os_label() + "   Theme: " + C.muted() + C.theme_label() + C.RESET)
    pl = persona_banner_line()
    if pl:
        print(pl)
    if is_code_explorer_unlocked():
        print("        " + C.danger() + C.BOLD + "\U0001f575\ufe0f  Code Explorer" + C.RESET)
    print()

def open_link(url, label=""):
    try:
        webbrowser.open(url)
        msg = "\n" + C.primary() + "  \u2713 Opened in browser" + C.RESET
        if label:
            msg += ": " + label
        print(msg)
    except Exception as e:
        print("\n" + C.danger() + "  Could not open browser: " + str(e) + C.RESET)
        print("  Manual link: " + C.secondary() + url + C.RESET)

# =============================================================
#  THEME SWITCHER
# =============================================================
def show_theme_menu():
    while True:
        clear(); banner()
        current = get_theme()
        print(C.secondary() + C.BOLD + "  \U0001f3a8 Theme Settings" + C.RESET + "\n")
        divider()
        for key, name in [("1", "dark"), ("2", "light")]:
            tick  = C.primary() + "\u25c9" + C.RESET if current == name else C.muted() + "\u25cb" + C.RESET
            label = THEMES[name]["label"]
            print("  " + tick + " " + C.primary() + "[" + key + "]" + C.RESET + " " + label)
        divider()
        print("  " + C.danger() + "[0]" + C.RESET + " Back")
        choice = input("\n  Select Theme: ").strip()
        if choice == "0":
            return
        elif choice == "1":
            set_theme("dark")
            print("\n  " + C.primary() + "\u2713 Dark theme applied! \U0001f319" + C.RESET)
            pause("Press Enter..."); return
        elif choice == "2":
            set_theme("light")
            print("\n  " + C.primary() + "\u2713 Light theme applied! \u2600\ufe0f" + C.RESET)
            pause("Press Enter..."); return
        else:
            print("\n  " + C.danger() + "Invalid choice." + C.RESET)
            pause("Press Enter...")

# =============================================================
#  PROGRESS TRACKING
# =============================================================
def save_progress():
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2)

def mark_tool_opened(tool_name):
    progress["tool::" + tool_name.lower().replace(" ", "_")] = True
    save_progress()

def is_tool_opened(tool_name):
    return progress.get("tool::" + tool_name.lower().replace(" ", "_"), False)

def count_tools_opened():
    return sum(1 for k in progress if k.startswith("tool::") and progress[k] is True)

def topic_done_key(phase_name, topic_name):
    return "done::" + phase_name + "::" + topic_name

def is_topic_done(phase_name, topic_name):
    return progress.get(topic_done_key(phase_name, topic_name), False)

def toggle_topic_done(phase_name, topic_name):
    key = topic_done_key(phase_name, topic_name)
    progress[key] = not progress.get(key, False)
    if progress[key]:
        mark_topic_done_today(phase_name, topic_name)
    save_progress()
    return progress[key]

def mark_topic_done_today(phase_name, topic_name):
    today = datetime.date.today().isoformat()
    progress["daily::" + today + "::" + phase_name + "::" + topic_name] = True
    save_progress()

def count_topics_done_today():
    today = datetime.date.today().isoformat()
    return sum(1 for k, v in progress.items()
               if k.startswith("daily::" + today + "::") and v is True)

def get_phase_stats(phase):
    topics = phase.get("topics", {})
    total  = len(topics)
    done   = sum(1 for t in topics.values() if is_topic_done(phase["name"], t["name"]))
    return done, total, 0, 0

def overall_progress(phases):
    total_done = total_all = 0
    for phase in phases.values():
        done, total, _, _ = get_phase_stats(phase)
        total_done += done
        total_all  += total
    pct = int((total_done / total_all) * 100) if total_all else 0
    return total_done, total_all, pct

def render_bar(done, total, width=20):
    if total == 0:
        pct    = 100
        filled = width
    else:
        pct    = int((done / total) * 100)
        filled = min(int((done / total) * width), width)
    filled    = max(0, filled)
    bar_color = (C.primary() if pct == 100 else
                 C.highlight() if pct >= 50 else C.muted())
    bar = bar_color + "[" + "\u2588" * filled + "\u2591" * (width - filled) + "]" + C.RESET
    return bar, pct

def show_progress_report(phases):
    clear(); banner()
    print(C.secondary() + C.BOLD + "  \U0001f4ca Progress Report" + C.RESET + "\n")
    divider()
    t_done, t_all, t_pct = overall_progress(phases)
    overall_bar, _ = render_bar(t_done, t_all, width=30)
    print("  Overall   " + overall_bar + "  " + C.BOLD + str(t_pct) + "%" + C.RESET +
          "  " + C.muted() + "(" + str(t_done) + "/" + str(t_all) + " topics)" + C.RESET + "\n")
    divider()
    for pk, phase in phases.items():
        done, total, _, _ = get_phase_stats(phase)
        bar, pct = render_bar(done, total, width=20)
        tick = C.primary() + "\u2713" + C.RESET if pct == 100 else " "
        print("  " + tick + " " + C.primary() + "[" + pk + "]" + C.RESET + " " + phase["name"])
        print("      " + bar + "  " + str(pct) + "%")
    divider()
    input("\n  " + C.danger() + "[0]" + C.RESET + " Press Enter to go back...")

# =============================================================
#  PERSONA / PROFILE
# =============================================================
SPECIALIZATIONS = [
    ("1", "Web Pentester",   "\U0001f578\ufe0f"),
    ("2", "Network Hacker",  "\U0001f4e1"),
    ("3", "Malware Analyst", "\U0001f9ec"),
    ("4", "Bug Hunter",      "\U0001f41b"),
    ("5", "All Rounder",     "\U0001f30d"),
]

RANKS = [
    (0,   "Newbie",        "\U0001f476"),
    (10,  "Script Kiddie", "\U0001f423"),
    (30,  "Hacker",        "\U0001f513"),
    (60,  "Elite Hacker",  "\U0001f480"),
    (100, "Zero Trace",    "\U0001f576\ufe0f"),
]

def save_profile():
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)

def get_spec_icon(spec_name):
    for _, name, icon in SPECIALIZATIONS:
        if name == spec_name:
            return icon
    return "\U0001f30d"

def get_rank(pct):
    rank = RANKS[0]
    for threshold, name, icon in RANKS:
        if pct >= threshold:
            rank = (threshold, name, icon)
    return rank

def get_next_rank(pct):
    for threshold, name, icon in RANKS:
        if pct < threshold:
            return (threshold, name, icon)
    return None

def profile_exists():
    return bool(profile.get("name"))

def show_setup_profile():
    clear(); banner()
    print(C.secondary() + C.BOLD + "  Welcome to RootHackersLab!" + C.RESET)
    print("  " + C.muted() + "Let's set up your hacker profile first." + C.RESET + "\n")
    divider()
    while True:
        name = input("  " + C.primary() + "Enter your hacker name: " + C.RESET).strip()
        if name: break
        print("  " + C.danger() + "Name cannot be empty." + C.RESET)
    print("\n  " + C.secondary() + "Choose your specialization:" + C.RESET + "\n")
    for key, spec, icon in SPECIALIZATIONS:
        print("  " + C.primary() + "[" + key + "]" + C.RESET + " " + icon + "  " + spec)
    spec_map = {k: (n, i) for k, n, i in SPECIALIZATIONS}
    while True:
        sc = input("\n  " + C.primary() + "Select [1-5]: " + C.RESET).strip()
        if sc in spec_map:
            spec_name, spec_icon = spec_map[sc]; break
        print("  " + C.danger() + "Invalid choice." + C.RESET)
    profile["name"]    = name
    profile["spec"]    = spec_name
    profile["created"] = datetime.datetime.now().strftime("%Y-%m-%d")
    save_profile()
    clear(); banner()
    sep = "=" * 44
    print("  " + C.primary() + sep + C.RESET)
    print("  " + C.primary() + C.BOLD + "  Profile Created! Welcome, " + name + "!" + C.RESET)
    print("  " + C.primary() + sep + C.RESET)
    print("\n  " + spec_icon + "  Specialization: " + C.secondary() + spec_name + C.RESET)
    print("  " + RANKS[0][2] + "  Starting Rank:  " + C.muted() + RANKS[0][1] + C.RESET)
    print("\n  " + C.muted() + "Your rank upgrades as you complete the roadmap." + C.RESET)
    pause("Press Enter to start your journey...")

def show_edit_profile():
    clear(); banner()
    print("  " + C.secondary() + C.BOLD + "  Edit Profile" + C.RESET + "\n")
    divider()
    print("  " + C.primary() + "[1]" + C.RESET + " Change hacker name")
    print("  " + C.primary() + "[2]" + C.RESET + " Change specialization")
    print("  " + C.danger()  + "[0]" + C.RESET + " Back")
    choice = input("\n  Select: ").strip()
    if choice == "1":
        name = input("\n  " + C.primary() + "New hacker name: " + C.RESET).strip()
        if name:
            profile["name"] = name; save_profile()
            print("  " + C.primary() + "\u2713 Name updated!" + C.RESET)
        pause("Press Enter...")
    elif choice == "2":
        print()
        for key, spec, icon in SPECIALIZATIONS:
            print("  " + C.primary() + "[" + key + "]" + C.RESET + " " + icon + "  " + spec)
        spec_map = {k: (n, i) for k, n, i in SPECIALIZATIONS}
        sc = input("\n  " + C.primary() + "Select [1-5]: " + C.RESET).strip()
        if sc in spec_map:
            profile["spec"] = spec_map[sc][0]; save_profile()
            print("  " + C.primary() + "\u2713 Specialization updated!" + C.RESET)
        pause("Press Enter...")

def show_profile_screen(phases):
    clear(); banner()
    name      = profile.get("name", "Unknown")
    spec      = profile.get("spec", "All Rounder")
    spec_icon = get_spec_icon(spec)
    created   = profile.get("created", "")
    t_done, t_all, t_pct = overall_progress(phases)
    _, rank_name, rank_icon = get_rank(t_pct)
    next_rank     = get_next_rank(t_pct)
    ctf_score     = get_total_ctf_score()
    ctf_max       = get_max_ctf_score()
    badges_earned = sum(1 for b in BADGE_DEFS if has_badge(b["id"]))
    print("  " + C.secondary() + C.BOLD + "  \U0001f9b8 Hacker Profile" + C.RESET + "\n")
    divider()
    print("  " + rank_icon + "  " + C.BOLD + C.primary() + name + C.RESET)
    print("  " + spec_icon + "  Specialization: " + C.secondary() + spec + C.RESET)
    if created:
        print("  \U0001f4c5  Member since:   " + C.muted() + created + C.RESET)
    divider()
    rank_bar, _ = render_bar(t_pct, 100, width=24)
    print("\n  " + C.highlight() + "Rank: " + rank_icon + " " + rank_name + C.RESET)
    print("  " + rank_bar + "  " + str(t_pct) + "%")
    if next_rank:
        needed = next_rank[0] - t_pct
        print("  " + C.muted() + "Next: " + next_rank[2] + " " + next_rank[1] +
              "  (" + str(needed) + "% more needed)" + C.RESET)
    else:
        print("  " + C.primary() + "MAX RANK ACHIEVED! \U0001f31f" + C.RESET)
    divider()
    print("\n  " + C.muted() + "Stats" + C.RESET + "\n")
    print("  \U0001f4da  Topics completed : " + C.primary() + str(t_done) + "/" + str(t_all) + C.RESET)
    print("  \U0001f9ea  CTF score        : " + C.primary() + str(ctf_score) + "/" + str(ctf_max) + " pts" + C.RESET)
    print("  \U0001f3c6  Badges earned    : " + C.primary() + str(badges_earned) + "/" + str(len(BADGE_DEFS)) + C.RESET)
    print("  \U0001f516  Bookmarks        : " + C.primary() + str(len(bookmarks)) + C.RESET)
    divider()
    print("  " + C.highlight() + "[e]" + C.RESET + " Edit profile")
    print("  " + C.danger()    + "[0]" + C.RESET + " Back")
    choice = input("\n  Select: ").strip().lower()
    if choice == "e":
        show_edit_profile()

def persona_banner_line():
    if not profile_exists():
        return ""
    name      = profile.get("name", "")
    spec      = profile.get("spec", "")
    spec_icon = get_spec_icon(spec)
    return ("        " + spec_icon + "  " + C.primary() + C.BOLD + name + C.RESET +
            "  " + C.muted() + "|  " + spec + C.RESET)

# =============================================================
#  BADGE SYSTEM
# =============================================================
BADGE_DEFS = [
    {"id": "first_step",   "icon": "\U0001f3c5", "name": "First Step",    "desc": "Marked your first topic as done"},
    {"id": "tool_hunter",  "icon": "\u26a1",      "name": "Tool Hunter",   "desc": "Opened 5 tool download links"},
    {"id": "bookworm",     "icon": "\U0001f4da",  "name": "Bookworm",      "desc": "Bookmarked 5 topics"},
    {"id": "on_fire",      "icon": "\U0001f525",  "name": "On Fire",       "desc": "Completed 3 topics in one day"},
    {"id": "night_owl",    "icon": "\U0001f319",  "name": "Night Owl",     "desc": "Marked a topic done after 11 PM"},
    {"id": "halfway",      "icon": "\U0001f4aa",  "name": "Halfway There", "desc": "Reached 50% overall progress"},
    {"id": "phase_master", "icon": "\U0001f947",  "name": "Phase Master",  "desc": "Completed an entire phase"},
    {"id": "zero_to_hero", "icon": "\U0001f3c6",  "name": "Zero to Hero",  "desc": "Completed all 11 phases!"},
]

def save_badges():
    with open(BADGE_FILE, "w", encoding="utf-8") as f:
        json.dump(badges, f, indent=2)

def has_badge(badge_id):
    return badges.get(badge_id, False)

def award_badge(badge_id):
    if has_badge(badge_id): return None
    for b in BADGE_DEFS:
        if b["id"] == badge_id:
            badges[badge_id] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            save_badges()
            return b
    return None

def show_badge_unlock(badge):
    sep = "=" * 40
    print("\n  " + C.highlight() + sep + C.RESET)
    print("  " + C.highlight() + C.BOLD + "  " + badge["icon"] + "  BADGE UNLOCKED!" + C.RESET)
    print("  " + C.primary()   + C.BOLD + "  " + badge["name"] + C.RESET)
    print("  " + C.muted()     + "  " + badge["desc"] + C.RESET)
    print("  " + C.highlight() + sep + C.RESET)
    pause("Press Enter to continue...")

def check_and_award(badge_id, condition):
    if condition and not has_badge(badge_id):
        b = award_badge(badge_id)
        if b: show_badge_unlock(b)
        return b
    return None

def is_night_time():
    return datetime.datetime.now().hour >= 23

def run_badge_checks(phases=None):
    newly_earned = []
    total_done = sum(1 for k, v in progress.items() if k.startswith("done::") and v is True)
    checks = [
        ("first_step",  total_done >= 1),
        ("tool_hunter", count_tools_opened() >= 5),
        ("bookworm",    len(bookmarks) >= 5),
        ("on_fire",     count_topics_done_today() >= 3),
        ("night_owl",   is_night_time() and total_done >= 1),
    ]
    for bid, cond in checks:
        b = check_and_award(bid, cond)
        if b: newly_earned.append(b)
    if phases:
        _, _, t_pct = overall_progress(phases)
        b = check_and_award("halfway", t_pct >= 50)
        if b: newly_earned.append(b)
        for phase in phases.values():
            done, total, _, _ = get_phase_stats(phase)
            if total > 0 and done == total:
                b = check_and_award("phase_master", True)
                if b: newly_earned.append(b)
                break
        all_done = all(
            get_phase_stats(ph)[0] == get_phase_stats(ph)[1] and get_phase_stats(ph)[1] > 0
            for ph in phases.values()
        )
        b = check_and_award("zero_to_hero", all_done)
        if b: newly_earned.append(b)
    return newly_earned

def show_badges_screen():
    clear(); banner()
    print(C.highlight() + C.BOLD + "  \U0001f3c6 Badges" + C.RESET)
    divider()
    earned = sum(1 for b in BADGE_DEFS if has_badge(b["id"]))
    print("  " + C.primary() + str(earned) + C.RESET + C.muted() + " / " + str(len(BADGE_DEFS)) + " earned" + C.RESET + "\n")
    for b in BADGE_DEFS:
        if has_badge(b["id"]):
            date_str = badges.get(b["id"], "")
            print("  " + C.primary() + b["icon"] + "  " + C.BOLD + b["name"] + C.RESET + "  " + C.muted() + date_str + C.RESET)
            print("     " + C.muted() + b["desc"] + C.RESET)
        else:
            print("  " + C.muted() + "?  " + b["name"] + C.RESET)
            print("     " + C.muted() + b["desc"] + C.RESET)
        print()
    divider()
    input("\n  Press Enter to go back...")

# =============================================================
#  CTF CHALLENGES
# =============================================================
DIFF_COLORS = {
    "Easy":   lambda: C.primary(),
    "Medium": lambda: C.highlight(),
    "Hard":   lambda: C.danger(),
}

def save_ctf_scores():
    with open(CTF_SCORES_FILE, "w", encoding="utf-8") as f:
        json.dump(ctf_scores, f, indent=2)

def is_challenge_solved(cid):
    return ctf_scores.get("solved::" + cid, False)

def get_total_ctf_score():
    return sum(c["points"] for c in ctf_data.get("challenges", []) if is_challenge_solved(c["id"]))

def get_max_ctf_score():
    return sum(c["points"] for c in ctf_data.get("challenges", []))

def check_answer(challenge, user_answer):
    user_hash = hashlib.sha256(user_answer.strip().lower().encode()).hexdigest()
    return user_hash == challenge["answer_hash"]

def show_ctf_challenge(challenge):
    ak = "attempts::" + challenge["id"]
    hk = "hint::"     + challenge["id"]
    while True:
        clear(); banner()
        diff_color = DIFF_COLORS.get(challenge["difficulty"], lambda: C.muted())()
        solved     = is_challenge_solved(challenge["id"])
        print("  " + C.secondary() + C.BOLD + "[CTF] " + challenge["title"] + C.RESET)
        print("  " + diff_color + challenge["difficulty"] + C.RESET +
              "  " + C.highlight() + "+" + str(challenge["points"]) + " pts" + C.RESET +
              "  " + C.muted() + "Category: " + challenge["category"] + C.RESET)
        if solved:
            print("  " + C.primary() + "\u2713 SOLVED!" + C.RESET)
        divider()
        for line in challenge["desc"].split("\n"):
            print("  " + line)
        divider()
        attempts  = ctf_scores.get(ak, 0)
        hint_used = ctf_scores.get(hk, False)
        if solved:
            print("  " + C.muted() + "Already solved. Good job!" + C.RESET)
            print("  " + C.danger() + "[0]" + C.RESET + " Back")
            if input("\n  Select: ").strip().lower() == "0":
                return
            continue
        print("  " + C.muted() + "Attempts: " + str(attempts) + C.RESET)
        if hint_used:
            print("  " + C.highlight() + "Hint: " + challenge["hint"] + C.RESET + "\n")
        print("  " + C.primary()   + "[1]" + C.RESET + " Submit Answer")
        if not hint_used:
            print("  " + C.highlight() + "[h]" + C.RESET + " Show Hint  " + C.muted() + "(reveals hint)" + C.RESET)
        print("  " + C.danger() + "[0]" + C.RESET + " Back")
        choice = input("\n  Select: ").strip().lower()
        if choice == "0":
            return
        elif choice == "h" and not hint_used:
            ctf_scores[hk] = True; save_ctf_scores()
        elif choice == "1":
            answer = input("\n  " + C.secondary() + "Your answer: " + C.RESET).strip()
            ctf_scores[ak] = attempts + 1; save_ctf_scores()
            if check_answer(challenge, answer):
                ctf_scores["solved::"    + challenge["id"]] = True
                ctf_scores["solved_at::" + challenge["id"]] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                save_ctf_scores()
                clear(); banner()
                sep = "=" * 44
                print("  " + C.primary() + sep + C.RESET)
                print("  " + C.primary() + C.BOLD + "  \U0001f389  CORRECT!  +" + str(challenge["points"]) + " points!" + C.RESET)
                print("  " + C.primary() + sep + C.RESET)
                print("\n  " + C.muted() + "Total CTF Score: " +
                      str(get_total_ctf_score()) + " / " + str(get_max_ctf_score()) + " pts" + C.RESET)
                pause("Press Enter to continue..."); return
            else:
                print("\n  " + C.danger() + "  \u2717 Wrong answer. Try again!" + C.RESET)
                pause("Press Enter...")

def show_ctf_menu():
    challenges = ctf_data.get("challenges", [])
    if not challenges:
        clear(); banner()
        print("  " + C.danger() + "No CTF challenges found!" + C.RESET)
        print("  " + C.muted()  + "Make sure challenges.json is in the same folder." + C.RESET)
        pause(); return
    categories = sorted(set(c["category"] for c in challenges))
    cat_keys   = {chr(ord("a") + i): cat for i, cat in enumerate(categories)}
    active_cat = "All"
    while True:
        clear(); banner()
        total_score  = get_total_ctf_score()
        max_score    = get_max_ctf_score()
        solved_count = sum(1 for c in challenges if is_challenge_solved(c["id"]))
        score_bar, _ = render_bar(total_score, max_score, width=20)
        print("  " + C.secondary() + C.BOLD + "  \U0001f9ea CTF Challenge Mode" + C.RESET + "\n")
        print("  Score: " + score_bar + "  " + C.BOLD + str(total_score) + "/" + str(max_score) + " pts" + C.RESET +
              "  " + C.muted() + "(" + str(solved_count) + "/" + str(len(challenges)) + " solved)" + C.RESET + "\n")
        divider()
        print("  " + C.muted() + "Filter by category:" + C.RESET)
        ac = C.primary() if active_cat == "All" else C.muted()
        print("  " + ac + "[*]" + C.RESET + " All", end="   ")
        for key, cat in cat_keys.items():
            cc = C.primary() if active_cat == cat else C.muted()
            print(cc + "[" + key + "]" + C.RESET + " " + cat, end="   ")
        print(); divider()
        filtered = [c for c in challenges if active_cat == "All" or c["category"] == active_cat]
        for i, c in enumerate(filtered, 1):
            solved    = is_challenge_solved(c["id"])
            tick      = C.primary() + "\u2713" + C.RESET if solved else C.muted() + "\u25cb" + C.RESET
            diff_c    = DIFF_COLORS.get(c["difficulty"], lambda: C.muted())()
            hint_used = ctf_scores.get("hint::" + c["id"], False)
            hint_tag  = " " + C.muted() + "[hint]" + C.RESET if hint_used and not solved else ""
            pts_color = C.muted() if solved else C.highlight()
            print("  " + tick + " " + C.primary() + "[" + str(i).rjust(2) + "]" + C.RESET + " " +
                  c["title"].ljust(26) + "  " + diff_c + c["difficulty"].ljust(6) + C.RESET +
                  "  " + pts_color + "+" + str(c["points"]) + "pts" + C.RESET + hint_tag)
        divider()
        print("  " + C.danger() + "[0]" + C.RESET + " Back")
        print("  " + C.muted() + "Letter = filter  |  Number = open challenge" + C.RESET)
        choice = input("\n  Select: ").strip().lower()
        if choice == "0": return
        elif choice == "*": active_cat = "All"
        elif choice in cat_keys: active_cat = cat_keys[choice]
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(filtered):
                show_ctf_challenge(filtered[idx])
            else:
                print("\n  " + C.danger() + "Invalid number." + C.RESET)
                pause("Press Enter...")
        else:
            print("\n  " + C.danger() + "Invalid input." + C.RESET)
            pause("Press Enter...")

# =============================================================
#  BOOKMARKS
# =============================================================
def save_bookmarks():
    with open(BOOKMARK_FILE, "w", encoding="utf-8") as f:
        json.dump(bookmarks, f, indent=2)

def make_bm_key(phase_name, topic_name):
    return phase_name + " > " + topic_name

def is_bookmarked(phase_name, topic_name):
    return make_bm_key(phase_name, topic_name) in bookmarks

def add_bookmark(phase_name, topic_name, topic_data):
    key = make_bm_key(phase_name, topic_name)
    if key in bookmarks:
        print("\n  " + C.highlight() + "Already bookmarked!" + C.RESET)
    else:
        bookmarks[key] = {"phase": phase_name, "topic": topic_name, "data": topic_data}
        save_bookmarks()
        print("\n  " + C.primary() + "\u2713 Bookmarked: " + topic_name + C.RESET)
    pause("Press Enter...")

def remove_bookmark(key):
    if key in bookmarks:
        del bookmarks[key]; save_bookmarks()
        print("\n  " + C.primary() + "\u2713 Bookmark removed." + C.RESET)
    else:
        print("\n  " + C.danger() + "Bookmark not found." + C.RESET)

def show_bookmarks(phases=None):
    while True:
        clear(); banner()
        print(C.highlight() + C.BOLD + "  \u2605 Bookmarks" + C.RESET + "\n")
        divider()
        if not bookmarks:
            print("  " + C.muted() + "No bookmarks yet." + C.RESET)
            print("  " + C.muted() + "Bookmark any topic from its menu." + C.RESET)
            divider(); pause(); return
        bm_list = list(bookmarks.items())
        for i, (key, bm) in enumerate(bm_list, 1):
            print("  " + C.primary() + "[" + str(i) + "]" + C.RESET + " " + C.BOLD + bm["topic"] + C.RESET)
            print("      " + C.muted() + bm["phase"] + C.RESET)
        divider()
        print("  " + C.secondary() + "[r]" + C.RESET + " Remove a bookmark")
        print("  " + C.danger()    + "[0]" + C.RESET + " Back")
        choice = input("\n  Select to open / [r] remove / [0] back: ").strip().lower()
        if choice == "0": return
        elif choice == "r":
            num_str = input("  Enter bookmark number to remove: ").strip()
            if num_str.isdigit():
                idx = int(num_str)
                if 1 <= idx <= len(bm_list):
                    remove_bookmark(bm_list[idx - 1][0]); pause("Press Enter...")
                else:
                    print("\n  " + C.danger() + "Invalid number." + C.RESET); pause("Press Enter...")
            else:
                print("\n  " + C.danger() + "Enter a valid number." + C.RESET); pause("Press Enter...")
        elif choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(bm_list):
                bm = bm_list[idx - 1][1]
                topic_menu(bm["data"], phase_name=bm["phase"], phases=phases)
            else:
                print("\n  " + C.danger() + "Invalid choice." + C.RESET); pause("Press Enter...")

# =============================================================
#  SEARCH
# =============================================================
def build_search_index(data):
    index = []
    for pk, phase in data.get("phases", {}).items():
        phase_name = phase["name"]
        for tk, topic in phase.get("topics", {}).items():
            topic_name = topic["name"]
            index.append({
                "type": "topic", "match": topic_name.lower(),
                "display": topic_name, "phase": phase_name,
                "topic_name": topic_name, "topic_data": topic
            })
            for tool_data in topic.get("tools", []):
                _, tool_name = get_tool_url(tool_data)
                index.append({
                    "type": "tool", "match": tool_name.lower(),
                    "display": tool_name, "phase": phase_name,
                    "topic_name": topic_name, "topic_data": topic
                })
    return index

def highlight_match(text, query):
    lower = text.lower()
    idx   = lower.find(query.lower())
    if idx == -1: return text
    return (text[:idx] + C.highlight() + C.BOLD +
            text[idx:idx + len(query)] + C.RESET + text[idx + len(query):])

def show_search(data, phases=None):
    while True:
        clear(); banner()
        print(C.secondary() + C.BOLD + "  \U0001f50d Search" + C.RESET + "\n")
        divider()
        query = input("  Enter keyword (or 0 to go back): ").strip()
        if query in ("0", ""): return
        index   = build_search_index(data)
        results = [r for r in index if query.lower() in r["match"]]
        seen, unique = set(), []
        for r in results:
            k = (r["type"], r["display"], r["topic_name"])
            if k not in seen:
                seen.add(k); unique.append(r)
        clear(); banner()
        print(C.secondary() + C.BOLD + "  \U0001f50d Results for: " +
              C.highlight() + '"' + query + '"' + C.RESET + "\n")
        divider()
        if not unique:
            print("  " + C.danger() + "No results found." + C.RESET)
            print("  " + C.muted()  + "Try a different keyword." + C.RESET)
            divider(); pause("Press Enter to search again..."); continue
        for i, r in enumerate(unique, 1):
            badge   = C.secondary() + "[topic]" + C.RESET if r["type"] == "topic" else C.accent() + "[tool] " + C.RESET
            name_hl = highlight_match(r["display"], query)
            print("  " + C.primary() + "[" + str(i) + "]" + C.RESET + " " + badge + " " + name_hl)
            print("        " + C.muted() + r["phase"] + " \u203a " + r["topic_name"] + C.RESET)
        divider()
        print("  " + C.danger() + "[0]" + C.RESET + " New search")
        pick = input("\n  Select result to open: ").strip()
        if pick == "0": continue
        elif pick.isdigit():
            idx = int(pick)
            if 1 <= idx <= len(unique):
                chosen = unique[idx - 1]
                topic_menu(chosen["topic_data"], phase_name=chosen["phase"], phases=phases)
            else:
                print("\n  " + C.danger() + "Invalid choice." + C.RESET); pause("Press Enter...")
        else:
            print("\n  " + C.danger() + "Please enter a number." + C.RESET); pause("Press Enter...")

# =============================================================
#  TOOL HANDLER
# =============================================================
def get_tool_url(tool_data):
    if isinstance(tool_data, str):
        return None, tool_data
    if isinstance(tool_data, dict):
        name = tool_data.get("name", "Unknown Tool")
        url  = tool_data.get(CURRENT_OS) or tool_data.get("all")
        return url, name
    return None, str(tool_data)

def open_tool(tool_data):
    if not isinstance(tool_data, dict):
        url, name = get_tool_url(tool_data)
        tool_data = {"name": name}
    else:
        url, name = get_tool_url(tool_data)

    linux_cmd = tool_data.get("linux_cmd", "") if isinstance(tool_data, dict) else ""

    print("\n" + C.secondary() + "  Tool: " + C.BOLD + name + C.RESET)
    divider()

    if CURRENT_OS == "linux" and linux_cmd:
        print("  " + C.primary() + "Linux Install Command:" + C.RESET)
        print("  " + C.highlight() + C.BOLD + "  " + linux_cmd + C.RESET + "\n")
        confirm = input("  Run install command now? [Y/n]: ").strip().lower()
        if confirm in ("", "y", "yes"):
            print("\n  " + C.info() + "Running: " + linux_cmd + C.RESET + "\n")
            ret = os.system(linux_cmd)
            if ret == 0:
                print("\n  " + C.primary() + "\u2713 Install command completed!" + C.RESET)
            else:
                print("\n  " + C.danger() + "Command exited with code " + str(ret) + ". Try running manually." + C.RESET)
            mark_tool_opened(name)
        else:
            print("  " + C.highlight() + "Skipped." + C.RESET)

    elif url:
        print("  " + C.primary() + "Download link for " + os_label() + C.RESET)
        print("  " + C.muted() + url + C.RESET + "\n")
        confirm = input("  Open in browser? [Y/n]: ").strip().lower()
        if confirm in ("", "y", "yes"):
            open_link(url, name); mark_tool_opened(name)
        else:
            print("  " + C.highlight() + "Skipped." + C.RESET)

    else:
        print("  " + C.highlight() + "No direct link/command for " + os_label() + "." + C.RESET)
        search_url = "https://www.google.com/search?q=" + name.replace(" ", "+") + "+download"
        print("  Search: " + C.secondary() + search_url + C.RESET)
        confirm = input("\n  Open Google search? [Y/n]: ").strip().lower()
        if confirm in ("", "y", "yes"):
            open_link(search_url, name)

    pause()

# =============================================================
#  TOPIC & TOOL MENUS
# =============================================================
def show_tools(topic):
    tools = topic.get("tools", [])
    while True:
        clear(); banner()
        print(C.accent() + C.BOLD + "  Tools \u2014 " + topic["name"] + C.RESET + "\n")
        if not tools:
            print("  " + C.muted() + "No tools listed for this topic." + C.RESET)
            pause(); return
        divider()
        for i, tool_data in enumerate(tools, 1):
            _, name = get_tool_url(tool_data)
            opened  = is_tool_opened(name)
            tick    = C.primary() + "\u2713" + C.RESET + " " if opened else "  "
            print("  " + tick + C.primary() + "[" + str(i) + "]" + C.RESET + " " + name)
        divider()
        print("\n  " + C.danger() + "[0]" + C.RESET + " Back")
        choice = input("\n  Select Tool: ").strip()
        if choice == "0": return
        elif choice.isdigit():
            num = int(choice)
            if 1 <= num <= len(tools):
                open_tool(tools[num - 1])
            else:
                print("\n  " + C.danger() + "Invalid choice." + C.RESET); pause("Press Enter...")
        else:
            print("\n  " + C.danger() + "Please enter a number." + C.RESET); pause("Press Enter...")

def show_tool_tutorials(tool_tutorials):
    while True:
        clear(); banner()
        print(C.info() + C.BOLD + "  \U0001f4fa Tool Tutorials" + C.RESET + "\n")
        divider()
        items = list(tool_tutorials.items())
        for i, (tool_name, link) in enumerate(items, 1):
            print("  " + C.primary() + "[" + str(i) + "]" + C.RESET + " " + tool_name)
        divider()
        print("  " + C.danger() + "[0]" + C.RESET + " Back")
        choice = input("\n  Select Tutorial: ").strip()
        if choice == "0": return
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(items):
                tool_name, link = items[idx]
                open_link(link, tool_name + " Tutorial")
                pause("Tutorial opened. Press Enter...")
            else:
                print("\n  " + C.danger() + "Invalid choice." + C.RESET); pause("Press Enter...")
        else:
            print("\n  " + C.danger() + "Please enter a number." + C.RESET); pause("Press Enter...")

def topic_menu(topic, phase_name="", phases=None):
    while True:
        clear(); banner()
        print(C.secondary() + C.BOLD + "  " + topic["name"] + C.RESET + "\n")
        divider()
        print("  " + C.primary() + "[1]" + C.RESET + " Tools")
        tutorial       = topic.get("tutorial", "")
        tool_tutorials = topic.get("tool_tutorials", {})
        if tutorial:
            print("  " + C.info() + "[2]" + C.RESET + " \U0001f4fa Watch Tutorial")
        if tool_tutorials:
            print("  " + C.info() + "[3]" + C.RESET + " \U0001f4fa Tool Tutorials")
        bm_status   = is_bookmarked(phase_name, topic["name"])
        done_status = is_topic_done(phase_name, topic["name"])
        if bm_status:
            print("  " + C.highlight() + "[b]" + C.RESET + " Remove Bookmark  " + C.highlight() + "\u2605" + C.RESET)
        else:
            print("  " + C.highlight() + "[b]" + C.RESET + " Add Bookmark  \u2606")
        if done_status:
            print("  " + C.primary() + "[d]" + C.RESET + " Mark as Undone  " + C.primary() + "\u2713 Done" + C.RESET)
        else:
            print("  " + C.muted() + "[d]" + C.RESET + " Mark as Done  \u25cb")
        divider()
        print("  " + C.danger() + "[0]" + C.RESET + " Back")
        choice = input("\n  Select Option: ").strip().lower()
        if choice == "1":
            show_tools(topic)
        elif choice == "2" and tutorial:
            open_link(tutorial, topic["name"] + " Tutorial")
            pause("Tutorial opened. Press Enter...")
        elif choice == "3" and tool_tutorials:
            show_tool_tutorials(tool_tutorials)
        elif choice == "b":
            if bm_status:
                remove_bookmark(make_bm_key(phase_name, topic["name"])); pause("Press Enter...")
            else:
                add_bookmark(phase_name, topic["name"], topic)
        elif choice == "d":
            result = toggle_topic_done(phase_name, topic["name"])
            if result: print("\n  " + C.primary() + "\u2713 Topic marked as Done!" + C.RESET)
            else:      print("\n  " + C.muted()   + "\u25cb Topic marked as Undone." + C.RESET)
            run_badge_checks(phases)
            pause("Press Enter...")
        elif choice == "0":
            return
        else:
            print("\n  " + C.danger() + "Invalid choice." + C.RESET); pause("Press Enter...")

def show_topics(phase, phases=None):
    while True:
        clear(); banner()
        print(C.highlight() + C.BOLD + "  Phase: " + phase["name"] + C.RESET + "\n")
        divider()
        topics = phase["topics"]
        for key, topic in topics.items():
            done = is_topic_done(phase["name"], topic["name"])
            bm   = C.highlight() + "\u2605 " + C.RESET if is_bookmarked(phase["name"], topic["name"]) else "  "
            tick = C.primary() + "\u2713" + C.RESET if done else C.muted() + "\u25cb" + C.RESET
            print("  " + bm + C.primary() + "[" + key + "]" + C.RESET + " " + tick + " " + topic["name"])
        divider()
        playlist = phase.get("playlist", "")
        if playlist:
            print("  " + C.info() + "[v]" + C.RESET + " \U0001f4fa Watch Phase Playlist")
        else:
            print("  " + C.muted() + "[v] Playlist: not available" + C.RESET)
        divider()
        print("  " + C.muted() + "Tip: open a topic and press [d] to mark done/undone" + C.RESET)
        divider()
        print("  " + C.danger() + "[0]" + C.RESET + " Back")
        choice = input("\n  Select Topic: ").strip().lower()
        if choice == "0": return
        elif choice == "v":
            if playlist:
                open_link(playlist, phase["name"] + " Playlist")
                pause("Playlist opened. Press Enter...")
            else:
                print("\n  " + C.highlight() + "No playlist available for this phase." + C.RESET)
                pause("Press Enter...")
        elif choice in topics:
            topic_menu(topics[choice], phase_name=phase["name"], phases=phases)
        else:
            print("\n  " + C.danger() + "Invalid choice." + C.RESET); pause("Press Enter...")

# =============================================================
#  DAILY FACT
# =============================================================
def show_daily_fact():
    facts = facts_data.get("facts", [])
    if not facts: return
    random.seed(int(datetime.date.today().strftime("%Y%m%d")))
    fact = random.choice(facts)
    random.seed()
    width  = 50
    h_line = "\u2500" * width
    pad_hdr = " " * (width - 26)
    print("  " + C.highlight() + "\u250c" + h_line + "\u2510" + C.RESET)
    print("  " + C.highlight() + "\u2502" + C.RESET + "  " + C.BOLD +
          "\U0001f4a1 Hacker Fact of the Day" + C.RESET + pad_hdr + C.highlight() + "\u2502" + C.RESET)
    print("  " + C.highlight() + "\u251c" + h_line + "\u2524" + C.RESET)
    words = fact.split(); line = ""; lines = []; max_w = width - 4
    for word in words:
        if len(line) + len(word) + 1 <= max_w:
            line = (line + " " + word).strip()
        else:
            lines.append(line); line = word
    if line: lines.append(line)
    for ln in lines:
        pad = " " * (width - len(ln) - 2)
        print("  " + C.highlight() + "\u2502" + C.RESET + " " + ln + pad + " " + C.highlight() + "\u2502" + C.RESET)
    print("  " + C.highlight() + "\u2514" + h_line + "\u2518" + C.RESET)
    print()

# =============================================================
#  VILLAIN MODE
# =============================================================
VILLAIN_BANNER = r"""
 __   _____ _    _      _      _   _   _  __  __  ___  ___  ___
 \ \ / /_ _| |  | |    / \    | | | | | ||  \/  |/ _ \|   \| __|
  \ V / | || |__| |__ / _ \   | |_| |_| || |\/| | (_) | |) | _|
   \_/ |___|____|____/_/ \_\   \___\___/ |_|  |_|\___/|___/|___|
"""

def is_villain_mode():
    return _villain_runtime

def toggle_villain_mode():
    global _villain_runtime
    _villain_runtime = not _villain_runtime
    settings["theme"] = "villain" if _villain_runtime else "dark"
    return _villain_runtime

def show_villain_toggle():
    clear()
    if is_villain_mode():
        sep = ">" * 46
        print("\n\n  " + C.primary() + C.BOLD + sep + C.RESET)
        print("  "     + C.primary() + C.BOLD + "  \U0001f608  VILLAIN MODE ACTIVATED  \U0001f608" + C.RESET)
        print("  "     + C.primary() + C.BOLD + sep + C.RESET)
        print("\n  " + C.muted() + "The shadows welcome you." + C.RESET)
        print("  "  + C.muted() + "Your targets await." + C.RESET + "\n")
    else:
        sep = "=" * 46
        print("\n\n  " + C.primary() + C.BOLD + sep + C.RESET)
        print("  "     + C.primary() + C.BOLD + "    Villain Mode deactivated." + C.RESET)
        print("  "     + C.primary() + C.BOLD + sep + C.RESET)
        print("\n  " + C.muted() + "Welcome back to the light side." + C.RESET + "\n")
    pause("Press Enter to continue...")

# =============================================================
#  EASTER EGG
# =============================================================
def is_code_explorer_unlocked():
    return settings.get("code_explorer", False)

def unlock_code_explorer():
    settings["code_explorer"] = True
    save_settings()

def show_easter_egg_unlock():
    clear(); banner()
    sep = "*" * 46
    print("  " + C.primary() + sep + C.RESET)
    print("  " + C.primary() + C.BOLD + "    Wow, you found it! \U0001f575\ufe0f" + C.RESET)
    print("  " + C.primary() + C.BOLD + "    CODE EXPLORER unlocked!" + C.RESET)
    print("  " + C.primary() + sep + C.RESET)
    print("\n  " + C.muted() + "You read the entire source code." + C.RESET)
    print("  "  + C.muted() + "That's the spirit of a true hacker." + C.RESET)
    print("  "  + C.muted() + "This title will stay with you forever." + C.RESET + "\n")
    pause("Press Enter to continue...")

# =============================================================
#  MAIN LOOP
# =============================================================
def main():
    data   = load_json("data.json")
    phases = data.get("phases", {})

    if not profile_exists():
        show_setup_profile()

    run_badge_checks(phases)

    while True:
        clear()
        if is_villain_mode():
            print(C.primary() + C.BOLD + VILLAIN_BANNER + C.RESET)
        else:
            banner()

        show_daily_fact()

        menu_title = ("  \U0001f608 Villain Mode \u2014 Select Your Target"
                      if is_villain_mode() else
                      "  Zero to Hero \u2014 Ethical Hacking Roadmap")
        print(C.accent() + C.BOLD + menu_title + C.RESET + "\n")
        divider()

        for key, phase in phases.items():
            done, total, _, _ = get_phase_stats(phase)
            bar, pct = render_bar(done, total, width=10)
            tick = C.primary() + "\u2713 " + C.RESET if pct == 100 else "  "
            print("  " + tick + C.primary() + "[" + key.rjust(2) + "]" + C.RESET +
                  " " + phase["name"] + "  " + bar + " " + C.muted() + str(pct) + "%" + C.RESET)

        divider()
        t_done, t_all, t_pct = overall_progress(phases)
        o_bar, _ = render_bar(t_done, t_all, width=20)
        print("  Overall: " + o_bar + " " + C.BOLD + str(t_pct) + "%" + C.RESET +
              "  " + C.muted() + "(" + str(t_done) + "/" + str(t_all) + " topics)" + C.RESET)
        divider()

        bm_count  = len(bookmarks)
        bm_label  = "  (" + str(bm_count) + ")" if bm_count else ""
        _, rank_name, rank_icon = get_rank(t_pct)
        earned     = sum(1 for b in BADGE_DEFS if has_badge(b["id"]))
        ctf_solved = sum(1 for c in ctf_data.get("challenges", []) if is_challenge_solved(c["id"]))
        ctf_total  = len(ctf_data.get("challenges", []))

        print("  " + C.primary()   + "[r]" + C.RESET + " Profile  " + rank_icon + " " + C.muted() + rank_name + C.RESET)
        print("  " + C.secondary() + "[s]" + C.RESET + " Search")
        print("  " + C.highlight() + "[b]" + C.RESET + " Bookmarks" + C.highlight() + bm_label + C.RESET)
        print("  " + C.info()      + "[p]" + C.RESET + " Progress Report")
        print("  " + C.highlight() + "[a]" + C.RESET + " Badges  " + C.muted() + str(earned) + "/" + str(len(BADGE_DEFS)) + C.RESET)
        print("  " + C.danger()    + "[c]" + C.RESET + " CTF Challenges  " + C.muted() + str(ctf_solved) + "/" + str(ctf_total) + " solved" + C.RESET)
        print("  " + C.info()      + "[t]" + C.RESET + " Theme  " + C.muted() + C.theme_label() + C.RESET)
        print("  " + C.danger()    + "[0]" + C.RESET + " Exit")

        choice = input("\n  Select Phase: ").strip().lower()

        if choice == "0":
            clear()
            print("\n" + C.primary() + C.BOLD + "  Goodbye! Keep hacking ethically. \U0001f512" + C.RESET + "\n")
            break
        elif choice == "r": show_profile_screen(phases)
        elif choice == "s": show_search(data, phases=phases)
        elif choice == "b": show_bookmarks(phases=phases)
        elif choice == "p": show_progress_report(phases)
        elif choice == "a": show_badges_screen()
        elif choice == "c": show_ctf_menu()
        elif choice == "t": show_theme_menu()
        elif choice in phases: show_topics(phases[choice], phases=phases)
        elif choice == "villain":
            toggle_villain_mode(); show_villain_toggle()
        elif choice == "ahsan":
            if not is_code_explorer_unlocked():
                unlock_code_explorer(); show_easter_egg_unlock()
            else:
                print("\n  " + C.primary() + "\U0001f575\ufe0f You are already a Code Explorer!" + C.RESET)
                pause("Press Enter...")
        else:
            print("\n  " + C.danger() + "Invalid choice. Enter a number or letter from the list." + C.RESET)
            pause("Press Enter...")


if __name__ == "__main__":
    main()
