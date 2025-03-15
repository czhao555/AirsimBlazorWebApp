using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;

namespace BlazorAppInterview.Services
{
    public class AirSimClient
    {
        private readonly UdpClient _udpClient;
        private readonly UdpClient _dataClient;

        public event Action<byte[]> OnFrameReceived;
        public event Action<string> OnDataReceived;

        public AirSimClient()
        {
            _udpClient = new UdpClient(5001); // Video stream UDP port
            _dataClient = new UdpClient(5002); // Drone data UDP port

            Task.Run(ReceiveVideoStream);
            Task.Run(ReceiveDroneData);
        }

        private async Task ReceiveVideoStream()
        {
            while (true)
            {
                try
                {
                    UdpReceiveResult result = await _udpClient.ReceiveAsync();
                    byte[] frameData = result.Buffer;
                    OnFrameReceived?.Invoke(frameData);
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[ERROR] Video reception error: {ex.Message}");
                }
            }
        }

        private async Task ReceiveDroneData()
        {
            while (true)
            {
                try
                {
                    UdpReceiveResult result = await _dataClient.ReceiveAsync();
                    string data = Encoding.UTF8.GetString(result.Buffer);
                    OnDataReceived?.Invoke(data);
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[ERROR] Data reception error: {ex.Message}");
                }
            }
        }

        public async Task MovementAsync(string command)
        {
            try
            {
                byte[] data = Encoding.UTF8.GetBytes(command);
                await _udpClient.SendAsync(data, data.Length, "172.26.112.1", 5000);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[ERROR] Failed to send command: {ex.Message}");
            }
        }

        public async Task RequestDroneData()
        {
            try
            {
                byte[] requestData = Encoding.UTF8.GetBytes("get_data");
                await _dataClient.SendAsync(requestData, requestData.Length, "172.26.112.1", 5003);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[ERROR] Failed to request drone data: {ex.Message}");
            }
        }
    }
}
