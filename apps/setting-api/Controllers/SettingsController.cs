using Microsoft.AspNetCore.Mvc;
using ConfigApi.Services;
using ConfigApi.Models;
using System.Linq;

namespace ConfigApi.Controllers;

[ApiController]
[Route("api/[controller]")]
public class SettingsController : ControllerBase
{
    private readonly IConfigurationService _configurationService;
    private readonly ILogger<SettingsController> _logger;

    public SettingsController(IConfigurationService configurationService, ILogger<SettingsController> logger)
    {
        _configurationService = configurationService;
        _logger = logger;
    }

    /// <summary>
    /// Get all settings
    /// </summary>
    /// <returns>List of all settings</returns>
    [HttpGet]
    public async Task<IActionResult> GetAllSettings()
    {
        _logger.LogInformation("Retrieving all settings");

        var allSettings = await _configurationService.GetAllSettingsAsync();
        var settings = allSettings.Where(r => r.Placeholder).ToList();
        
        return Ok(new { 
            count = settings.Count,
            settings = settings 
        });
    }

    /// <summary>
    /// Get a specific setting by ID
    /// </summary>
    /// <param name="id">The setting ID to retrieve</param>
    /// <returns>Setting with the specified ID</returns>
    [HttpGet("{id}")]
    public async Task<IActionResult> GetSetting(string id)
    {
        if (string.IsNullOrWhiteSpace(id))
        {
            return BadRequest(new { error = "ID parameter is required" });
        }

        _logger.LogInformation("Retrieving setting with ID: {Id}", id);

        var setting = await _configurationService.GetSettingAsync(id);
        
        if (setting == null)
        {
            return NotFound(new { error = $"Setting with ID '{id}' not found" });
        }

        return Ok(setting);
    }
}
