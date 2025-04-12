fn main() {
    #[cfg(windows)]
    {
        let mut res = winres::WindowsResource::new();
        res.set_icon("sigma.ico");
        res.compile().unwrap();
    }
}