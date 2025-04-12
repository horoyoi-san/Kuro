use std::{fs, io, io::Write, path::{Path, PathBuf}};
use md5::{Digest, Md5};

use crate::config::status::Status;

pub fn calculate_md5(path: &Path) -> String {
    let mut file = fs::File::open(path).unwrap();
    let mut hasher = Md5::new();
    io::copy(&mut file, &mut hasher).unwrap();
    format!("{:x}", hasher.finalize())
}

pub fn check_existing_file(path: &Path, expected_md5: Option<&str>, expected_size: Option<u64>) -> bool {
    if !path.exists() {
        return false;
    }

    if let Some(size) = expected_size {
        if fs::metadata(path).map(|m| m.len()).unwrap_or(0) != size {
            return false;
        }
    }

    if let Some(md5) = expected_md5 {
        if calculate_md5(path) != md5 {
            return false;
        }
    }

    true
}

pub fn get_filename(path: &str) -> String {
    Path::new(path)
        .file_name()
        .and_then(|n| n.to_str())
        .unwrap_or(path)
        .to_string()
}

pub fn get_dir() -> PathBuf {
    loop {
        print!(
            "{} Enter download directory (Enter for current): ",
            Status::question()
        );
        io::stdout().flush().unwrap();

        let mut input = String::new();
        io::stdin().read_line(&mut input).unwrap();
        let path = input.trim();

        let path = if path.is_empty() {
            std::env::current_dir().unwrap()
        } else {
            PathBuf::from(shellexpand::tilde(path).into_owned())
        };

        if path.is_dir() {
            return path;
        }

        print!(
            "{} Directory doesn't exist. Create? (y/n): ",
            Status::warning()
        );
        io::stdout().flush().unwrap();

        let mut input = String::new();
        io::stdin().read_line(&mut input).unwrap();

        if input.trim().to_lowercase() == "y" {
            fs::create_dir_all(&path).unwrap();
            return path;
        }
    }
}