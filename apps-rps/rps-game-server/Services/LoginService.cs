using System.Text.Json;
using RpsGameServer.Models;

namespace RpsGameServer.Services;

public class LoginService : ILoginService
{
    private readonly string _loginFilePath;
    private readonly SemaphoreSlim _lock = new(1, 1);

    public LoginService(IWebHostEnvironment environment)
    {
        _loginFilePath = Path.Combine(environment.ContentRootPath, "login.json");
    }

    public async Task<List<LoginEntry>> GetAllLoginsAsync()
    {
        await _lock.WaitAsync();
        try
        {
            if (!File.Exists(_loginFilePath))
            {
                return new List<LoginEntry>();
            }

            var json = await File.ReadAllTextAsync(_loginFilePath);
            var options = new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            };
            var logins = JsonSerializer.Deserialize<List<LoginEntry>>(json, options) ?? new List<LoginEntry>();
            return logins;
        }
        finally
        {
            _lock.Release();
        }
    }

    public async Task<LoginEntry?> ClaimLoginAsync(string claimedBy)
    {
        await _lock.WaitAsync();
        try
        {
            var logins = await GetAllLoginsWithoutLockAsync();
            var availableLogin = logins.FirstOrDefault(l => string.IsNullOrEmpty(l.ClaimedBy));
            
            if (availableLogin == null)
            {
                return null;
            }

            availableLogin.ClaimedBy = claimedBy;
            await SaveLoginsAsync(logins);
            return availableLogin;
        }
        finally
        {
            _lock.Release();
        }
    }

    private async Task<List<LoginEntry>> GetAllLoginsWithoutLockAsync()
    {
        if (!File.Exists(_loginFilePath))
        {
            return new List<LoginEntry>();
        }

        var json = await File.ReadAllTextAsync(_loginFilePath);
        var options = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true
        };
        var logins = JsonSerializer.Deserialize<List<LoginEntry>>(json, options) ?? new List<LoginEntry>();
        return logins;
    }

    private async Task SaveLoginsAsync(List<LoginEntry> logins)
    {
        var options = new JsonSerializerOptions 
        { 
            WriteIndented = true
        };
        var json = JsonSerializer.Serialize(logins, options);
        await File.WriteAllTextAsync(_loginFilePath, json);
    }
}
