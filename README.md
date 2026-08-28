# 🛡️ CyberSentinel AI

## Real-Time Network Intrusion Detection System using Machine Learning

CyberSentinel AI is an AI-powered network intrusion detection system designed to identify potentially malicious network traffic using machine learning.

The system was developed using the **CICIDS2017 intrusion detection dataset** and evaluates multiple machine learning algorithms — **Logistic Regression, K-Nearest Neighbors (KNN), Random Forest, and XGBoost** — for binary network traffic classification.

The selected model can be integrated with a live network-flow monitoring pipeline to analyze traffic and classify it as:

- ✅ **NOT ATTACK**
- 🚨 **ATTACK**

The project also includes an interactive **Streamlit web interface** for network-flow analysis, prediction visualization, and security analytics, along with a local Windows monitoring component using **Scapy and Npcap**.

---

## 🚀 Project Overview

Traditional network intrusion detection systems often rely heavily on predefined signatures and rules. CyberSentinel AI explores a machine-learning-based approach in which network-flow characteristics are analyzed to identify suspicious traffic patterns.

The project follows an end-to-end machine-learning workflow:

```text
CICIDS2017 Dataset
        │
        ▼
Feature Selection
        │
        ▼
Data Cleaning
        │
        ▼
Duplicate Removal
        │
        ▼
Binary Target Creation
        │
        ▼
Train / Test Split
        │
        ├───────────────┐
        ▼               ▼
Logistic Regression    KNN
        │               │
        ├───────────────┤
        ▼               ▼
Random Forest        XGBoost
        │               │
        └───────┬───────┘
                ▼
        Model Comparison
                │
                ▼
          Best Model
                │
                ▼
       Threshold Optimization
                │
                ▼
        Live Flow Inference
                │
                ▼
       Streamlit Dashboard


🎯 Objectives

The main objectives of CyberSentinel AI are:

1. Build a machine-learning-based network intrusion detection system.
2. Convert multiclass intrusion labels into a binary classification problem.
3. Compare several classical and ensemble machine-learning algorithms.
4. Evaluate models using security-relevant classification metrics.
5. Select the best-performing model based on appropriate evaluation criteria.
6. Implement probability-based threat classification.
7. Develop a local real-time network monitoring prototype.
8. Provide an interactive interface for network-flow analysis and predictions.

🧠 Classification Problem

The original CICIDS2017 dataset contains multiple types of network traffic and attacks.

For this project, the original labels are converted into a binary target.

Target Mapping
| Original Label         | Binary Class |
| ---------------------- | ------------ |
| `BENIGN`               | `NOT ATTACK` |
| `DDoS`                 | `ATTACK`     |
| `DoS Hulk`             | `ATTACK`     |
| `DoS GoldenEye`        | `ATTACK`     |
| `PortScan`             | `ATTACK`     |
| `FTP-Patator`          | `ATTACK`     |
| `SSH-Patator`          | `ATTACK`     |
| `Bot`                  | `ATTACK`     |
| `Web Attack`           | `ATTACK`     |
| `Infiltration`         | `ATTACK`     |
| `Heartbleed`           | `ATTACK`     |
| Other malicious labels | `ATTACK`     |

Final encoding:

0 → NOT ATTACK
1 → ATTACK

This allows the model to focus on the primary security question:

Is this network flow benign or potentially malicious?

📊 Dataset

CICIDS2017

The project uses the CICIDS2017 intrusion detection dataset developed by the Canadian Institute for Cybersecurity.

The dataset contains benign network traffic and several realistic attack scenarios represented using network-flow features.

Dataset source

Official source:

https://www.unb.ca/cic/datasets/ids-2017.html

Dataset characteristics

The dataset contains network-flow features such as:
>Destination Port
>Flow Duration
>Forward packet count
>Backward packet count
>Forward bytes
>Backward bytes
>Flow byte rate
>Flow packet rate
>TCP flag statistics
>Packet-length statistics
>Network traffic labels

The original dataset contains substantially more features; this project creates a reduced feature dataset containing only the features required for the modelling and live-flow prototype.


🔧 Selected Features
CyberSentinel AI currently uses the following 18 network-flow features:

Destination Port
Flow Duration
Total Fwd Packets
Total Backward Packets
Total Length of Fwd Packets
Total Length of Bwd Packets
Flow Bytes/s
Flow Packets/s
Fwd Packets/s
Bwd Packets/s
SYN Flag Count
ACK Flag Count
RST Flag Count
Average Packet Size
Min Packet Length
Max Packet Length
Packet Length Mean
Packet Length Std

These features describe traffic volume, packet behavior, connection duration, flow rates, packet statistics, and TCP flag characteristics.

🗂️ Project Structure

CyberSentinel-AI/
│
├── data/
│   ├── processed/
│   │   ├── cicids_required_features.csv
│   │   └── cicids2017_combined.csv
│   │
│   └── raw/
│       ├── Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv
│       ├── Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv
│       ├── Friday-WorkingHours-Morning.pcap_ISCX.csv
│       ├── Monday-WorkingHours.pcap_ISCX.csv
│       ├── Thursday-WorkingHours-Afternoon-Infiltration.pcap_ISCX.csv
│       ├── Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv
│       ├── Tuesday-WorkingHours.pcap_ISCX.csv
│       └── Wednesday-workingHours.pcap_ISCX.csv
│
├── notebooks/
│   └── 01_XGBoost_Training.ipynb
│
├── models/
│   ├── best_model.pkl
│   ├── features.pkl
│   ├── knn_pipeline.pkl
│   ├── logistic_regression_pipeline.pkl
│   ├── model_metadata.json
│   ├── random_forest.pkl
│   └── xgboost.pkl
│
├── src/
│   ├── check_data.py
│   ├── combine_data.py
│   ├── combine_required_features.py
│   ├── live_detector.py
│   ├── live_flow.py
│   ├── live_monitor.py
│   └── prepare_data.py
│
├── app.py
├── requirements.txt
├── run_live.py
├── README.md
└── .gitignore

🔄 Machine Learning Pipeline

1. Data Preparation

The original CICIDS2017 CSV files are first reduced to the required network-flow features.

Raw CICIDS2017 CSVs
        ↓
Feature Selection
        ↓
cicids_required_features.csv

The reduced dataset is used as the input for the modelling notebook.

2. Data Cleaning

The modelling pipeline performs several cleaning operations:
Column normalization
Leading/trailing whitespace is removed from column names.
Numeric conversion
Network-flow features are converted to numeric values.
Infinite-value handling
Infinite values are replaced with NaN.
Missing-value handling
Rows containing invalid feature values are removed.
Duplicate handling
Exact duplicate rows are identified and removed before model training.
This is important because duplicate flows appearing in both training and testing data can result in overly optimistic evaluation results.

⚖️ Class Imbalance

Network intrusion datasets often contain more benign traffic than malicious traffic.
CyberSentinel AI therefore checks the class distribution before training.

For the tree-based models, training uses class weighting through:

scale_pos_weight

The weight is calculated from the training split:

scale_pos_weight =
    number_of_NOT_ATTACK_samples /
    number_of_ATTACK_samples

This helps the classifier pay more attention to the minority attack class.   

✂️ Train/Test Split

The cleaned dataset is divided into:

80% → Training
20% → Testing

A stratified split is used:

train_test_split(
    X,
    y,
    test_size=0.20,
    stratify=y,
    random_state=42
)

Stratification ensures that the proportion of ATTACK and NOT ATTACK samples remains approximately consistent between the training and test sets.

🤖 Machine Learning Models

Four algorithms are evaluated.

1. Logistic Regression

Logistic Regression is used as a simple linear baseline.

It provides a useful reference point for determining whether more complex models provide meaningful improvements.

Scaling is applied before Logistic Regression.

2. K-Nearest Neighbors

KNN is included as a distance-based baseline.

Because KNN becomes computationally expensive on millions of network flows, a representative training subset is used for the KNN experiment.

Standardization is applied because KNN is distance-based.

3. Random Forest

Random Forest provides a strong non-linear ensemble baseline.

It works directly on the network-flow features without standardization.

Class balancing is enabled during training.

4. XGBoost

XGBoost is used as the primary gradient-boosting candidate.

Configuration includes:

XGBClassifier(
    objective="binary:logistic",
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=scale_pos_weight,
    eval_metric="logloss",
    tree_method="hist",
    random_state=42
)

The histogram tree method is used to improve training efficiency on the large tabular dataset.

📏 Model Evaluation

The models are evaluated using multiple metrics rather than accuracy alone.

Accuracy

Measures the overall proportion of correctly classified flows.

Accuracy =
correct predictions / total predictions

Precision

Measures how many flows predicted as attacks were actually attacks.

Important for controlling false alarms.

Precision =
True Positives /
(True Positives + False Positives)

Recall

Measures how many real attacks were successfully detected.

This is especially important for an intrusion detection system because missed attacks are potentially costly.

Recall =
True Positives /
(True Positives + False Negatives)

F1-Score

Provides a balance between precision and recall.

F1 =
2 × Precision × Recall /
(Precision + Recall)

ROC-AUC

Measures how well the model separates attack and non-attack flows across classification thresholds.

PR-AUC

Precision-Recall AUC is particularly useful for imbalanced binary classification and is used as the primary model-selection metric in this project.

🏆 Model Selection

All four models are compared in a single evaluation table:

Model
Accuracy
Precision
Recall
F1
ROC-AUC
PR-AUC
Inference Time

Example:

                        Accuracy  Precision  Recall  F1  ROC-AUC  PR-AUC
Logistic Regression
KNN
Random Forest
XGBoost

The final model is selected using PR-AUC, with F1-score and Recall also considered.

The project does not assume that XGBoost will always win; the final model is selected based on the measured performance of the trained models.

🎚️ Threshold Optimization

The default binary classification threshold is:

0.50

However, the optimal threshold for an intrusion detector may not be 0.50.

CyberSentinel AI tests multiple thresholds:

0.10
0.15
0.20
...
0.90

For each threshold, the system calculates:

Precision
Recall
F1-score

The threshold that produces the highest F1-score is stored and can be used during inference.

This provides more flexibility than relying on a fixed 0.50 decision boundary.

🔍 Feature Importance

For the XGBoost model, feature importance is analyzed to identify the network-flow characteristics contributing most strongly to the classification process.

Examples of feature categories include:

Flow rates
Packet counts
Packet lengths
Destination ports
TCP flag counts
Flow duration

The feature importance analysis helps interpret which network characteristics the model relies on most.

🖥️ Real-Time Monitoring

CyberSentinel AI also includes a local Windows real-time monitoring prototype.

The local monitoring architecture is:

Network Interface
       ↓
Npcap
       ↓
Scapy
       ↓
Packet Capture
       ↓
Flow Aggregation
       ↓
Feature Extraction
       ↓
Trained ML Model
       ↓
ATTACK / NOT ATTACK
       ↓
Threat Probability

Technologies

Npcap

Provides packet capture support on Windows.

Scapy

Captures and parses network packets.

Flow Engine

Aggregates packets into network-flow statistics.

Machine Learning Model

Classifies the resulting flow.

📡 Live Flow Processing

The live monitoring component extracts features corresponding to the training feature set, including:

Destination Port
Flow Duration
Forward Packet Count
Backward Packet Count
Forward Bytes
Backward Bytes
Flow Bytes/s
Flow Packets/s
Fwd Packets/s
Bwd Packets/s
SYN Flag Count
ACK Flag Count
RST Flag Count
Packet Size Statistics

The extracted flow is converted to the same feature schema expected by the trained model.

The model returns an attack probability:

P(ATTACK) = 0.91

and the configured threshold determines the final classification:

0.91 >= threshold

→ ATTACK

🌐 Streamlit Application

The Streamlit application provides a shareable web interface for network-flow analysis.

Main capabilities
Upload network-flow CSV files
Validate required features
Clean invalid input values
Run model predictions
Display attack probabilities
Calculate attack rate
Display traffic statistics
Visualize prediction results
Display recent classification results
Download prediction results

Example workflow:

Upload CSV
    ↓
Validate Features
    ↓
Clean Input
    ↓
ML Prediction
    ↓
Attack Probability
    ↓
Classification
    ↓
Analytics Dashboard

🖥️ Local Desktop Monitoring

A local Windows application can be used for live monitoring.

Unlike the Streamlit Cloud application, the local application can access the Windows machine's network interface through Npcap/Scapy.

Windows Machine
      ↓
Network Interface
      ↓
Npcap
      ↓
Scapy
      ↓
CyberSentinel AI
      ↓
Real-Time Prediction

The local monitoring component is intended for authorized traffic and controlled environments.

☁️ Streamlit Cloud Deployment

The Streamlit application can be deployed using GitHub and Streamlit Community Cloud.

Cloud architecture

GitHub Repository
        ↓
Streamlit Community Cloud
        ↓
CyberSentinel AI
        ↓
Upload Network-Flow CSV
        ↓
Best Model
        ↓
Prediction

The cloud application does not directly capture the user's local Wi-Fi/Ethernet traffic because it executes on a remote server.

For real-time local monitoring, use the Windows application.

📦 Installation

1. Clone the repository

git clone https://github.com/SoudipMondal12/CyberSentinel-AI.git

cd CyberSentinel-AI

2. Create a virtual environment

Windows:

python -m venv venv

Activate:

.\venv\Scripts\Activate.ps1

3. Install dependencies

pip install -r requirements.txt

▶️ Running the Streamlit Application

Run:

streamlit run app.py

Then open:

http://localhost:8501

Upload a CSV containing the required network-flow features.

🛡️ Running the Local Real-Time Monitor

Install Npcap first:

https://npcap.com/

Then run PowerShell as Administrator:

python run_live.py

📓 Model Development Notebook

The complete modelling workflow is contained in:

notebooks/01_XGBoost_Training.ipynb

The notebook performs:

Load reduced dataset
        ↓
Data inspection
        ↓
Data cleaning
        ↓
Duplicate removal
        ↓
Binary target creation
        ↓
Exploratory analysis
        ↓
Train/Test split
        ↓
Logistic Regression
        ↓
KNN
        ↓
Random Forest
        ↓
XGBoost
        ↓
Model comparison
        ↓
Confusion Matrix
        ↓
ROC Curve
        ↓
Precision-Recall Curve
        ↓
Threshold analysis
        ↓
Feature importance
        ↓
Best model selection
        ↓
Model saving

💾 Model Artifacts

After training, the project stores:

models/
├── best_model.pkl
├── features.pkl
└── model_metadata.json

best_model.pkl

Contains the selected trained machine-learning model.

features.pkl

Contains the exact feature order expected by the model.

model_metadata.json

Stores information such as:

{
    "best_model": "XGBoost",
    "threshold": 0.5,
    "target_mapping": {
        "0": "NOT ATTACK",
        "1": "ATTACK"
    }
}

The exact values depend on the model-selection results produced during training.

🔐 Security and Ethical Considerations

CyberSentinel AI should only be used for:

Networks you own
Systems you administer
Authorized security testing
Academic/research environments
Controlled laboratory environments

Do not capture or analyze network traffic belonging to other people or organizations without appropriate authorization.

The system is designed as a machine-learning research and monitoring prototype, not a replacement for a complete enterprise security stack.

⚠️ Current Limitations
1. Dataset-to-live distribution shift

The model is trained using CICIDS2017 traffic, while real-world network traffic can have significantly different characteristics.

Therefore:

High ATTACK probability

does not automatically mean that a real attack has occurred.

False positives and false negatives are possible.

2. Live feature compatibility

The live monitoring pipeline calculates network-flow features from captured packets. While the feature names and overall definitions are aligned with the training schema, exact implementation details can differ from the feature-generation process used to create the original CICIDS2017 flow data.

For production deployment, the live feature-generation process should be validated against the exact training-time feature definitions.

3. Local monitoring scope

The Windows application monitors traffic visible to the local capture interface.

It does not automatically provide visibility into every device connected to a network.

4. Production IDS limitations

CyberSentinel AI is not intended to replace enterprise IDS/IPS or SIEM systems.

Production deployment would require additional components such as:

Network sensors
Flow collectors
Authentication
Alert management
Data retention
Model monitoring
Concept-drift detection
Centralized logging
Security operations workflows

🔮 Future Improvements

Possible future development includes:

Advanced Feature Engineering

Add additional network-flow features such as:

Inter-arrival time statistics
TCP window features
Active/idle statistics
Subflow statistics
Header statistics
Multiclass Detection

Extend the current binary classifier:

NOT ATTACK
ATTACK

to:

BENIGN
DDoS
DoS
PortScan
Brute Force
Bot
Web Attack
Infiltration
...

Improved Live Feature Extraction

Develop a more complete CICFlowMeter-compatible live flow-generation pipeline.

Explainability

Integrate SHAP or another model-explanation framework to provide feature-level explanations for individual predictions.

Model Monitoring

Add:

Concept drift detection
Prediction monitoring
False-positive tracking
Model retraining
Performance monitoring

Centralized Architecture

A larger deployment could use:

Network Sensors
      ↓
Flow Collector
      ↓
Message Queue
      ↓
Inference API
      ↓
XGBoost
      ↓
Alert Engine
      ↓
Database
      ↓
Security Dashboard


🧰 Technology Stack

| Technology       | Purpose                              |
| ---------------- | ------------------------------------ |
| Python           | Core development                     |
| Pandas           | Data processing                      |
| NumPy            | Numerical computation                |
| Scikit-learn     | ML preprocessing and baseline models |
| XGBoost          | Gradient-boosting classifier         |
| Scapy            | Network packet capture and analysis  |
| Npcap            | Windows packet capture               |
| Streamlit        | Web-based analysis dashboard         |
| PySide6          | Local desktop monitoring interface   |
| Plotly           | Interactive visualization            |
| Joblib           | Model serialization                  |
| Jupyter Notebook | Model experimentation                |


📈 Project Workflow

                   DATA
                    │
                    ▼
              CICIDS2017
                    │
                    ▼
          Feature Reduction
                    │
                    ▼
             Data Cleaning
                    │
                    ▼
           Duplicate Handling
                    │
                    ▼
            Binary Labeling
                    │
              ┌─────┴─────┐
              │           │
              ▼           ▼
         NOT ATTACK     ATTACK
              │           │
              └─────┬─────┘
                    ▼
             Train/Test Split
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
    Logistic       KNN      Random Forest
       │            │            │
       └────────────┼────────────┘
                    ▼
                 XGBoost
                    │
                    ▼
             Model Evaluation
                    │
                    ▼
              Best Model
                    │
                    ▼
          Threshold Optimization
                    │
                    ▼
             Model Artifact
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
   Local Monitoring      Streamlit Cloud
    Scapy + Npcap          CSV Analysis
          │                   │
          └─────────┬─────────┘
                    ▼
             ATTACK / NOT ATTACK


📌 Example Prediction

A network-flow record may produce:

Destination Port: 443
Flow Duration: 125000
Flow Packets/s: 1842.6
Flow Bytes/s: 958421.2
SYN Flag Count: 2
ACK Flag Count: 10
Packet Length Mean: 520.4

The model may return:

Attack Probability: 94.72%

Prediction:
🚨 ATTACK

Another flow may produce:

Attack Probability: 3.18%

Prediction:
✅ NOT ATTACK

The probability is a model confidence score, not proof that an attack actually occurred.

📁 Dataset Handling

Large datasets are intentionally excluded from the Git repository.

The following are ignored:

data/raw/
*.csv
*.zip
*.parquet

The trained model artifacts are retained:

models/
├── best_model.pkl
├── features.pkl
└── model_metadata.json

This keeps the repository manageable while allowing the application to run using the trained model.

👨‍💻 Author

Soudip Mondal

Machine Learning / AI Project

⭐ Project Highlights

Binary network intrusion detection
CICIDS2017-based modelling
Four-model comparison
Logistic Regression
KNN
Random Forest
XGBoost
Class-imbalance handling
Stratified train/test evaluation
PR-AUC-based model selection
Threshold optimization
Feature importance analysis
Real-time local network monitoring prototype
Scapy + Npcap integration
Streamlit web interface
Windows desktop monitoring
Model serialization and deployment workflow

⚖️ Disclaimer

CyberSentinel AI is an educational and research-oriented network security project.

Predictions generated by machine-learning models should be treated as security signals requiring further investigation, rather than definitive proof of malicious activity.