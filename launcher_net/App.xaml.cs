using System;
using System.Windows;

namespace PersonalLocalAIWorkstation
{
    public partial class App : Application
    {
        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);

            AppDomain.CurrentDomain.UnhandledException += (s, args) =>
            {
                if (args.ExceptionObject is Exception ex)
                {
                    MessageBox.Show($"Fatal Error: {ex.Message}\n{ex.StackTrace}", "Workstation Error", MessageBoxButton.OK, MessageBoxImage.Error);
                }
            };

            DispatcherUnhandledException += (s, args) =>
            {
                MessageBox.Show($"Runtime Error: {args.Exception.Message}\n{args.Exception.InnerException?.Message}", "Workstation Notice", MessageBoxButton.OK, MessageBoxImage.Warning);
                args.Handled = true;
            };

            var splash = new SplashWindow();
            splash.Show();
        }
    }
}
