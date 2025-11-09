using Microsoft.AspNetCore.Mvc;
using RpsGameServer.Models;
using RpsGameServer.Services;

namespace RpsGameServer.Controllers;

[ApiController]
[Route("api/[controller]")]
public class PlayerController : ControllerBase
{
    private readonly ITournamentService _tournamentService;

    public PlayerController(ITournamentService tournamentService)
    {
        _tournamentService = tournamentService;
    }

    [HttpPost("register")]
    public ActionResult<RegisterPlayerResponse> RegisterPlayer([FromBody] RegisterPlayerRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.Name))
        {
            return BadRequest(new RegisterPlayerResponse
            {
                PlayerId = 0,
                Message = "Player name is required"
            });
        }

        if (request.RoomId != 1 && request.RoomId != 2)
        {
            return BadRequest(new RegisterPlayerResponse
            {
                PlayerId = 0,
                Message = "Room ID must be 1 or 2"
            });
        }

        var response = _tournamentService.RegisterPlayer(request.Name, request.RoomId);
        
        if (response.PlayerId == 0)
        {
            return BadRequest(response);
        }

        return Ok(response);
    }

    [HttpGet("{playerId}/status")]
    public ActionResult<TournamentStatusResponse> GetStatus(int playerId, [FromQuery] int roomId = 1)
    {
        var status = _tournamentService.GetTournamentStatus(playerId, roomId);
        return Ok(status);
    }

    [HttpPost("submit-answer")]
    public ActionResult<SubmitAnswerResponse> SubmitAnswer([FromBody] SubmitAnswerRequest request, [FromQuery] int roomId = 1)
    {
        if (request.PlayerId <= 0)
        {
            return BadRequest(new SubmitAnswerResponse
            {
                Success = false,
                Message = "Invalid player ID"
            });
        }

        if (string.IsNullOrWhiteSpace(request.Answer))
        {
            return BadRequest(new SubmitAnswerResponse
            {
                Success = false,
                Message = "Answer is required"
            });
        }

        var response = _tournamentService.SubmitAnswer(request, roomId);
        
        if (!response.Success)
        {
            return BadRequest(response);
        }

        return Ok(response);
    }

    [HttpGet("{playerId}/results")]
    public ActionResult<List<PlayerRoundResult>> GetPlayerResults(int playerId, [FromQuery] int roomId = 1)
    {
        var results = _tournamentService.GetPlayerResults(playerId, roomId);
        return Ok(results);
    }
}