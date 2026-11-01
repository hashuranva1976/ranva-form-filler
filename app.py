import os
import sys

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import json
import uuid
import logging
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont
import jinja2

from engine import FormFillerEngine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "profiles.json")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

template_dir = os.path.join(BASE_DIR, "templates") if os.path.isdir(os.path.join(BASE_DIR, "templates")) else BASE_DIR
app = Flask(__name__, template_folder=template_dir, static_folder="static")
CORS(app)

# Support templates both in templates/ folder and in root directory
template_search_dirs = [
    os.path.join(BASE_DIR, "templates"),
    BASE_DIR
]
app.jinja_loader = jinja2.ChoiceLoader([
    jinja2.FileSystemLoader(d) for d in template_search_dirs if os.path.exists(d)
])

os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

# In-memory browser engine instance tracking so user can keep multiple sessions or active window
active_engines = {}

def get_profiles():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_profiles(profiles):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(profiles, f, ensure_ascii=False, indent=2)

@app.route("/")
def index():
    try:
        return render_template("index.html")
    except Exception:
        pass
    for path in [os.path.join(BASE_DIR, "index.html"), os.path.join(BASE_DIR, "templates", "index.html")]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read(), 200, {"Content-Type": "text/html; charset=utf-8"}
    return "<h3>Error: index.html not found</h3>", 404

@app.route("/demo-form")
def demo_form():
    try:
        return render_template("demo_portal.html")
    except Exception:
        pass
    for path in [os.path.join(BASE_DIR, "demo_portal.html"), os.path.join(BASE_DIR, "templates", "demo_portal.html")]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read(), 200, {"Content-Type": "text/html; charset=utf-8"}
    return "<h3>Error: demo_portal.html not found</h3>", 404

@app.route("/api/profiles", methods=["GET"])
def list_profiles():
    return jsonify(get_profiles())

@app.route("/api/profiles/save", methods=["POST"])
def save_profile():
    try:
        profile_id = request.form.get("id") or str(uuid.uuid4())[:8]
        profiles = get_profiles()
        
        # Check existing
        existing = next((p for p in profiles if p["id"] == profile_id), None)
        profile_data = existing or {"id": profile_id, "files": {}}
        
        # Update text fields
        fields = [
            "first_name", "middle_name", "last_name", "full_name",
            "dob", "gender", "category", "marital_status", "nationality", "religion",
            "mobile", "alternate_mobile", "email", "address_line1", "address_line2",
            "village_city", "taluka", "district", "state", "pincode",
            "aadhaar", "pan", "voter_id", "bank_name", "account_number", "ifsc_code",
            "qualification", "board_university", "passing_year", "percentage",
            "trials_count"
        ]
        for field in fields:
            if field in request.form:
                profile_data[field] = request.form.get(field).strip()

        # Handle file uploads (including multiple trial marksheets & certificates)
        file_keys = [
            "photo", "signature", "aadhaar_doc", "pan_doc", "ration_card",
            "fee_receipt", "bonafide_id", "break_affidavit", "caste_cert",
            "income_cert", "lc_doc", "bank_passbook", "ssc_marksheet",
            "marksheet", "marksheet_trial1", "marksheet_trial2", "marksheet_trial3",
            "trial_cert", "hsc_marksheet", "degree_marksheet", "otr_slip", "resume"
        ]
        for fk in file_keys:
            form_file_name = f"file_{fk}"
            if form_file_name in request.files:
                file = request.files[form_file_name]
                if file and file.filename:
                    ext = os.path.splitext(file.filename)[1]
                    saved_filename = f"{profile_id}_{fk}{ext}"
                    filepath = os.path.join(UPLOADS_DIR, saved_filename)
                    file.save(filepath)
                    profile_data.setdefault("files", {})[fk] = filepath

        if not existing:
            profiles.append(profile_data)
        
        save_profiles(profiles)
        return jsonify({"success": True, "profile": profile_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/profiles/import-folder", methods=["POST"])
def import_from_folder():
    """Scans a local folder and automatically links all document images to candidate profile."""
    try:
        data = request.json or {}
        folder_path = data.get("folder_path")
        candidate_name = data.get("candidate_name", "New Candidate")

        if not folder_path or not os.path.isdir(folder_path):
            return jsonify({"success": False, "error": "આપેલ ફોલ્ડર મળ્યું નથી."}), 400

        files = os.listdir(folder_path)
        detected_files = {}

        for f in files:
            fp = os.path.join(folder_path, f)
            if not os.path.isfile(fp):
                continue
            fl = f.lower()

            if "photo" in fl:
                detected_files["photo"] = fp
            elif "aadhaar" in fl and fl.endswith((".jpg", ".jpeg", ".png")):
                detected_files["aadhaar_doc"] = fp
            elif "aadhaar" in fl and fl.endswith(".pdf"):
                detected_files["aadhaar_pdf"] = fp
            elif "ration" in fl or "kupan" in fl:
                detected_files["ration_card"] = fp
            elif "fee" in fl:
                detected_files["fee_receipt"] = fp
            elif "idcard" in fl or "bonafide" in fl:
                detected_files["bonafide_id"] = fp
            elif "break" in fl or "affidavit" in fl or "gap" in fl:
                detected_files["break_affidavit"] = fp
            elif "caste" in fl:
                detected_files["caste_cert"] = fp
            elif "income" in fl:
                detected_files["income_cert"] = fp
            elif "lc" in fl or "leaving" in fl:
                detected_files["lc_doc"] = fp
            elif "passbook" in fl or "bank" in fl:
                detected_files["bank_passbook"] = fp
            elif "ssc" in fl:
                detected_files["ssc_marksheet"] = fp
                detected_files["marksheet"] = fp
            elif "hsc" in fl or "12" in fl:
                detected_files["hsc_marksheet"] = fp
            elif "mar-2024" in fl or "mar_2024" in fl or "mar2024" in fl:
                detected_files["marksheet_trial1"] = fp
            elif "jun" in fl or "jun2024" in fl:
                detected_files["marksheet_trial2"] = fp
            elif "otr" in fl:
                detected_files["otr_slip"] = fp
            elif "resume" in fl or "cv" in fl:
                detected_files["resume"] = fp

        return jsonify({
            "success": True, 
            "detected_count": len(detected_files),
            "files": detected_files
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/profiles/<profile_id>/merge-marksheets", methods=["POST"])
def merge_marksheets(profile_id):
    """Combines all uploaded marksheets into a single multi-page PDF."""
    try:
        profiles = get_profiles()
        p = next((x for x in profiles if x["id"] == profile_id), None)
        if not p or "files" not in p:
            return jsonify({"success": False, "error": "Profile not found"}), 404

        marksheet_keys = ["marksheet", "marksheet_trial1", "marksheet_trial2", "marksheet_trial3", "trial_cert", "hsc_marksheet", "degree_marksheet"]
        image_files = []
        for k in marksheet_keys:
            if k in p["files"] and os.path.exists(p["files"][k]):
                fp = p["files"][k]
                ext = os.path.splitext(fp)[1].lower()
                if ext in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
                    image_files.append(fp)

        if not image_files:
            return jsonify({"success": False, "error": "કોઈ માર્કશીટ ઈમેજ ફાઇલ મળી નથી."}), 400

        pil_images = []
        for impath in image_files:
            im = Image.open(impath).convert("RGB")
            pil_images.append(im)

        merged_pdf_path = os.path.join(UPLOADS_DIR, f"{profile_id}_merged_marksheets.pdf")
        pil_images[0].save(merged_pdf_path, save_all=True, append_images=pil_images[1:])
        
        p["files"]["merged_marksheets"] = merged_pdf_path
        save_profiles(profiles)

        return jsonify({
            "success": True, 
            "count": len(image_files),
            "merged_path": merged_pdf_path
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/profiles/<profile_id>", methods=["DELETE"])
def delete_profile(profile_id):
    profiles = get_profiles()
    profiles = [p for p in profiles if p["id"] != profile_id]
    save_profiles(profiles)
    return jsonify({"success": True})

@app.route("/api/files/<profile_id>/<file_key>")
def serve_profile_file(profile_id, file_key):
    profiles = get_profiles()
    p = next((x for x in profiles if x["id"] == profile_id), None)
    if p and "files" in p and file_key in p["files"]:
        fp = p["files"][file_key]
        if os.path.exists(fp):
            return send_file(fp)
    return "File not found", 404

@app.route("/api/profiles/load-sample", methods=["POST"])
def load_sample():
    """Generates a rich sample Gujarati candidate profile with demo photo and sign."""
    try:
        sample_id = "sample_rajesh"
        profiles = get_profiles()
        profiles = [p for p in profiles if p["id"] != sample_id]

        # Generate sample passport photo
        photo_path = os.path.join(UPLOADS_DIR, f"{sample_id}_photo.png")
        img = Image.new("RGB", (200, 240), color=(224, 242, 254))
        d = ImageDraw.Draw(img)
        # Head & body silhouette
        d.ellipse([(60, 40), (140, 120)], fill=(37, 99, 235))
        d.pieslice([(30, 130), (170, 260)], 180, 360, fill=(30, 64, 175))
        d.text((50, 210), "PASSPORT PHOTO", fill=(100, 116, 139))
        img.save(photo_path)

        # Generate sample signature
        sign_path = os.path.join(UPLOADS_DIR, f"{sample_id}_signature.png")
        sign_img = Image.new("RGB", (250, 100), color=(255, 255, 255))
        sd = ImageDraw.Draw(sign_img)
        sd.line([(20, 60), (60, 40), (90, 70), (140, 35), (200, 55), (230, 50)], fill=(15, 23, 42), width=3)
        sd.text((70, 75), "Rajesh Patel", fill=(71, 85, 105))
        sign_img.save(sign_path)

        sample_profile = {
            "id": sample_id,
            "first_name": "રાજેશકુમાર",
            "middle_name": "મહેશભાઈ",
            "last_name": "પટેલ",
            "full_name": "રાજેશકુમાર મહેશભાઈ પટેલ",
            "dob": "1998-05-15",
            "gender": "Male",
            "category": "OBC",
            "marital_status": "Single",
            "nationality": "Indian",
            "religion": "Hindu",
            "mobile": "9876543210",
            "alternate_mobile": "9898989898",
            "email": "rajesh.patel.demo@gmail.com",
            "address_line1": "૪૨, શાંતિ નિકેતન સોસાયટી, સી.જી. રોડ",
            "address_line2": "નવરંગપુરા",
            "village_city": "અમદાવાદ",
            "taluka": "અમદાવાદ સિટી",
            "district": "અમદાવાદ",
            "state": "Gujarat",
            "pincode": "380009",
            "aadhaar": "987654321012",
            "pan": "ABCDE1234F",
            "voter_id": "GJ012345678",
            "bank_name": "State Bank of India (SBI)",
            "account_number": "30123456789",
            "ifsc_code": "SBIN0001234",
            "qualification": "Graduate",
            "board_university": "Gujarat University",
            "passing_year": "2020",
            "percentage": "76.40",
            "files": {
                "photo": photo_path,
                "signature": sign_path
            }
        }

        profiles.append(sample_profile)
        save_profiles(profiles)
        return jsonify({"success": True, "profile_id": sample_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/fill", methods=["POST"])
def fill_form():
    """Fills the target URL in real Chrome using Playwright."""
    data = request.json or {}
    profile_id = data.get("profile_id")
    url = data.get("url")

    if not profile_id or not url:
        return jsonify({"success": False, "error": "Profile ID અને URL બંને જરૂરી છે."}), 400

    profiles = get_profiles()
    profile = next((p for p in profiles if p["id"] == profile_id), None)
    if not profile:
        return jsonify({"success": False, "error": "પ્રોફાઇલ મળી નથી."}), 404

    logs = []
    def log_tracker(msg):
        logs.append(msg)
        print(f"[FormFiller] {msg}")

    # Close previous browser instance for this profile if still open
    if profile_id in active_engines:
        try:
            active_engines[profile_id].close()
        except Exception:
            pass

    browser_choice = data.get("browser", "chrome")
    is_cloud = os.environ.get("IS_CLOUD_DEPLOY") == "true" or sys.platform != "win32"

    def do_fill():
        engine = FormFillerEngine(headless=False, browser_channel=browser_choice)
        try:
            engine.start()
            if not is_cloud:
                active_engines[profile_id] = engine

            res = engine.fill(url, profile, log_cb=log_tracker)
            if not is_cloud:
                engine.bring_to_front_window()
            else:
                engine.close()
            return res
        except Exception:
            try:
                engine.close()
            except Exception:
                pass
            raise

    try:
        import concurrent.futures
        # Execute in a dedicated clean worker thread to completely prevent "Playwright Sync API inside asyncio loop"
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            res = executor.submit(do_fill).result()

        return jsonify({
            "success": True,
            "filled_count": res.get("filled_count", 0),
            "skipped_count": res.get("skipped_count", 0),
            "details": res.get("details", []),
            "screenshot_url": res.get("screenshot_url"),
            "logs": logs
        })
    except Exception as e:
        if profile_id in active_engines:
            del active_engines[profile_id]
        return jsonify({"success": False, "error": str(e), "logs": logs}), 500

if __name__ == "__main__":
    port = 5000
    print(f"===============================================================")
    print(f"🚀 AI Online Form Auto-Filler is running!")
    print(f"👉 Open in browser: http://127.0.0.1:{port}")
    print(f"👉 Built-in Demo Form: http://127.0.0.1:{port}/demo-form")
    print(f"===============================================================")
    app.run(host="0.0.0.0", port=port, debug=False)
