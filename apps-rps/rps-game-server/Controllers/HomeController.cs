using Microsoft.AspNetCore.Mvc;
using RpsGameServer.Models;
using RpsGameServer.Services;

namespace RpsGameServer.Controllers;

public class HomeController : Controller
{
    private readonly ITournamentService _tournamentService;
    private const string AdminSessionKey = "AdminAuthenticated";

    public HomeController(ITournamentService tournamentService)
    {
        _tournamentService = tournamentService;
    }

    private bool IsAuthenticated()
    {
        return HttpContext.Session.GetString(AdminSessionKey) == "true";
    }

    public IActionResult Index(int roomId = 1)
    {
        ViewBag.RoomId = roomId;
        var tournament = _tournamentService.GetTournament(roomId);
        return View(tournament);
    }

    [HttpPost]
    public IActionResult StartTournament(int roomId = 1)
    {
        if (!IsAuthenticated())
        {
            TempData["Error"] = "Admin access required to start tournament";
            return RedirectToAction("Index", new { roomId });
        }

        _tournamentService.StartTournament(roomId);
        return RedirectToAction("Index", new { roomId });
    }

    [HttpPost]
    public IActionResult EndTournament(int roomId = 1)
    {
        if (!IsAuthenticated())
        {
            TempData["Error"] = "Admin access required to end tournament";
            return RedirectToAction("Index", new { roomId });
        }

        _tournamentService.EndTournament(roomId);
        return RedirectToAction("GrandFinish", new { roomId });
    }

    [HttpPost]
    public IActionResult ResetTournament(int roomId = 1)
    {
        if (!IsAuthenticated())
        {
            TempData["Error"] = "Admin access required to reset tournament";
            return RedirectToAction("Index", new { roomId });
        }

        _tournamentService.ResetTournament(roomId);
        return RedirectToAction("Index", new { roomId });
    }

    [HttpPost]
    public IActionResult StartRound(int roundNumber, int roomId = 1)
    {
        if (!IsAuthenticated())
        {
            TempData["Error"] = "Admin access required to start round";
            return RedirectToAction("Index", new { roomId });
        }

        var success = _tournamentService.StartRound(roomId, roundNumber);
        if (!success)
        {
            TempData["Error"] = "Failed to start round";
        }
        
        return RedirectToAction("Index", new { roomId });
    }

    [HttpPost]
    public IActionResult EndRound(int roundNumber, int roomId = 1)
    {
        if (!IsAuthenticated())
        {
            TempData["Error"] = "Admin access required to end round";
            return RedirectToAction("Index", new { roomId });
        }

        var success = _tournamentService.EndRound(roomId, roundNumber);
        if (!success)
        {
            TempData["Error"] = "Failed to end round";
            return RedirectToAction("Index", new { roomId });
        }
        
        return RedirectToAction("RoundComplete", new { roundNumber, roomId });
    }

    public IActionResult RoundComplete(int roundNumber, int roomId = 1)
    {
        ViewBag.RoomId = roomId;
        var tournament = _tournamentService.GetTournament(roomId);
        var viewModel = new RoundCompleteViewModel
        {
            Tournament = tournament,
            CompletedRoundNumber = roundNumber,
            RoundResults = _tournamentService.GetRoundResults(roomId, roundNumber),
            IsLastRound = roundNumber >= Tournament.MaxRounds
        };
        return View(viewModel);
    }

    public IActionResult TournamentWaiting(int roomId = 1)
    {
        ViewBag.RoomId = roomId;
        var tournament = _tournamentService.GetTournament(roomId);
        return View(tournament);
    }

    public IActionResult GrandFinish(int roomId = 1)
    {
        ViewBag.RoomId = roomId;
        var tournament = _tournamentService.GetTournament(roomId);
        return View(tournament);
    }

    public IActionResult Results(int roomId = 1)
    {
        ViewBag.RoomId = roomId;
        var tournament = _tournamentService.GetTournament(roomId);
        return View(tournament);
    }

    public IActionResult Grid(int roomId = 1)
    {
        ViewBag.RoomId = roomId;
        var tournament = _tournamentService.GetTournament(roomId);
        var viewModel = new GridViewModel
        {
            Players = tournament.Players,
            Rounds = tournament.Rounds.Where(r => r.Status == RoundStatus.Completed).ToList()
        };
        return View(viewModel);
    }

    public IActionResult Register()
    {
        return View();
    }

    [HttpPost]
    public IActionResult Register(string playerName, int roomId = 1)
    {
        if (string.IsNullOrWhiteSpace(playerName))
        {
            TempData["Error"] = "Player name is required";
            return View();
        }

        var response = _tournamentService.RegisterPlayer(playerName, roomId);
        if (response.PlayerId > 0)
        {
            ViewBag.Success = true;
            ViewBag.PlayerId = response.PlayerId;
            ViewBag.PlayerName = playerName;
            ViewBag.RoomId = roomId;
            ViewBag.Message = response.Message;
        }
        else
        {
            TempData["Error"] = response.Message;
        }

        return View();
    }

    public IActionResult Play(int roomId = 1)
    {
        ViewBag.RoomId = roomId;
        var currentRound = _tournamentService.GetCurrentRound(roomId);
        if (currentRound != null && currentRound.Status == RoundStatus.InProgress)
        {
            ViewBag.CurrentQuestion = currentRound.Question;
            ViewBag.CurrentRound = currentRound.RoundNumber;
        }
        return View();
    }

    [HttpPost]
    public IActionResult Play(int playerId, string answer, string move, int roomId = 1)
    {
        ViewBag.RoomId = roomId;
        
        if (playerId <= 0)
        {
            TempData["Error"] = "Invalid player ID";
            return View();
        }

        if (!Enum.TryParse<Move>(move, true, out var parsedMove))
        {
            TempData["Error"] = "Invalid move selection";
            return View();
        }

        var tournament = _tournamentService.GetTournament(roomId);
        var currentRound = _tournamentService.GetCurrentRound(roomId);
        
        if (currentRound == null || currentRound.Status != RoundStatus.InProgress)
        {
            TempData["Error"] = "No active round to submit to";
            return View();
        }

        var request = new SubmitAnswerRequest
        {
            PlayerId = playerId,
            RoundNumber = currentRound.RoundNumber,
            Answer = answer?.Trim() ?? "",
            Move = parsedMove
        };

        var response = _tournamentService.SubmitAnswer(request, roomId);
        if (response.Success)
        {
            ViewBag.Success = true;
            ViewBag.Message = response.Message;
            ViewBag.Question = currentRound.Question;
            ViewBag.PlayerAnswer = answer;
            ViewBag.PlayerMove = parsedMove.ToString();
            ViewBag.ServerMove = currentRound.ServerMove.ToString();
        }
        else
        {
            TempData["Error"] = response.Message;
        }

        return View();
    }
}

public class GridViewModel
{
    public List<Player> Players { get; set; } = new();
    public List<Round> Rounds { get; set; } = new();
}

public class RoundCompleteViewModel
{
    public Tournament Tournament { get; set; } = new();
    public int CompletedRoundNumber { get; set; }
    public List<RoundResultEntry> RoundResults { get; set; } = new();
    public bool IsLastRound { get; set; }
}