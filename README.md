# CRONDA (Cloud Resource Organization and Deletion Automation)

CRONDA is an open-source tool designed to automate the management and cleanup of Google Cloud Storage (GCS) buckets. It provides both a web interface and CLI for managing cloud resources efficiently.

## Features

- 🖥️ Modern web dashboard for bucket management
- 🔍 Automatic scanning of old and unused buckets
- 🏷️ Tag-based bucket organization
- 🗑️ Safe deletion with confirmation and dry-run options
- 📊 Analytics and reporting
- 🔐 Authentication and authorization
- ⚡ CLI for automation and scripting
- 📝 Detailed deletion history

## Installation

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

## Usage

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

## Development

### Project Structure

```
cronda/
├── src/                    # Backend source code
│   ├── api/               # FastAPI application
│   ├── cli/               # CLI implementation
│   ├── services/          # Business logic
│   └── utils/             # Utility functions
├── frontend/              # React frontend
├── tests/                 # Test suite
├── logs/                  # Log files
└── requirements.txt       # Python dependencies
```

### Running Tests

```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- FastAPI for the backend framework
- React for the frontend framework
- Google Cloud Storage API
- Material-UI for the frontend components

## Support

For support, please open an issue in the GitHub repository or contact the maintainers. 