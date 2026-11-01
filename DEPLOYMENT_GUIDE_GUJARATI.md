# 🌐 AI Form Auto-Filler - ૨૪x૭ ઓનલાઇન ક્લાઉડ ડિપ્લોયમેન્ટ ગાઈડ

આ ગાઈડની મદદથી તમે આ સોફ્ટવેરને ઇન્ટરનેટ પર **Render.com (૧૦૦% મફત)** અથવા કોઈપણ **Linux VPS (DigitalOcean / AWS / Hetzner)** પર ૨૪ કલાક લાઈવ મૂકી શકો છો, જેથી તમે **ગમે ત્યાંથી મોબાઈલ કે લેપટોપ વડે** ફોર્મ ભરી શકો!

---

## 🌟 વિકલ્પ ૧: Render.com પર મફતમાં ૨૪x૭ લાઈવ કરવું (સૌથી સરળ - ૫ મિનિટમાં)

Render.com પર આપણે બનાવેલ `Dockerfile` આપોઆપ ચાલે છે, જેમાં Python, Google Chromium અને તમામ ગુજરાતી ફોન્ટ પહેલેથી સેટ કરેલા છે.

### 📝 સ્ટેપ ૧: કોડ GitHub પર અપલોડ કરો (Upload to GitHub)
1. તમારા બ્રાઉઝરમાં [github.com](https://github.com) ખોલો અને એક નવું રિપોઝીટરી (Repository) બનાવો (દા.ત. `ai-form-filler`).
2. તમારા કમ્પ્યુટરમાં `d:\ai-auto-video-editor\ai_form_filler` ફોલ્ડરમાંથી ફાઇલો ગીટહબમાં પુશ (Push) કરો:
```bash
cd d:\ai-auto-video-editor\ai_form_filler
git init
git add .
git commit -m "AI Form Auto-Filler Cloud Ready"
git branch -M main
git remote add origin https://github.com/તમારું-યુઝરનેમ/ai-form-filler.git
git push -u origin main
```

---

### 📝 સ્ટેપ ૨: Render.com પર સર્વિસ શરૂ કરો
1. [render.com](https://render.com) પર જાઓ અને મફતમાં એકાઉન્ટ બનાવી સાઇન-ઇન કરો (GitHub થી સીધું સાઇન-ઇન થઈ જશે).
2. ડેશબોર્ડ પર **"New +"** બટન દબાવો અને **"Web Service"** પસંદ કરો.
3. તમે ગીટહબ પર બનાવેલ રિપોઝીટરી (`ai-form-filler`) સિલેક્ટ કરો અને **Connect** દબાવો.
4. નીચે મુજબની સરળ સેટિંગ્સ ભરો:
   - **Name**: `my-form-filler` (અથવા તમારી પસંદનું નામ)
   - **Region**: `Singapore` (ભારત માટે સૌથી ફાસ્ટ સ્પીડ આપશે)
   - **Environment**: **`Docker`** (આપણી Dockerfile આપોઆપ સિલેક્ટ થઈ જશે)
   - **Plan Type**: **`Free`** ($0 / મહિનો - ૧૦૦% મફત!)
5. નીચે આપેલ **"Create Web Service"** વાદળી બટન દબાવો!

---

### 🚀 સ્ટેપ ૩: તમારી લાઈવ લિંક તૈયાર!
- ૨-૩ મિનિટમાં Render આપમેળે Docker કન્ટેનર બિલ્ડ કરી દેશે.
- સ્ક્રીન પર તમને તમારી કાયમી લાઈવ વેબસાઇટ લિંક મળશે:  
  👉 **`https://my-form-filler.onrender.com`**
- આ લિંક તમે તમારા મોબાઈલમાં, ટેબ્લેટમાં કે કોઈ પણ કમ્પ્યુટરમાં ૨૪ કલાક ખોલી શકો છો!

---

## 🌟 વિકલ્પ ૨: પોતાના Linux VPS પર ડિપ્લોય કરવું (Docker વડે)

જો તમારી પાસે DigitalOcean, Hostinger કે AWS નું VPS સર્વર હોય, તો ૧ જ કમાન્ડથી આખું સોફ્ટવેર ચાલી જશે:

```bash
# ૧. પ્રોજેક્ટ ફોલ્ડરમાં જાઓ
cd ai_form_filler

# ૨. ડોકર ઇમેજ બિલ્ડ કરો
docker build -t form-filler .

# ૩. ૨૪ કલાક બેકગ્રાઉન્ડમાં રન કરો (Port 5000)
docker run -d --restart=always -p 5000:5000 --name ai-form-filler form-filler
```

હવે તમે તમારા સર્વરના IP વડે બ્રાઉઝરમાં ઓપન કરી શકો છો:
`http://તમારો-સર્વર-IP:5000`

---

## 📱 ક્લાઉડ પર ફોર્મ કેવી રીતે ભરાશે?
1. તમે મોબાઇલ કે અન્ય પીસીમાંથી તમારી લાઈવ વેબસાઇટ ખોલો.
2. ઉમેદવાર પસંદ કરો અને ફોર્મની લિંક નાખીને **"ઓટોમેટિક ફોર્મ ભરો"** દબાવો.
3. ક્લાઉડ સર્વર બેકગ્રાઉન્ડમાં ફોર્મ ખોલીને બધી વિગતો અને ડોક્યુમેન્ટ્સ ૧ સેકન્ડમાં ભરી દેશે.
4. **લાઈવ સ્ક્રીનશોટ**: ફોર્મ ભરાઈ ગયા પછી તેનો આખો ફોટો (Screenshot) તમારી મોબાઇલ સ્ક્રીન પર દેખાશે જેથી તમે ચકાસી શકો!
