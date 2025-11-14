#[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
use windows::core::{PCSTR, s};
use curly_injector::CurlConfig;

#[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
pub(crate) struct ReplacementDefaults {
    pub(crate) config_server_default: &'static str,
    // pub(crate) hotpatch_server_default: &'static str,
    pub(crate) log_server_default: &'static str,
    #[cfg(feature = "enable-sdk")]
    pub(crate) sdk_server_default: &'static str,
    pub(crate) watermark_server_default: &'static str,
}

#[cfg(all(not(feature = "enable-sdk"), not(feature = "only-sig-bypass"), feature = "regular"))]
pub(crate) struct DisableSdkConfiguration {
    pub(crate) sdk_dll: PCSTR,
    pub(crate) eula_accept: usize,
    pub(crate) sdk_go_away: usize,
}

#[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
pub(crate) struct ReplacementConfig {
    pub(crate) config_server_regex: &'static str,
    // pub(crate) hotpatch_server_regex: &'static str,
    pub(crate) log_server_regex: &'static str,
    #[cfg(feature = "enable-sdk")]
    pub(crate) sdk_server_regex: &'static str,
    pub(crate) watermark_server_regex: &'static str,
    pub(crate) replacement_defaults: &'static ReplacementDefaults,
}

#[cfg(all(feature = "enable-sdk", not(feature = "only-sig-bypass"), feature = "regular"))]
pub(crate) struct KrCurlConfiguration {
    pub(crate) curl_dll: PCSTR,
    pub(crate) curl_config: CurlConfig,
}

pub(crate) struct InjectConfiguration {
    pub(crate) f_pak_file_check: usize,
    pub(crate) f_pak_file_check_preamble: u64,
    pub(crate) resize_grow: usize,
    pub(crate) f_print_f: usize,
    pub(crate) add_pak_folders_entry: usize,
    pub(crate) add_pak_folders_ret: usize,
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    pub(crate) ue_curl_config: CurlConfig,
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    pub(crate) replacement_config: ReplacementConfig,
    #[cfg(all(not(feature = "enable-sdk"), not(feature = "only-sig-bypass"), feature = "regular"))]
    pub(crate) disable_sdk: DisableSdkConfiguration,
    #[cfg(all(feature = "enable-sdk", not(feature = "only-sig-bypass"), feature = "regular"))]
    pub(crate) kr_curl: KrCurlConfiguration,
}

// TODO: Too lazy
#[cfg(feature = "cn_beta_2_8_0")]
pub(crate) const CONFIG: InjectConfiguration = InjectConfiguration {
    f_pak_file_check: 0x4618D30,
    f_pak_file_check_preamble: 0xCCCCCC050311F1E9,
    resize_grow: 0x090AB90,
    f_print_f: 0x2C2C270,
    add_pak_folders_entry: 0x460E8B0,
    add_pak_folders_ret: 0x4611150,
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    ue_curl_config: CurlConfig {
        handle_rcx_relative_offset: 0x110,
        url_handle_relative_offset: 0x880,
        http_headers_handle_relative_offset: None,
        curl_easy_setopt: 0x6A155A0,
        curl_easy_perform: 0x3F93CB0,
    },
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    replacement_config: ReplacementConfig {
        config_server_regex: r#"^(https|http)://.*/([a-zA-Z0-9]{32}/index\.json)$"#,
        // hotpatch_server_regex: "",
        log_server_regex: r#"^(https|http)://.*\.cos\..*\.myqcloud\.com/(.*)$"#,
        #[cfg(feature = "enable-sdk")]
        sdk_server_regex: r#"^(https|http)://.*\.cos\..*\.myqcloud\.com/(.*)$"#,
        watermark_server_regex: "^(https|http)://(?:(?:csas.aliyuncs.com)|(?:sase-public-server-files.oss-cn-hangzhou.aliyuncs.com)|(?:beta-package-server-sh.aki-game.com)|(?:beta-package-server-sg.aki-game.net))/(.*)$",
        replacement_defaults: &ReplacementDefaults {
            config_server_default: "127.0.0.1:10001",
            // hotpatch_server_default: "127.0.0.1:10001",
            log_server_default: "127.0.0.1:10010",
            #[cfg(feature = "enable-sdk")]
            sdk_server_default: "127.0.0.1:10001",
            watermark_server_default: "nigga.kys:1337",
        },
    },
    #[cfg(all(not(feature = "enable-sdk"), not(feature = "only-sig-bypass"), feature = "regular"))]
    disable_sdk: DisableSdkConfiguration {
        sdk_dll: s!("KRSDKEx.dll"),
        eula_accept: 0x50E20,
        sdk_go_away: 0x95AD0,
    },
    #[cfg(all(feature = "enable-sdk", not(feature = "only-sig-bypass"), feature = "regular"))]
    kr_curl: KrCurlConfiguration {
        curl_dll: s!("libkrsdkcurl.dll"),
        curl_config: CurlConfig {
            handle_rcx_relative_offset: 0,
            url_handle_relative_offset: 0x1220,
            http_headers_handle_relative_offset: Some(0x340),
            curl_easy_setopt: 0x36E50,
            curl_easy_perform: 0xE3D0,
        },
    }
};

#[cfg(feature = "os_beta_2_8_0")]
pub(crate) const CONFIG: InjectConfiguration = InjectConfiguration {
    f_pak_file_check: 0x40BCB70,
    f_pak_file_check_preamble: 0xCCCCCC0540CCE7E9,
    resize_grow: 0x09226B0,
    f_print_f: 0x26823A0,
    add_pak_folders_entry: 0x40B2350,
    add_pak_folders_ret: 0x40B4C40,
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    ue_curl_config: CurlConfig {
        handle_rcx_relative_offset: 0x110,
        url_handle_relative_offset: 0x880,
        http_headers_handle_relative_offset: None,
        curl_easy_setopt: 0x678CCE0,
        curl_easy_perform: 0x3A33AF0,
    },
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    replacement_config: ReplacementConfig {
        config_server_regex: r#"^(https|http)://.*/([a-zA-Z0-9]{32}/index\.json)$"#,
        // hotpatch_server_regex: "",
        log_server_regex: r#"^(https|http)://.*\.cos\..*\.myqcloud\.com/(.*)$"#,
        #[cfg(feature = "enable-sdk")]
        sdk_server_regex: r#"^(https|http)://.*\.cos\..*\.myqcloud\.com/(.*)$"#,
        watermark_server_regex: "^(https|http)://(?:(?:csas.aliyuncs.com)|(?:sase-public-server-files.oss-cn-hangzhou.aliyuncs.com)|(?:beta-package-server-sh.aki-game.com)|(?:beta-package-server-sg.aki-game.net))/(.*)$",
        replacement_defaults: &ReplacementDefaults {
            config_server_default: "127.0.0.1:10001",
            // hotpatch_server_default: "127.0.0.1:10001",
            log_server_default: "127.0.0.1:10010",
            #[cfg(feature = "enable-sdk")]
            sdk_server_default: "127.0.0.1:10001",
            watermark_server_default: "nigga.kys:1337",
        },
    },
    #[cfg(all(not(feature = "enable-sdk"), not(feature = "only-sig-bypass"), feature = "regular"))]
    disable_sdk: DisableSdkConfiguration {
        sdk_dll: s!("KRSDK.dll"),
        eula_accept: 0xA4720,
        sdk_go_away: 0xBBA70,
    },
    #[cfg(all(feature = "enable-sdk", not(feature = "only-sig-bypass"), feature = "regular"))]
    kr_curl: KrCurlConfiguration {
        curl_dll: s!("libkrsdkcurl.dll"),
        curl_config: CurlConfig {
            handle_rcx_relative_offset: 0,
            url_handle_relative_offset: 0x1220,
            http_headers_handle_relative_offset: Some(0x340),
            curl_easy_setopt: 0x36E50,
            curl_easy_perform: 0xE3D0,
        },
    }
};

#[cfg(feature = "os_live_2_7_0")]
pub(crate) const CONFIG: InjectConfiguration = InjectConfiguration {
    f_pak_file_check: 0x3FF9700,
    f_pak_file_check_preamble: 0xCCCCCC05380F87E9,
    resize_grow: 0x091A130,
    f_print_f: 0x25F7C30,
    add_pak_folders_entry: 0x3FEEEC0,
    add_pak_folders_ret: 0x3FF17B0,
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    ue_curl_config: CurlConfig {
        handle_rcx_relative_offset: 0x110,
        url_handle_relative_offset: 0x880,
        http_headers_handle_relative_offset: None,
        curl_easy_setopt: 0x66A1EE0,
        curl_easy_perform: 0x3972090,
    },
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    replacement_config: ReplacementConfig {
        config_server_regex: r#"^(https|http)://.*/([a-zA-Z0-9]{32}/index\.json)$"#,
        // hotpatch_server_regex: "",
        log_server_regex: r#"^(https|http)://.*\.cos\..*\.myqcloud\.com/(.*)$"#,
        #[cfg(feature = "enable-sdk")]
        sdk_server_regex: r#"^(https|http)://.*\.cos\..*\.myqcloud\.com/(.*)$"#,
        watermark_server_regex: "^(https|http)://(?:(?:csas.aliyuncs.com)|(?:sase-public-server-files.oss-cn-hangzhou.aliyuncs.com)|(?:beta-package-server-sh.aki-game.com)|(?:beta-package-server-sg.aki-game.net))/(.*)$",
        replacement_defaults: &ReplacementDefaults {
            config_server_default: "127.0.0.1:10001",
            // hotpatch_server_default: "127.0.0.1:10001",
            log_server_default: "127.0.0.1:10010",
            #[cfg(feature = "enable-sdk")]
            sdk_server_default: "127.0.0.1:10001",
            watermark_server_default: "nigga.kys:1337",
        },
    },
    #[cfg(all(not(feature = "enable-sdk"), not(feature = "only-sig-bypass"), feature = "regular"))]
    disable_sdk: DisableSdkConfiguration {
        sdk_dll: s!("KRSDK.dll"),
        eula_accept: 0xA4720,
        sdk_go_away: 0xBBA70,
    },
    #[cfg(all(feature = "enable-sdk", not(feature = "only-sig-bypass"), feature = "regular"))]
    kr_curl: KrCurlConfiguration {
        curl_dll: s!("libkrsdkcurl.dll"),
        curl_config: CurlConfig {
            handle_rcx_relative_offset: 0,
            url_handle_relative_offset: 0x1220,
            http_headers_handle_relative_offset: Some(0x340),
            curl_easy_setopt: 0x36E50,
            curl_easy_perform: 0xE3D0,
        },
    }
};

#[cfg(feature = "cn_live_2_7_0")]
pub(crate) const CONFIG: InjectConfiguration = InjectConfiguration {
    f_pak_file_check: 0x3FF9700,
    f_pak_file_check_preamble: 0xCCCCCC05380F87E9,
    resize_grow: 0x091A130,
    f_print_f: 0x25F7C30,
    add_pak_folders_entry: 0x3FEEEC0,
    add_pak_folders_ret: 0x3FF17B0,
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    ue_curl_config: CurlConfig {
        handle_rcx_relative_offset: 0x110,
        url_handle_relative_offset: 0x880,
        http_headers_handle_relative_offset: None,
        curl_easy_setopt: 0x66A1EE0,
        curl_easy_perform: 0x3972090,
    },
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    replacement_config: ReplacementConfig {
        config_server_regex: r#"^(https|http)://.*/([a-zA-Z0-9]{32}/index\.json)$"#,
        // hotpatch_server_regex: "",
        log_server_regex: r#"^(https|http)://.*\.cos\..*\.myqcloud\.com/(.*)$"#,
        #[cfg(feature = "enable-sdk")]
        sdk_server_regex: r#"^(https|http)://.*\.cos\..*\.myqcloud\.com/(.*)$"#,
        watermark_server_regex: "^(https|http)://(?:(?:csas.aliyuncs.com)|(?:sase-public-server-files.oss-cn-hangzhou.aliyuncs.com)|(?:beta-package-server-sh.aki-game.com)|(?:beta-package-server-sg.aki-game.net))/(.*)$",
        replacement_defaults: &ReplacementDefaults {
            config_server_default: "127.0.0.1:10001",
            // hotpatch_server_default: "127.0.0.1:10001",
            log_server_default: "127.0.0.1:10010",
            #[cfg(feature = "enable-sdk")]
            sdk_server_default: "127.0.0.1:10001",
            watermark_server_default: "nigga.kys:1337",
        },
    },
    #[cfg(all(not(feature = "enable-sdk"), not(feature = "only-sig-bypass"), feature = "regular"))]
    disable_sdk: DisableSdkConfiguration {
        sdk_dll: s!("KRSDK.dll"),
        eula_accept: 0xA4720,
        sdk_go_away: 0xBBA70,
    },
    #[cfg(all(feature = "enable-sdk", not(feature = "only-sig-bypass"), feature = "regular"))]
    kr_curl: KrCurlConfiguration {
        curl_dll: s!("libkrsdkcurl.dll"),
        curl_config: CurlConfig {
            handle_rcx_relative_offset: 0,
            url_handle_relative_offset: 0x1220,
            http_headers_handle_relative_offset: Some(0x340),
            curl_easy_setopt: 0x36E50,
            curl_easy_perform: 0xE3D0,
        },
    }
};
