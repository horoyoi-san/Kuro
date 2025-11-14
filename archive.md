# CN BETA 2.7.0
```rust
#[cfg(feature = "cn_beta_2_7_0")]
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
```

# OS BETA 2.7.0
```rust
#[cfg(feature = "os_beta_2_7_0")]
pub(crate) const CONFIG: InjectConfiguration = InjectConfiguration {
    f_pak_file_check: 0x3FEA380,
    f_pak_file_check_preamble: 0xCCCCCC053611C2E9,
    resize_grow: 0x0918350,
    f_print_f: 0x25E6740,
    add_pak_folders_entry: 0x3FDFC20,
    add_pak_folders_ret: 0x3FE24C0,
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    ue_curl_config: CurlConfig {
        handle_rcx_relative_offset: 0x110,
        url_handle_relative_offset: 0x880,
        http_headers_handle_relative_offset: None,
        curl_easy_setopt: 0x6690240,
        curl_easy_perform: 0x3961210,
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
```

# CN BETA 2.6.0
```rust
#[cfg(feature = "cn_beta_2_6_0")]
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
            log_server_default: "127.0.0.1:10001",
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
```

# OS BETA 2.6.0
```rust
#[cfg(feature = "os_beta_2_6_0")]
pub(crate) const CONFIG: InjectConfiguration = InjectConfiguration {
    f_pak_file_check: 0x45BFFC0,
    f_pak_file_check_preamble: 0xCCCCCC04F95A43E9,
    resize_grow: 0x0907F50,
    f_print_f: 0x2BD1DE0,
    add_pak_folders_entry: 0x45B5B40,
    add_pak_folders_ret: 0x45B83E0,
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    ue_curl_config: CurlConfig {
        handle_rcx_relative_offset: 0x110,
        url_handle_relative_offset: 0x880,
        http_headers_handle_relative_offset: None,
        curl_easy_setopt: 0x6984060,
        curl_easy_perform: 0x3F37ED0,
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
            log_server_default: "127.0.0.1:10001",
            #[cfg(feature = "enable-sdk")]
            sdk_server_default: "127.0.0.1:10001",
            watermark_server_default: "nigga.kys:1337",
        },
    },
    #[cfg(all(not(feature = "enable-sdk"), not(feature = "only-sig-bypass"), feature = "regular"))]
    disable_sdk: DisableSdkConfiguration {
        sdk_dll: s!("KRSDK.dll"),
        eula_accept: 0xA20E0,
        sdk_go_away: 0xAFE60,
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
```

# CN BETA 2.6.0 Dev (Thanks to Maykt / SeleeLeaks & Subai66 / StarDomain)
```rust
#[cfg(feature = "cn_beta_2_6_0")]
pub(crate) const CONFIG: InjectConfiguration = InjectConfiguration {
    f_pak_file_check: 0x4618D30,
    f_pak_file_check_preamble: 0xCCCCCC05030B9CE9,
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
            log_server_default: "127.0.0.1:10001",
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
```

# CN BETA 2.4.0
```rust
#[cfg(feature = "cn_beta_2_4_0")]
pub(crate) const CONFIG: InjectConfiguration = InjectConfiguration {
        f_pak_file_check: 0x42CF240,
        f_pak_file_check_preamble: 0x8D48574157565540,
        resize_grow: 0x08E1690,
        f_print_f: 0x2912CF0,
        add_pak_folders_entry: 0x42D6720,
        add_pak_folders_ret: 0x42D8FC0,
        #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
        ue_curl_config: CurlConfig {
            handle_rcx_relative_offset: 0x110,
            url_handle_relative_offset: 0x880,
            http_headers_handle_relative_offset: None,
            curl_easy_setopt: 0x66B3720,
            curl_easy_perform: 0x3C65C60,
        },
        #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
        replacement_config: ReplacementConfig {
            config_server_regex: r#"^(https|http)://.*/([a-zA-Z0-9]{32}/index\.json)$"#,
            // hotpatch_server_regex: "",
            log_server_regex: r#"^(https|http)://.*\.cos\..*\.myqcloud\.com/(.*)$"#,
            #[cfg(feature = "enable-sdk")]
            sdk_server_regex: r#"^(https|http)://.*\.cos\..*\.myqcloud\.com/(.*)$"#,
            replacement_defaults: &ReplacementDefaults {
                config_server_default: "127.0.0.1:10001",
                // hotpatch_server_default: "127.0.0.1:10001",
                log_server_default: "127.0.0.1:10001",
                #[cfg(feature = "enable-sdk")]
                sdk_server_default: "127.0.0.1:10001",
            },
        },
        #[cfg(all(not(feature = "enable-sdk"), not(feature = "only-sig-bypass"), feature = "regular"))]
        disable_sdk: DisableSdkConfiguration {
            sdk_dll: s!("KRSDKEx.dll"),
            eula_accept: 0x4F490,
            sdk_go_away: 0x93FD0,
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
```

# CN BETA 2.3.0
```rust
#[cfg(feature = "cn_beta_2_3_0")]
pub(crate) const CONFIG: InjectConfiguration = InjectConfiguration {
    f_pak_file_check: 0x4274440,
    f_pak_file_check_preamble: 0x8D48574157565540,
    resize_grow: 0x8E2D30,
    f_print_f: 0x28E5F70,
    add_pak_folders_entry: 0x427B910,
    add_pak_folders_ret: 0x427E1B0,
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    ue_curl_config: CurlConfig {
        handle_rcx_relative_offset: 0x110,
        url_handle_relative_offset: 0x880,
        http_headers_handle_relative_offset: None,
        curl_easy_setopt: 0x66325A0,
        curl_easy_perform: 0x3C0BFA0,
    },
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    replacement_config: ReplacementConfig {
        config_server_regex: r#"^(https|http)://.*/([a-zA-Z0-9]{32}/index\.json)$"#,
        // hotpatch_server_regex: "",
        log_server_regex: r#"^(https|http)://.*\.cos\..*\.myqcloud\.com/(.*)$"#,
        sdk_server_regex: r#"^(https|http)://.*\.cos\..*\.myqcloud\.com/(.*)$"#,
        replacement_defaults: &ReplacementDefaults {
            config_server_default: "127.0.0.1:10001",
            // hotpatch_server_default: "127.0.0.1:10001",
            log_server_default: "127.0.0.1:10001",
            sdk_server_default: "127.0.0.1:10001",
        },
    },
    #[cfg(all(not(feature = "enable-sdk"), not(feature = "only-sig-bypass"), feature = "regular"))]
    disable_sdk: DisableSdkConfiguration {
        sdk_dll: s!("KRSDKEx.dll"),
        eula_accept: 0x4F410,
        sdk_go_away: 0x93620,
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
```

# OS LIVE 2.2.0
```rust
#[cfg(feature = "os_live_2_2_0")]
pub(crate) const CONFIG: InjectConfiguration = InjectConfiguration {
    f_pak_file_check: 0x418A2F0,
    f_pak_file_check_preamble: 0x8D48574157565540,
    resize_grow: 0x08D6D70,
    f_print_f: 0x280B240,
    add_pak_folders_entry: 0x41917D0,
    add_pak_folders_ret: 0x4194070,
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    ue_curl_config: CurlConfig {
        handle_rcx_relative_offset: Some(0x110),
        url_handle_relative_offset: 0x880,
        http_headers_handle_relative_offset: None,
        curl_easy_setopt: 0x64FF840,
        curl_easy_perform: 0x3B21490,
    },
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    replacement_config: ReplacementConfig {
        config_server_regex: r#"^(https|http)://.*/([a-zA-Z0-9]{32}/index\.json)$"#,
        // hotpatch_server_regex: "",
        log_server_regex: r#"^(https|http)://.*\.cos\..*\.myqcloud\.com/(.*)$"#,
        // sdk_server_regex: "",
        //         replacement_defaults: &ReplacementDefaults {
        //             config_server_default: "127.0.0.1:10001",
        //             // hotpatch_server_default: "127.0.0.1:10001",
        //             log_server_default: "127.0.0.1:10001",
        //             sdk_server_default: "127.0.0.1:10001",
        //         },
    },
    #[cfg(all(not(feature = "enable-sdk"), not(feature = "only-sig-bypass"), feature = "regular"))]
    disable_sdk: DisableSdkConfiguration {
        sdk_dll: s!("KRSDK.dll"),
        eula_accept: 0x96800,
        sdk_go_away: 0xA2680,
    },
    // TODO: Ported for compliance in the future, not supported on 2.2.0 OS
    #[cfg(all(feature = "enable-sdk", not(feature = "only-sig-bypass"), feature = "regular"))]
    kr_curl: KrCurlConfiguration {
        curl_dll: s!("libkrsdkcurl.dll"),
        curl_config: CurlConfig {
            handle_rcx_relative_offset: None,
            url_handle_relative_offset: 0,
            http_headers_handle_relative_offset: None,
            curl_easy_setopt: 0,
            curl_easy_perform: 0,
        },
    }
};
```

# CN BETA 2.2.1

```rust
#[cfg(feature = "cn_beta_2_2_1")]
pub(crate) const CONFIG: InjectConfiguration = InjectConfiguration {
    f_pak_file_check: 0x41CE7F0,
    f_pak_file_check_preamble: 0x8D48574157565540,
    resize_grow: 0x08D9510,
    f_print_f: 0x2852CE0,
    add_pak_folders_entry: 0x41D5CD0,
    add_pak_folders_ret: 0x41D8570,
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    ue_curl_config: CurlConfig {
        handle_rcx_relative_offset: 0x110,
        url_handle_relative_offset: 0x880,
        curl_easy_setopt: 0x657A660,
        curl_easy_perform: 0x3B6A440,
    },
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    replacement_config: ReplacementConfig {
        config_server_regex: r#"^(https|http)://.*/([a-zA-Z0-9]{32}/index\.json)$"#,
        // hotpatch_server_regex: "",
        log_server_regex: r#"^(https|http)://.*\.cos\..*\.myqcloud\.com/(.*)$"#,
        // sdk_server_regex: "",
    },
    #[cfg(all(not(feature = "enable-sdk"), not(feature = "only-sig-bypass"), feature = "regular"))]
    disable_sdk: DisableSdkConfiguration {
        sdk_dll: s!("KRSDKEx.dll"),
        eula_accept: 0x4ED80,
        sdk_go_away: 0x91FE0,
    },
};
```

# OS LIVE 2.1.0

```rust
#[cfg(feature = "os_live_2_1_0")]
pub(crate) const CONFIG: InjectConfiguration = InjectConfiguration {
        f_pak_file_check: 0x40A6840,
        f_pak_file_check_preamble: 0x8D48574157565540,
        resize_grow: 0x08D1430,
        f_print_f: 0x2736C10,
        add_pak_folders_entry: 0x40ADD20,
        add_pak_folders_ret: 0x40B05C0,
        #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
        ue_curl_config: CurlConfig {
            handle_rcx_relative_offset: 0x110,
            url_handle_relative_offset: 0x880,
            curl_easy_setopt: 0x6415920,
            curl_easy_perform: 0x3A430D0,
        },
        #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
        replacement_config: ReplacementConfig {
            config_server_regex: r#"^(https|http)://.*/([a-zA-Z0-9]{32}/index\.json)$"#,
            // hotpatch_server_regex: "",
            log_server_regex: r#"^(https|http)://.*\.cos\..*\.myqcloud\.com/(.*)$"#,
            // sdk_server_regex: "",
        },
        #[cfg(all(not(feature = "enable-sdk"), not(feature = "only-sig-bypass"), feature = "regular"))]
        disable_sdk: DisableSdkConfiguration {
            sdk_dll: s!("KRSDK.dll"),
            eula_accept: 0x96800,
            sdk_go_away: 0xA2680,
        },
    };
```

# CN BETA 2.2.0

```rust
#[cfg(feature = "cn_beta_2_2_0")]
pub(crate) const CONFIG: InjectConfiguration = InjectConfiguration {
    f_pak_file_check: 0x41CA5F0,
    f_pak_file_check_preamble: 0x8D48574157565540,
    resize_grow: 0x08D93D0,
    f_print_f: 0x284EB20,
    add_pak_folders_entry: 0x41D1AD0,
    add_pak_folders_ret: 0x41D4370,
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    ue_curl_config: CurlConfig {
        handle_rcx_relative_offset: 0x110,
        url_handle_relative_offset: 0x880,
        curl_easy_setopt: 0x6576460,
        curl_easy_perform: 0x3B66280,
    },
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    replacement_config: ReplacementConfig {
        config_server_regex: r#"^(https|http)://.*/([a-zA-Z0-9]{32}/index\.json)$"#,
        // hotpatch_server_regex: "",
        log_server_regex: r#"^(https|http)://.*\.cos\..*\.myqcloud\.com/(.*)$"#,
        // sdk_server_regex: "",
    },
    #[cfg(all(not(feature = "enable-sdk"), not(feature = "only-sig-bypass"), feature = "regular"))]
    disable_sdk: DisableSdkConfiguration {
        sdk_dll: s!("KRSDKEx.dll"),
        eula_accept: 0x4ED80,
        sdk_go_away: 0x91FE0,
    },
};
```

# CN LIVE 2.0.0

```rust
#[cfg(feature = "cn_live_2_0_2")]
pub(crate) const CONFIG: InjectConfiguration = InjectConfiguration {
    f_pak_file_check: 0x4052560,
    f_pak_file_check_preamble: 0x8D48574157565540,
    resize_grow: 0x08C8E00,
    f_print_f: 0x27440D0,
    add_pak_folders_entry: 0x4059A40,
    add_pak_folders_ret: 0x405C270,
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    ue_curl_config: CurlConfig {
        handle_rcx_relative_offset: 0x110,
        url_handle_relative_offset: 0x880,
        curl_easy_setopt: 0x63EB660,
        curl_easy_perform: 0x39F47C0,
    },
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    replacement_config: ReplacementConfig {
        config_server_regex: r#"^(https|http)://.*/([a-zA-Z0-9]{32}/index\.json)$"#,
        // hotpatch_server_regex: "",
        log_server_regex: r#"^(https|http)://.*\.cos\..*\.myqcloud\.com/(.*)$"#,
        // sdk_server_regex: "",
    },
    #[cfg(all(not(feature = "enable-sdk"), not(feature = "only-sig-bypass"), feature = "regular"))]
    disable_sdk: DisableSdkConfiguration {
        sdk_dll: s!("KRSDKEx.dll"),
        eula_accept: 0x4E710,
        sdk_go_away: 0x91960,
    },
};
```

# CN LIVE BILIBILI 2.0.0

```rust
#[cfg(feature = "cn_live_bilibili_2_0_2")]
pub(crate) const CONFIG: InjectConfiguration = InjectConfiguration {
    f_pak_file_check: 0x4052560,
    f_pak_file_check_preamble: 0x8D48574157565540,
    resize_grow: 0x08C8E00,
    f_print_f: 0x27440D0,
    add_pak_folders_entry: 0x4059A40,
    add_pak_folders_ret: 0x405C270,
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    ue_curl_config: CurlConfig {
        handle_rcx_relative_offset: 0x110,
        url_handle_relative_offset: 0x880,
        curl_easy_setopt: 0x63EB660,
        curl_easy_perform: 0x39F47C0,
    },
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    replacement_config: ReplacementConfig {
        config_server_regex: r#"^(https|http)://.*/([a-zA-Z0-9]{32}/index\.json)$"#,
        // hotpatch_server_regex: "",
        log_server_regex: r#"^(https|http)://.*\.cos\..*\.myqcloud\.com/(.*)$"#,
        // sdk_server_regex: "",
    },
    #[cfg(all(not(feature = "enable-sdk"), not(feature = "only-sig-bypass"), feature = "regular"))]
    disable_sdk: DisableSdkConfiguration {
        sdk_dll: s!("KRSDKEx.dll"),
        eula_accept: 0x53310,
        sdk_go_away: 0x925F0,
    },
};
```

# OS LIVE 2.0.0

```rust
#[cfg(feature = "os_live_2_0_2")]
pub(crate) const CONFIG: InjectConfiguration = InjectConfiguration {
    f_pak_file_check: 0x3FF8E50,
    f_pak_file_check_preamble: 0x8D48574157565540,
    resize_grow: 0x08C61C0,
    f_print_f: 0x26E96F0,
    add_pak_folders_entry: 0x4000330,
    add_pak_folders_ret: 0x4002B60,
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    ue_curl_config: CurlConfig {
        handle_rcx_relative_offset: 0x110,
        url_handle_relative_offset: 0x880,
        curl_easy_setopt: 0x63598C0,
        curl_easy_perform: 0x3997FA0,
    },
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    replacement_config: ReplacementConfig {
        config_server_regex: r#"^(https|http)://.*/([a-zA-Z0-9]{32}/index\.json)$"#,
        // hotpatch_server_regex: "",
        log_server_regex: r#"^(https|http)://.*\.cos\..*\.myqcloud\.com/(.*)$"#,
        // sdk_server_regex: "",
    },
    #[cfg(all(not(feature = "enable-sdk"), not(feature = "only-sig-bypass"), feature = "regular"))]
    disable_sdk: DisableSdkConfiguration {
        sdk_dll: s!("KRSDK.dll"),
        eula_accept: 0x96800,
        sdk_go_away: 0xA2680,
    },
};
```

# CN BETA 2.0.0

```rust
#[cfg(feature = "cn_beta_2_0_0")]
pub(crate) const CONFIG: InjectConfiguration = InjectConfiguration {
    f_pak_file_check: 0x403AD00,
    f_pak_file_check_preamble: 0x8D48574157565540,
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    ue_curl_config: CurlConfig {
        handle_rcx_relative_offset: 0x110,
        url_handle_relative_offset: 0x880,
        curl_easy_setopt: 0x63D30C0,
        curl_easy_perform: 0x39DD6E0,
    },
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    replacement_config: ReplacementConfig {
        config_server_regex: r#"^(https|http)://.*/([a-zA-Z0-9]{32}/index\.json)$"#,
        // hotpatch_server_regex: "",
        log_server_regex: r#"^(https|http)://.*\.cos\..*\.myqcloud\.com/(.*)$"#,
        // sdk_server_regex: "",
    },
    #[cfg(all(not(feature = "enable-sdk"), not(feature = "only-sig-bypass"), feature = "regular"))]
    disable_sdk: DisableSdkConfiguration {
        sdk_dll: s!("KRSDKEx.dll"),
        eula_accept: 0x4E580,
        sdk_go_away: 0x90B90,
    },
};
```

# OS BETA 2.0.0

```rust
#[cfg(feature = "os_beta_2_0_0")]
pub(crate) const CONFIG: InjectConfiguration = InjectConfiguration { // TODO
    f_pak_file_check: 0x3E37D90,
    f_pak_file_check_preamble: 0x8148574157565340,
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    ue_curl_config: CurlConfig {
        handle_rcx_relative_offset: 0x110,
        url_handle_relative_offset: 0x880,
        curl_easy_setopt: 0x6187020,
        curl_easy_perform: 0x37DDDD0,
    },
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    replacement_config: ReplacementConfig {
        config_server_regex: r#"^(https|http)://.*/([a-zA-Z0-9]{32}/index\.json)$"#,
        // hotpatch_server_regex: "",
        log_server_regex: r#"^(https|http)://.*\.cos\..*\.myqcloud\.com/(.*)$"#,
        // sdk_server_regex: "",
    },
    #[cfg(all(not(feature = "enable-sdk"), not(feature = "only-sig-bypass"), feature = "regular"))]
    disable_sdk: DisableSdkConfiguration {
        sdk_dll: s!("KRSDKEx.dll"),
        eula_accept: 0x4A6D0,
        sdk_go_away: 0x8BB40,
    },
};
```

# CN LIVE 1.4

```rust
#[cfg(feature = "cn_live_1_4_0")]
pub(crate) const CONFIG: InjectConfiguration = InjectConfiguration { // TODO
    f_pak_file_check: 0x3E37D90,
    f_pak_file_check_preamble: 0x8148574157565340,
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    ue_curl_config: CurlConfig {
        handle_rcx_relative_offset: 0x110,
        url_handle_relative_offset: 0x880,
        curl_easy_setopt: 0x6187020,
        curl_easy_perform: 0x37DDDD0,
    },
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    replacement_config: ReplacementConfig {
        config_server_regex: r#"^(https|http)://.*/([a-zA-Z0-9]{32}/index\.json)$"#,
        // hotpatch_server_regex: "",
        log_server_regex: r#"^(https|http)://.*\.cos\..*\.myqcloud\.com/(.*)$"#,
        // sdk_server_regex: "",
    },
    #[cfg(all(not(feature = "enable-sdk"), not(feature = "only-sig-bypass"), feature = "regular"))]
    disable_sdk: DisableSdkConfiguration {
        sdk_dll: s!("KRSDKEx.dll"),
        eula_accept: 0x4A6D0,
        sdk_go_away: 0x8BB40,
    },
};
```

# OS LIVE 1.4

```rust
#[cfg(feature = "os_live_1_4_0")]
pub(crate) const CONFIG: InjectConfiguration = InjectConfiguration { // TODO
    f_pak_file_check: 0x3DE6650, // 0x3DE6650 // 0x8879a13
    f_pak_file_check_preamble: 0x5741544156535540, // 0x5741544156535540 // 0x8D49575355e38949
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    ue_curl_config: CurlConfig {
        handle_rcx_relative_offset: 0x110,
        url_handle_relative_offset: 0x880,
        curl_easy_setopt: 0x60FD460,
        curl_easy_perform: 0x37894E0,
    },
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    replacement_config: ReplacementConfig {
        config_server_regex: r#"^(https|http)://.*/([a-zA-Z0-9]{32}/index\.json)$"#,
        // hotpatch_server_regex: "",
        log_server_regex: r#"^(https|http)://.*\.cos\..*\.myqcloud\.com/(.*)$"#,
        // sdk_server_regex: "",
    },
    #[cfg(all(not(feature = "enable-sdk"), not(feature = "only-sig-bypass"), feature = "regular"))]
    disable_sdk: DisableSdkConfiguration {
        sdk_dll: s!("KRSDKEx.dll"),
        eula_accept: 0x959D0,
        sdk_go_away: 0xA1810,
    },
};
```

# CN BETA 1.4

```rust
#[cfg(feature = "cn_beta_1_4_0")]
pub(crate) const CONFIG: InjectConfiguration = InjectConfiguration {
    f_pak_file_check: 0x3E37D90,
    f_pak_file_check_preamble: 0x8148574157565340,
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    ue_curl_config: CurlConfig {
        handle_rcx_relative_offset: 0x110,
        url_handle_relative_offset: 0x880,
        curl_easy_setopt: 0x6187020,
        curl_easy_perform: 0x37DDDD0,
    },
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    replacement_config: ReplacementConfig {
        config_server_regex: r#"^(https|http)://.*/([a-zA-Z0-9]{32}/index\.json)$"#,
        // hotpatch_server_regex: "",
        log_server_regex: r#"^(https|http)://.*\.cos\..*\.myqcloud\.com/(.*)$"#,
        // sdk_server_regex: "",
    },
    #[cfg(all(not(feature = "enable-sdk"), not(feature = "only-sig-bypass"), feature = "regular"))]
    disable_sdk: DisableSdkConfiguration {
        sdk_dll: s!("KRSDKEx.dll"),
        eula_accept: 0x4A6D0,
        sdk_go_away: 0x8BB40,
    },
};
```

# OS BETA 1.4

```rust
#[cfg(feature = "os_beta_1_4_0")]
pub(crate) const CONFIG: InjectConfiguration = InjectConfiguration {
    f_pak_file_check: 0x3E37D90,
    f_pak_file_check_preamble: 0x8148574157565340,
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    ue_curl_config: CurlConfig {
        handle_rcx_relative_offset: 0x110,
        url_handle_relative_offset: 0x880,
        curl_easy_setopt: 0x6187020,
        curl_easy_perform: 0x37DDDD0,
    },
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    replacement_config: ReplacementConfig {
        config_server_regex: r#"^(https|http)://.*/([a-zA-Z0-9]{32}/index\.json)$"#,
        // hotpatch_server_regex: "",
        log_server_regex: r#"^(https|http)://.*\.cos\..*\.myqcloud\.com/(.*)$"#,
        // sdk_server_regex: "",
    },
    #[cfg(all(not(feature = "enable-sdk"), not(feature = "only-sig-bypass"), feature = "regular"))]
    disable_sdk: DisableSdkConfiguration {
        sdk_dll: s!("KRSDKEx.dll"),
        eula_accept: 0x4A6D0,
        sdk_go_away: 0x8BB40,
    },
};
```

# CN LIVE 1.3

```rust
#[cfg(feature = "cn_live_1_3_0")]
pub(crate) const CONFIG: InjectConfiguration = InjectConfiguration {
    f_pak_file_check: 0x3D35DF0,
    f_pak_file_check_preamble: 0x8148574157565340,
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    kuro_http_get: 0xFC9900,
    #[cfg(all(not(feature = "enable-sdk"), not(feature = "only-sig-bypass"), feature = "regular"))]
    disable_sdk: DisableSdkConfiguration {
        sdk_dll: s!("KRSDKEx.dll"),
        eula_accept: 0x4A690,
        sdk_go_away: 0x8B9F0,
    },
};
```

# OS LIVE 1.3

```rust
#[cfg(feature = "os_live_1_3_0")]
pub(crate) const CONFIG: InjectConfiguration = InjectConfiguration {
    f_pak_file_check: 0x3CDC430,
    f_pak_file_check_preamble: 0x8148574157565340,
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    kuro_http_get: 0xFC6C20,
    #[cfg(all(not(feature = "enable-sdk"), not(feature = "only-sig-bypass"), feature = "regular"))]
    disable_sdk: DisableSdkConfiguration {
        sdk_dll: s!("KRSDK.dll"),
        eula_accept: 0x95440,
        sdk_go_away: 0xA1280,
    },
};
```

# CN BETA 1.3

```rust
#[cfg(feature = "cn_beta_1_3_0")]
pub(crate) const CONFIG: InjectConfiguration = InjectConfiguration {
    f_pak_file_check: 0x3D2F460,
    f_pak_file_check_preamble: 0x8148574157565340,
    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    kuro_http_get: 0xFC8CF0,
    #[cfg(all(not(feature = "enable-sdk"), not(feature = "only-sig-bypass"), feature = "regular"))]
    disable_sdk: DisableSdkConfiguration {
        sdk_dll: s!("KRSDKEx.dll"),
        eula_accept: 0x4A690,
        sdk_go_away: 0x8BB80,
    },
};
```
