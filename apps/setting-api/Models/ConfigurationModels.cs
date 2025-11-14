namespace ConfigApi.Models;

public class Setting
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public string Value { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string Category { get; set; } = string.Empty;
    public bool Placeholder { get; set; }
}

public class SettingsRoot
{
    public List<Setting> Settings { get; set; } = new();
}

public class ConfigurationResponse
{
    public int Id { get; set; }
    public string Key { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string? Value { get; set; }
}

public class LoginEntry
{
    public string LoginEmail { get; set; } = string.Empty;
    public string LoginPassword { get; set; } = string.Empty;
    public string? ClaimedBy { get; set; }
    public string Region { get; set; } = string.Empty;
}

public class AzureLoginViewModel
{
    public List<LoginEntry> LoginEntries { get; set; } = new();
    public string ClaimedByName { get; set; } = string.Empty;
    public LoginEntry? AssignedLogin { get; set; }
}

public class LoginViewModel
{
    public string Password { get; set; } = string.Empty;
    public string? ErrorMessage { get; set; }
}