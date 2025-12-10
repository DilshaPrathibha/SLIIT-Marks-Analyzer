import streamlit as st
import re
import pandas as pd
from PyPDF2 import PdfReader
import matplotlib.pyplot as plt
import tempfile

# Page config
st.set_page_config(page_title="📘 SLIIT Marks Analyzer", layout="wide")

# 🔹 Apply outer frame and layout fix
st.markdown("""
    <style>
        /* Global dark theme */
        :root, html, body, [data-testid="stAppViewContainer"] {
            background-color: #0d1117 !important;
            color: #e6edf3 !important;
        }

        /* Limit max width & center all content */
        .main {
            padding-left: 300px !important;
            padding-right: 300px !important;
            background-color: #0d1117 !important;
            color: #e6edf3 !important;
        }

        /* Optional: Adjust spacing below inputs */
        .element-container:has(.stTextInput) {
            margin-bottom: 1.5rem;
        }

        /* Responsive breakpoints for smoother transitions */
        
        /* Large tablets and small desktops (1200px and below) */
        @media (max-width: 1200px) {
            .main {
                padding-left: 200px !important;
                padding-right: 200px !important;
            }
        }
        
        /* Medium tablets (992px and below) */
        @media (max-width: 992px) {
            .main {
                padding-left: 100px !important;
            padding-right: 100px !important;
            }
        }
        
        /* Small tablets (768px and below) */
        @media (max-width: 768px) {
            .main {
                padding-left: 50px !important;
                padding-right: 50px !important;
            }
        }
        
        /* Mobile devices (576px and below) */
        @media (max-width: 576px) {
            .main {
                padding-left: 20px !important;
                padding-right: 20px !important;
            }
        }

        /* Tables on dark */
        table, th, td {
            color: #e6edf3 !important;
            border-color: #30363d !important;
        }

        /* Links on dark */
        a { color: #58a6ff !important; }
        hr { border-color: #30363d !important; }
    </style>
""", unsafe_allow_html=True)


with st.container():
    st.title("📘 SLIIT Marks Analyzer")
    st.markdown("Analyze student performance from exam PDFs with ranks, grades, and insights.")

    uploaded_file = st.file_uploader("📂 Upload SLIIT Final Exam PDF File", type=["pdf"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    try:
        reader = PdfReader(tmp_path)
    except Exception:
        st.error("❌ Unable to read the uploaded PDF. Ensure it's a valid exam report.")
        st.stop()

    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    # 🔹 Detect module
    mod_match = re.search(r"(IT\d{4})\s*-\s*([^\n\-]+)", text)
    module_code = mod_match.group(1).strip() if mod_match else "Unknown"
    module_name = mod_match.group(2).strip() if mod_match else "Unknown"

    st.markdown(f"### 🧾 Module: {module_code} - {module_name}")

    # 🔹 Pattern 1: PDFs WITH CA marks (old behaviour)
    pattern_with_ca = (
        r"\b\d+\s+"
        r"(IT\s?\d{2}\s?\d{4}\s?\d{2})"     # RegNo like 'IT 23 8313 22'
        r"\s+"
        r"(\d{1,3}(?:\.\d{1,2})?)"          # CA mark column
        r"\s+"
        r"([A-Z\+\-]+)"                     # Grade
        r"\s+"
        r"(Pass|Fail|IC)"                   # Status
    )

    matches = re.findall(pattern_with_ca, text)
    has_ca_marks = True

    # 🔹 Pattern 2: PDFs WITHOUT CA marks
    if not matches:
        pattern_no_ca = (
            r"\b\d+\s+"
            r"(IT\s?\d{2}\s?\d{4}\s?\d{2})"  # RegNo only
            r"\s+"
            r"([A-Z\+\-]+)"                  # Grade
            r"\s+"
            r"(Pass|Fail|IC)"                # Status
        )
        matches = re.findall(pattern_no_ca, text)
        has_ca_marks = False

    if not matches:
        st.error("❌ No student data found. Please make sure to upload valid *SLIIT Final Exam PDF* files only.")
        st.stop()

    # 🔹 Build DataFrame depending on format
    if has_ca_marks:
        data = []
        for reg_no, ca_percent, grade, status in matches:
            clean_id = re.sub(r"\s+", "", reg_no.upper())
            data.append([clean_id, float(ca_percent), grade, status])

        df = pd.DataFrame(data, columns=["RegNo", "CAMarksPercent", "Grade", "Status"])
    else:
        # Grade-only PDFs (no CA column)
        data = []
        for reg_no, grade, status in matches:
            clean_id = re.sub(r"\s+", "", reg_no.upper())
            data.append([clean_id, grade, status])

        df = pd.DataFrame(data, columns=["RegNo", "Grade", "Status"])

    # -------------------------------------------------------------
    # Common grade meta
    # -------------------------------------------------------------
    grade_ranges = {
        "A+": (90, 100), "A": (80, 89), "A-": (75, 79),
        "B+": (70, 74), "B": (65, 69), "B-": (60, 64),
        "C+": (55, 59), "C": (45, 54), "C-": (40, 44),
        "D+": (35, 39), "D": (30, 34), "E": (0, 29),
        "F": (0, 29)
    }

    grade_order = {
        "A+": 1, "A": 2, "A-": 3,
        "B+": 4, "B": 5, "B-": 6,
        "C+": 7, "C": 8, "C-": 9,
        "D+": 10, "D": 11, "E": 12, "F": 13
    }

    grade_to_perf = {
        "A+": "Excellent", "A": "Excellent", "A-": "Excellent",
        "B+": "High Performer", "B": "High Performer",
        "B-": "Average", "C+": "Average", "C": "Average",
        "C-": "Below Average", "D+": "Below Average",
        "D": "Below Average", "E": "Below Average", "F": "Below Average"
    }

    def performance_emoji(perf):
        return {
            # old categories (grade-only branch)
            "Excellent": "🌟 Excellent",
            "High Performer": "✅ High Performer",
            "Average": "🟡 Average",
            "Below Average": "🔻 Below Average",
            # new combined CA + Total categories
            "Dual Star": "🌟 Dual Star (CA & Final Strong)",
            "Exam Booster": "📘 Exam Booster (Final > CA)",
            "CA Anchor": "🧩 CA Anchor (CA > Final)",
            "Developing": "🔻 Developing (Needs Support)"
        }.get(perf, perf)

    # -------------------------------------------------------------
    # Branch 1: PDFs WITH CA marks
    # -------------------------------------------------------------
    if has_ca_marks:
        # Module weight settings
        sixty_forty = {"IT1010", "IT1050", "IT1090", "IT2020", "IT2060", "IT2050", "IT2070", "IT2090"}
        fifty_fifty = {"IT1020", "IT1030", "IT1040", "IT1060", "IT1080", "IT1100", "IT2030", "IT2040", "IT2010", "IT2110"}

        # Initialize session state for custom weight if not exists
        if 'custom_ca_weight' not in st.session_state:
            st.session_state.custom_ca_weight = 40

        if module_code in sixty_forty:
            ca_weight, final_weight = 0.4, 0.6
            weight_info = "📊 **Weight Detected**: 60% Final + 40% CA"
        elif module_code in fifty_fifty:
            ca_weight, final_weight = 0.5, 0.5
            weight_info = "📊 **Weight Detected**: 50% Final + 50% CA"
        else:
            st.warning(f"⚠️ Module {module_code} not recognized. Please set custom CA weight:")
            custom_weight = st.number_input(
                "Enter CA Weight %", 
                min_value=0, 
                max_value=100, 
                value=st.session_state.custom_ca_weight,
                step=5,
                key="ca_weight_input"
            )
            st.session_state.custom_ca_weight = custom_weight
            ca_weight = custom_weight / 100
            final_weight = 1.0 - ca_weight
            weight_info = f"📊 **Custom Weight**: {int(final_weight*100)}% Final + {int(ca_weight*100)}% CA"
        
        st.info(weight_info)

        df["CA_Scaled"] = df["CAMarksPercent"] * ca_weight
        df["FinalGrade"] = df["CA_Scaled"]

        # 🔹 NEW: Performance uses BOTH CA and Total (from grade band midpoint)
        grade_mid = {g: (lo + hi) / 2 for g, (lo, hi) in grade_ranges.items()}

        def performance_category_combined(row):
            ca = row["CAMarksPercent"]
            approx_total = grade_mid.get(row["Grade"], ca)

            if ca >= 70 and approx_total >= 70:
                return "Dual Star"          # strong CA and strong final
            elif ca < 70 and approx_total >= 70:
                return "Exam Booster"       # exam pulled the grade up
            elif ca >= 70 and approx_total < 70:
                return "CA Anchor"          # CA is strong, final weaker
            else:
                return "Developing"         # both sides need work

        df["Performance"] = df.apply(performance_category_combined, axis=1)

        # Ranking
        df_sorted = df.sort_values(by="CA_Scaled", ascending=False).reset_index(drop=True)
        df_sorted["Rank"] = df_sorted.index + 1

        # 🔍 Student search
        reg_input = st.text_input("🔍 Enter Student ID Number", max_chars=20)

        if reg_input:
            cleaned = re.sub(r"[^A-Z0-9]", "", reg_input.upper())
            matches_student = df_sorted[df_sorted["RegNo"].str.startswith(cleaned)]

            if matches_student.empty:
                st.warning("⚠ No matching registration found.")
            elif len(matches_student) > 1:
                st.info("Multiple matches found. Please enter full RegNo:")
                st.markdown("Matching RegNos:")
                for m in matches_student["RegNo"].tolist():
                    st.markdown(f"- {m}")
            else:
                student = matches_student.iloc[0]
                total = len(df_sorted)
                rank = int(student["Rank"])
                # show "Top X%" where X is small (better visual)
                percentile = 100 * (rank / total)
                avg = df_sorted["CA_Scaled"].mean()
                ca_percent = student["CAMarksPercent"]
                ca_scaled = ca_percent * ca_weight
                grade = student["Grade"]
                status = student["Status"]
                perf = performance_emoji(student["Performance"])

                min_total, max_total = grade_ranges.get(grade, (0, 0))
                exam_min = ((min_total / 100) - ca_weight * (ca_percent / 100)) * 100 / final_weight
                exam_max = ((max_total / 100) - ca_weight * (ca_percent / 100)) * 100 / final_weight

                if exam_max > 100:
                    exam_max = 100

                st.markdown(f"""
                    <h3>📊 Student Performance Report</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr>
                                <th style="text-align: left; padding: 8px;">Key</th>
                                <th style="text-align: left; padding: 8px;">Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td>🎓 RegNo</td><td>{student['RegNo']}</td></tr>
                            <tr><td>🎯 Grade / 🧾 Status</td><td>{grade} &nbsp;|&nbsp; {status}</td></tr>
                            <tr><td>📈 CA Marks / 🎯 Scaled CA</td><td><span style='color: green;'>{ca_percent:.2f}%</span> &nbsp;|&nbsp; <span style='color: green;'>{ca_scaled:.1f}</span> / {int(ca_weight * 100)}</td></tr>
                            <tr><td>🎓 Rank (Based on CA marks)</td><td><span style='color: green;'>{rank}</span> / {total}</td></tr>
                            <tr><td>📊 Top Percentile (Based on CA)</td><td>Top <span style='color: green;'>{percentile:.2f}%</span></td></tr>
                            <tr><td>🧪 Final Exam Marks</td><td>Between <span style='color: green;'>{exam_min:.1f}</span> - <span style='color: green;'>{exam_max:.1f}</span></td></tr>
                            <tr><td>🎯 Total Marks</td><td>Between <span style='color: green;'>{min_total:.2f}</span> - <span style='color: green;'>{max_total:.2f}</span></td></tr>
                            <tr><td>📌 Performance</td><td>{perf}</td></tr>
                        </tbody>
                    </table>
                """, unsafe_allow_html=True)

        # ---------- Charts & Summary (CA version) ----------
        st.markdown("---")
        st.subheader("📊 Performance Overview")

        performance_order = ["Dual Star", "Exam Booster", "CA Anchor", "Developing"]
        df_sorted["PerformanceClean"] = df_sorted["Performance"]
        perf_counts = df_sorted["PerformanceClean"].value_counts().reindex(performance_order, fill_value=0)

        fig, axs = plt.subplots(2, 2, figsize=(16, 10))
        fig.patch.set_facecolor('#000000')
        fig.suptitle(f" Performance Overview - {module_name} ({module_code})", fontsize=18, weight='bold', color='white')

        # Performance distribution
        axs[0, 0].bar(performance_order, perf_counts.values, color=["gold", "limegreen", "orange", "red"])
        axs[0, 0].set_title("Overall Performance", fontsize=14)
        axs[0, 0].set_ylabel("No. of Students")
        for i, val in enumerate(perf_counts.values):
            axs[0, 0].text(i, val + 1, str(val), ha='center', fontsize=10, color='#e6edf3')
        axs[0, 0].grid(axis="y", linestyle="--", alpha=0.2, color='white')

        # Grade Distribution
        custom_grade_order = ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "E", "F", "N/A"]
        grade_counts = df_sorted["Grade"].value_counts().reindex(custom_grade_order, fill_value=0)
        axs[0, 1].bar(grade_counts.index, grade_counts.values, color="coral")
        axs[0, 1].set_title("Grade Distribution")
        axs[0, 1].set_xlabel("Grades")
        axs[0, 1].set_ylabel("Number of Students")
        axs[0, 1].tick_params(axis='x', rotation=45)
        axs[0, 1].grid(axis="y", linestyle="--", alpha=0.2, color='white')

        # Status Breakdown
        status_counts = df_sorted["Status"].value_counts()
        colors = ["skyblue", "salmon", "orange"]
        wedges, texts, autotexts = axs[1, 0].pie(
            status_counts.values,
            labels=status_counts.index,
            autopct='%1.1f%%',
            startangle=140,
            colors=colors,
            wedgeprops={'linewidth': 1, 'edgecolor': 'white'},
            textprops={'color': '#e6edf3'}
        )
        for t in autotexts:
            t.set_color('#e6edf3')
        axs[1, 0].set_title("Status Breakdown", fontsize=14)

        # Final Grade Distribution (CA Scaled)
        axs[1, 1].hist(df_sorted["CA_Scaled"], bins=10, color="mediumpurple", edgecolor="#e6edf3")
        axs[1, 1].set_title("CA Distribution", fontsize=14)
        axs[1, 1].set_xlabel("Final Grade")
        axs[1, 1].set_ylabel("No. of Students")
        axs[1, 1].grid(True, linestyle="--", alpha=0.2, color='white')

        # Apply dark styling to all axes
        for ax in axs.flatten():
            ax.set_facecolor('#0d1117')
            ax.title.set_color('white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.tick_params(colors='#e6edf3')
            for spine in ax.spines.values():
                spine.set_color('#30363d')

        fig.subplots_adjust(hspace=0.5)
        st.pyplot(fig)

        total_students = len(df_sorted)
        class_avg = df_sorted["CA_Scaled"].mean()
        num_pass = df_sorted[df_sorted["Status"] == "Pass"].shape[0]
        num_fail = df_sorted[df_sorted["Status"] != "Pass"].shape[0]

        st.markdown(f"""
        ### 📋 Summary
        - 👥 Total Students: <span style='color: green'>{total_students}</span>  
        - 📚 Average CA: <span style='color: green'>{class_avg:.2f}</span> (Raw Avg: <span style='color: green'>{class_avg / ca_weight:.2f}%</span>)  
        - ✅ Passed: <span style='color: green'>{num_pass}</span>  
        - ❌ Not Passed: <span style='color: green'>{num_fail}</span>  
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # Branch 2: PDFs WITHOUT CA marks (grade-only)
    # -------------------------------------------------------------
    else:
        st.info("📊 This PDF does **not** contain CA marks. Analysis is based on final **grades only**.")

        # Map grade to an approximate numeric score (midpoint of band) for charts/ranks
        grade_mid = {g: (lo + hi) / 2 for g, (lo, hi) in grade_ranges.items()}
        df["ScoreApprox"] = df["Grade"].map(grade_mid)
        df["GradeOrder"] = df["Grade"].map(grade_order)
        df["Performance"] = df["Grade"].map(grade_to_perf)

        # Sort by grade order then RegNo
        df_sorted = df.sort_values(by=["GradeOrder", "RegNo"]).reset_index(drop=True)
        df_sorted["Rank"] = df_sorted.index + 1

        # 🔍 Student search (grade-only)
        reg_input = st.text_input("🔍 Enter Student ID Number", max_chars=20)

        if reg_input:
            cleaned = re.sub(r"[^A-Z0-9]", "", reg_input.upper())
            matches_student = df_sorted[df_sorted["RegNo"].str.startswith(cleaned)]

            if matches_student.empty:
                st.warning("⚠ No matching registration found.")
            elif len(matches_student) > 1:
                st.info("Multiple matches found. Please enter full RegNo:")
                st.markdown("Matching RegNos:")
                for m in matches_student["RegNo"].tolist():
                    st.markdown(f"- {m}")
            else:
                student = matches_student.iloc[0]
                total = len(df_sorted)
                rank = int(student["Rank"])
                percentile = 100 * (rank / total)
                grade = student["Grade"]
                status = student["Status"]
                perf = performance_emoji(student["Performance"])
                min_total, max_total = grade_ranges.get(grade, (0, 0))
                approx_score = student["ScoreApprox"]

                st.markdown(f"""
                    <h3>📊 Student Grade Report</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr>
                                <th style="text-align: left; padding: 8px;">Key</th>
                                <th style="text-align: left; padding: 8px;">Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td>🎓 RegNo</td><td>{student['RegNo']}</td></tr>
                            <tr><td>🎯 Grade / 🧾 Status</td><td>{grade} &nbsp;|&nbsp; {status}</td></tr>
                            <tr><td>📈 Estimated Total Marks</td><td><span style='color: green;'>{approx_score:.1f}</span> (from grade band)</td></tr>
                            <tr><td>🎯 Grade Band Range</td><td><span style='color: green;'>{min_total:.1f}</span> - <span style='color: green;'>{max_total:.1f}</span></td></tr>
                            <tr><td>🎓 Rank (by grade)</td><td><span style='color: green;'>{rank}</span> / {total}</td></tr>
                            <tr><td>📊 Top Percentile</td><td>Top <span style='color: green;'>{percentile:.2f}%</span></td></tr>
                            <tr><td>📌 Performance</td><td>{perf}</td></tr>
                            <tr><td>ℹ️ Note</td><td>This module PDF does not show CA or exam breakdown — only final grades are available.</td></tr>
                        </tbody>
                    </table>
                """, unsafe_allow_html=True)

        # ---------- Charts & Summary (grade-only version) ----------
        st.markdown("---")
        st.subheader("📊 Performance Overview")

        performance_order = ["Excellent", "High Performer", "Average", "Below Average"]
        perf_counts = df_sorted["Performance"].value_counts().reindex(performance_order, fill_value=0)

        fig, axs = plt.subplots(2, 2, figsize=(16, 10))
        fig.patch.set_facecolor('#000000')
        fig.suptitle(f" Performance Overview - {module_name} ({module_code})", fontsize=18, weight='bold', color='white')

        # Performance distribution
        axs[0, 0].bar(performance_order, perf_counts.values, color=["gold", "limegreen", "orange", "red"])
        axs[0, 0].set_title("Performance Distribution", fontsize=14)
        axs[0, 0].set_ylabel("No. of Students")
        for i, val in enumerate(perf_counts.values):
            axs[0, 0].text(i, val + 1, str(val), ha='center', fontsize=10, color='#e6edf3')
        axs[0, 0].grid(axis="y", linestyle="--", alpha=0.2, color='white')

        # Grade Distribution
        custom_grade_order = ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "E", "F"]
        grade_counts = df_sorted["Grade"].value_counts().reindex(custom_grade_order, fill_value=0)
        axs[0, 1].bar(grade_counts.index, grade_counts.values, color="coral")
        axs[0, 1].set_title("Grade Distribution")
        axs[0, 1].set_xlabel("Grades")
        axs[0, 1].set_ylabel("Number of Students")
        axs[0, 1].tick_params(axis='x', rotation=45)
        axs[0, 1].grid(axis="y", linestyle="--", alpha=0.2, color='white')

        # Status Breakdown
        status_counts = df_sorted["Status"].value_counts()
        colors = ["skyblue", "salmon", "orange"]
        wedges, texts, autotexts = axs[1, 0].pie(
            status_counts.values,
            labels=status_counts.index,
            autopct='%1.1f%%',
            startangle=140,
            colors=colors,
            wedgeprops={'linewidth': 1, 'edgecolor': 'white'},
            textprops={'color': '#e6edf3'}
        )
        for t in autotexts:
            t.set_color('#e6edf3')
        axs[1, 0].set_title("Status Breakdown", fontsize=14)

        # Estimated final mark distribution from grade
        axs[1, 1].hist(df_sorted["ScoreApprox"], bins=10, color="mediumpurple", edgecolor="#e6edf3")
        axs[1, 1].set_title("Estimated Final Mark Distribution (from Grade)", fontsize=14)
        axs[1, 1].set_xlabel("Estimated Total Mark")
        axs[1, 1].set_ylabel("No. of Students")
        axs[1, 1].grid(True, linestyle="--", alpha=0.2, color='white')

        # Apply dark styling to all axes
        for ax in axs.flatten():
            ax.set_facecolor('#0d1117')
            ax.title.set_color('white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.tick_params(colors='#e6edf3')
            for spine in ax.spines.values():
                spine.set_color('#30363d')

        fig.subplots_adjust(hspace=0.5)
        st.pyplot(fig)

        total_students = len(df_sorted)
        class_avg = df_sorted["ScoreApprox"].mean()
        num_pass = df_sorted[df_sorted["Status"] == "Pass"].shape[0]
        num_fail = df_sorted[df_sorted["Status"] != "Pass"].shape[0]

        st.markdown(f"""
        ### 📋 Summary
        - 👥 Total Students: <span style='color: green'>{total_students}</span>  
        - 📚 Average Estimated Mark: <span style='color: green'>{class_avg:.2f}</span>  
        - ✅ Passed: <span style='color: green'>{num_pass}</span>  
        - ❌ Not Passed: <span style='color: green'>{num_fail}</span>  
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # Footer - Creator info
    # -------------------------------------------------------------
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:#6c757d;'>Created by <b>Dilsha Prathibha</b></div>",
        unsafe_allow_html=True
    )
    st.markdown("---")
