use colored::*;
use reqwest::blocking::Client;
use serde_json::Value;
#[cfg(windows)]
use winconsole::console::{clear, set_title};

use wuwa_downloader::{
    config::status::Status,
    io::{
        console::print_results,
        file::get_dir,
        util::{
            calculate_total_size, download_resources, exit_with_error, setup_ctrlc, track_progress, start_title_thread
        },
        logging::setup_logging,
    },
    network::client::{fetch_index, get_config},
};

fn main() {
    #[cfg(windows)]
    set_title("Wuthering Waves Downloader").unwrap();

    let log_file = setup_logging();
    let client = Client::new();

    let config = match get_config(&client) {
        Ok(c) => c,
        Err(e) => exit_with_error(&log_file, &e),
    };

    let folder = get_dir();

    #[cfg(windows)]
    clear().unwrap();
    println!(
        "\n{} Download folder: {}\n",
        Status::info(),
        folder.display().to_string().cyan()
    );

    let data = fetch_index(&client, &config, &log_file);
    let resources = match data.get("resource").and_then(Value::as_array) {
        Some(res) => res,
        None => exit_with_error(&log_file, "No resources found in index file"),
    };

    println!(
        "{} Found {} files to download\n",
        Status::info(),
        resources.len().to_string().cyan()
    );

    let total_size = calculate_total_size(resources, &client, &config);

    #[cfg(windows)]
    clear().unwrap();

    let (should_stop, success, progress) = track_progress(total_size);

    let title_thread = start_title_thread(
        should_stop.clone(),
        success.clone(),
        progress.clone(),
        resources.len(),
    );

    setup_ctrlc(should_stop.clone());

    download_resources(
        &client,
        &config,
        resources,
        &folder,
        &log_file,
        &should_stop,
        &progress,
        &success,
    );

    should_stop.store(true, std::sync::atomic::Ordering::SeqCst);
    title_thread.join().unwrap();

    #[cfg(windows)]
    clear().unwrap();
    
    print_results(
        success.load(std::sync::atomic::Ordering::SeqCst),
        resources.len(),
        &folder,
    );
}
