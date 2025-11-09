using RpsGameServer.Models;

namespace RpsGameServer.Services;

public interface ITournamentService
{
    // Player registration
    RegisterPlayerResponse RegisterPlayer(string playerName, int roomId = 1);
    bool UnregisterPlayer(int playerId, int roomId = 1);
    bool UnregisterAllPlayers(int roomId = 1);
    
    // Tournament management
    Tournament GetTournament(int roomId = 1);
    bool StartTournament(int roomId = 1);
    bool EndTournament(int roomId = 1);
    bool ResetTournament(int roomId = 1);
    
    // Round management
    bool StartRound(int roomId, int roundNumber, string? question = null, string? correctAnswer = null);
    bool EndRound(int roomId, int roundNumber);
    bool ResetCurrentRound(int roomId = 1);
    Round? GetCurrentRound(int roomId = 1);
    
    // Player actions
    TournamentStatusResponse GetTournamentStatus(int playerId, int roomId = 1);
    SubmitAnswerResponse SubmitAnswer(SubmitAnswerRequest request, int roomId = 1);
    
    // Results and leaderboard
    List<LeaderboardEntry> GetLeaderboard(int roomId = 1, bool hideForLastTwoRounds = false);
    List<RoundResultEntry> GetRoundResults(int roomId, int roundNumber);
    List<PlayerRoundResult> GetPlayerResults(int playerId, int roomId = 1);
}