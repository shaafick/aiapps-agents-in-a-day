using Microsoft.AspNetCore.Mvc;
using RpsGameServer.Models;
using RpsGameServer.Services;

namespace RpsGameServer.Controllers;

public class AdminController : Controller
{
    private readonly ITournamentService _tournamentService;
    private readonly IQuestionService _questionService;
    private readonly ITournamentHistoryService _historyService;
    private const string AdminPasscode = "9999";
    private const string AdminSessionKey = "AdminAuthenticated";

    public AdminController(ITournamentService tournamentService, IQuestionService questionService, ITournamentHistoryService historyService)
    {
        _tournamentService = tournamentService;
        _questionService = questionService;
        _historyService = historyService;
    }

    public IActionResult Login()
    {
        // If already authenticated, redirect to admin index
        if (IsAuthenticated())
        {
            return RedirectToAction("Index");
        }
        
        return View();
    }

    [HttpPost]
    public IActionResult Login(string passcode)
    {
        if (passcode == AdminPasscode)
        {
            HttpContext.Session.SetString(AdminSessionKey, "true");
            return RedirectToAction("Index");
        }

        TempData["Error"] = "Invalid passcode. Please try again.";
        return View();
    }

    public IActionResult Index(int roomId = 1)
    {
        if (!IsAuthenticated())
        {
            return RedirectToAction("Login");
        }

        ViewBag.RoomId = roomId;
        var tournament = _tournamentService.GetTournament(roomId);
        return View(tournament);
    }

    [HttpPost]
    public IActionResult UnregisterPlayer(int playerId, int roomId = 1)
    {
        if (!IsAuthenticated())
        {
            return RedirectToAction("Login");
        }

        var success = _tournamentService.UnregisterPlayer(playerId, roomId);
        if (success)
        {
            TempData["Success"] = "Player unregistered successfully.";
        }
        else
        {
            TempData["Error"] = "Failed to unregister player.";
        }

        return RedirectToAction("Index", new { roomId });
    }

    [HttpPost]
    public IActionResult UnregisterAllPlayers(int roomId = 1)
    {
        if (!IsAuthenticated())
        {
            return RedirectToAction("Login");
        }

        var success = _tournamentService.UnregisterAllPlayers(roomId);
        if (success)
        {
            TempData["Success"] = "All players unregistered successfully.";
        }
        else
        {
            TempData["Error"] = "No players to unregister or operation failed.";
        }

        return RedirectToAction("Index", new { roomId });
    }

    [HttpPost]
    public IActionResult ResetCurrentRound(int roomId = 1)
    {
        if (!IsAuthenticated())
        {
            return RedirectToAction("Login");
        }

        var success = _tournamentService.ResetCurrentRound(roomId);
        if (success)
        {
            TempData["Success"] = "Current round reset successfully.";
        }
        else
        {
            TempData["Error"] = "Failed to reset current round.";
        }

        return RedirectToAction("Index", new { roomId });
    }

    [HttpPost]
    public IActionResult ResetTournament(int roomId = 1)
    {
        if (!IsAuthenticated())
        {
            return RedirectToAction("Login");
        }

        var success = _tournamentService.ResetTournament(roomId);
        if (success)
        {
            TempData["Success"] = "Tournament reset successfully. All players remain registered.";
        }
        else
        {
            TempData["Error"] = "Failed to reset tournament.";
        }

        return RedirectToAction("Index", new { roomId });
    }

    [HttpPost]
    public IActionResult Logout()
    {
        HttpContext.Session.Remove(AdminSessionKey);
        return RedirectToAction("Login");
    }

    // Questions management
    public async Task<IActionResult> Questions()
    {
        if (!IsAuthenticated())
        {
            return RedirectToAction("Login");
        }

        var questions = await _questionService.GetAllQuestionsAsync();
        return View(questions);
    }

    [HttpPost]
    public async Task<IActionResult> UpdateQuestions(string questionsJson)
    {
        if (!IsAuthenticated())
        {
            return RedirectToAction("Login");
        }

        var success = await _questionService.UpdateQuestionsFromJsonAsync(questionsJson);
        if (success)
        {
            TempData["Success"] = "Questions updated successfully.";
        }
        else
        {
            TempData["Error"] = "Failed to update questions. Please check the JSON format.";
        }

        return RedirectToAction("Questions");
    }

    [HttpGet]
    public async Task<IActionResult> GetQuestionsJson()
    {
        if (!IsAuthenticated())
        {
            return Unauthorized();
        }

        var json = await _questionService.GetQuestionsAsJsonAsync();
        return Json(json);
    }

    // Tournament history management
    public async Task<IActionResult> History()
    {
        if (!IsAuthenticated())
        {
            return RedirectToAction("Login");
        }

        var tournaments = await _historyService.GetAllTournamentsAsync();
        return View(tournaments);
    }

    public async Task<IActionResult> HistoryDetails(int id)
    {
        if (!IsAuthenticated())
        {
            return RedirectToAction("Login");
        }

        var tournament = await _historyService.GetTournamentByIdAsync(id);
        if (tournament == null)
        {
            return NotFound();
        }

        return View(tournament);
    }

    [HttpPost]
    public async Task<IActionResult> DeleteTournament(int id)
    {
        if (!IsAuthenticated())
        {
            return RedirectToAction("Login");
        }

        var success = await _historyService.DeleteTournamentAsync(id);
        if (success)
        {
            TempData["Success"] = "Tournament deleted successfully.";
        }
        else
        {
            TempData["Error"] = "Failed to delete tournament.";
        }

        return RedirectToAction("History");
    }

    private bool IsAuthenticated()
    {
        return HttpContext.Session.GetString(AdminSessionKey) == "true";
    }
}