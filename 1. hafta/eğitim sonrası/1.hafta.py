import pandas as pd
import unicodedata
from fpdf import FPDF
from io import BytesIO
import tempfile

# Veri setini yükle
file_path = '/Users/beyzaozdemir/Documents/GitHub/YetGenCorePython2025/1. hafta/eğitim sonrası/inditex_120_product_synthetic_dataset.csv'
df = pd.read_csv(file_path)




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


# PDF için metin temizleyici
def clean_text(text):
    if isinstance(text, str):
        text = unicodedata.normalize('NFKD', text)
        text = text.encode('ascii', 'ignore').decode('ascii')
    return str(text)


# PDF rapor sınıfı
class FinalCarbonReportPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Carbon Footprint Report Card", ln=True, align="C")
        self.ln(10)

    def product_report(self, row):
        self.set_font("Arial", "", 12)
        self.multi_cell(0, 10, f"Company: {clean_text(row.get('Company', 'N/A'))}")
        self.multi_cell(0, 10, f"Product Type: {clean_text(row.get('Product_Type', 'N/A'))}")
        self.ln(5)

        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Indicators:", ln=True)
        self.set_font("Arial", "", 12)

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
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Top Strategy Recommendations:", ln=True)
        self.set_font("Arial", "", 12)

        for s in row.get("Strategy_Combo", []):
            self.multi_cell(0, 10, f"- {clean_text(s)}")

        self.ln(5)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Opportunity Insight:", ln=True)
        self.set_font("Arial", "", 12)
        self.multi_cell(0, 10, clean_text(row.get("Opportunity_Insight", "N/A")))


# PDF üretimi
with tempfile.NamedTemporaryFile(delete=False) as temp_file:
    pdf_final = FinalCarbonReportPDF()
    pdf_final.add_page()

    example = df.iloc[0]  # İsterseniz bu kısmı döngüye alarak birden fazla ürün raporlayabilirsiniz
    pdf_final.product_report(example)

    pdf_final.output(temp_file.name)
    temp_file.seek(0)
    pdf_data = temp_file.read()

# Örnek çıktı: ilk 500 byte gösterilir
print(pdf_data[:500])