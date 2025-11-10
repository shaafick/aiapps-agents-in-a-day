using RpsGameServer.Models;

namespace RpsGameServer.Services;

public interface ILoginService
{
    Task<List<LoginEntry>> GetAllLoginsAsync();
    Task<LoginEntry?> ClaimLoginAsync(string claimedBy);
}
