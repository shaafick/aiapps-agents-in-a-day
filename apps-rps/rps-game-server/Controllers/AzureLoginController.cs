using Microsoft.AspNetCore.Mvc;
using RpsGameServer.Services;

namespace RpsGameServer.Controllers;

public class AzureLoginController : Controller
{
    private readonly ILoginService _loginService;

    public AzureLoginController(ILoginService loginService)
    {
        _loginService = loginService;
    }

    public async Task<IActionResult> Index()
    {
        var logins = await _loginService.GetAllLoginsAsync();
        return View(logins);
    }

    [HttpPost]
    public async Task<IActionResult> ClaimLogin(string claimedBy)
    {
        if (string.IsNullOrWhiteSpace(claimedBy))
        {
            TempData["Error"] = "Please enter your name to claim a login.";
            return RedirectToAction("Index");
        }

        var login = await _loginService.ClaimLoginAsync(claimedBy);
        if (login == null)
        {
            TempData["Error"] = "No available logins to claim. All entries have been claimed.";
            return RedirectToAction("Index");
        }

        TempData["Success"] = $"Login claimed successfully!";
        TempData["LoginEmail"] = login.LoginEmail;
        TempData["LoginPassword"] = login.LoginPassword;
        TempData["ClaimedBy"] = login.ClaimedBy;
        
        return RedirectToAction("Index");
    }
}
