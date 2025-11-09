using RpsGameServer.Models;
using System.Collections.Concurrent;

namespace RpsGameServer.Services;

public class TournamentService : ITournamentService
{
    private readonly Dictionary<int, Tournament> _tournaments = new()
    {
        { 1, new Tournament { RoomId = 1 } },
        { 2, new Tournament { RoomId = 2 } }
    };
    private readonly Dictionary<int, int> _nextPlayerIds = new()
    {
        { 1, 1 },
        { 2, 1 }
    };
    private readonly object _lock = new();
    private readonly Random _random = new();
    private readonly IQuestionService _questionService;
    private readonly IServiceProvider _serviceProvider;
    private readonly ILogger<TournamentService> _logger;

    public TournamentService(IQuestionService questionService, IServiceProvider serviceProvider, ILogger<TournamentService> logger)
    {
        _questionService = questionService;
        _serviceProvider = serviceProvider;
        _logger = logger;
    }

    public Tournament GetTournament(int roomId = 1)
    {
        lock (_lock)
        {
            if (!_tournaments.ContainsKey(roomId))
            {
                _tournaments[roomId] = new Tournament { RoomId = roomId };
                _nextPlayerIds[roomId] = 1;
            }
            return _tournaments[roomId];
        }
    }

    public RegisterPlayerResponse RegisterPlayer(string playerName, int roomId = 1)
    {
        lock (_lock)
        {
            var tournament = GetTournament(roomId);
            
            if (tournament.Status != TournamentStatus.Pending)
            {
                return new RegisterPlayerResponse
                {
                    PlayerId = 0,
                    Message = "Tournament has already started or completed"
                };
            }

            var player = new Player
            {
                Id = _nextPlayerIds[roomId]++,
                Name = playerName,
                RegisteredAt = DateTime.UtcNow,
                RoomId = roomId
            };

            tournament.Players.Add(player);

            return new RegisterPlayerResponse
            {
                PlayerId = player.Id,
                Message = $"Player {playerName} registered successfully with ID {player.Id} in Room {roomId}"
            };
        }
    }

    public bool UnregisterPlayer(int playerId, int roomId = 1)
    {
        lock (_lock)
        {
            var tournament = GetTournament(roomId);
            var player = tournament.Players.FirstOrDefault(p => p.Id == playerId);
            if (player == null)
                return false;

            tournament.Players.Remove(player);

            foreach (var round in tournament.Rounds)
            {
                var playerResult = round.PlayerResults.FirstOrDefault(pr => pr.PlayerId == playerId);
                if (playerResult != null)
                {
                    round.PlayerResults.Remove(playerResult);
                }
            }

            return true;
        }
    }

    public bool UnregisterAllPlayers(int roomId = 1)
    {
        lock (_lock)
        {
            var tournament = GetTournament(roomId);
            
            if (!tournament.Players.Any())
                return false;

            tournament.Players.Clear();

            foreach (var round in tournament.Rounds)
            {
                round.PlayerResults.Clear();
            }

            _nextPlayerIds[roomId] = 1;

            return true;
        }
    }

    public bool StartTournament(int roomId = 1)
    {
        lock (_lock)
        {
            var tournament = GetTournament(roomId);
            
            if (tournament.Status != TournamentStatus.Pending)
                return false;

            tournament.Status = TournamentStatus.InProgress;
            tournament.StartedAt = DateTime.UtcNow;
            tournament.CurrentRound = 1;

            for (int i = 1; i <= Tournament.MaxRounds; i++)
            {
                tournament.Rounds.Add(new Round { RoundNumber = i });
            }

            return true;
        }
    }

    public bool EndTournament(int roomId = 1)
    {
        lock (_lock)
        {
            var tournament = GetTournament(roomId);
            
            if (tournament.Status != TournamentStatus.InProgress)
                return false;

            tournament.Status = TournamentStatus.Completed;
            tournament.EndedAt = DateTime.UtcNow;
            
            _ = Task.Run(async () =>
            {
                try
                {
                    using var scope = _serviceProvider.CreateScope();
                    var historyService = scope.ServiceProvider.GetRequiredService<ITournamentHistoryService>();
                    await historyService.SaveTournamentAsync(tournament);
                    _logger.LogInformation("Tournament saved to history successfully");
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Failed to save tournament to history");
                }
            });
            
            return true;
        }
    }

    public bool ResetTournament(int roomId = 1)
    {
        lock (_lock)
        {
            var tournament = GetTournament(roomId);
            
            tournament.Status = TournamentStatus.Pending;
            tournament.CurrentRound = 1;
            tournament.StartedAt = null;
            tournament.EndedAt = null;
            
            foreach (var player in tournament.Players)
            {
                player.TotalScore = 0;
            }
            
            tournament.Rounds.Clear();
            
            return true;
        }
    }

    public bool StartRound(int roomId, int roundNumber, string? question = null, string? correctAnswer = null)
    {
        lock (_lock)
        {
            var tournament = GetTournament(roomId);
            
            if (tournament.Status != TournamentStatus.InProgress)
                return false;

            var round = tournament.Rounds.FirstOrDefault(r => r.RoundNumber == roundNumber);
            if (round == null || round.Status != RoundStatus.Pending)
                return false;

            QuestionAnswer qa;
            if (string.IsNullOrWhiteSpace(question) || string.IsNullOrWhiteSpace(correctAnswer))
            {
                var sequentialQuestion = _questionService.GetQuestionByOrderAsync(roundNumber).GetAwaiter().GetResult();
                if (sequentialQuestion != null)
                {
                    qa = sequentialQuestion;
                }
                else
                {
                    _logger.LogWarning($"No question found for round {roundNumber}, falling back to random question");
                    qa = _questionService.GetRandomQuestionAsync().GetAwaiter().GetResult();
                }
            }
            else
            {
                qa = new QuestionAnswer(question, correctAnswer);
            }

            round.Status = RoundStatus.InProgress;
            round.Question = qa.Question;
            round.CorrectAnswer = qa.Answer;
            round.AnswerRule = qa.AnswerRule;
            round.QuestionType = qa.Type;
            round.MediaUrl = qa.MediaUrl;
            round.ServerMove = GenerateRandomMove();
            round.StartedAt = DateTime.UtcNow;

            foreach (var player in tournament.Players)
            {
                round.PlayerResults.Add(new PlayerRoundResult
                {
                    PlayerId = player.Id,
                    RoundNumber = roundNumber
                });
            }

            tournament.CurrentRound = roundNumber;
            return true;
        }
    }

    public bool EndRound(int roomId, int roundNumber)
    {
        lock (_lock)
        {
            var tournament = GetTournament(roomId);
            var round = tournament.Rounds.FirstOrDefault(r => r.RoundNumber == roundNumber);
            if (round == null || round.Status != RoundStatus.InProgress)
                return false;

            round.Status = RoundStatus.Completed;
            round.EndedAt = DateTime.UtcNow;

            CalculateRoundScores(round, tournament);

            if (roundNumber < Tournament.MaxRounds)
            {
                tournament.CurrentRound = roundNumber + 1;
            }

            return true;
        }
    }

    public bool ResetCurrentRound(int roomId = 1)
    {
        lock (_lock)
        {
            var currentRound = GetCurrentRound(roomId);
            if (currentRound == null)
                return false;

            var tournament = GetTournament(roomId);

            currentRound.Status = RoundStatus.Pending;
            currentRound.StartedAt = null;
            currentRound.EndedAt = null;
            currentRound.Question = string.Empty;
            currentRound.CorrectAnswer = string.Empty;
            currentRound.ServerMove = Move.Rock;

            foreach (var playerResult in currentRound.PlayerResults)
            {
                playerResult.Answer = null;
                playerResult.Move = null;
                playerResult.AnswerCorrect = false;
                playerResult.Score = 0;
                playerResult.SubmittedAt = null;
            }

            foreach (var player in tournament.Players)
            {
                var playerResult = currentRound.PlayerResults.FirstOrDefault(pr => pr.PlayerId == player.Id);
                if (playerResult != null)
                {
                    player.TotalScore -= playerResult.Score;
                }
            }

            return true;
        }
    }

    public Round? GetCurrentRound(int roomId = 1)
    {
        lock (_lock)
        {
            var tournament = GetTournament(roomId);
            return tournament.Rounds.FirstOrDefault(r => r.RoundNumber == tournament.CurrentRound);
        }
    }

    public TournamentStatusResponse GetTournamentStatus(int playerId, int roomId = 1)
    {
        lock (_lock)
        {
            var tournament = GetTournament(roomId);
            var currentRound = GetCurrentRound(roomId);
            var playerResult = currentRound?.PlayerResults.FirstOrDefault(pr => pr.PlayerId == playerId);
            
            return new TournamentStatusResponse
            {
                TournamentStatus = tournament.Status,
                CurrentRound = tournament.CurrentRound,
                CurrentRoundStatus = currentRound?.Status,
                CurrentQuestion = currentRound?.Status == RoundStatus.InProgress ? currentRound.Question : null,
                CanSubmit = currentRound?.Status == RoundStatus.InProgress && 
                          (playerResult == null || (playerResult != null && !playerResult.HasSubmitted)),
                RoomId = roomId
            };
        }
    }

    public SubmitAnswerResponse SubmitAnswer(SubmitAnswerRequest request, int roomId = 1)
    {
        lock (_lock)
        {
            var tournament = GetTournament(roomId);
            var round = tournament.Rounds.FirstOrDefault(r => r.RoundNumber == request.RoundNumber);
            if (round == null || round.Status != RoundStatus.InProgress)
            {
                return new SubmitAnswerResponse
                {
                    Success = false,
                    Message = "Round is not active"
                };
            }

            var playerResult = round.PlayerResults.FirstOrDefault(pr => pr.PlayerId == request.PlayerId);
            if (playerResult == null)
            {
                return new SubmitAnswerResponse
                {
                    Success = false,
                    Message = "Player not found in round"
                };
            }

            if (playerResult.HasSubmitted)
            {
                return new SubmitAnswerResponse
                {
                    Success = false,
                    Message = "Answer already submitted for this round"
                };
            }

            playerResult.Answer = request.Answer;
            playerResult.Move = request.Move;
            playerResult.SubmittedAt = DateTime.UtcNow;
            playerResult.AnswerCorrect = ValidateAnswer(request.Answer.Trim(), round.CorrectAnswer.Trim(), round.AnswerRule);

            return new SubmitAnswerResponse
            {
                Success = true,
                Message = "Answer submitted successfully"
            };
        }
    }

    public List<LeaderboardEntry> GetLeaderboard(int roomId = 1, bool hideForLastTwoRounds = false)
    {
        lock (_lock)
        {
            var tournament = GetTournament(roomId);
            
            if (hideForLastTwoRounds && tournament.CurrentRound >= Tournament.MaxRounds - 1)
            {
                return new List<LeaderboardEntry>();
            }

            var leaderboard = tournament.Players
                .Select(p => new LeaderboardEntry
                {
                    PlayerId = p.Id,
                    PlayerName = p.Name,
                    TotalScore = p.TotalScore
                })
                .OrderByDescending(le => le.TotalScore)
                .ThenBy(le => le.PlayerName)
                .ToList();

            for (int i = 0; i < leaderboard.Count; i++)
            {
                leaderboard[i].Position = i + 1;
            }

            return leaderboard;
        }
    }

    public List<RoundResultEntry> GetRoundResults(int roomId, int roundNumber)
    {
        lock (_lock)
        {
            var tournament = GetTournament(roomId);
            var round = tournament.Rounds.FirstOrDefault(r => r.RoundNumber == roundNumber);
            if (round == null)
                return new List<RoundResultEntry>();

            return round.PlayerResults
                .Join(tournament.Players, pr => pr.PlayerId, p => p.Id, (pr, p) => new RoundResultEntry
                {
                    PlayerId = p.Id,
                    PlayerName = p.Name,
                    Answer = pr.Answer,
                    Move = pr.Move,
                    AnswerCorrect = pr.AnswerCorrect,
                    ServerMove = round.ServerMove,
                    WonRound = pr.Move.HasValue && DetermineWinner(pr.Move.Value, round.ServerMove),
                    Score = pr.Score
                })
                .OrderByDescending(rre => rre.Score)
                .ThenBy(rre => rre.PlayerName)
                .ToList();
        }
    }

    public List<PlayerRoundResult> GetPlayerResults(int playerId, int roomId = 1)
    {
        lock (_lock)
        {
            var tournament = GetTournament(roomId);
            return tournament.Rounds
                .SelectMany(r => r.PlayerResults)
                .Where(pr => pr.PlayerId == playerId)
                .OrderBy(pr => pr.RoundNumber)
                .ToList();
        }
    }

    private Move GenerateRandomMove()
    {
        var moves = Enum.GetValues<Move>();
        return moves[_random.Next(moves.Length)];
    }

    private void CalculateRoundScores(Round round, Tournament tournament)
    {
        foreach (var result in round.PlayerResults)
        {
            if (!result.HasSubmitted || !result.Move.HasValue)
            {
                result.Score = 0;
                continue;
            }

            int score = 0;

            if (result.AnswerCorrect)
            {
                score += 30;
            }

            if (DetermineWinner(result.Move.Value, round.ServerMove))
            {
                score += 20;
            }
            else if (result.Move.Value == round.ServerMove)
            {
                score += 10;
            }

            result.Score = score;

            var player = tournament.Players.FirstOrDefault(p => p.Id == result.PlayerId);
            if (player != null)
            {
                player.TotalScore += score;
            }
        }
    }

    private bool ValidateAnswer(string playerAnswer, string correctAnswer, string? answerRule)
    {
        if (string.IsNullOrWhiteSpace(answerRule) || answerRule.Equals("Exact", StringComparison.OrdinalIgnoreCase))
        {
            return string.Equals(playerAnswer, correctAnswer, StringComparison.OrdinalIgnoreCase);
        }
        
        if (answerRule.Equals("FuzzyMatch", StringComparison.OrdinalIgnoreCase))
        {
            return playerAnswer.Contains(correctAnswer, StringComparison.OrdinalIgnoreCase);
        }
        
        return string.Equals(playerAnswer, correctAnswer, StringComparison.OrdinalIgnoreCase);
    }

    private bool DetermineWinner(Move playerMove, Move serverMove)
    {
        return playerMove switch
        {
            Move.Rock => serverMove == Move.Scissors,
            Move.Paper => serverMove == Move.Rock,
            Move.Scissors => serverMove == Move.Paper,
            _ => false
        };
    }
}