using System;
using System.IO;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace GameLauncher
{
    public partial class LauncherForm : Form
    {
        private JsonElement[] fileEntries;
        private string baseDownloadUrl = "";

        public LauncherForm()
        {
            InitializeComponent();
            LoadIndexJson();
        }

        private async void LoadIndexJson()
        {
            try
            {
                string url = "https://prod-cn-alicdn-gamestarter.kurogame.com/launcher/game/G152/10008_Pa0Q0EMFxukjEqX33pF9Uyvdc8MaGPSz/index.json";

                using HttpClient client = new HttpClient();
                string json = await client.GetStringAsync(url);

                var doc = JsonDocument.Parse(json);
                baseDownloadUrl = doc.RootElement.GetProperty("base_url").GetString();

                var files = doc.RootElement.GetProperty("packages");
                fileEntries = new JsonElement[files.GetArrayLength()];
                fileListBox.Items.Clear();

                for (int i = 0; i < files.GetArrayLength(); i++)
                {
                    var file = files[i];
                    string path = file.GetProperty("path").GetString();
                    fileListBox.Items.Add(path);
                    fileEntries[i] = file;
                }

                Log($"โหลดรายการไฟล์ทั้งหมด {fileEntries.Length} ไฟล์");
            }
            catch (Exception ex)
            {
                Log("โหลดข้อมูลล้มเหลว: " + ex.Message);
            }
        }

        private async void downloadButton_Click(object sender, EventArgs e)
        {
            if (fileListBox.SelectedIndex < 0)
            {
                MessageBox.Show("กรุณาเลือกไฟล์");
                return;
            }

            var selected = fileEntries[fileListBox.SelectedIndex];
            string path = selected.GetProperty("path").GetString();
            string fullUrl = baseDownloadUrl + path;

            try
            {
                using HttpClient client = new HttpClient();
                byte[] data = await client.GetByteArrayAsync(fullUrl);

                string fileName = Path.GetFileName(path);
                string savePath = Path.Combine(Application.StartupPath, fileName);
                File.WriteAllBytes(savePath, data);

                Log($"ดาวน์โหลดสำเร็จ: {fileName}");
            }
            catch (Exception ex)
            {
                Log("เกิดข้อผิดพลาด: " + ex.Message);
            }
        }

        private void Log(string message)
        {
            logBox.AppendText($"[{DateTime.Now:HH:mm:ss}] {message}{Environment.NewLine}");
        }
    }
}