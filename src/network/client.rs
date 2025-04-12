use colored::Colorize;
use flate2::read::GzDecoder;
use reqwest::blocking::Client;
use serde_json::{from_reader, from_str, Value};
use std::{io::{Read, Write}, fs, io, path::Path, time::Duration};
#[cfg(windows)]
use winconsole::console::clear;

use crate::config::cfg::Config;
use crate::download::progress::DownloadProgress;
use crate::io::file::{calculate_md5, check_existing_file, get_filename};
use crate::io::{logging::log_error, util::get_version};
use crate::config::status::Status;

const INDEX_URL: &str = "https://gist.githubusercontent.com/horoyoi-san/1ab06a46cfd9075b3aecf327a42d59bc/raw/7b63fe3c43123242ba6caa99d6af8e209f10f244/wuwa.json";
const MAX_RETRIES: usize = 3;
const DOWNLOAD_TIMEOUT: u64 = 300;
const BUFFER_SIZE: usize = 8192;

pub fn fetch_index(client: &Client, config: &Config, log_file: &fs::File) -> Value {
    println!("{} Fetching index file...", Status::info());

    let mut response = match client
        .get(&config.index_url)
        .timeout(Duration::from_secs(30))
        .send()
    {
        Ok(resp) => resp,
        Err(e) => {
            log_error(log_file, &format!("Error fetching index file: {}", e));

            #[cfg(windows)]
            clear().unwrap();

            println!("{} Error fetching index file: {}", Status::error(), e);
            println!("\n{} Press Enter to exit...", Status::warning());
            let _ = io::stdin().read_line(&mut String::new());
            std::process::exit(1);
        }
    };

    if !response.status().is_success() {
        let msg = format!("Error fetching index file: HTTP {}", response.status());
        log_error(log_file, &msg);

        #[cfg(windows)]
        clear().unwrap();
        
        println!("{} {}", Status::error(), msg);
        println!("\n{} Press Enter to exit...", Status::warning());
        let _ = io::stdin().read_line(&mut String::new());
        std::process::exit(1);
    }

    let content_encoding = response
        .headers()
        .get("content-encoding")
        .and_then(|v| v.to_str().ok())
        .unwrap_or("");

    let text = if content_encoding.contains("gzip") {
        let mut buffer = Vec::new();
        if let Err(e) = response.copy_to(&mut buffer) {
            log_error(log_file, &format!("Error reading index file bytes: {}", e));

            #[cfg(windows)]
            clear().unwrap();
            
            println!("{} Error reading index file: {}", Status::error(), e);
            println!("\n{} Press Enter to exit...", Status::warning());
            let _ = io::stdin().read_line(&mut String::new());
            std::process::exit(1);
        }

        let mut gz = GzDecoder::new(&buffer[..]);
        let mut decompressed_text = String::new();
        if let Err(e) = gz.read_to_string(&mut decompressed_text) {
            log_error(log_file, &format!("Error decompressing index file: {}", e));
            
            #[cfg(windows)]
            clear().unwrap();
            
            println!("{} Error decompressing index file: {}", Status::error(), e);
            println!("\n{} Press Enter to exit...", Status::warning());
            let _ = io::stdin().read_line(&mut String::new());
            std::process::exit(1);
        }
        decompressed_text
    } else {
        match response.text() {
            Ok(t) => t,
            Err(e) => {
                log_error(
                    log_file,
                    &format!("Error reading index file response: {}", e),
                );

                #[cfg(windows)]
                clear().unwrap();
                
                println!("{} Error reading index file: {}", Status::error(), e);
                println!("\n{} Press Enter to exit...", Status::warning());
                let _ = io::stdin().read_line(&mut String::new());
                std::process::exit(1);
            }
        }
    };

    println!("{} Index file downloaded successfully", Status::success());

    match from_str(&text) {
        Ok(v) => v,
        Err(e) => {
            log_error(log_file, &format!("Error parsing index file JSON: {}", e));
            
            #[cfg(windows)]
            clear().unwrap();
            
            println!("{} Error parsing index file: {}", Status::error(), e);
            println!("\n{} Press Enter to exit...", Status::warning());
            let _ = io::stdin().read_line(&mut String::new());
            std::process::exit(1);
        }
    }
}

pub fn download_file(
    client: &Client,
    config: &Config,
    dest: &str,
    folder: &Path,
    expected_md5: Option<&str>,
    log_file: &fs::File,
    should_stop: &std::sync::atomic::AtomicBool,
    progress: &DownloadProgress,
) -> bool {
    if should_stop.load(std::sync::atomic::Ordering::SeqCst) {
        return false;
    }

    let dest = dest.replace('\\', "/");
    let path = folder.join(&dest);
    let filename = get_filename(&dest);

    let mut file_size = None;

    for base_url in &config.zip_bases {
        if should_stop.load(std::sync::atomic::Ordering::SeqCst) {
            return false;
        }

        let url = format!("{}{}", base_url, dest);

        if let Ok(head_response) = client.head(&url).timeout(Duration::from_secs(10)).send() {
            if let Some(size) = head_response.headers()
                .get("content-length")
                .and_then(|v| v.to_str().ok())
                .and_then(|s| s.parse::<u64>().ok())
            {
                file_size = Some(size);
                progress.total_bytes.fetch_add(size, std::sync::atomic::Ordering::SeqCst);
                break;
            }
        }
    }

    if let (Some(md5), Some(size)) = (expected_md5, file_size) {
        if should_skip_download(&path, Some(md5), Some(size)) {
            println!("{} File is valid: {}", Status::matched(), filename.bright_purple());
            return true;
        }
    }

    if let Some(parent) = path.parent() {
        if let Err(e) = fs::create_dir_all(parent) {
            log_error(log_file, &format!("Directory error for {}: {}", dest, e));
            println!("{} Directory error: {}", Status::error(), e);
            return false;
        }
    }

    for (i, base_url) in config.zip_bases.iter().enumerate() {
        let url = format!("{}{}", base_url, dest);

        let head_response = match client.head(&url).timeout(Duration::from_secs(10)).send() {
            Ok(resp) if resp.status().is_success() => resp,
            Ok(resp) => {
                log_error(log_file, &format!("CDN {} failed for {} (HTTP {})", i+1, dest, resp.status()));
                continue;
            },
            Err(e) => {
                log_error(log_file, &format!("CDN {} failed for {}: {}", i+1, dest, e));
                continue;
            }
        };

        let expected_size = file_size.or_else(|| head_response.headers()
            .get("content-length")
            .and_then(|v| v.to_str().ok())
            .and_then(|s| s.parse::<u64>().ok()));

        if let (Some(md5), Some(size)) = (expected_md5, expected_size) {
            if check_existing_file(&path, Some(md5), Some(size)) {
                println!("{} File is valid: {}", Status::matched(), filename.bright_purple());
                return true;
            }
        }

        println!("{} Downloading: {}", Status::progress(), filename.purple());

        let mut retries = MAX_RETRIES;
        let mut last_error = None;

        while retries > 0 {
            let result = download_single_file(&client, &url, &path, should_stop, progress);
            
            match result {
                Ok(_) => break,
                Err(e) => {
                    if should_stop.load(std::sync::atomic::Ordering::SeqCst) {
                        return false;
                    }

                    last_error = Some(e);
                    retries -= 1;
                    let _ = fs::remove_file(&path);
                    
                    if retries > 0 {
                        println!("{} Retrying {}... ({} left)", 
                            Status::warning(), filename.yellow(), retries);
                    }
                }
            }
        }

        if should_stop.load(std::sync::atomic::Ordering::SeqCst) {
            return false;
        }

        if retries == 0 {
            log_error(log_file, &format!("Failed after retries for {}: {}", dest, 
                last_error.unwrap_or_default()));
            println!("{} Failed: {}", Status::error(), filename.red());
            return false;
        }

        if let Some(expected) = expected_md5 {
            if should_stop.load(std::sync::atomic::Ordering::SeqCst) {
                return false;
            }
            
            let actual = calculate_md5(&path);
            if actual != expected {
                log_error(log_file, &format!("Checksum failed for {}: expected {}, got {}", 
                    dest, expected, actual));
                fs::remove_file(&path).unwrap();
                println!("{} Checksum failed: {}", Status::error(), filename.red());
                return false;
            }
        }

        println!("{} Downloaded: {}", Status::success(), filename.green());
        return true;
    }

    log_error(log_file, &format!("All CDNs failed for {}", dest));
    println!("{} All CDNs failed for {}", Status::error(), filename.red());
    false
}

fn download_single_file(
    client: &Client,
    url: &str,
    path: &Path,
    should_stop: &std::sync::atomic::AtomicBool,
    progress: &DownloadProgress,
) -> Result<(), String> {
    let mut response = client
        .get(url)
        .timeout(Duration::from_secs(DOWNLOAD_TIMEOUT))
        .send()
        .map_err(|e| format!("Network error: {}", e))?;

    if !response.status().is_success() {
        return Err(format!("HTTP error: {}", response.status()));
    }

    let mut file = fs::File::create(path)
        .map_err(|e| format!("File error: {}", e))?;

    let mut buffer = [0; BUFFER_SIZE];
    loop {
        if should_stop.load(std::sync::atomic::Ordering::SeqCst) {
            return Err("Download interrupted".into());
        }
        
        let bytes_read = response.read(&mut buffer)
            .map_err(|e| format!("Read error: {}", e))?;
            
        if bytes_read == 0 {
            break;
        }
        
        file.write_all(&buffer[..bytes_read])
            .map_err(|e| format!("Write error: {}", e))?;
            
        progress.downloaded_bytes.fetch_add(bytes_read as u64, std::sync::atomic::Ordering::SeqCst);
    }

    Ok(())
}

pub fn get_config(client: &Client) -> Result<Config, String> {
    let selected_index_url = fetch_gist(client)?;
    
    #[cfg(windows)]
    clear().unwrap();

    println!("{} Fetching download configuration...", Status::info());

    let mut response = client
        .get(&selected_index_url)
        .timeout(Duration::from_secs(30))
        .send()
        .map_err(|e| format!("Network error: {}", e))?;

    if !response.status().is_success() {
        return Err(format!("Server error: HTTP {}", response.status()));
    }

    let content_encoding = response
        .headers()
        .get("content-encoding")
        .and_then(|v| v.to_str().ok())
        .unwrap_or("");

    let config: Value = if content_encoding.contains("gzip") {
        let mut buffer = Vec::new();
        response
            .copy_to(&mut buffer)
            .map_err(|e| format!("Error reading response bytes: {}", e))?;

        let mut gz = GzDecoder::new(&buffer[..]);
        let mut decompressed = String::new();
        gz.read_to_string(&mut decompressed)
            .map_err(|e| format!("Error decompressing content: {}", e))?;

        from_str(&decompressed).map_err(|e| format!("Invalid JSON: {}", e))?
    } else {
        from_reader(response).map_err(|e| format!("Invalid JSON: {}", e))?
    };

    let has_default = config.get("default").is_some();
    let has_predownload = config.get("predownload").is_some();

    let selected_config = match (has_default, has_predownload) {
        (true, false) => {
            println!("{} Using default.config", Status::info());
            "default"
        }
        (false, true) => {
            println!("{} Using predownload.config", Status::info());
            "predownload"
        }
        (true, true) => {
            loop {
                print!("{} Choose config to use (1=default, 2=predownload): ", Status::question());
                io::stdout().flush().map_err(|e| format!("Failed to flush stdout: {}", e))?;
                
                let mut input = String::new();
                io::stdin()
                    .read_line(&mut input)
                    .map_err(|e| format!("Failed to read input: {}", e))?;
                
                match input.trim() {
                    "1" => break "default",
                    "2" => break "predownload",
                    _ => println!("{} Invalid choice, please enter 1 or 2", Status::error()),
                }
            }
        }
        (false, false) => return Err("Neither default.config nor predownload.config found in response".to_string()),
    };

    let config_data = config
        .get(selected_config)
        .ok_or_else(|| format!("Missing {} config in response", selected_config))?;

    let base_config = config_data
        .get("config")
        .ok_or_else(|| format!("Missing config in {} response", selected_config))?;

    let base_url = base_config
        .get("baseUrl")
        .and_then(Value::as_str)
        .ok_or("Missing or invalid baseUrl")?;

    let index_file = base_config
        .get("indexFile")
        .and_then(Value::as_str)
        .ok_or("Missing or invalid indexFile")?;

    let cdn_list = config_data
        .get("cdnList")
        .and_then(Value::as_array)
        .ok_or("Missing or invalid cdnList")?;

    let mut cdn_urls = Vec::new();
    for cdn in cdn_list {
        if let Some(url) = cdn.get("url").and_then(Value::as_str) {
            cdn_urls.push(url.trim_end_matches('/').to_string());
        }
    }

    if cdn_urls.is_empty() {
        return Err("No valid CDN URLs found".to_string());
    }

    let full_index_url = format!("{}/{}", cdn_urls[0], index_file.trim_start_matches('/'));
    let zip_bases = cdn_urls
        .iter()
        .map(|cdn| format!("{}/{}", cdn, base_url.trim_start_matches('/')))
        .collect();

    Ok(Config {
        index_url: full_index_url,
        zip_bases,
    })
}

fn should_skip_download(path: &Path, md5: Option<&str>, size: Option<u64>) -> bool {
    if let (Some(md5), Some(size)) = (md5, size) {
        check_existing_file(path, Some(md5), Some(size))
    } else {
        false
    }
}

pub fn fetch_gist(client: &Client) -> Result<String, String> {
    let mut response = client
        .get(INDEX_URL)
        .timeout(Duration::from_secs(30))
        .send()
        .map_err(|e| format!("Network error: {}", e))?;

    if !response.status().is_success() {
        return Err(format!("Server error: HTTP {}", response.status()));
    }

    let content_encoding = response
        .headers()
        .get("content-encoding")
        .and_then(|v| v.to_str().ok())
        .unwrap_or("");

    let gist_data: Value = if content_encoding.contains("gzip") {
        let mut buffer = Vec::new();
        response.copy_to(&mut buffer)
            .map_err(|e| format!("Error reading response: {}", e))?;
        
        let mut gz = GzDecoder::new(&buffer[..]);
        let mut decompressed = String::new();
        gz.read_to_string(&mut decompressed)
            .map_err(|e| format!("Error decompressing: {}", e))?;
        
        from_str(&decompressed).map_err(|e| format!("Invalid JSON: {}", e))?
    } else {
        from_reader(response).map_err(|e| format!("Invalid JSON: {}", e))?
    };

    println!("{} Available versions:", Status::info());
    println!("1. Live - OS");
    println!("2. Live - CN");
    println!("3. Beta - OS");
    println!("4. Beta - CN");

    loop {
        print!("{} Select version: ", Status::question());
        io::stdout().flush().unwrap();

        let mut input = String::new();
        io::stdin().read_line(&mut input).unwrap();

        match input.trim() {
            "1" => return get_version(&gist_data, "live", "os"),
            "2" => return get_version(&gist_data, "live", "cn"),
            "3" => return get_version(&gist_data, "beta", "os"),
            "4" => return get_version(&gist_data, "beta", "cn"),
            _ => println!("{} Invalid selection", Status::error()),
        }
    }
}
