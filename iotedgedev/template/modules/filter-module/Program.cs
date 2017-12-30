namespace filter_module {
    using System.Collections.Generic;
    using System.IO;
    using System.Runtime.InteropServices;
    using System.Runtime.Loader;
    using System.Security.Cryptography.X509Certificates;
    using System.Text;
    using System.Threading.Tasks;
    using System.Threading;
    using System;
    using Microsoft.Azure.Devices.Client.Transport.Mqtt;
    using Microsoft.Azure.Devices.Client;
    using Microsoft.Azure.Devices.Shared;
    using Newtonsoft.Json;

    class Program {
        static int counter;
        static int temperatureThreshold { get; set; } = 25;

        class MessageBody {
            public Machine machine { get; set; }
            public Ambient ambient { get; set; }
            public string timeCreated { get; set; }
        }

        class Machine {
            public double temperature { get; set; }
            public double pressure { get; set; }
        }

        class Ambient {
            public double temperature { get; set; }
            public int humidity { get; set; }
        }

        static void Main (string[] args) {
            // The Edge runtime gives us the connection string we need -- it is injected as an environment variable
            string connectionString = Environment.GetEnvironmentVariable ("EdgeHubConnectionString");

            // Cert verification is not yet fully functional when using Windows OS for the container
            bool bypassCertVerification = RuntimeInformation.IsOSPlatform (OSPlatform.Windows);
            if (!bypassCertVerification) InstallCert ();
            Init (connectionString, bypassCertVerification).Wait ();

            // Wait until the app unloads or is cancelled
            var cts = new CancellationTokenSource ();
            AssemblyLoadContext.Default.Unloading += (ctx) => cts.Cancel ();
            Console.CancelKeyPress += (sender, cpe) => cts.Cancel ();
            WhenCancelled (cts.Token).Wait ();
        }

        /// <summary>
        /// Handles cleanup operations when app is cancelled or unloads
        /// </summary>
        public static Task WhenCancelled (CancellationToken cancellationToken) {
            var tcs = new TaskCompletionSource<bool> ();
            cancellationToken.Register (s => ((TaskCompletionSource<bool>) s).SetResult (true), tcs);
            return tcs.Task;
        }

        /// <summary>
        /// Add certificate in local cert store for use by client for secure connection to IoT Edge runtime
        /// </summary>
        static void InstallCert () {
            string certPath = Environment.GetEnvironmentVariable ("EdgeModuleCACertificateFile");
            if (string.IsNullOrWhiteSpace (certPath)) {
                // We cannot proceed further without a proper cert file
                Console.WriteLine ($"Missing path to certificate collection file: {certPath}");
                throw new InvalidOperationException ("Missing path to certificate file.");
            } else if (!File.Exists (certPath)) {
                // We cannot proceed further without a proper cert file
                Console.WriteLine ($"Missing path to certificate collection file: {certPath}");
                throw new InvalidOperationException ("Missing certificate file.");
            }
            X509Store store = new X509Store (StoreName.Root, StoreLocation.CurrentUser);
            store.Open (OpenFlags.ReadWrite);
            store.Add (new X509Certificate2 (X509Certificate2.CreateFromCertFile (certPath)));
            Console.WriteLine ("Added Cert: " + certPath);
            store.Close ();
        }

        /// <summary>
        /// Initializes the DeviceClient and sets up the callback to receive
        /// messages containing temperature information
        /// </summary>
        static async Task Init (string connectionString, bool bypassCertVerification = false) {

            MqttTransportSettings mqttSetting = new MqttTransportSettings (TransportType.Mqtt_Tcp_Only);
            // During dev you might want to bypass the cert verification. It is highly recommended to verify certs systematically in production
            if (bypassCertVerification) {
                mqttSetting.RemoteCertificateValidationCallback = (sender, certificate, chain, sslPolicyErrors) => true;
            }
            ITransportSettings[] settings = { mqttSetting };

            // Open a connection to the Edge runtime
            DeviceClient ioTHubModuleClient = DeviceClient.CreateFromConnectionString (connectionString, settings);
            await ioTHubModuleClient.OpenAsync ();
            Console.WriteLine ("IoT Hub module client initialized.");

            // Register callback to be called when a message is received by the module
            // await ioTHubModuleClient.SetImputMessageHandlerAsync("input1", PipeMessage, iotHubModuleClient);

            // Attach callback for Twin desired properties updates
            await ioTHubModuleClient.SetDesiredPropertyUpdateCallbackAsync (onDesiredPropertiesUpdate, null);

            // Register callback to be called when a message is received by the module
            await ioTHubModuleClient.SetInputMessageHandlerAsync ("input1", FilterMessages, ioTHubModuleClient);
        }

        static Task onDesiredPropertiesUpdate (TwinCollection desiredProperties, object userContext) {
            try {
                Console.WriteLine ("Desired property change:");
                Console.WriteLine (JsonConvert.SerializeObject (desiredProperties));

                if (desiredProperties["TemperatureThreshold"] != null)
                    temperatureThreshold = desiredProperties["TemperatureThreshold"];

            } catch (AggregateException ex) {
                foreach (Exception exception in ex.InnerExceptions) {
                    Console.WriteLine ();
                    Console.WriteLine ("Error when receiving desired property: {0}", exception);
                }
            } catch (Exception ex) {
                Console.WriteLine ();
                Console.WriteLine ("Error when receiving desired property: {0}", ex.Message);
            }
            return Task.CompletedTask;
        }

        static async Task<MessageResponse> FilterMessages (Message message, object userContext) {
            int counterValue = Interlocked.Increment (ref counter);

            try {
                DeviceClient deviceClient = (DeviceClient) userContext;

                byte[] messageBytes = message.GetBytes ();
                string messageString = Encoding.UTF8.GetString (messageBytes);
                Console.WriteLine ($"Received message {counterValue}: [{messageString}]");

                // Get message body
                var messageBody = JsonConvert.DeserializeObject<MessageBody> (messageString);

                if (messageBody != null && messageBody.machine.temperature > temperatureThreshold) {
                    Console.WriteLine ($"Machine temperature {messageBody.machine.temperature} " +
                        $"exceeds threshold {temperatureThreshold}");
                    var filteredMessage = new Message (messageBytes);
                    foreach (KeyValuePair<string, string> prop in message.Properties) {
                        filteredMessage.Properties.Add (prop.Key, prop.Value);
                    }

                    filteredMessage.Properties.Add ("MessageType", "Alert");
                    await deviceClient.SendEventAsync ("output1", filteredMessage);
                }

                // Indicate that the message treatment is completed
                return MessageResponse.Completed;
            } catch (AggregateException ex) {
                foreach (Exception exception in ex.InnerExceptions) {
                    Console.WriteLine ();
                    Console.WriteLine ("Error in sample: {0}", exception);
                }
                // Indicate that the message treatment is not completed
                DeviceClient deviceClient = (DeviceClient) userContext;
                return MessageResponse.Abandoned;
            } catch (Exception ex) {
                Console.WriteLine ();
                Console.WriteLine ("Error in sample: {0}", ex.Message);
                // Indicate that the message treatment is not completed
                DeviceClient deviceClient = (DeviceClient) userContext;
                return MessageResponse.Abandoned;
            }
        }
    }
}