# Rusty launcher

## CMD

To use this, please provide a route to configuration file, and if desired log level(info default)

```cmd
launcher.exe -h
A generic application launcher that allows dll injection into the process(Only for Windows)

Usage: launcher.exe [OPTIONS]

Options:
  -c, --config-file <CONFIG_FILE>  The location of the config file [default: ./config.toml]
  -l, --log-level <LOG_LEVEL>      The log level for the launcher [possible values: off, error, warn, info, debug, trace]
  -h, --help                       Print help (see more with '--help')
  -V, --version                    Print version

```

## Examples

In the samples directory you will find some samples that are listed here to for completion

### WW

```toml
[launcher]
executable_file = 'Client-Win64-Shipping.exe'
cmd_line_args = '-fileopenlog'
current_dir = '<REPLACE_THIS_FOR_YOUR_GAME_FOLDER>\Client\Binaries\Win64'
dll_list = ['<FULL_PATH_TO_SHOREKEEPER_DLL>']

[environment]
#environment = ['TESTVAR1=AAAAAA', 'TESTVAR2=AAAAAA']
#use_system_env = true
#environment_append = false
```