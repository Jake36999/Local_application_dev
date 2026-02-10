# Directory Bundler Web Interface

## 🌐 Overview

A modern web-based interface for the Directory Bundler v4.5, allowing you to scan, analyze, and explore code repositories through your browser.

## ✨ Features

- **Custom Path Selection**: Point the bundler at any directory on your system
- **Real-time Progress Tracking**: Watch your scan progress in real-time
- **Interactive Results Viewer**: Browse files, tree structure, duplicates, and security findings
- **Scan History**: Access all your previous scans
- **AI Integration**: Optional LM Studio integration for AI-powered analysis
- **Responsive Design**: Works on desktop and mobile browsers

## 🚀 Quick Start

### 1. Start the Web Server

Double-click `Start_Web_Interface.bat` or run:

```bash
python -c "from Directory_bundler_v4_5 import BundlerAPIHandler; handler = BundlerAPIHandler(port=8000); handler.start_server()"
```

### 2. Open Your Browser

Navigate to: **http://localhost:8000**

### 3. Configure Your Scan

1. Enter the target directory path (or use `.` for current directory)
2. Select analysis mode (Quick or Full)
3. Configure options (file size limits, include tests, etc.)
4. Click "Start Scan"

### 4. View Results

- Monitor real-time progress
- View comprehensive scan results across multiple tabs
- Access scan history for previous analyses

## 📁 Web Interface Files

```
static/
  ├── index.html    # Main web interface
  ├── styles.css    # Styling and layout
  └── app.js        # JavaScript functionality
```

## 🎯 Usage Examples

### Scan Current Directory
```
Target Path: .
Mode: Quick Static Analysis
```

### Scan Specific Project
```
Target Path: C:\Users\YourName\Documents\MyProject
Mode: Full Dynamic Analysis
Max File Size: 50 MB
Include Tests: ✓
```

### Scan with AI Analysis
```
Target Path: ./src
Mode: Full
Enable AI Analysis: ✓
AI Persona: Security Auditor
```

## 🔧 API Endpoints

The web interface communicates with these backend endpoints:

- `POST /api/scan` - Start a new scan
- `GET /api/status?uid={uid}` - Check scan status
- `GET /api/results?uid={uid}` - Get scan results
- `GET /api/history` - Get scan history
- `GET /api/report?uid={uid}` - Generate report

## 📊 Results Structure

Scan results are stored in `bundler_scans/{uid}/`:

```
bundler_scans/
  └── {scan_uid}/
      ├── manifest.json      # Scan metadata
      ├── tree.json          # Directory hierarchy
      ├── labels.json        # Duplicates and labels
      ├── files/             # Individual file analysis
      │   ├── file_0001.json
      │   └── file_0002.json
      └── chunks/            # Chunked content
          ├── chunk_01.json
          └── chunk_02.json
```

## 🎨 Interface Tabs

### Summary Tab
- Total files, size, chunks
- Scan metadata and configuration
- Overall statistics

### Files Tab
- List of all scanned files
- File metadata and paths
- Quick access to file details

### Tree View Tab
- Hierarchical directory structure
- Navigate through folders
- Visual representation of codebase

### Duplicates Tab
- Content-based duplicate detection
- Grouped by file hash
- Identify redundant files

### Security Tab
- Security vulnerability findings
- Dangerous function detection
- Hardcoded secrets detection
- OWASP pattern matching

## 🔒 Security Features

The web interface includes:

- Path traversal prevention
- Input sanitization
- File size limits
- Secure directory validation
- CORS headers for API access

## 🐛 Troubleshooting

### Server Won't Start
- Check Python is installed: `python --version`
- Install dependencies: `pip install -r requirements.txt`
- Verify port 8000 is available

### Can't Connect to Server
- Ensure server is running (check terminal)
- Check firewall settings
- Try accessing http://127.0.0.1:8000

### Scans Fail to Complete
- Verify target path exists
- Check file permissions
- Review console logs for errors

## 💡 Tips

1. **Use Absolute Paths**: For best results, use full paths like `C:\Users\...`
2. **Watch File Sizes**: Large repositories may take time to scan
3. **Enable Cache**: Speed up repeated scans of the same directory
4. **Review History**: Access previous scans without re-scanning

## 🔗 Integration with LM Studio

For AI-powered analysis:

1. Install and start LM Studio (http://localhost:1234)
2. Check "Enable AI Analysis" in the web interface
3. Select an AI Persona (Security Auditor, Code Tutor, etc.)
4. Run your scan with enhanced AI insights

## 📝 Notes

- The web interface requires the Directory Bundler backend running
- Results persist in the `bundler_scans/` directory
- Scan history is stored in `bundler_scans/scan_index.json`
- Cache data is stored in `.bundler_cache/`

## 🎉 Enjoy Your Enhanced Directory Bundler Experience!

For command-line usage, see the main README.md
