use ilhook::x64::Registers;
use interceptor_rs::Interceptor;
use std::sync::OnceLock;
use std::thread;
use std::time::Duration;
use unreal_niggery_rs::f_string::{FString, Printf};
use unreal_niggery_rs::t_array::TArray;
use unreal_niggery_rs::Add;
use windows::core::PCSTR;
#[cfg(any(feature = "only-sig-bypass", feature = "regular"))]
use windows::core::PCWSTR;
use windows::Win32::Foundation::HINSTANCE;
use windows::Win32::System::Console;
use windows::Win32::System::LibraryLoader::GetModuleHandleA;
use windows::Win32::System::SystemServices::DLL_PROCESS_ATTACH;

use config::CONFIG;

mod config;
#[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
mod curl_hook;
#[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
mod sdk;

static CUSTOM_PAK_FOLDER: OnceLock<String> = OnceLock::new();

fn thread_func() {
    unsafe { Console::AllocConsole() }.unwrap();
    println!("Wuthering Waves สำหรับ Kuro ");
    println!("BETA");

    println!("Waiting for ACE init");
    let module = unsafe { GetModuleHandleA(PCSTR::null()) }.unwrap();
    let pak_file_offset = ((module.0 as usize) + CONFIG.f_pak_file_check) as *const u64;
    loop {
        if unsafe { std::ptr::read(pak_file_offset) } == CONFIG.f_pak_file_check_preamble {
            println!("ACE Initialization finished");
            break;
        }
        thread::sleep(Duration::from_millis(1))
    }

    let mut interceptor = Interceptor::new();
    #[cfg(any(feature = "only-sig-bypass", feature = "regular"))]
    interceptor
        .replace(
            (module.0 as usize) + CONFIG.f_pak_file_check,
            fpakfile_check_replacement,
            None,
        )
        .unwrap();

    TArray::set_t_array_resize_grow_ptr(module.0 as usize + CONFIG.resize_grow);
    FString::set_f_string_printf_ptr(module.0 as usize + CONFIG.f_print_f);

    if let Ok(value) = std::env::var("CFG_WUWA_CUSTOM_PAK_DIR") {
        println!("Found custom location for pak files: {value}");
        let _ = CUSTOM_PAK_FOLDER.set(value).unwrap();
        interceptor
            .attach(
                (module.0 as usize) + CONFIG.add_pak_folders_entry,
                add_pak_folders,
                None,
            )
            .unwrap();
        interceptor
            .attach(
                (module.0 as usize) + CONFIG.add_pak_folders_ret,
                debug_get_pak_folders,
                None,
            )
            .unwrap();
    }

    #[cfg(feature = "advanced")]
    wicked_waifus_win_payload_advanced::enable_advanced_features(
        module.0 as usize,
        &mut interceptor,
        &wicked_waifus_win_payload_advanced::AdvancedConfig {
            enable_debug_view: false,
            enable_dev_tools: false,
            enable_dump_paks: false,
            enable_dump_buffer_contents: false,
            enable_hook_find_file_in_pak: false,
            enable_dump_magic: false,
        },
    );

    #[cfg(all(not(feature = "only-sig-bypass"), feature = "regular"))]
    curl_hook::configure_ue_curl(
        &mut interceptor,
        None,
        &CONFIG.ue_curl_config,
        &CONFIG.replacement_config,
    );
    #[cfg(all(
        not(feature = "enable-sdk"),
        not(feature = "only-sig-bypass"),
        feature = "regular"
    ))]
    sdk::configure_sdk(&mut interceptor);
    #[cfg(all(
        feature = "enable-sdk",
        not(feature = "only-sig-bypass"),
        feature = "regular"
    ))]
    curl_hook::configure_kr_curl(
        &mut interceptor,
        Some(CONFIG.kr_curl.curl_dll),
        &CONFIG.kr_curl.curl_config,
        &CONFIG.replacement_config,
    );

    println!("Successfully initialized!");

    thread::sleep(Duration::from_secs(u64::MAX));
}

#[cfg(any(feature = "only-sig-bypass", feature = "regular"))]
unsafe extern "win64" fn fpakfile_check_replacement(
    reg: *mut Registers,
    _: usize,
    _: usize,
) -> usize {
    let pak_name = unsafe {
        let v4_ptr = *(((*reg).rcx + 16) as *const usize);
        let parent_ptr = *(v4_ptr as *const usize);
        PCWSTR::from_raw(*((parent_ptr + 8) as *const usize) as *const u16)
            .to_string()
            .unwrap()
    };
    println!("Trying to verify pak: {pak_name}, returning true");

    1
}

unsafe extern "win64" fn add_pak_folders(reg: *mut Registers, _: usize) {
    let local_ptr = unsafe { ((*reg).rbp - 0x20) as usize }; // Uninitialized local FString pointer
    let pak_folder = CUSTOM_PAK_FOLDER.get().unwrap();
    let _ = FString::printf(local_ptr, pak_folder).unwrap();
    let mut f_string = FString(TArray::read(local_ptr));
    println!("Injecting custom pak folder: {}", f_string);
    unsafe {
        TArray::read((*reg).rdx as usize).add(&mut f_string.0);
    }
}

unsafe extern "win64" fn debug_get_pak_folders(reg: *mut Registers, _: usize) {
    println!("Loading Paks from: {}", unsafe {
        TArray::read((*reg).rbx as usize)
    });
}

#[unsafe(no_mangle)]
unsafe extern "system" fn DllMain(_: HINSTANCE, call_reason: u32, _: *mut ()) -> bool {
    if call_reason == DLL_PROCESS_ATTACH {
        thread::spawn(|| thread_func());
    }

    true
}
