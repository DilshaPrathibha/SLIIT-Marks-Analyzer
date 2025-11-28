---
title: SLIIT Marks Analyzer
emoji: 📘
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: "1.29.0"
app_file: app.py
pinned: false
---

---
title: SLIIT Marks Analyzer
emoji: 📘
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: "1.29.0"
app_file: app.py
pinned: false
---

# 📘 SLIIT Marks Analyzer

A comprehensive student performance analysis tool designed specifically for SLIIT (Sri Lanka Institute of Information Technology) exam results. This application extracts student data from PDF exam reports and provides detailed insights into individual and class performance metrics.

## 🔗 Live Application

[👉 Visit the SLIIT Marks Analyzer](https://huggingface.co/spaces/Dilshaprathibha/sliitMarksAnalyzer)

## 🚀 Key Features

### 📊 Individual Student Analysis
- **Performance Ranking**: Get your rank among all students in the module
- **Percentile Calculation**: Understand your position in the top X% of the class
- **Grade Projection**: Calculate required final exam marks to achieve target grades
- **Performance Categorization**: Classified as Excellent, High Performer, Average, or Below Average

### 📈 Class Performance Analytics
- **Grade Distribution**: Visual representation of class grade breakdown
- **Performance Overview**: Statistical analysis of class performance patterns
- **Status Breakdown**: Pass/Fail/IC statistics with percentage breakdown
- **Module-Specific Weighting**: Automatic CA/Final exam weight detection for different IT modules

### 📋 Comprehensive Reports
- **Detailed Student Reports**: Individual performance cards with key metrics
- **Visual Analytics**: Charts and graphs for better data interpretation
- **Summary Statistics**: Class averages, total students, and performance trends

## 📸 Screenshots

### Main Interface
![Main Application Interface](images/Screenshot%201.png)
*Upload PDF files and search for student performance with an intuitive interface*

### Analytics Dashboard
![Performance Analytics Dashboard](images/Screenshot%202.png)
*Comprehensive performance analytics with charts, rankings, and detailed insights*

## 🛠️ Technology Stack

### Core Framework
- **Streamlit** - Modern web application framework for Python that enables rapid development of data applications
- **Python 3.x** - Primary programming language for backend logic and data processing

### Data Processing & Analysis
- **Pandas** - Powerful data manipulation and analysis library for handling student data structures
- **PyPDF2** - PDF processing library for extracting text content from SLIIT exam report PDFs
- **Regular Expressions (re)** - Pattern matching for parsing structured data from PDF text

### Visualization & UI
- **Matplotlib** - Comprehensive plotting library for creating statistical charts and graphs
- **Custom CSS Styling** - Responsive design with mobile-friendly layouts
- **HTML/CSS Integration** - Enhanced user interface with styled tables and components

### Key Technical Features
- **PDF Text Extraction**: Automated parsing of SLIIT exam PDFs using PyPDF2
- **Pattern Recognition**: Advanced regex patterns for extracting student registration numbers, marks, and grades
- **Dynamic Weight Calculation**: Module-specific CA/Final exam weight detection
- **Responsive Design**: Mobile-optimized interface with CSS media queries
- **Real-time Analytics**: Instant calculation of rankings, percentiles, and performance metrics

### Architecture
- **Single-Page Application**: Streamlit-based SPA for seamless user experience
- **Client-Side Processing**: All calculations performed locally for data privacy
- **Temporary File Handling**: Secure PDF processing without persistent storage
- **Error Handling**: Robust validation and error messaging for invalid inputs

## 🚦 Getting Started

## 📁 Project Structure

```
SLIIT-Marks-Analyzer/
├── images/
│   ├── Screenshot 1.png
│   └── Screenshot 2.png
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md          # Project documentation
```

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/DilshaPrathibha/SLIIT-Marks-Analyzer.git
cd SLIIT-Marks-Analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## 📝 Usage

1. **Upload PDF**: Select and upload a valid SLIIT Final Exam PDF file
2. **Module Detection**: The system automatically detects module code and name
3. **Student Search**: Enter your registration number to view individual performance
4. **Analyze Results**: Review detailed performance metrics, rankings, and projections
5. **Class Overview**: Explore comprehensive class performance analytics

### Application Preview
<div align="center">
  <img src="images/Screenshot%202.png" alt="Student Performance Report" width="600">
  <br>
  <em>Example of detailed student performance report with rankings and grade projections</em>
</div>

## ⚠️ Important Notes

- Only SLIIT Final Exam PDF files are supported
- The application automatically detects module-specific CA/Final exam weightings
- All data processing is done locally for privacy protection
- No student data is stored or transmitted externally

## 🏫 Supported SLIIT Modules

The application automatically recognizes weighting schemes for various IT modules:
- **60/40 Weight**: IT1010, IT1050, IT1090, IT2020, IT2060, IT2050
- **50/50 Weight**: IT1020, IT1030, IT1040, IT1060, IT1080, IT1100, IT2030, IT2040
- **Custom Weight**: Manual input for other modules

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📄 License

This project is open source and available under the MIT License.
