import pandas as pd
import unicodedata
from fpdf import FPDF
import tempfile
import os
import subprocess

# FONT DOSYA YOLUNU BURAYA YAZ (Kendi bilgisayarındaki tam yol)
FONT_PATH = '/Users/beyzaozdemir/Downloads/dejavu-sans'

# Veri setini yükle
file_path = '/Users/beyzaozdemir/Documents/adsız klasör/inditex_120_product_synthetic_dataset.csv'

df = pd.read_csv(file_path, sep=";")

# Karbon Karnesi hesaplama fonksiyonu
def karbon_karnesi(row):
    score = 0
    median_emission = df["Greenhouse_Gas_Emissions(kg_CO2e)"].median()

    if pd.notna(row["Greenhouse_Gas_Emissions(kg_CO2e)"]) and row["Greenhouse_Gas_Emissions(kg_CO2e)"] <= median_emission:
        score += 30
    if pd.notna(row["Expected_CO2_Reduction(kg)"]) and row["Expected_CO2_Reduction(kg)"] >= 1.5:
        score += 30
    if pd.notna(row["ROI_Months"]) and row["ROI_Months"] <= 12:
        score += 20
    if pd.notna(row["Recycled_Material_Use(%)"]) and row["Recycled_Material_Use(%)"] >= 30:
        score += 10
    if pd.notna(row["Renewable_Energy_Use(%)"]) and row["Renewable_Energy_Use(%)"] >= 50:
        score += 10

    return score

df["Carbon_Report_Score"] = df.apply(karbon_karnesi, axis=1)

# Strateji öneri fonksiyonu
def strateji_onerisi(row):
    öneriler = []

    if pd.notna(row["Greenhouse_Gas_Emissions(kg_CO2e)"]) and row["Greenhouse_Gas_Emissions(kg_CO2e)"] > df["Greenhouse_Gas_Emissions(kg_CO2e)"].median():
        öneriler.append("Malzeme değiştir (geri dönüştürülmüş kullan)")
    if pd.notna(row["Renewable_Energy_Use(%)"]) and row["Renewable_Energy_Use(%)"] < 40:
        öneriler.append("Yenilenebilir enerji kullanımını artır")
    if pd.notna(row["Energy_Efficiency_Score"]) and row["Energy_Efficiency_Score"] < 70:
        öneriler.append("Enerji verimliliği yatırımı yap")
    if pd.notna(row["Recycled_Material_Use(%)"]) and row["Recycled_Material_Use(%)"] < 20:
        öneriler.append("Geri dönüştürülmüş içerik oranını artır")
    if pd.notna(row["ROI_Months"]) and row["ROI_Months"] > 12:
        öneriler.append("Düşük geri dönüşlü stratejilerden kaçın")

    return öneriler[:3]

df["Strategy_Combo"] = df.apply(strateji_onerisi, axis=1)

# Fırsat değerlendirme fonksiyonu
def fırsat_değerlendirme(row):
    if pd.notna(row["Consumer_Trend_Score"]) and pd.notna(row["Greenhouse_Gas_Emissions(kg_CO2e)"]):
        if row["Consumer_Trend_Score"] >= 80 and row["Greenhouse_Gas_Emissions(kg_CO2e)"] <= 3.0:
            return "Yüksek tüketici ilgisiyle öne çıkarılabilir"
        elif row["Consumer_Trend_Score"] < 70 and row["Greenhouse_Gas_Emissions(kg_CO2e)"] > 4.5:
            return "İmaj riski yüksek, dönüşüm önerilir"
    return "Dengeli"

df["Opportunity_Insight"] = df.apply(fırsat_değerlendirme, axis=1)

# PDF için metin temizleyici (Türkçe karakter sorununu engellemek için sadece gerekli)
def clean_text(text):
    if isinstance(text, str):
        # unicodedata ile türkçe karakterler korunabilir ama fpdf default latin1 hatası için font gerekli
        return text
    return str(text)

# PDF rapor sınıfı
class FinalCarbonReportPDF(FPDF):
    def header(self):
        self.set_font("DejaVu", "", 14)
        self.cell(0, 10, "Carbon Footprint Report Card", ln=True, align="C")
        self.ln(10)

    def product_report(self, row):
        self.set_font("DejaVu", "", 12)
        self.multi_cell(0, 10, f"Company: {clean_text(row.get('Company', 'N/A'))}")
        self.multi_cell(0, 10, f"Product Type: {clean_text(row.get('Product_Type', 'N/A'))}")
        self.ln(5)

        self.set_font("DejaVu", "", 12)
        self.cell(0, 10, "Indicators:", ln=True)
        self.set_font("DejaVu", "", 12)

        indicators = {
            "CO2 Emissions (kg)": row.get("Greenhouse_Gas_Emissions(kg_CO2e)", "N/A"),
            "Water Consumption (L)": row.get("Water_Consumption(L)", "N/A"),
            "Energy Consumption (kWh)": row.get("Energy_Consumption(kWh)", "N/A"),
            "Waste Generation (kg)": row.get("Waste_Generation(kg)", "N/A"),
            "Recycled Material (%)": row.get("Recycled_Material_Use(%)", "N/A"),
            "Renewable Energy (%)": row.get("Renewable_Energy_Use(%)", "N/A"),
            "Strategy Cost ($)": row.get("Strategy_Cost_USD", "N/A"),
            "Expected CO2 Reduction (kg)": row.get("Expected_CO2_Reduction(kg)", "N/A"),
            "ROI (months)": row.get("ROI_Months", "N/A"),
            "Carbon Score": row.get("Carbon_Report_Score", "N/A"),
            "Regulation Risk": row.get("Regulation_Risk", "N/A"),
            "Consumer Trend Score": row.get("Consumer_Trend_Score", "N/A"),
        }

        for label, value in indicators.items():
            self.multi_cell(0, 10, f"{label}: {value}")

        self.ln(5)
        self.set_font("DejaVu", "", 12)
        self.cell(0, 10, "Top Strategy Recommendations:", ln=True)
        self.set_font("DejaVu", "", 12)

        for s in row.get("Strategy_Combo", []):
            self.multi_cell(0, 10, f"- {clean_text(s)}")

        self.ln(5)
        self.set_font("DejaVu", "", 12)
        self.cell(0, 10, "Opportunity Insight:", ln=True)
        self.set_font("DejaVu", "", 12)
        self.multi_cell(0, 10, clean_text(row.get("Opportunity_Insight", "N/A")))

# PDF üretimi
pdf_final = FinalCarbonReportPDF()
FONT_PATH = r"C:\Users\hp\OneDrive\Masaüstü\Python Proje\DejaVuSans.ttf"
pdf_final.add_font("DejaVu", "", FONT_PATH, uni=True) 
pdf_final.set_font("DejaVu", "", 14) 
pdf_final.add_page()

# DejaVu fontunu ekle (Unicode karakterler için)
pdf_final.add_font("DejaVu", "", FONT_PATH, uni=True)

example = df.iloc[0]  # İlk satır raporu

pdf_final.product_report(example)

# Masaüstüne kaydetmek için yol (kendine göre ayarla)
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
output_path = os.path.join(desktop_path, "carbon_report_example.pdf")

pdf_final.output(output_path)

print(f"PDF başarıyla kaydedildi: {output_path}")

# PDF dosyasını otomatik açma (Windows için)
try:
    os.startfile(output_path)
except AttributeError:
    # Windows dışı ise
    try:
        subprocess.call(["open", output_path])  # macOS
    except:
        try:
            subprocess.call(["xdg-open", output_path])  # Linux
        except:
            print("PDF dosyası açılırken hata oluştu. Lütfen manuel açınız.")
        
import os
from ctypes import wintypes, windll, create_unicode_buffer

def get_desktop_path():
    CSIDL_DESKTOP = 0
    SHGFP_TYPE_CURRENT = 0
    buf = create_unicode_buffer(wintypes.MAX_PATH)
    windll.shell32.SHGetFolderPathW(None, CSIDL_DESKTOP, None, SHGFP_TYPE_CURRENT, buf)
    return buf.value

desktop_path = get_desktop_path()

# Klasör yoksa oluştur
if not os.path.exists(desktop_path):
    os.makedirs(desktop_path)

output_path = os.path.join(desktop_path, "carbon_report_example.pdf")

pdf_final.output(output_path)
print(f"PDF başarıyla kaydedildi: {output_path}")