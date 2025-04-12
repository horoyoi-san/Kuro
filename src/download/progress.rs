use std::{sync::Arc, time::Instant};

#[derive(Clone)]
pub struct DownloadProgress {
    pub total_bytes: Arc<std::sync::atomic::AtomicU64>,
    pub downloaded_bytes: Arc<std::sync::atomic::AtomicU64>,
    pub start_time: Instant,
}