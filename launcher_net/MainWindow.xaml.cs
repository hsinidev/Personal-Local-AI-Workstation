using System;
using System.Diagnostics;
using System.Windows;

namespace PersonalLocalAIWorkstation
{
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
            Closing += MainWindow_Closing;
        }

        private void MainWindow_Closing(object? sender, System.ComponentModel.CancelEventArgs e)
        {
            try
            {
                var proc = SplashWindow.ServerProcess;
                if (proc != null && !proc.HasExited)
                {
                    proc.Kill(entireProcessTree: true);
                }
            }
            catch { }
        }

        private void BtnOpenBrowser_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                Process.Start(new ProcessStartInfo
                {
                    FileName = "http://localhost:3009",
                    UseShellExecute = true
                });
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Could not launch browser: {ex.Message}", "Browser Notice");
            }
        }

        private void BtnAskDeveloper_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                Process.Start(new ProcessStartInfo
                {
                    FileName = "mailto:hsini.jk@gmail.com?subject=Personal%20Local%20AI%20Workstation%20Inquiry%20%26%20Support",
                    UseShellExecute = true
                });
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Contact Developer: hsini.jk@gmail.com\nPortfolio: https://hsini.dev", "Developer Information");
            }
        }

        private void BtnRefresh_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                WebViewControl.Reload();
            }
            catch { }
        }
    }
}