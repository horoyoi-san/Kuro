use std::collections::HashMap;
use std::ffi::{c_void, CString};
use std::path::{Path, PathBuf};
use std::ptr::null_mut;
use std::str::FromStr;

use log::{debug, error, info, trace};
use path_clean::PathClean;
use serde::{Deserialize, Serialize};
use windows::core::{PSTR, s};
use windows::Win32::Foundation::{CloseHandle, GetLastError, HANDLE, NTSTATUS};
use windows::Win32::System::Diagnostics::Debug::WriteProcessMemory;
use windows::Win32::System::LibraryLoader::{GetModuleHandleA, GetProcAddress};
use windows::Win32::System::Memory::{MEM_COMMIT, MEM_RELEASE, MEM_RESERVE, PAGE_READWRITE,
                                     VirtualAllocEx, VirtualFreeEx};
use windows::Win32::System::Threading::{CREATE_SUSPENDED, CreateProcessA, CreateRemoteThread, GetExitCodeProcess, PROCESS_INFORMATION, ResumeThread, STARTUPINFOA, TerminateProcess, TerminateThread, WaitForSingleObject};

type FarProcUnwrapped = unsafe extern "system" fn() -> isize;
type LPThreadStartRoutine = unsafe extern "system" fn(param: *mut c_void) -> u32;

macro_rules! path_buf_to_str {
    ($expression:expr) => {
        match $expression.to_str() { 
            None => Err(Error::Generic("Error casting to string")), 
            Some(val) => Ok(val) 
        }
    };
}

macro_rules! split_str_to_string {
    ($expression:expr) => {
        match $expression.next() { 
            None => Err(Error::Generic("Split part missing")), 
            Some(val) => Ok(val.to_string()) 
        }
    };
}

macro_rules! pstr_from_cstring {
    ($name:ident, $cstring:expr, $log:literal) => {
        let $name = PSTR::from_raw($cstring.as_ptr() as *mut u8);
        debug!($log, unsafe{$name.to_string()}?);
    };
}

macro_rules! pstr_from_opt_cstring {
    ($name:ident, $cstring:expr, $log:literal) => {
        let $name = match $cstring { 
            None => PSTR(null_mut()), 
            Some(args) => PSTR::from_raw(args.as_ptr() as *mut u8)
        };
        debug!($log, unsafe{$name.to_string()}?);
    };
}

#[cfg(target_os = "windows")]
const ENV_VAR_SEPARATOR: &str = ";";
#[cfg(not(target_os = "windows"))]
const ENV_VAR_SEPARATOR: &str = ":";

#[derive(thiserror::Error, Debug)]
pub enum Error<'a> {
    #[error("Windows core error: {0}")]
    Windows(#[from] windows::core::Error),
    #[error("Nul error: {0}")]
    Nul(#[from] std::ffi::NulError),
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    #[error("Infallible error: {0}")]
    Infallible(#[from] std::convert::Infallible),
    #[error("FromUtf8 error: {0}")]
    FromUtf8(#[from] std::string::FromUtf8Error),
    #[error("Generic error: {0}")]
    Generic(&'a str),
    #[error("Dll Injection error: {0}")]
    DllInjection(String),
}

fn yes() -> bool {
    true
}

#[derive(Serialize, Deserialize, Debug, Default)]
pub struct Environment {
    pub vars: Option<Vec<String>>,
    #[serde(default = "yes")]
    pub use_system_env: bool,
    #[serde(default)]
    pub environment_append: bool,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct Launcher {
    pub executable_file: String,
    pub cmd_line_args: Option<String>,
    pub current_dir: Option<String>,
    #[serde(default)]
    pub dll_list: Vec<String>,
}

pub struct Context {
    pub proc_info: PROCESS_INFORMATION,
    pub environment: Vec<u8>,
}

fn absolute_path(cwd: &Path, path: impl AsRef<Path>) -> PathBuf {
    let path = path.as_ref();
    if path.is_absolute() {
        path.to_path_buf()
    } else {
        cwd.join(path)
    }.clean()
}

fn inject_standard(h_target: HANDLE, dll_path: &str) -> Result<(), Error> {
    let kernel32 = match unsafe {
        GetProcAddress(GetModuleHandleA(s!("kernel32.dll"))?, s!("LoadLibraryA"))
    } {
        None => Err(Error::Generic("GetProcAddress failed")),
        Some(ptr) => Ok(ptr)
    }?;
    let dll_path_cstr = CString::new(dll_path)?;
    let dll_path_addr = unsafe {
        VirtualAllocEx(
            h_target,
            None,
            dll_path_cstr.to_bytes_with_nul().len(),
            MEM_COMMIT | MEM_RESERVE,
            PAGE_READWRITE,
        )
    };
    if dll_path_addr.is_null() {
        error!(
            "Failed allocating memory in the target process. GetLastError(): {:?}",
            unsafe { GetLastError() }
        );
        return Err(Error::Generic("Failed to allocated dll path into the binary"));
    }
    unsafe {
        WriteProcessMemory(
            h_target,
            dll_path_addr,
            dll_path_cstr.as_ptr() as _,
            dll_path_cstr.to_bytes_with_nul().len(),
            None,
        )?;

        let h_thread = CreateRemoteThread(
            h_target,
            None,
            0,
            Some(std::mem::transmute::<FarProcUnwrapped, LPThreadStartRoutine>(kernel32)),
            Some(dll_path_addr),
            0,
            None,
        )?;
        WaitForSingleObject(h_thread, 0xFFFFFFFF);

        VirtualFreeEx(h_target, dll_path_addr, 0, MEM_RELEASE)?;
        CloseHandle(h_thread)?;
    }
    Ok(())
}

pub fn spawn_process<'a>(launcher: Launcher, env: Environment) -> Result<Context, Error<'a>> {
    let working_dir = match &launcher.current_dir {
        None => std::env::current_dir()?,
        Some(dir) => PathBuf::from_str(dir.as_str())?
    };
    trace!("working_dir: {:?}", working_dir);
    let executable_file = CString::new(
        path_buf_to_str!(absolute_path(&working_dir, launcher.executable_file))?
    )?;
    trace!("executable_file: {:?}", executable_file);
    let dlls = launcher.dll_list.iter()
        .map(|path| {
            let cleaned_path = absolute_path(&working_dir, path);
            if !cleaned_path.is_file() {
                panic!("{:?} not found", cleaned_path); // TODO: avoid this panic!
            }
            cleaned_path
        }).collect::<Vec<_>>();
    trace!("dlls: {:?}", dlls);

    let mut proc_info = PROCESS_INFORMATION::default();
    let startup_info = STARTUPINFOA::default();
    let cmd_line_args = launcher.cmd_line_args.map(
        |cmd_line_args| CString::new(cmd_line_args).unwrap() // TODO: avoid this panic!
    );
    trace!("cmd_line_args: {:?}", cmd_line_args);
    let mut environment: Vec<u8> = Vec::with_capacity(4096);
    let environment_ptr = match env.vars {
        None => None,
        Some(variables) => {
            let mut system_variables = match env.use_system_env {
                true => std::env::vars().collect::<HashMap<String, String>>(),
                false => HashMap::new()
            };
            for var in variables {
                let mut parts = var.split("=");
                let key = split_str_to_string!(parts)?;
                let mut value = split_str_to_string!(parts)?;
                let entry = system_variables.get(&key);
                if entry.is_some() & env.environment_append {
                    // Usually when injecting you want your modifications to take precedence so 
                    // prepend is the correct operation
                    value = format!("{value}{ENV_VAR_SEPARATOR}{}", entry.unwrap()); // Has to hold value
                }
                system_variables.insert(key, value); // If key exists, it will be replaced
            }
            let vars = system_variables.iter()
                .map(|(key, value)| {
                    CString::new(format!("{key}={value}")).unwrap() // TODO: avoid this panic!
                }).collect::<Vec<_>>();

            for var in vars {
                environment.extend_from_slice(var.as_bytes_with_nul());
            }
            environment.extend_from_slice(b"\0");
            Some(environment.as_ptr() as *const c_void)
        }
    };
    trace!("environment: {:?}", environment_ptr);

    let current_directory = CString::new(path_buf_to_str!(working_dir)?)?;

    pstr_from_cstring!(lp_application_name, executable_file, "lp_application_name: {}");
    pstr_from_opt_cstring!(lp_command_line, &cmd_line_args, "lp_command_line: {}");
    pstr_from_cstring!(lp_current_directory, current_directory, "lp_current_directory: {}");
    unsafe {
        CreateProcessA(
            lp_application_name,
            lp_command_line,
            None,
            None,
            false,
            CREATE_SUSPENDED,
            environment_ptr,
            lp_current_directory,
            &startup_info,
            &mut proc_info,
        )?;
    }

    for dll in dlls {
        let inject = path_buf_to_str!(dll)?;
        if let Err(err) = inject_standard(proc_info.hProcess, inject) {
            unsafe {
                TerminateThread(proc_info.hThread, 0)?;
                TerminateProcess(proc_info.hProcess, 0)?;
                CloseHandle(proc_info.hThread)?;
                CloseHandle(proc_info.hProcess)?;
            }
            return Err(Error::DllInjection(format!("Injection of dll: {inject} failed!\n{}", err)));
        }
        debug!("Injection of dll: {inject} succeeded!");
    }

    unsafe { ResumeThread(proc_info.hThread); }
    info!("Successful injection finished");
    Ok(Context { proc_info, environment })
}

pub fn is_process_running(proc_info: PROCESS_INFORMATION) -> bool {
    let mut exit_code = 0u32;
    let result = unsafe { GetExitCodeProcess(proc_info.hProcess, &mut exit_code) };
    match result {
        Ok(_) => {
            match NTSTATUS(exit_code as i32) {
                windows::Win32::Foundation::STILL_ACTIVE => true,
                _ => {
                    unsafe {
                        CloseHandle(proc_info.hThread).unwrap();
                        CloseHandle(proc_info.hProcess).unwrap();
                    }
                    false
                }
            }
        }
        Err(err) => {
            error!("Error while getting exit result: {err:?}");
            true
        }
    }
}