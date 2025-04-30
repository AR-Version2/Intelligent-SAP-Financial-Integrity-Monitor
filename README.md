## Overview

This project demonstrates a proof-of-concept system for detecting financial document anomalies within core SAP FI/CO data, specifically leveraging the New General Ledger table (`FAGLFLEXA`) and document headers (`BKPF`). It addresses the challenge that standard SAP reporting and rule-based checks often struggle to identify subtle, complex, or novel irregularities in high-volume financial postings.

The solution employs a **Hybrid Anomaly Detection strategy**, combining unsupervised Machine Learning models with expert-defined SAP business rules. Findings are prioritized using a multi-faceted scoring system and presented via an interactive dashboard built with Streamlit for efficient investigation.

This project was developed as a capstone, showcasing the application of AI/ML techniques to enhance financial controls within an SAP context, bridging deep SAP domain knowledge with modern data science practices.

**Author:** AR-Version2

**Dataset Origin:** [Kaggle SAP Dataset by Sunitha Siva](https://www.kaggle.com/datasets/sunithasiva/sap-dataset) 
License:Other (specified in description)-No description available.

## Motivation

Financial integrity is critical. Undetected anomalies in SAP FI/CO postings can lead to:
*   Inaccurate financial reporting
*   Significant reconciliation efforts
*   Potential audit failures or compliance issues
*   Masking of operational errors or fraud

Standard SAP tools may not catch all types of anomalies, especially complex or novel patterns. This project explores how AI/ML can augment traditional methods to provide more robust and efficient financial monitoring.

## Key Features

*   **Data Cleansing & Preparation:** Rigorous process to handle common SAP data extract issues (duplicates, financial imbalance), prioritizing `FAGLFLEXA` for reliability.
*   **Exploratory Data Analysis (EDA):** Uncovered baseline patterns in posting times, user activity, amounts, and process context.
*   **Feature Engineering:** Created 16 context-aware features (`FE_...`) to quantify potential deviations from normalcy based on EDA and SAP knowledge.
*   **Hybrid Anomaly Detection:**
    *   **Ensemble ML:** Utilized unsupervised models: Isolation Forest (IF), Local Outlier Factor (LOF) (via Scikit-learn), and an Autoencoder (AE) (via TensorFlow/Keras).
    *   **Expert Rules (HRFs):** Implemented highly customizable High-Risk Flags based on percentile thresholds and SAP logic (e.g., weekend posting, missing cost center).
*   **Multi-Faceted Prioritization:** Combined ML model consensus (`Model_Anomaly_Count`) and HRF counts (`HRF_Count`) into a `Priority_Tier` for focusing investigation efforts.
*   **Contextual Anomaly Reason:** Generated a `Review_Focus` text description summarizing why an item was flagged.
*   **Interactive Dashboard (Streamlit):**
    *   File upload for anomaly/feature data.
    *   Overview KPIs (including multi-currency "Value at Risk by CoCode").
    *   Comprehensive filtering capabilities.
    *   Dynamic visualizations (User/Doc Type/HRF frequency, Time Trends).
    *   Interactive AgGrid table for anomaly list investigation.
    *   Detailed drill-down view for selected anomalies.

## Methodology Overview

The project followed a structured approach:

1.  **Phase 1: Data Quality Assessment & Preparation:** Cleaned and validated raw `BKPF` and `FAGLFLEXA` data extracts. Discarded `BSEG` due to imbalances. Removed duplicates.
2.  **Phase 2: Exploratory Data Analysis & Feature Engineering:** Analyzed cleaned data patterns and engineered 16 features quantifying anomaly indicators. Resulted in `sap_engineered_features.csv`.
3.  **Phase 3: Baseline Anomaly Detection & Evaluation:** Scaled features, applied IF and LOF models, evaluated initial results.
4.  **Phase 4: Advanced Modeling & Prioritization:** Trained Autoencoder model, combined all model outputs and HRFs, implemented prioritization logic, generated context, and created the final anomaly list.
5.  **Phase 5: UI Development:** Built the Streamlit dashboard for interactive analysis and investigation.

*(For detailed methodology, please refer to the `Comprehensive_Project_Report.pdf` in the `/docs` folder - if you include it).*

## Technology Stack

*   **Core Language:** Python 3.x
*   **Data Manipulation & Analysis:** Pandas, NumPy
*   **Machine Learning:** Scikit-learn (IsolationForest, LocalOutlierFactor, StandardScaler), TensorFlow/Keras (Autoencoder)
*   **Visualization:** Matplotlib, Seaborn, Plotly Express
*   **Dashboard:** Streamlit, streamlit-aggrid
*   **Utilities:** Joblib (for saving scaler)

## Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone [Your Repository URL]
    cd [Your Repository Name]
    ```
2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    # Activate the environment (Windows)
    .\venv\Scripts\activate
    # Activate the environment (Linux/macOS)
    source venv/bin/activate
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: Installing TensorFlow might require specific system configurations, especially for GPU support. Refer to official TensorFlow documentation if needed.)*

## Usage

1.  **Prepare Data:** Ensure the required input files (generated from previous steps or provided as samples *derived from the public dataset*) are available:
    *   `phase4_step6_prioritize_anomalies_[TIMESTAMP].csv` (The prioritized list)
    *   `sap_engineered_features__[TIMESTAMP].csv` (The features file)
    *(Update the filenames in the Streamlit script (`enhanced_sap_anomaly_explorer_7.py`) or use the file uploader interface).*
2.  **Run the Streamlit Application:**
    ```bash
    streamlit run enhanced_sap_anomaly_explorer_7.py
    ```
3.  **Interact:** Use the file uploaders in the Streamlit app, then interact with the filters, visualizations, and tables to explore the anomaly data.

## Project Structure 
.
├── docs/
│ └── Comprehensive_Project_Report.pdf # Optional: Detailed Report
├── notebooks/ # Optional: Jupyter notebooks for EDA/Eval
│ └── eda_analysis.ipynb
├── scripts/ # Python scripts for each phase
│ ├── phase1_data_quality.py
│ ├── phase2_eda_feature_eng.py
│ ├── phase3_step3_prep_and_baseline.py
│ ├── phase3_step4b_baseline_eval.py
│ ├── phase3_step4c_visualization.py
│ ├── phase4_step5_autoencoder_gpu_2.py
│ ├── phase4_step6_prioritize_anomalies_2.py
│ └── enhanced_sap_anomaly_explorer_7.py # Streamlit App
├── data/ # Optional: For SMALL samples derived from public data ONLY
│ └── sample_prioritized_anomalies.csv
├── sap_logo.png # If used by Streamlit app
├── requirements.txt # Python dependencies
└── README.md # This file


## Future Work & SAP Integration

This POC establishes a strong foundation. Next steps include:


*   Rigorous quantitative model evaluation and tuning.
*   Developing a robust integration strategy for operational deployment within an SAP landscape, potentially leveraging:
    *   **Data:** OData Services (from CDS Views), SAP Data Intelligence Cloud.
    *   **Models:** SAP BTP AI Core / AI Launchpad.
    *   **UI/Actions:** Custom Fiori Apps, SAP Analytics Cloud, SAP Workflow (Build Process Automation).

## License

**All rights reserved.**

Copyright (c) 2025 Anitha R

The code and content in this repository are the proprietary intellectual property of the author. **No part of this repository may be copied, modified, distributed, or used in any form without the express prior written permission of the author.**

For inquiries regarding licensing for commercial or other use, please contact AR-Version2.

## Contact

AR-Version2
