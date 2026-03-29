# CRONDA (Cloud Resource Operations and Deletion Automation)
It is a Google Cloud Resource management tool for Free tier monitoring. It can be be used for GCS (Google Cloud Storage - Bucket) and GCE (Google Compute Engine - VM) resources for Scanning and Deletion processes. Scanning includes tag analysis and filtering options. With CRONDA, one can perform batch analysis & batch deletion process across different projects. Batch deletion also includes a --dry-run capability for safe-deletions. 

### Prerequisites

- Python 3.8+
- Node.js 14+
- Google Cloud account with appropriate permissions
- Google Cloud SDK installed

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cronda.git
cd cronda
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up Google Cloud credentials:
```bash
# Create a service account and download the key
gcloud iam service-accounts create cronda-service-account
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:cronda-service-account@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"
gcloud iam service-accounts keys create cronda-key.json \
    --iam-account=cronda-service-account@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

### Web Interface

1. Start the backend server:
```bash
cd src
python run_api.py
```

2. Access the web interface at `http://localhost:3000`

### CLI Usage

```bash
# List all buckets
cronda scan

# Scan for old buckets
cronda scan --days 30

# Delete a specific bucket (dry run)
cronda delete gs://your-bucket-name --dry-run

# Delete a bucket (actual deletion)
cronda delete gs://your-bucket-name --no-dry-run

# Cleanup old buckets
cronda cleanup --days 30 --dry-run
```
