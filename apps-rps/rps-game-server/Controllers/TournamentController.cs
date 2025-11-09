using Microsoft.AspNetCore.Mvc;
using RpsGameServer.Models;
using RpsGameServer.Services;

namespace RpsGameServer.Controllers;

[ApiController]
[Route("api/[controller]")]
public class TournamentController : ControllerBase
{
    private readonly ITournamentService _tournamentService;

    public TournamentController(ITournamentService tournamentService)
    {
        _tournamentService = tournamentService;
    }

    [HttpGet("status")]
    public ActionResult<Tournament> GetTournamentStatus([FromQuery] int roomId = 1)
    {
        var tournament = _tournamentService.GetTournament(roomId);
        return Ok(tournament);
    }

    [HttpGet("leaderboard")]
    public ActionResult<List<LeaderboardEntry>> GetLeaderboard([FromQuery] int roomId = 1)
    {
        var leaderboard = _tournamentService.GetLeaderboard(roomId, hideForLastTwoRounds: true);
        return Ok(leaderboard);
    }

    [HttpGet("round/{roundNumber}/results")]
    public ActionResult<List<RoundResultEntry>> GetRoundResults(int roundNumber, [FromQuery] int roomId = 1)
    {
        var results = _tournamentService.GetRoundResults(roomId, roundNumber);
        return Ok(results);
    }
}