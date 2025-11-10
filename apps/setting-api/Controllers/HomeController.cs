using Microsoft.AspNetCore.Mvc;
using ConfigApi.Services;
using ConfigApi.Models;
using System.Text.Json;

namespace ConfigApi.Controllers;

public class HomeController : Controller
{
    private readonly IConfigurationService _configurationService;
    private readonly ILogger<HomeController> _logger;
    private readonly string _loginFilePath;
    private static readonly object _fileLock = new object();

    public HomeController(IConfigurationService configurationService, ILogger<HomeController> logger, IWebHostEnvironment env)
    {
        _configurationService = configurationService;
        _logger = logger;
        _loginFilePath = Path.Combine(env.ContentRootPath, "login.json");
    }

    public IActionResult Index()
    {
        _logger.LogInformation("Loading home page");
        
        return View();
    }

    public async Task<IActionResult> Settings()
    {
        _logger.LogInformation("Loading settings page with settings list");
        
        var settings = await _configurationService.GetAllSettingsAsync();
        
        return View(settings);
    }

    public async Task<IActionResult> AzureLogin()
    {
        _logger.LogInformation("Loading Azure login page");

        var viewModel = new AzureLoginViewModel
        {
            LoginEntries = await GetLoginEntriesAsync()
        };

        return View(viewModel);
    }

    [HttpPost]
    public async Task<IActionResult> AzureLogin(string claimedByName)
    {
        _logger.LogInformation("Processing Azure login claim for {ClaimedBy}", claimedByName);

        if (string.IsNullOrWhiteSpace(claimedByName))
        {
            ModelState.AddModelError("ClaimedByName", "Please enter your name");
            var viewModel = new AzureLoginViewModel
            {
                LoginEntries = await GetLoginEntriesAsync(),
                ClaimedByName = claimedByName
            };
            return View(viewModel);
        }

        try
        {
            var assignedLogin = await AssignLoginAsync(claimedByName);
            
            var resultViewModel = new AzureLoginViewModel
            {
                LoginEntries = await GetLoginEntriesAsync(),
                ClaimedByName = claimedByName,
                AssignedLogin = assignedLogin
            };

            if (assignedLogin == null)
            {
                ModelState.AddModelError("", "No available login credentials. All logins have been claimed or an error occurred during assignment.");
            }

            return View(resultViewModel);
        }
        catch (InvalidOperationException ex)
        {
            _logger.LogWarning(ex, "Login assignment failed for {ClaimedBy}", claimedByName);
            ModelState.AddModelError("", ex.Message);
            
            var viewModel = new AzureLoginViewModel
            {
                LoginEntries = await GetLoginEntriesAsync(),
                ClaimedByName = claimedByName
            };
            return View(viewModel);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unexpected error during login assignment for {ClaimedBy}", claimedByName);
            ModelState.AddModelError("", "An unexpected error occurred. Please try again or contact support.");
            
            var viewModel = new AzureLoginViewModel
            {
                LoginEntries = await GetLoginEntriesAsync(),
                ClaimedByName = claimedByName
            };
            return View(viewModel);
        }
    }

    private async Task<List<LoginEntry>> GetLoginEntriesAsync()
    {
        try
        {
            if (!System.IO.File.Exists(_loginFilePath))
            {
                return new List<LoginEntry>();
            }

            var jsonContent = await System.IO.File.ReadAllTextAsync(_loginFilePath);
            var entries = JsonSerializer.Deserialize<List<dynamic>>(jsonContent) ?? new List<dynamic>();
            
            return entries.Select(entry => 
            {
                var jsonElement = (JsonElement)entry;
                return new LoginEntry
                {
                    LoginEmail = jsonElement.GetProperty("loginemail").GetString() ?? "",
                    LoginPassword = jsonElement.GetProperty("loginpassword").GetString() ?? "",
                    ClaimedBy = jsonElement.TryGetProperty("claimedby", out var claimedBy) && claimedBy.ValueKind != JsonValueKind.Null 
                        ? claimedBy.GetString() : null
                };
            }).ToList();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error reading login entries");
            return new List<LoginEntry>();
        }
    }

    private async Task<LoginEntry?> AssignLoginAsync(string claimedByName)
    {
        // Use lock to ensure thread-safety for concurrent requests
        return await Task.Run(() =>
        {
            lock (_fileLock)
            {
                try
                {
                    _logger.LogDebug("Acquiring file lock for login assignment to {ClaimedBy}", claimedByName);

                    // Check if user already has a claimed login
                    var existingEntries = GetLoginEntriesSync();
                    var existingClaim = existingEntries.FirstOrDefault(e => 
                        !string.IsNullOrEmpty(e.ClaimedBy) && 
                        string.Equals(e.ClaimedBy, claimedByName, StringComparison.OrdinalIgnoreCase));
                    
                    if (existingClaim != null)
                    {
                        _logger.LogWarning("User {ClaimedBy} already has a claimed login: {Email}", claimedByName, existingClaim.LoginEmail);
                        throw new InvalidOperationException($"You already have a login assigned: {existingClaim.LoginEmail}");
                    }

                    // Find first available entry
                    var availableEntry = existingEntries.FirstOrDefault(e => string.IsNullOrEmpty(e.ClaimedBy));
                    
                    if (availableEntry == null)
                    {
                        _logger.LogWarning("No available login entries for {ClaimedBy}", claimedByName);
                        return null;
                    }

                    // Assign the login
                    availableEntry.ClaimedBy = claimedByName;

                    // Convert back to original format for JSON serialization
                    var jsonEntries = existingEntries.Select(e => new
                    {
                        loginemail = e.LoginEmail,
                        loginpassword = e.LoginPassword,
                        claimedby = e.ClaimedBy
                    }).ToList();

                    var jsonContent = JsonSerializer.Serialize(jsonEntries, new JsonSerializerOptions { WriteIndented = true });
                    
                    // Write to file with retry mechanism
                    var maxRetries = 3;
                    var retryCount = 0;
                    
                    while (retryCount < maxRetries)
                    {
                        try
                        {
                            System.IO.File.WriteAllText(_loginFilePath, jsonContent);
                            break;
                        }
                        catch (IOException ex) when (retryCount < maxRetries - 1)
                        {
                            _logger.LogWarning(ex, "File write attempt {RetryCount} failed, retrying...", retryCount + 1);
                            retryCount++;
                            Thread.Sleep(100); // Wait 100ms before retry
                        }
                    }

                    _logger.LogInformation("Successfully assigned login {Email} to {ClaimedBy}", availableEntry.LoginEmail, claimedByName);
                    return availableEntry;
                }
                catch (InvalidOperationException)
                {
                    throw; // Re-throw validation exceptions
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Error assigning login for {ClaimedBy}", claimedByName);
                    throw new InvalidOperationException("Failed to assign login due to a system error. Please try again.");
                }
            }
        });
    }

    private List<LoginEntry> GetLoginEntriesSync()
    {
        try
        {
            if (!System.IO.File.Exists(_loginFilePath))
            {
                _logger.LogWarning("Login file not found: {FilePath}", _loginFilePath);
                return new List<LoginEntry>();
            }

            var jsonContent = System.IO.File.ReadAllText(_loginFilePath);
            var entries = JsonSerializer.Deserialize<List<dynamic>>(jsonContent) ?? new List<dynamic>();
            
            return entries.Select(entry => 
            {
                var jsonElement = (JsonElement)entry;
                return new LoginEntry
                {
                    LoginEmail = jsonElement.GetProperty("loginemail").GetString() ?? "",
                    LoginPassword = jsonElement.GetProperty("loginpassword").GetString() ?? "",
                    ClaimedBy = jsonElement.TryGetProperty("claimedby", out var claimedBy) && claimedBy.ValueKind != JsonValueKind.Null 
                        ? claimedBy.GetString() : null
                };
            }).ToList();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error reading login entries from file");
            throw new InvalidOperationException("Failed to read login entries. Please try again or contact support.");
        }
    }
}
