use clap::Parser;
use log::{error, info, trace};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
struct Configuration {
    launcher: injector::Launcher,
    environment: Option<injector::Environment>,
}

#[derive(thiserror::Error, Debug)]
pub enum Error {
    #[error("Error reading config file at: {0}\n{1}")]
    ReadFileError(String, std::io::Error),
    #[error("Toml Error: {0}")]
    Toml(#[from] toml::de::Error),
    #[error("Injector Error: {0}")]
    Injector(#[from] injector::Error<'static>),
}

#[derive(clap::ValueEnum, Clone, Default, Debug, Serialize)]
#[serde(rename_all = "kebab-case")]
enum LogLevel {
    /// A level lower than all log levels.
    Off,
    /// Corresponds to the `Error` log level.
    Error,
    /// Corresponds to the `Warn` log level.
    Warn,
    /// Corresponds to the `Info` log level.
    #[default]
    Info,
    /// Corresponds to the `Debug` log level.
    Debug,
    /// Corresponds to the `Trace` log level.
    Trace,
}

/// A generic application launcher that allows dll injection into the process(Only for Windows)
#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    /// The location of the config file
    #[arg(short, long, default_value = "./config.toml")]
    config_file: String,
    /// The log level for the launcher
    #[arg(short, long)]
    log_level: Option<LogLevel>,
}

impl LogLevel {
    fn into_level_filter(self) -> log::LevelFilter {
        match self {
            LogLevel::Off => log::LevelFilter::Off,
            LogLevel::Error => log::LevelFilter::Error,
            LogLevel::Warn => log::LevelFilter::Warn,
            LogLevel::Info => log::LevelFilter::Info,
            LogLevel::Debug => log::LevelFilter::Debug,
            LogLevel::Trace => log::LevelFilter::Trace,
        }
    }
}

#[inline]
fn run(config_file: String) -> Result<injector::Context, Error> {
    // Load launcher config
    let content = match std::fs::read_to_string(&config_file) {
        Ok(content) => Ok(content),
        Err(err) => Err(Error::ReadFileError(config_file, err))
    }?;
    let configuration: Configuration = toml::from_str(content.as_str())?;

    trace!("{:?}", configuration);
    Ok(injector::spawn_process(
        configuration.launcher,
        configuration.environment.unwrap_or_default(),
    )?)
}

fn main() {
    let args = Args::parse();
    colog::default_builder()
        .filter_level(args.log_level.unwrap_or_default().into_level_filter())
        .init();

    match run(args.config_file) {
        Ok(context) => {
            // Since environment pointer has to outlive the process, here we can do several things,
            // either we join the thread of the process, or we just wait
            while injector::is_process_running(context.proc_info) {
                std::thread::sleep(std::time::Duration::from_secs(1))
            }
            info!("Application exited");
        }
        Err(err) => error!("{}", err.to_string())
    }
}