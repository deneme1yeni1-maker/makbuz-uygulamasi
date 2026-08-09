import flet as ft
import os
import sys
from datetime import datetime
import threading
import time

# --- AYARLAR ---
COLOR_BG = "#0F0F0F"
COLOR_ACCENT = "#FFFFFF"  
COLOR_WHITE = "#FFFFFF"

if getattr(sys, 'frozen', False): 
    application_path = os.path.dirname(sys.executable)
else: 
    application_path = os.path.dirname(os.path.abspath(__file__))

# APK için galeri yolu (Android'de DCIM klasörü galeride görünür)
if sys.platform == "android":
    BASE_SAVE_DIR = "/sdcard/DCIM/Apartman_Makbuzlari"
else:
    BASE_SAVE_DIR = os.path.join(application_path, "MAKBUZLAR_GALERI")

if not os.path.exists(BASE_SAVE_DIR):
    os.makedirs(BASE_SAVE_DIR, exist_ok=True)

# Yılın tüm ayları
AYLAR = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]

def makbuz_uret(daire_bilgisi, ay):
    from PIL import Image, ImageDraw, ImageFont
    
    daire_no = daire_bilgisi.split(":")[0].strip()
    kisi_bilgisi = daire_bilgisi.split(":")[1].strip()
    
    # Her sakinin kendi ismine özel klasör yolu
    sakin_klasor_adi = f"Daire NO-{daire_no} {kisi_bilgisi}"
    sakin_klasor_yolu = os.path.join(BASE_SAVE_DIR, sakin_klasor_adi)
    
    if not os.path.exists(sakin_klasor_yolu):
        os.makedirs(sakin_klasor_yolu, exist_ok=True)
    
    temiz_ay = ay.split('_')[0]
    dosya_adi = f"{sakin_klasor_adi}_2026_{temiz_ay}_AİDAT_MAKBUZU.jpg"
    arsiv_tam_yol = os.path.join(sakin_klasor_yolu, dosya_adi)
    
    img = Image.new("RGB", (1000, 700), "white")
    
    resimler = [
        (os.path.join(application_path, "3-Başlık Resmi.jpg"), (50, 40)), 
        (os.path.join(application_path, "6.jpg"), (520, 40)), 
        (os.path.join(application_path, "1-kaşe ve imza.jpg"), (600, 450))
    ]
    for dosya, konum in resimler:
        if os.path.exists(dosya):
            with Image.open(dosya) as r: img.paste(r, konum)
    
    onay_yolu = os.path.join(application_path, "onay.png")
    if os.path.exists(onay_yolu):
        with Image.open(onay_yolu).convert("RGBA") as onay: img.paste(onay, (650, 250), onay)
    
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(os.path.join(application_path, "DejaVuSans.ttf"), 35)
        font_bold = ImageFont.truetype(os.path.join(application_path, "DejaVuSans-Bold.ttf"), 40)
        font_small = ImageFont.truetype(os.path.join(application_path, "DejaVuSans-Bold.ttf"), 30)
    except: 
        font = font_bold = font_small = ImageFont.load_default()
        
    draw.text((100, 260), f"SAYIN: {kisi_bilgisi.upper()}", fill="black", font=font_bold)
    draw.text((100, 310), f"DAİRE NO: {daire_no}", fill="black", font=font)
    draw.text((100, 360), f"DÖNEM: {temiz_ay.upper()} AYI AİDATI", fill="black", font=font)
    draw.text((100, 410), "YALNIZ: - ÜÇ YÜZ ELLİ TL -", fill="black", font=font_bold)
    
    draw.text((680, 150), datetime.now().strftime("%d.%m.%Y"), fill="red", font=font)
    draw.rectangle([100, 520, 630, 580], outline="black", width=1) 
    draw.text((112, 532), f"2026/AYLIK AİDAT 350 TL", fill="red", font=font_small)
    
    draw.rectangle([10, 10, 990, 690], outline="black", width=5)
    img.convert("RGB").save(arsiv_tam_yol, "JPEG")
    return arsiv_tam_yol

class MakbuzUygulamasi:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Sabahoğlu Apartmanı"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = COLOR_BG
        
        self.sakinler = [
            "1: Ahmet KAYA", "2: Ahmet DOKUMACI", "3: Osman ÖZDUYGU", "4: Aygün KAPLAN", 
            "5: Vidat ÇALIŞ", "6: Salih ESMER", "7: Hadra ŞEN", "8: İlyas ZARİFGİL", 
            "9: Mehmet KAZAK", "10: Yeliz DÜNDAR", "11: Mehmet Emin KARAKURT", "12: Mustafa UĞURLU", 
            "13: Ahmet SABAHOĞLU", "15: Veysel AKTAŞ", "16: Mehmet GELMEZ"
        ]
        
        self.borc_text = ft.Text(value="", size=14, color=COLOR_WHITE, weight="bold")
        
        self.isim_dropdown = ft.Dropdown(
            label="Sakin Seçin", 
            options=[ft.dropdown.Option(i) for i in self.sakinler], 
            width=260, color=COLOR_WHITE, border_color=COLOR_ACCENT
        )
        self.isim_dropdown.on_change = self.sakin_secildi
        
        self.sorgula_btn = ft.ElevatedButton(
            "BORÇ SORGU", 
            on_click=self.sakin_secildi, 
            bgcolor="#D32F2F", 
            color="#FFFFFF", 
            width=120, 
            height=50
        )
        
        self.ay_dropdown = ft.Dropdown(
            label="Dönem Seçin", 
            options=[ft.dropdown.Option(f"{m}_2026") for m in AYLAR], 
            width=390, color=COLOR_WHITE, border_color=COLOR_ACCENT
        )
        
        self.btn = ft.ElevatedButton(
            "MAKBUZ ÜRET / İPTAL ET", 
            on_click=self.uret_tiklandi, 
            bgcolor=COLOR_ACCENT, 
            color="black", 
            width=390, 
            height=50
        )
        
        self.paylas_btn = ft.ElevatedButton(
            "WHATSAPP'TAN PAYLAŞ", 
            on_click=self.whatsapp_ile_paylas, 
            bgcolor="#25D366", 
            color="white", 
            width=390, 
            height=50
        )
        
        self.page.add(
            ft.Container(height=20),
            ft.Row([ft.Text("SABAHOĞLU APARTMANI MAKBUZ", size=20, weight="bold", color=COLOR_ACCENT)], alignment="center"),
            ft.Container(height=15),
            ft.Row([self.isim_dropdown, self.sorgula_btn], alignment="center", spacing=10),
            ft.Container(height=5),
            ft.Row([self.borc_text], alignment="center"),
            ft.Container(height=10),
            ft.Row([self.ay_dropdown], alignment="center"),
            ft.Container(height=15),
            ft.Row([self.btn], alignment="center"),
            ft.Container(height=10),
            ft.Row([self.paylas_btn], alignment="center")
        )

    def sakin_secildi(self, e):
        if not self.isim_dropdown.value:
            self.borc_text.value = "Lütfen önce bir sakin seçin."
            self.borc_text.update()
            return
        
        daire_bilgisi = self.isim_dropdown.value
        daire_no = daire_bilgisi.split(":")[0].strip()
        kisi_bilgisi = daire_bilgisi.split(":")[1].strip()
        
        sakin_klasor_adi = f"Daire NO-{daire_no} {kisi_bilgisi}"
        sakin_klasor_yolu = os.path.join(BASE_SAVE_DIR, sakin_klasor_adi)
        
        simdi = datetime.now()
        su_anki_ay_index = simdi.month if simdi.year == 2026 else 12
        
        odenmeyenler = []
        for i in range(su_anki_ay_index):
            ay = AYLAR[i]
            dosya_adi = f"{sakin_klasor_adi}_2026_{ay}_AİDAT_MAKBUZU.jpg"
            arsiv_tam_yol = os.path.join(sakin_klasor_yolu, dosya_adi)
            
            if not os.path.exists(arsiv_tam_yol):
                odenmeyenler.append(ay)
        
        if odenmeyenler:
            self.borc_text.value = f"Borçlu Olduğu Aylar: {', '.join(odenmeyenler)}"
        else:
            self.borc_text.value = "Güncel aya kadar tüm borçlar ödenmiş."
            
        self.borc_text.update()

    def uret_tiklandi(self, e):
        if not self.isim_dropdown.value or not self.ay_dropdown.value:
            return
        
        daire_bilgisi = self.isim_dropdown.value
        daire_no = daire_bilgisi.split(":")[0].strip()
        kisi_bilgisi = daire_bilgisi.split(":")[1].strip()
        
        sakin_klasor_adi = f"Daire NO-{daire_no} {kisi_bilgisi}"
        sakin_klasor_yolu = os.path.join(BASE_SAVE_DIR, sakin_klasor_adi)
        
        temiz_ay = self.ay_dropdown.value.split('_')[0]
        dosya_adi = f"{sakin_klasor_adi}_2026_{temiz_ay}_AİDAT_MAKBUZU.jpg"
        arsiv_tam_yol = os.path.join(sakin_klasor_yolu, dosya_adi)

        if os.path.exists(arsiv_tam_yol):
            os.remove(arsiv_tam_yol)
            self.btn.text = "MAKBUZ SİLİNDİ"
            self.btn.bgcolor = "#d32f2f" 
            self.btn.color = "white"
        else:
            makbuz_uret(daire_bilgisi, self.ay_dropdown.value)
            self.btn.text = "MAKBUZ OLUŞTURULDU"
            self.btn.bgcolor = "#2e7d32" 
            self.btn.color = "white"
            
        self.btn.update()
        self.sakin_secildi(None)
        
        def reset():
            time.sleep(2)
            self.btn.text = "MAKBUZ ÜRET / İPTAL ET"
            self.btn.bgcolor = COLOR_ACCENT
            self.btn.color = "black"
            self.btn.update()
        threading.Thread(target=reset).start()

    def whatsapp_ile_paylas(self, e):
        if not self.isim_dropdown.value or not self.ay_dropdown.value:
            self.borc_text.value = "Önce sakin ve dönem seçmelisiniz."
            self.borc_text.update()
            return

        daire_bilgisi = self.isim_dropdown.value
        daire_no = daire_bilgisi.split(":")[0].strip()
        kisi_bilgisi = daire_bilgisi.split(":")[1].strip()
        sakin_klasor_adi = f"Daire NO-{daire_no} {kisi_bilgisi}"
        temiz_ay = self.ay_dropdown.value.split('_')[0]
        dosya_adi = f"{sakin_klasor_adi}_2026_{temiz_ay}_AİDAT_MAKBUZU.jpg"
        arsiv_tam_yol = os.path.join(BASE_SAVE_DIR, sakin_klasor_adi, dosya_adi)

        if os.path.exists(arsiv_tam_yol):
            if sys.platform == "android":
                try:
                    cmd = f"am start -a android.intent.action.SEND -t image/jpeg --eu android.intent.extra.STREAM file://{arsiv_tam_yol}"
                    os.system(cmd)
                except Exception:
                    self.borc_text.value = "Paylaşım başlatılamadı."
                    self.borc_text.update()
            else:
                self.borc_text.value = "Bu özellik yalnızca Android cihazlarda çalışır."
                self.borc_text.update()
        else:
            self.borc_text.value = "Önce bu döneme ait makbuz üretmelisiniz!"
            self.borc_text.update()

ft.app(target=MakbuzUygulamasi)