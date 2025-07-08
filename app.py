import streamlit as st
import re
import pandas as pd
from PyPDF2 import PdfReader
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Marks Analyzer", layout="wide")

st.title("📊 Student Marks Analyzer")

uploaded_file = st.file_uploader("📎 Upload PDF File", type="pdf")
if not uploaded_file:
    st.warning("Please upload a .pdf file")
    st.stop()

# Extract text from PDF
reader = PdfReader(uploaded_file)
text = ""
for page in reader.pages:
    page_text = page.extract_text()
    if page_text:
        text += page_text + "\n"

# Extract module details
mod_match = re.search(r"(IT\d{4})\s*-\s*([^\n\-]+)", text)
module_code = mod_match.group(1).strip() if mod_match else "Unknown"
module_name = mod_match.group(2).strip() if mod_match else "Unknown"

st.subheader(f"📘 Module: {module_code} - {module_name}")

# Extract student marks
pattern = r"\d+\s+(IT\s?\d{2}\s?\d{4}\s?\d{2})\s+(\d{1,3}(?:\.\d{1,2})?)\s+([A-Z\+\-]+)\s+(Pass|Fail|IC)"
matches = re.findall(pattern, text)
if not matches:
    st.error("No student data found. Check PDF format.")
    st.stop()

data = []
for reg_no, ca_percent, grade, status in matches:
    clean_id = re.sub(r"\s+", "", reg_no.upper())
    data.append([clean_id, float(ca_percent), grade, status])

df = pd.DataFrame(data, columns=["RegNo", "CAMarksPercent", "Grade", "Status"])

# Determine weightages
sixty_forty = {"IT1010", "IT1050", "IT1090", "IT2020", "IT2060", "IT2050"}
fifty_fifty = {"IT1020", "IT1030", "IT1040", "IT1060", "IT1080", "IT1100", "IT2030", "IT2040"}

if module_code in sixty_forty:
    ca_weight, final_weight = 0.4, 0.6
elif module_code in fifty_fifty:
    ca_weight, final_weight = 0.5, 0.5
else:
    final_weight = st.number_input("Enter % weight of Final Exam", min_value=10, max_value=90, value=60)
    final_weight = final_weight / 100.0
    ca_weight = 1.0 - final_weight

# Add calculations
df["CA_Scaled"] = df["CAMarksPercent"] * ca_weight
df["FinalGrade"] = df["CA_Scaled"]
df = df.sort_values(by="CA_Scaled", ascending=False).reset_index(drop=True)
df["Rank"] = df.index + 1

def performance_category(mark):
    if mark >= 85: return "Excellent (Top Tier)"
    elif mark >= 70: return "High Performer"
    elif mark >= 50: return "Average"
    else: return "Below Average"

df["Performance"] = df["CAMarksPercent"].apply(performance_category)

# Search student
st.subheader("🔍 Search Student")
reg_input = st.text_input("Enter Registration Number").upper()
if reg_input:
    reg_clean = re.sub(r"[^A-Z0-9]", "", reg_input)
    matches = df[df["RegNo"].str.startswith(reg_clean)]
    
    if len(matches) == 0:
        st.error("No matching student found.")
    elif len(matches) > 1:
        st.warning("Multiple matches found. Please enter full RegNo.")
        st.dataframe(matches)
    else:
        student = matches.iloc[0]
        total = len(df)
        rank = student["Rank"]
        percentile = 100 * (1 - rank / total)
        avg = df["CA_Scaled"].mean()
        grade_ranges = {
            "A+": (90, 100), "A": (80, 89), "A-": (75, 79),
            "B+": (70, 74), "B": (65, 69), "B-": (60, 64),
            "C+": (55, 59), "C": (45, 54), "C-": (40, 44),
            "D+": (35, 39), "D": (30, 34), "E": (0, 29)
        }

        min_total, max_total = grade_ranges.get(student["Grade"], (0, 0))
        exam_min = ((min_total / 100) - ca_weight * (student["CAMarksPercent"] / 100)) * 100 / final_weight
        exam_max = ((max_total / 100) - ca_weight * (student["CAMarksPercent"] / 100)) * 100 / final_weight

        st.markdown("### 📊 Student Performance Report")
        st.markdown(f"""
        **RegNo**: {student["RegNo"]}  
        **Grade**: {student["Grade"]}  
        **Status**: {student["Status"]} ({student["Performance"]})  
        **CA Marks (%)**: {student["CAMarksPercent"]}  
        **CA Marks (scaled)**: {student["CA_Scaled"]:.1f} out of {ca_weight*100:.0f}  
        **Final Marks Range**: {min_total} - {max_total}  
        **Final Exam Marks Needed**: {exam_min:.1f} - {exam_max:.1f}  
        **Rank**: {rank} / {total}  
        **Percentile**: Top {percentile:.2f}%  
        **Class Average (CA)**: {avg:.2f} (Raw Avg: {(avg / ca_weight):.2f}%)  
        """)

# Show charts
st.subheader("📈 Class Summary Charts")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Performance Distribution**")
    perf_counts = df["Performance"].value_counts()
    st.bar_chart(perf_counts)

with col2:
    st.markdown("**Grade Distribution**")
    grade_counts = df["Grade"].value_counts().sort_index()
    st.bar_chart(grade_counts)

st.markdown("**Status Breakdown**")
status_counts = df["Status"].value_counts()
st.pyplot(plt.figure(figsize=(4, 4)))
plt.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=140)
plt.title("Status")
plt.axis("equal")
