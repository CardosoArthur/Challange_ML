# GEMINI.md: Project Overview

## 1. Project Overview

This is a data science project that analyzes company financial data to determine their business "life stage" and understand their relationships within a transactional network. The project consists of two main components:

1.  **Data Analysis Notebook (`Desafio_Completo.ipynb`):** A Jupyter Notebook that processes raw transactional data to segment companies and analyze their network connections.
2.  **Interactive Dashboard (`app.py`):** A Streamlit web application that provides a rich, interactive visualization of the analysis results.

### Key Technologies
- **Language:** Python
- **Data Analysis & ML:** Pandas, NumPy, Scikit-learn (K-Means), NetworkX, python-louvain.
- **Dashboard & Visualization:** Streamlit, Plotly, PyVis.

---

## 2. Core Components

### 2.1. Data Analysis (`Desafio_Completo.ipynb`)

This notebook performs the core data processing and modeling.

- **Feature Engineering:** It calculates key financial metrics from the source data (`Base1_ID.xlsx`, `Base2_Transacoes.xlsx`), such as total received/paid amounts, transaction counts, net cash flow, and average ticket size.
- **Company Segmentation (Clustering):** It uses an unsupervised K-Means algorithm to group companies into four distinct business stages:
    - **Início (Startup)**
    - **Expansão (Growth)**
    - **Maturidade (Maturity)**
    - **Declínio (Decline)**
- **Network Analysis:** It models the transactions as a directed graph to calculate network centrality metrics (e.g., degree, betweenness) and identify business communities using the Louvain method.
- **Data Export:** The final processed data, including company segments and network metrics, is exported to `data/dados_para_powerbi.csv` and `data/dados_rede_para_powerbi.csv`, which serve as the data source for the dashboard.

### 2.2. Interactive Dashboard (`app.py`)

This is a Streamlit application for exploring the analysis results.

- **Interactive KPIs:** Displays key performance indicators like total revenue, payments, and cash flow, which update based on user selections.
- **Global Filters:** Allows users to filter the entire dashboard by business sector (CNAE), company life stage, and time period (Month/Year).
- **Multiple Analysis Tabs:**
    - **Visão Geral:** An overview of the entire business ecosystem.
    - **Início, Maturidade, Expansão, Declínio:** Dedicated tabs for in-depth analysis of each company stage.
    - **Detalhamento:** A detailed drill-down view for any selected company, featuring its specific KPIs, a historical transaction timeline, and an interactive network graph of its direct connections.
- **Rich Visualizations:** Uses Plotly for interactive charts and PyVis to render the dynamic, explorable network graphs.

---

## 3. Building and Running the Project

Follow these steps to set up and run the interactive dashboard.

### Step 1: Install Dependencies

Ensure you have Python 3.10+ installed. Open your terminal in the project root directory and run the following command to install the necessary libraries:

```bash
pip install -r requirements.txt
```

### Step 2: Run the Streamlit Dashboard

After the dependencies are installed, run the following command:

```bash
streamlit run app.py
```

This will start the web server and open the interactive dashboard in your default web browser.

### (Optional) Step 3: Regenerate Analysis Data

If you need to re-run the data analysis and modeling from scratch, you can execute the Jupyter Notebook `Desafio_Completo.ipynb`. This will overwrite the existing CSV files in the `data/` directory.
