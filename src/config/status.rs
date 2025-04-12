use colored::*;

#[derive(Clone, Copy)]
pub struct Status;

impl Status {
    pub fn info() -> ColoredString { "[*]".cyan() }
    pub fn success() -> ColoredString { "[+]".green() }
    pub fn warning() -> ColoredString { "[!]".yellow() }
    pub fn error() -> ColoredString { "[-]".red() }
    pub fn question() -> ColoredString { "[?]".blue() }
    pub fn progress() -> ColoredString { "[→]".purple() }
    pub fn matched() -> ColoredString { "[↓]".bright_purple() }
}