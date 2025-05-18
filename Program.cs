using System;
using System.Windows.Forms;

namespace GameLauncher
{
    static class Program
    {
        [STAThread]
        static void Main()
        {
            ApplicationConfiguration.Initialize();
            Application.Run(new LauncherForm());
        }
    }
}