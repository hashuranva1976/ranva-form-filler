import re
import os
import sys
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from typing import Dict, Any, List, Optional
from playwright.sync_api import sync_playwright, Page, ElementHandle

# Common synonyms and matching patterns
FIELD_MAPPINGS = {
    "first_name": [
        "first name", "fname", "first_name", "first", "given name", "forename",
        "પ્રથમ નામ", "નામ", "ઉમેદવારનું નામ", "applicant first name"
    ],
    "middle_name": [
        "middle name", "mname", "middle_name", "father name", "father's name", "husband name",
        "પિતાનું નામ", "વાલીનું નામ", "પતિનું નામ", "middle"
    ],
    "last_name": [
        "last name", "lname", "last_name", "surname", "family name",
        "અટક", "શાખ"
    ],
    "full_name": [
        "full name", "fullname", "applicant name", "candidate name", "name of applicant",
        "name as per aadhaar", "પૂરું નામ", "સંપૂર્ણ નામ", "નામ (પૂરું)"
    ],
    "email": [
        "email", "e-mail", "email address", "mail id", "ઇમેઇલ", "ઈ-મેઈલ", "mail"
    ],
    "mobile": [
        "mobile", "phone", "contact", "mobile number", "cell", "contact number",
        "phone number", "મોબાઈલ", "ફોન નંબર", "સંપર્ક નંબર", "whatsapp"
    ],
    "alternate_mobile": [
        "alt mobile", "alternate mobile", "alternate phone", "emergency contact",
        "બીજો મોબાઈલ", "વૈકલ્પિક ફોન", "secondary phone"
    ],
    "dob": [
        "dob", "date of birth", "birth date", "birthdate", "જન્મ તારીખ", "જન્મતારીખ", "d.o.b"
    ],
    "gender": [
        "gender", "sex", "જાતિ", "લિંગ"
    ],
    "marital_status": [
        "marital status", "marital", "marriage", "વૈવાહિક સ્થિતિ", "લગ્ન સ્થિતિ"
    ],
    "category": [
        "category", "caste", "social category", "reservation", "કેટેગરી", "જાતિ કેટેગરી",
        "general", "obc", "sebc", "sc", "st", "ews"
    ],
    "nationality": [
        "nationality", "citizenship", "રાષ્ટ્રીયતા", "નાગરિકતા", "country"
    ],
    "religion": [
        "religion", "faith", "ધર્મ"
    ],
    "aadhaar": [
        "aadhaar", "aadhar", "uid", "adhar", "uidai", "aadhaar number", "આધાર કાર્ડ", "આધાર નંબર"
    ],
    "pan": [
        "pan", "pan number", "pan card", "income tax pan", "પાન કાર્ડ", "પાન નંબર"
    ],
    "voter_id": [
        "voter id", "epic", "election card", "ચૂંટણી કાર્ડ"
    ],
    "address_line1": [
        "address", "address 1", "address line 1", "street", "house", "flat",
        "residential address", "communication address", "સરનામું", "ઘર નંબર", "શેરી"
    ],
    "address_line2": [
        "address 2", "address line 2", "area", "locality", "landmark", "વિસ્તાર"
    ],
    "village_city": [
        "city", "village", "town", "place", "શહેર", "ગામ", "વતન"
    ],
    "taluka": [
        "taluka", "tehsil", "block", "sub district", "તાલુકો"
    ],
    "district": [
        "district", "જિલ્લો"
    ],
    "state": [
        "state", "province", "રાજ્ય"
    ],
    "pincode": [
        "pincode", "pin code", "pin", "zip code", "zip", "postal code", "પિનકોડ"
    ],
    "qualification": [
        "qualification", "highest qualification", "degree", "education",
        "લાયકાત", "અભ્યાસ", "શિક્ષણ", "ડિગ્રી"
    ],
    "passing_year": [
        "passing year", "year of passing", "passing_year", "પાસ કર્યાનું વર્ષ", "વર્ષ"
    ],
    "trials_count": [
        "trials", "trial", "attempts", "number of attempts", "no of attempts", "no of trials",
        "ટ્રાયલ", "પ્રયત્નોની સંખ્યા", "ટ્રાયલ સંખ્યા", "પ્રયત્નો", "number of trials"
    ],
    "percentage": [
        "percentage", "marks", "percent", "cgpa", "score", "ટકાવારી", "ટકા", "પરસેન્ટેજ"
    ],
    "board_university": [
        "board", "university", "school", "college", "institute", "બોર્ડ", "યુનિવર્સિટી"
    ],
    "bank_name": [
        "bank name", "bank", "બેંકનું નામ"
    ],
    "account_number": [
        "account number", "acc no", "account no", "bank account", "ખાતા નંબર"
    ],
    "ifsc_code": [
        "ifsc", "ifsc code", "આઈએફએસસી"
    ]
}

FILE_MAPPINGS = {
    "photo": ["photo", "photograph", "passport photo", "profile photo", "image", "તસવીર", "ફોટો"],
    "signature": ["signature", "sign", "specimen signature", "સહી", "હસ્તાક્ષર"],
    "aadhaar_doc": ["aadhaar", "aadhar card", "identity proof", "id proof", "uid", "આધાર કાર્ડ", "આધાર"],
    "pan_doc": ["pan card", "pan document", "પાન કાર્ડ", "પાન નંબર"],
    "ration_card": ["ration", "ration card", "rationcard", "કૂપન", "kupan", "રેશન કાર્ડ", "રેશનકાર્ડ"],
    "fee_receipt": ["fee", "fees", "fee receipt", "fees receipt", "payment receipt", "challan", "ફી પહોંચ", "ફી રસીદ", "ચલણ"],
    "bonafide_id": ["bonafide", "id card", "identity card", "student id", "college id", "બોનાફાઇડ", "આઈડી કાર્ડ", "ઓળખપત્ર", "વિદ્યાર્થી કાર્ડ"],
    "break_affidavit": ["affidavit", "break affidavit", "gap affidavit", "gap certificate", "એફિડેવિટ", "સોગંદનામું", "ગેપ સર્ટિફિકેટ", "બ્રેક એફિડેવિટ"],
    "caste_cert": ["caste certificate", "category certificate", "જાતિનો દાખલો", "જાતિ પ્રમાણપત્ર", "સામાજિક પ્રમાણપત્ર"],
    "income_cert": ["income certificate", "income proof", "આવકનો દાખલો", "આવક પ્રમાણપત્ર"],
    "lc_doc": ["school leaving certificate", "leaving certificate", "lc", "transfer certificate", "tc", "શાળા છોડ્યાનું પ્રમાણપત્ર", "એલ.સી", "એલસી", "જન્મ પુરાવો"],
    "bank_passbook": ["passbook", "bank passbook", "bank document", "cheque", "cancelled cheque", "બેંક પાસબુક", "પાસબુક"],
    "ssc_marksheet": ["ssc marksheet", "10th marksheet", "ધોરણ ૧૦ માર્કશીટ", "એસએસસી માર્કશીટ"],
    "hsc_marksheet": ["hsc marksheet", "12th marksheet", "ધોરણ ૧૨ માર્કશીટ", "એચએસસી માર્કશીટ"],
    "marksheet_trial1": ["trial 1", "attempt 1", "first trial", "mar 2024", "માર્ચ ૨૦૨૪", "પ્રથમ ટ્રાયલ", "ટ્રાયલ ૧", "ટ્રાયલ 1", "1st attempt"],
    "marksheet_trial2": ["trial 2", "attempt 2", "second trial", "jun 2024", "જૂન ૨૦૨૪", "બીજી ટ્રાયલ", "ટ્રાયલ ૨", "ટ્રાયલ 2", "2nd attempt"],
    "marksheet_trial3": ["trial 3", "attempt 3", "third trial", "ત્રીજી ટ્રાયલ", "ટ્રાયલ ૩", "ટ્રાયલ 3", "3rd attempt"],
    "trial_cert": ["trial certificate", "attempt certificate", "ટ્રાયલ સર્ટિફિકેટ", "પ્રયત્ન પ્રમાણપત્ર"],
    "degree_marksheet": ["degree marksheet", "graduation marksheet", "sem marksheet", "ડિગ્રી માર્કશીટ", "કોલેજ માર્કશીટ"],
    "merged_marksheets": ["all marksheets", "combined marksheet", "single pdf", "તમામ માર્કશીટ", "બધી માર્કશીટ"],
    "marksheet": ["marksheet", "certificate", "passing marksheet", "ssc marksheet", "માર્કશીટ", "પાસ માર્કશીટ", "પ્રમાણપત્ર"],
    "otr_slip": ["otr", "otr slip", "one time registration", "ઓટીઆર"],
    "resume": ["resume", "cv", "curriculum vitae", "બાયોડેટા", "રેઝ્યૂમે"]
}

# Bilingual synonym dictionary for Dropdowns and Radio Buttons
VALUE_SYNONYMS = {
    # States
    "gujarat": ["gujarat", "ગુજરાત", "guj", "gj"],
    "maharashtra": ["maharashtra", "મહારાષ્ટ્ર", "mh"],
    "rajasthan": ["rajasthan", "રાજસ્થાન", "rj"],
    "delhi": ["delhi", "દિલ્હી", "dl"],
    "madhya pradesh": ["madhya pradesh", "મધ્ય પ્રદેશ", "mp"],
    "uttar pradesh": ["uttar pradesh", "ઉત્તર પ્રદેશ", "up"],

    # Genders
    "male": ["male", "m", "પુરુષ", "પુરૂષ", "purush"],
    "female": ["female", "f", "સ્ત્રી", "મહિલા", "stri", "mahila"],
    "other": ["other", "અન્ય", "transgender"],

    # Categories
    "general": ["general", "gen", "open", "સામાન્ય", "જનરલ"],
    "obc": ["obc", "sebc", "other backward class", "ઓબીસી", "ઓ.બી.સી", "ઓ બી સી", "બક્ષીપંચ", "સામાજિક અને શૈક્ષણિક"],
    "sc": ["sc", "scheduled caste", "એસસી", "એસ.સી", "અનુસૂચિત જાતિ"],
    "st": ["st", "scheduled tribe", "એસટી", "એસ.ટી", "અનુસૂચિત જનજાતિ"],
    "ews": ["ews", "economically weaker section", "ઈડબલ્યુએસ", "ઈ.ડબ્લ્યુ.એસ"],

    # Marital Status
    "single": ["single", "unmarried", "અપરિણીત", "અપરિણિત", "કુવારા"],
    "married": ["married", "પરિણીત", "પરિણિત"],

    # Education
    "10th": ["10th", "ssc", "ધોરણ ૧૦", "ધોરણ 10", "10", "matriculation"],
    "12th": ["12th", "hsc", "ધોરણ ૧૨", "ધોરણ 12", "12", "intermediate", "higher secondary"],
    "graduate": ["graduate", "graduation", "bachelor", "સ્નાતક", "degree", "be", "btech", "ba", "bcom", "bsc"],
    "post graduate": ["post graduate", "pg", "master", "અનુસ્નાતક", "me", "mtech", "ma", "mcom", "msc"],
    "diploma": ["diploma", "ડિપ્લોમા"]
}


def clean_text(s: str) -> str:
    if not s:
        return ""
    return re.sub(r"[_\-\s\:\*\.\(\)\[\]\/]+", " ", str(s).lower()).strip()


def get_synonyms_for_value(target_val: str) -> List[str]:
    """Expands a target value into its bilingual synonyms."""
    target_clean = clean_text(target_val)
    synonyms = [target_clean]
    for canonical, syn_list in VALUE_SYNONYMS.items():
        clean_syns = [clean_text(s) for s in syn_list]
        if target_clean == canonical or target_clean in clean_syns:
            synonyms.extend(clean_syns)
            synonyms.append(canonical)
    return list(set(filter(None, synonyms)))


def calculate_match_score(element_context: str, keywords: List[str]) -> int:
    """Calculates how well the context of an element matches keywords."""
    score = 0
    element_context = clean_text(element_context)
    words = set(element_context.split())

    for kw in keywords:
        clean_kw = clean_text(kw)
        if clean_kw == element_context:
            score += 100
        elif f" {clean_kw} " in f" {element_context} ":
            score += 50
        elif clean_kw in element_context:
            score += 30
        else:
            # Check individual word matches
            kw_words = clean_kw.split()
            if kw_words and all(w in words for w in kw_words):
                score += 25

    return score


def extract_element_context(element: ElementHandle, page: Page) -> str:
    """Extracts label, name, id, placeholder, aria-label, and nearby text."""
    try:
        attrs = page.evaluate("""(el) => {
            let texts = [];
            if (el.name) texts.push(el.name);
            if (el.id) {
                texts.push(el.id);
                // Check for label with for="id"
                let lbl = document.querySelector('label[for="' + el.id + '"]');
                if (lbl && lbl.innerText) texts.push(lbl.innerText);
            }
            if (el.placeholder) texts.push(el.placeholder);
            if (el.getAttribute('aria-label')) texts.push(el.getAttribute('aria-label'));
            if (el.title) texts.push(el.title);

            // Check parent label or parent container text
            let parentLabel = el.closest('label');
            if (parentLabel && parentLabel.innerText) {
                texts.push(parentLabel.innerText);
            }

            // Check previous sibling or parent header/th/td
            let prev = el.previousElementSibling;
            if (prev && prev.innerText && prev.innerText.length < 50) {
                texts.push(prev.innerText);
            }

            // Check closest form-group or row
            let group = el.closest('.form-group, .form-row, .field, .mb-3, tr');
            if (group) {
                let lbl = group.querySelector('label, th, .label');
                if (lbl && lbl.innerText) texts.push(lbl.innerText);
            }

            return texts.join(' ');
        }""", element)
        return attrs or ""
    except Exception:
        return ""


class FormFillerEngine:
    def __init__(self, headless: bool = False, browser_channel: str = "chrome"):
        self.headless = headless
        self.browser_channel = browser_channel or "chrome"
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None

    def start(self):
        self.playwright = sync_playwright().start()
        is_cloud = os.environ.get("IS_CLOUD_DEPLOY") == "true" or sys.platform != "win32"
        effective_headless = True if is_cloud else self.headless

        browser_args = [
            "--start-maximized",
            "--disable-blink-features=AutomationControlled",
            "--no-first-run",
            "--no-default-browser-check"
        ]

        if is_cloud:
            browser_args.extend(["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"])

        target_channel = self.browser_channel if self.browser_channel in ["chrome", "msedge"] else "chrome"

        try:
            if is_cloud:
                # On cloud Linux (Render/VPS), use bundled Chromium
                self.browser = self.playwright.chromium.launch(
                    headless=True,
                    args=browser_args
                )
            else:
                self.browser = self.playwright.chromium.launch(
                    channel=target_channel,
                    headless=effective_headless,
                    args=browser_args
                )
        except Exception:
            # Fallback to standard Chromium
            self.browser = self.playwright.chromium.launch(
                headless=effective_headless,
                args=browser_args
            )

        self.context = self.browser.new_context(no_viewport=True)
        self.page = self.context.new_page()

    def bring_to_front_window(self):
        """Forces the browser window to pop up in the foreground on Windows."""
        try:
            if self.page:
                self.page.bring_to_front()
        except Exception:
            pass

        try:
            import win32gui, win32con
            def enum_cb(hwnd, results):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd).lower()
                    if any(w in title for w in ["edge", "chrome", "પોર્ટલ", "recruitment", "demo", "form"]):
                        results.append(hwnd)
            hwnds = []
            win32gui.EnumWindows(enum_cb, hwnds)
            for h in hwnds:
                try:
                    win32gui.ShowWindow(h, win32con.SW_RESTORE)
                    win32gui.ShowWindow(h, win32con.SW_MAXIMIZE)
                    win32gui.SetForegroundWindow(h)
                    break
                except Exception:
                    pass
        except Exception:
            pass

    def close(self):
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except Exception:
            pass

    def fill(self, url: str, profile: Dict[str, Any], log_cb=None) -> Dict[str, Any]:
        """Fills online form using profile data and documents."""
        if log_cb is None:
            log_cb = print

        log_cb(f"🚀 Opening Chrome and navigating to: {url}")
        self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(1)
        self.bring_to_front_window()
        time.sleep(1)  # Give modern JS apps time to render

        log_cb("🔍 Analyzing form fields, textareas, selects, and upload inputs...")

        filled_count = 0
        skipped_count = 0
        details = []

        # Prepare field values from profile
        field_values = {
            "first_name": profile.get("first_name", ""),
            "middle_name": profile.get("middle_name", ""),
            "last_name": profile.get("last_name", ""),
            "full_name": profile.get("full_name") or f"{profile.get('first_name', '')} {profile.get('middle_name', '')} {profile.get('last_name', '')}".strip(),
            "email": profile.get("email", ""),
            "mobile": profile.get("mobile", ""),
            "alternate_mobile": profile.get("alternate_mobile", ""),
            "dob": profile.get("dob", ""),
            "gender": profile.get("gender", ""),
            "marital_status": profile.get("marital_status", ""),
            "category": profile.get("category", ""),
            "nationality": profile.get("nationality", "Indian"),
            "religion": profile.get("religion", ""),
            "aadhaar": profile.get("aadhaar", ""),
            "pan": profile.get("pan", ""),
            "voter_id": profile.get("voter_id", ""),
            "address_line1": profile.get("address_line1", ""),
            "address_line2": profile.get("address_line2", ""),
            "village_city": profile.get("village_city", ""),
            "taluka": profile.get("taluka", ""),
            "district": profile.get("district", ""),
            "state": profile.get("state", "Gujarat"),
            "pincode": profile.get("pincode", ""),
            "qualification": profile.get("qualification", ""),
            "passing_year": profile.get("passing_year", ""),
            "percentage": profile.get("percentage", ""),
            "board_university": profile.get("board_university", ""),
            "bank_name": profile.get("bank_name", ""),
            "account_number": profile.get("account_number", ""),
            "ifsc_code": profile.get("ifsc_code", "")
        }

        # Add custom fields if any
        if "custom_fields" in profile and isinstance(profile["custom_fields"], dict):
            for k, v in profile["custom_fields"].items():
                field_values[k] = str(v)

        # File documents
        files = profile.get("files", {})

        # Process inputs and textareas
        elements = self.page.query_selector_all("input, textarea, select")
        log_cb(f"📋 Found {len(elements)} candidate interactive elements.")

        # To prevent double filling of radio groups
        handled_radio_names = set()
        uploaded_file_keys = set()

        for el in elements:
            try:
                # Skip hidden or invisible elements
                if not el.is_visible():
                    continue

                tag_name = el.evaluate("e => e.tagName.toLowerCase()")
                el_type = el.evaluate("e => e.getAttribute('type') || ''").lower() if tag_name == "input" else tag_name
                context = extract_element_context(el, self.page)

                # 1. FILE UPLOAD INPUTS
                if el_type == "file":
                    best_file_key = None
                    highest_score = 0
                    for file_key, patterns in FILE_MAPPINGS.items():
                        if file_key in files and files[file_key] and os.path.exists(files[file_key]):
                            score = calculate_match_score(context, patterns)
                            # Give higher priority to files not yet uploaded
                            if file_key not in uploaded_file_keys:
                                score += 10
                            if score > highest_score and score >= 25:
                                highest_score = score
                                best_file_key = file_key

                    # Sequential marksheet fallback if form has generic marksheet inputs
                    if not best_file_key and any(w in clean_text(context) for w in ["marksheet", "માર્કશીટ", "trial", "ટ્રાયલ", "certificate", "પ્રમાણપત્ર"]):
                        for mk in ["marksheet", "marksheet_trial1", "marksheet_trial2", "marksheet_trial3", "trial_cert", "hsc_marksheet", "degree_marksheet", "merged_marksheets"]:
                            if mk in files and mk not in uploaded_file_keys and os.path.exists(files[mk]):
                                best_file_key = mk
                                break

                    if best_file_key and files.get(best_file_key):
                        filepath = files[best_file_key]
                        el.set_input_files(filepath)
                        uploaded_file_keys.add(best_file_key)
                        self._highlight_element(el, "#3b82f6")
                        filled_count += 1
                        log_cb(f"📎 Uploading {best_file_key} ({os.path.basename(filepath)}) -> {context[:35]}")
                        details.append(f"ફાઇલ અપલોડ કરી: {best_file_key} ({os.path.basename(filepath)})")
                    elif files and len(uploaded_file_keys) == 0:
                        # Fallback for generic file input if nothing uploaded yet
                        first_key, first_doc = list(files.items())[0]
                        if first_doc and os.path.exists(first_doc):
                            el.set_input_files(first_doc)
                            uploaded_file_keys.add(first_key)
                            self._highlight_element(el, "#3b82f6")
                            filled_count += 1
                            details.append(f"ફાઇલ અપલોડ કરી: {os.path.basename(first_doc)}")

                # 2. RADIO BUTTONS
                elif el_type == "radio":
                    radio_name = el.evaluate("e => e.name || ''")
                    radio_val = clean_text(el.evaluate("e => e.value || ''"))
                    radio_label = clean_text(el.evaluate("""e => {
                        let l = e.closest('label');
                        if (l) return l.innerText;
                        if (e.id) {
                            let lbl = document.querySelector('label[for="' + e.id + '"]');
                            if (lbl) return lbl.innerText;
                        }
                        return '';
                    }"""))

                    # Test gender or category or marital status
                    for field_key in ["gender", "marital_status", "category"]:
                        raw_val = field_values.get(field_key, "")
                        if not raw_val:
                            continue

                        # Check if context matches field
                        if calculate_match_score(context, FIELD_MAPPINGS[field_key]) >= 20:
                            synonyms = get_synonyms_for_value(str(raw_val))
                            matched = False
                            for syn in synonyms:
                                if syn and (syn == radio_val or syn == radio_label or 
                                            f" {syn} " in f" {radio_label} " or f" {syn} " in f" {radio_val} "):
                                    el.check()
                                    self._highlight_element(el)
                                    filled_count += 1
                                    details.append(f"પસંદ કર્યું: {field_key} = {raw_val}")
                                    matched = True
                                    break
                            if matched:
                                break

                # 3. CHECKBOXES
                elif el_type == "checkbox":
                    cb_context = clean_text(context)
                    # Automatically tick declaration or terms & conditions checkboxes
                    if any(w in cb_context for w in ["declaration", "agree", "accept", "terms", "ખરાઈ", "મંજૂર", "બાંયધરી"]):
                        el.check()
                        self._highlight_element(el)
                        filled_count += 1
                        details.append("બાંયધરી સ્વીકારી (Declaration Checked)")

                # 4. SELECT / DROPDOWN
                elif tag_name == "select":
                    best_match_key = None
                    highest_score = 0
                    for key, patterns in FIELD_MAPPINGS.items():
                        score = calculate_match_score(context, patterns)
                        if score > highest_score and score >= 20:
                            highest_score = score
                            best_match_key = key

                    if best_match_key and field_values.get(best_match_key):
                        target_val = str(field_values[best_match_key]).strip()
                        target_synonyms = get_synonyms_for_value(target_val)

                        # Select option matching synonyms, avoiding empty placeholder options
                        res = self.page.evaluate(r"""({select, targetSynonyms}) => {
                            let clean = (t) => (t || '').toLowerCase().replace(/[^a-zA-Z0-9\u0A80-\u0AFF\s]/g, ' ').replace(/\s+/g, ' ').trim();
                            
                            let bestOption = null;
                            let highestScore = 0;

                            for (let opt of select.options) {
                                let optVal = clean(opt.value);
                                let optText = clean(opt.text);

                                // Skip disabled or placeholder options
                                if (opt.disabled) continue;
                                if (!optVal && (optText.includes('select') || optText.includes('choose') || optText.includes('પસંદ') || optText.includes('dropdown') || optText.length === 0)) {
                                    continue;
                                }

                                let score = 0;
                                for (let syn of targetSynonyms) {
                                    if (!syn || syn.length === 0) continue;
                                    
                                    // Exact match
                                    if (optText === syn || optVal === syn) {
                                        score = Math.max(score, 100);
                                    }
                                    // Word boundary match
                                    else if ((' ' + optText + ' ').includes(' ' + syn + ' ') || (' ' + optVal + ' ').includes(' ' + syn + ' ')) {
                                        score = Math.max(score, 80);
                                    }
                                    // Substring match only if length >= 3
                                    else if (syn.length >= 3 && (optText.includes(syn) || optVal.includes(syn))) {
                                        score = Math.max(score, 50);
                                    }
                                    else if (optText.length >= 3 && syn.includes(optText)) {
                                        score = Math.max(score, 30);
                                    }
                                }

                                if (score > highestScore) {
                                    highestScore = score;
                                    bestOption = opt;
                                }
                            }

                            if (bestOption && highestScore > 0) {
                                select.value = bestOption.value;
                                select.dispatchEvent(new Event('input', { bubbles: true }));
                                select.dispatchEvent(new Event('change', { bubbles: true }));
                                return { success: true, selectedText: bestOption.text || bestOption.value };
                            }
                            return { success: false };
                        }""", {"select": el, "targetSynonyms": target_synonyms})

                        if res.get("success"):
                            self._highlight_element(el)
                            filled_count += 1
                            selected_name = res.get("selectedText", target_val)
                            details.append(f"ડ્રોપડાઉનમાંથી પસંદ કર્યું: {best_match_key} -> \"{selected_name}\"")

                # 5. TEXT, NUMBER, EMAIL, TEL, DATE, TEXTAREA
                else:
                    best_match_key = None
                    highest_score = 0
                    for key, patterns in FIELD_MAPPINGS.items():
                        score = calculate_match_score(context, patterns)
                        if score > highest_score and score >= 20:
                            highest_score = score
                            best_match_key = key

                    if best_match_key and field_values.get(best_match_key):
                        val_to_fill = str(field_values[best_match_key]).strip()

                        # Format DOB if type is date
                        if el_type == "date" and best_match_key == "dob":
                            # normalize date YYYY-MM-DD
                            val_to_fill = self._format_date_for_input(val_to_fill)

                        el.fill(val_to_fill)
                        self._highlight_element(el)
                        filled_count += 1
                        display_val = val_to_fill if len(val_to_fill) <= 30 else val_to_fill[:27] + "..."
                        details.append(f"ભર્યું: {best_match_key} -> {display_val}")
                    else:
                        skipped_count += 1

            except Exception as e:
                # element might have become detached or dynamic
                continue

        # Inject assistant banner at the top of the webpage
        self._inject_success_banner(filled_count)

        # Capture high-res screenshot of filled form for Cloud and Mobile preview
        screenshot_url = None
        try:
            screenshots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "screenshots")
            os.makedirs(screenshots_dir, exist_ok=True)
            shot_filename = f"filled_{int(time.time())}.png"
            shot_path = os.path.join(screenshots_dir, shot_filename)
            self.page.screenshot(path=shot_path, full_page=True)
            screenshot_url = f"/static/screenshots/{shot_filename}"
            log_cb(f"📸 ફોર્મનો લાઈવ પ્રિવ્યુ સ્ક્રીનશોટ લેવાઈ ગયો છે.")
        except Exception as e:
            pass

        log_cb(f"✅ Auto-fill complete! Filled {filled_count} fields and files.")
        log_cb("💡 Browser is remaining open for you to verify, fill any captcha, and submit!")

        return {
            "success": True,
            "filled_count": filled_count,
            "skipped_count": skipped_count,
            "details": details,
            "screenshot_url": screenshot_url
        }

    def _format_date_for_input(self, dob_str: str) -> str:
        """Attempts to format date as YYYY-MM-DD."""
        dob_clean = dob_str.replace("/", "-").replace(".", "-").strip()
        parts = dob_clean.split("-")
        if len(parts) == 3:
            # If DD-MM-YYYY
            if len(parts[0]) <= 2 and len(parts[2]) == 4:
                return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
            # If YYYY-MM-DD
            elif len(parts[0]) == 4:
                return f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
        return dob_str

    def _highlight_element(self, element: ElementHandle, color: str = "#10b981"):
        """Draws a noticeable colored highlight around auto-filled elements."""
        try:
            element.evaluate(f"""(el) => {{
                el.style.border = '2px solid {color}';
                el.style.boxShadow = '0 0 8px {color}88';
                el.style.transition = 'all 0.3s ease';
            }}""")
        except Exception:
            pass

    def _inject_success_banner(self, count: int):
        """Injects a floating helper notification in the target webpage."""
        try:
            self.page.evaluate(f"""() => {{
                let existing = document.getElementById('ai-form-filler-banner');
                if (existing) existing.remove();

                let banner = document.createElement('div');
                banner.id = 'ai-form-filler-banner';
                banner.style.position = 'fixed';
                banner.style.bottom = '20px';
                banner.style.right = '20px';
                banner.style.zIndex = '9999999';
                banner.style.backgroundColor = '#0f172a';
                banner.style.color = '#ffffff';
                banner.style.padding = '14px 20px';
                banner.style.borderRadius = '12px';
                banner.style.boxShadow = '0 10px 25px -5px rgba(0, 0, 0, 0.4)';
                banner.style.fontFamily = 'system-ui, -apple-system, sans-serif';
                banner.style.fontSize = '14px';
                banner.style.display = 'flex';
                banner.style.alignItems = 'center';
                banner.style.gap = '12px';
                banner.style.border = '1px solid #334155';

                banner.innerHTML = `
                    <div style="background:#10b981; color:#fff; width:30px; height:30px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:16px;">✓</div>
                    <div>
                        <div style="font-weight:600; color:#38bdf8;">AI Smart Form Filler Active</div>
                        <div style="color:#cbd5e1; font-size:12px;">સફળતાપૂર્વક <b>${count}</b> ફીલ્ડ અને ફાઇલ ભરાઈ ગઈ છે. કૃપા કરીને ચકાસીને સબમિટ કરો.</div>
                    </div>
                    <button onclick="this.parentElement.remove()" style="background:transparent; border:none; color:#94a3b8; font-size:18px; cursor:pointer; margin-left:10px;">✕</button>
                `;
                document.body.appendChild(banner);
            }}""")
        except Exception:
            pass

    def close(self):
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except Exception:
            pass
