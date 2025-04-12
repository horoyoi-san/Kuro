# 🌊 Wuthering Waves Downloader

*A high-performance, reliable downloader for Wuthering Waves with multi-CDN support and verification*

> Feel free to open Pull requests if you want to contribute with improvements!

[![Rust](https://img.shields.io/badge/Rust-1.87.0--nightly-orange?logo=rust)](https://www.rust-lang.org/)
[![License](https://img.shields.io/badge/License-MIT-blue)](LICENSE)

## 📦 Requirements
- **Rust nightly toolchain** - 1.87.0-nightly or newer
- **Windows** - for full console feature support

### 🛠️ Installation & Usage
- **Install the nightly toolchain:**
```bash
rustup toolchain install nightly
rustup default nightly
```

- **Clone the repository:**
```bash
git clone https://github.com/yourusername/wuthering-waves-downloader.git
cd wuthering-waves-downloader
```

- **Build the project:**
```bash
cargo build --release
```

## 🌟 Key Features

### 🚀 Download Management
- **Multi-CDN Fallback** - Automatically tries all available CDN mirrors

- **Version Selection** - Interactive menu for Live/Beta versions

- **Verified Downloads** - MD5 checksum validation for every file

- **Smart Retry Logic** - 3 retry attempts per CDN with timeout protection

- **GZIP Support** - Handles compressed responses efficiently

### 🛡️ Reliability
- **Atomic Operations** - Thread-safe progress tracking

- **Graceful Interrupt** - CTRL-C handling with summary display

- **Comprehensive Logging** - Detailed error logging with timestamps

- **Validation Failures** - Auto-removes files with checksum mismatches

### 📂 File Management
- **Smart Path Handling** - Cross-platform path support

- **Auto-directory Creation** - Builds full directory trees as needed

- **Clean Failed Downloads** - Removes corrupted files automatically

### 💻 User Interface
- **Color-coded Output** - Clear visual feedback (success/warning/error)

- **Dynamic Title Updates** - Real-time progress in window title

- **Clean Progress Display** - Simplified download status without clutter

- **Formatted Duration** - Clear elapsed time display (HH:MM:SS)

### ⚙️ Technical Details
- **Streaming Downloads** - Memory-efficient chunked transfers

- **HEAD Request Verification** - Pre-checks file availability

- **Multi-threaded** - Safe concurrent progress tracking

- **Configurable Timeouts** - 30s for metadata, 300s for downloads
