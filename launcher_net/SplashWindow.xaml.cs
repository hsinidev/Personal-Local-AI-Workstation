using System;
using System.Diagnostics;
using System.IO;
using System.Net.Http;
using System.Threading.Tasks;
using System.Windows;

namespace PersonalLocalAIWorkstation
{
    public partial class SplashWindow : Window
    {
        private static Process? _serverProcess;
        private readonly HttpClient _httpClient = new() { Timeout = TimeSpan.FromSeconds(2) };

        public SplashWindow()
        {
            InitializeComponent();
            Loaded += async (s, e) => await InitializeWorkstationAsync();
        }

        public static Process? ServerProcess => _serverProcess;

        private async Task InitializeWorkstationAsync()
        {
            try
            {
                // Step 1: Initialize
                UpdateStatus("INITIALIZING NEURAL ENGINE CORE...", 20);
                await Task.Delay(400);

                // Step 2: Check / Start Ollama
                UpdateStatus("CHECKING LOCAL OLLAMA DAEMON...", 40);
                await CheckAndStartOllamaAsync();
                await Task.Delay(300);

                // Step 3: Start Python Dashboard Server
                UpdateStatus("MOUNTING SWARM DAG & HYBRID RAG VECTOR STORE...", 65);
                StartDashboardServer();
                await Task.Delay(400);

                // Step 4: Await Server Readiness
                UpdateStatus("LAUNCHING WORKSTATION CONTROL DASHBOARD...", 85);
                bool ready = await WaitForServerAsync("http://127.0.0.1:3009/", maxRetries: 15);

                // Step 5: Ready
                UpdateStatus("READY! OPENING INTERACTIVE WORKSTATION...", 100);
                await Task.Delay(400);

                // Open Main Window
                var mainWindow = new MainWindow();
                Application.Current.MainWindow = mainWindow;
                mainWindow.Show();

                // Close splash
                Close();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Workstation startup note: {ex.Message}\nLaunching fallback dashboard...", "Workstation Startup", MessageBoxButton.OK, MessageBoxImage.Information);
                var mainWindow = new MainWindow();
                Application.Current.MainWindow = mainWindow;
                mainWindow.Show();
                Close();
            }
        }

        private void UpdateStatus(string message, double percent)
        {
            Dispatcher.Invoke(() =>
            {
                StatusText.Text = message;
                LoadProgress.Value = percent;
                PercentText.Text = $"{(int)percent}%";
            });
        }

        private async Task CheckAndStartOllamaAsync()
        {
            try
            {
                var response = await _httpClient.GetAsync("http://127.0.0.1:11434/api/tags");
                if (response.IsSuccessStatusCode)
                {
                    return;
                }
            }
            catch
            {
                try
                {
                    var psi = new ProcessStartInfo
                    {
                        FileName = "ollama",
                        Arguments = "serve",
                        CreateNoWindow = true,
                        UseShellExecute = false,
                        WindowStyle = ProcessWindowStyle.Hidden
                    };
                    Process.Start(psi);
                }
                catch { }
            }
        }

        private void StartDashboardServer()
        {
            try
            {
                string baseDir = AppDomain.CurrentDomain.BaseDirectory;
                
                string servePath = Path.Combine(baseDir, "apps", "dashboard", "serve.py");
                if (!File.Exists(servePath))
                {
                    string parentDir = Path.GetFullPath(Path.Combine(baseDir, "..", "..", "..", ".."));
                    servePath = Path.Combine(parentDir, "apps", "dashboard", "serve.py");
                }
                if (!File.Exists(servePath))
                {
                    servePath = Path.Combine(Directory.GetCurrentDirectory(), "apps", "dashboard", "serve.py");
                }

                if (File.Exists(servePath))
                {
                    var psi = new ProcessStartInfo
                    {
                        FileName = "python",
                        Arguments = $"\"{servePath}\"",
                        WorkingDirectory = Path.GetDirectoryName(Path.GetDirectoryName(Path.GetDirectoryName(servePath))) ?? Directory.GetCurrentDirectory(),
                        CreateNoWindow = true,
                        UseShellExecute = false,
                        WindowStyle = ProcessWindowStyle.Hidden
                    };
                    _serverProcess = Process.Start(psi);
                }
            }
            catch { }
        }

        private async Task<bool> WaitForServerAsync(string url, int maxRetries)
        {
            for (int i = 0; i < maxRetries; i++)
            {
                try
                {
                    var res = await _httpClient.GetAsync(url);
                    if (res.IsSuccessStatusCode) return true;
                }
                catch
                {
                    await Task.Delay(300);
                }
            }
            return false;
        }
    }
}
