// FIXME(static_mut_refs): Do not allow `static_mut_refs` lint
#![allow(static_mut_refs)]

use crate::config::ReplacementConfig;
use curly_injector::replacer::AbstractReplacer;
use curly_injector::utils::EnvBoolMapper;
use curly_injector::{CurlConfig, CurlUserData};
use std::sync::OnceLock;
use windows::core::PCSTR;

static mut UE_CURL_EASY: OnceLock<CurlUserData> = OnceLock::new();
#[cfg(feature = "enable-sdk")]
static mut KR_CURL_EASY: OnceLock<CurlUserData> = OnceLock::new();

pub(crate) fn configure_ue_curl(
    interceptor: &mut interceptor_rs::Interceptor,
    module_name: Option<PCSTR>,
    config: &'static CurlConfig,
    replacement: &ReplacementConfig,
) {
    let module = injector_utils::get_module_base(module_name);
    let replacer = vec![
        // Config Server Replacer
        AbstractReplacer::GenericReplacer(curly_injector::replacer::GenericReplacer {
            regex: regex::Regex::new(replacement.config_server_regex).unwrap(),
            replacement: std::env::var("CFG_SERVER_URL").unwrap_or(
                replacement
                    .replacement_defaults
                    .config_server_default
                    .to_string(),
            ),
            force_http: std::env::var("CFG_SERVER_FORCE_HTTP").map_env_bool(true),
        }),
        // TODO: Hotpatch Server replacer
        // Log server replacer
        AbstractReplacer::GenericReplacer(curly_injector::replacer::GenericReplacer {
            regex: regex::Regex::new(replacement.log_server_regex).unwrap(),
            replacement: std::env::var("LOG_SERVER_URL").unwrap_or(
                replacement
                    .replacement_defaults
                    .log_server_default
                    .to_string(),
            ),
            force_http: std::env::var("LOG_SERVER_FORCE_HTTP").map_env_bool(true),
        }),
    ];
    unsafe {
        curly_injector::hook_curl(
            interceptor,
            module.0 as usize,
            config,
            replacer,
            None,
            &UE_CURL_EASY,
        );
    }
}

// Not sig bypass and regular check already done at top of the file
#[cfg(feature = "enable-sdk")]
pub(crate) fn configure_kr_curl(
    interceptor: &mut interceptor_rs::Interceptor,
    module_name: Option<PCSTR>,
    config: &'static CurlConfig,
    replacement: &ReplacementConfig,
) {
    let module = injector_utils::get_module_base(module_name);
    let replacer = vec![
        // SDK server replacer
        AbstractReplacer::GenericReplacer(curly_injector::replacer::GenericReplacer {
            regex: regex::Regex::new(replacement.sdk_server_regex).unwrap(),
            replacement: std::env::var("SDK_SERVER_URL").unwrap_or(
                replacement
                    .replacement_defaults
                    .sdk_server_default
                    .to_string(),
            ),
            force_http: std::env::var("SDK_SERVER_FORCE_HTTP").map_env_bool(true),
        }),
    ];
    let proxy_config = Some(ProxyConfig {
        proxy_url: "http://127.0.0.1:8888",
        skip_url_replace: true,
    });
    curly_injector::hook_curl(
        interceptor,
        module.0 as usize,
        config,
        replacer,
        proxy_config,
        &KR_CURL_EASY,
    );
}
