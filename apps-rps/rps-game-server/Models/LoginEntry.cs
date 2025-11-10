using System.Text.Json.Serialization;

namespace RpsGameServer.Models;

public class LoginEntry
{
    [JsonPropertyName("loginEmail")]
    public string LoginEmail { get; set; } = string.Empty;
    
    [JsonPropertyName("loginPassword")]
    public string LoginPassword { get; set; } = string.Empty;
    
    [JsonPropertyName("claimedBy")]
    public string? ClaimedBy { get; set; }
}
