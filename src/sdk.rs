#![cfg(all(not(feature = "enable-sdk"), not(feature = "only-sig-bypass"), feature = "regular"))]

use std::thread;
use std::time::Duration;

use ilhook::x64::Registers;
use windows::Win32::System::LibraryLoader::GetModuleHandleA;

use crate::config::CONFIG;

pub(crate) fn configure_sdk(interceptor: &mut interceptor_rs::Interceptor) {
    let krsdk_ex = loop {
        match unsafe { GetModuleHandleA(CONFIG.disable_sdk.sdk_dll) } {
            Ok(handle) => break handle,
            Err(_) => thread::sleep(Duration::from_millis(1)),
        }
    };

    interceptor
        .replace(
            (krsdk_ex.0 as usize) + CONFIG.disable_sdk.eula_accept,
            dummy,
            None,
        )
        .unwrap();

    interceptor
        .replace(
            (krsdk_ex.0 as usize) + CONFIG.disable_sdk.sdk_go_away,
            dummy,
            None,
        )
        .unwrap();
}

unsafe extern "win64" fn dummy(_: *mut Registers, _: usize, _: usize) -> usize {
    1
}
