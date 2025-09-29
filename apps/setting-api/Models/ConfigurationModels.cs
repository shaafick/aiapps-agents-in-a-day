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