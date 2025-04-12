use std::{io, path::Path};
use colored::Colorize;
use crate::config::status::Status;

pub fn print_results(success: usize, total: usize, folder: &Path) {
    let title = if success == total {
        " DOWNLOAD COMPLETE ".on_blue().white().bold()
    } else {
        " PARTIAL DOWNLOAD ".on_blue().white().bold()
    };

    println!("\n{}\n", title);
    println!(
        "{} Successfully downloaded: {}",
        Status::success(),
        success.to_string().green()
    );
    println!(
        "{} Failed downloads: {}",
        Status::error(),
        (total - success).to_string().red()
    );
    println!(
        "{} Files saved to: {}",
        Status::info(),
        folder.display().to_string().cyan()
    );
    println!("\n{} Press Enter to exit...", Status::warning());
    let _ = io::stdin().read_line(&mut String::new());
}
