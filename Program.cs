using System.Diagnostics;
using System.Net;
using System.Text.Json;

namespace LingyangServer.Proxy
{
    internal static class Program
    {
        private const string Title = "LingyangServer-Proxy (Alter)";
        private const string ConfigPath = "config.json";
        private const string ConfigTemplatePath = "config.tmpl.json";

        private static ProxyService s_proxyService = null!;
        private static bool s_clearupd = false;
        
        private static void Main(string[] args)
        {
            Console.Title = Title;
            Console.WriteLine($"LingyangServer.Proxy");
            CheckProxy();
            InitConfig();

            var conf = JsonSerializer.Deserialize(File.ReadAllText(ConfigPath), ProxyConfigContext.Default.ProxyConfig) ?? throw new FileLoadException("Please correctly configure config.json.");
            s_proxyService = new ProxyService(conf.DestinationHost, conf.DestinationPort, conf);
            Console.WriteLine($"代理正在运行");
            AppDomain.CurrentDomain.ProcessExit += OnProcessExit;
            Console.CancelKeyPress += OnProcessExit;

            Thread.Sleep(-1);
        }



        private static void InitConfig()
        {
            if (!File.Exists(ConfigPath))
            {
                File.Copy(ConfigTemplatePath, ConfigPath);
            }
        }

        private static void OnProcessExit(object? sender, EventArgs? args)
        {
            if (s_clearupd) return;
            s_proxyService?.Shutdown();
            s_clearupd = true;
        }

        public static void CheckProxy()
        {
            try
            {
                string? ProxyInfo = GetProxyInfo();
                if (ProxyInfo != null)
                {
                    Console.WriteLine("嗯...看来你正在使用其他代理软件(例如 Clash、V2RayN、Fiddler 等)");
                    Console.WriteLine($"您的系统代理: {ProxyInfo}");
                    Console.WriteLine("您必须关闭所有其他代理软件以确保 Lingyang-Proxy 能够正常工作.");
                    Console.WriteLine("如果您关闭了其他代理软件或者您认为没有使用其他代理，请按任意键继续.");
                    Console.ReadKey();
                }
            }
            catch (NullReferenceException)
            {

            }
        }

        public static string? GetProxyInfo()
        {
            try
            {
                IWebProxy proxy = WebRequest.GetSystemWebProxy();
                Uri? proxyUri = proxy.GetProxy(new Uri("https://www.example.com"));
                if (proxyUri == null) return null;

                string proxyIP = proxyUri.Host;
                int proxyPort = proxyUri.Port;
                string info = proxyIP + ":" + proxyPort;
                return info;
            }
            catch
            {
                return null;
            }
        }
    }
}
