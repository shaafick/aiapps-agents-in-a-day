param (
    [string]$subscriptionId, # "xxxxx-xxxx-xxx-xxx",
    [string]$domain, # "xxx.com",
    [string]$labName,  # "lab3"
    [int]$startNumber = 200,
    [int]$endNumber = 0
)

# az login --tenant f1146386-451a-4cc6-846b-a67f747921e9

# sub-aiaaa-lab1
# .\entra-lab-provision.ps1 ba15181f-9a45-4eff-9043-4ddf263b6dc2 aiapps.top lab1 310 319

# sub-aiaaa-lab2
# .\entra-lab-provision.ps1 22f484c3-b754-45aa-8cec-e40bb48bcb34 aiapps.top lab2 320 329

# sub-aiaaa-lab3
# .\entra-lab-provision.ps1 bb2b6250-daa2-4e16-8387-2fa677dc4d7f aiapps.top lab3 330 339

# sub-aiaaa-lab4
# .\entra-lab-provision.ps1 ac5c4d49-95c6-4b65-a273-5e3e562e7544 aiapps.top lab4 340 349

# sub-aiaaa-lab5
# .\entra-lab-provision.ps1 bfa1eb08-61a0-41d1-99ef-f02f3286f537 aiapps.top lab5 350 359





az account set --subscription $subscriptionId

$EntraIdGroupName = "aad-$labName"

Write-Host "---------Lab--------------"
$existingGroup = az ad group show --group $EntraIdGroupName 2>$null
if ($existingGroup) {
    Write-Host "AAD group $EntraIdGroupName already exists"
} else {
    az ad group create --display-name $EntraIdGroupName --mail-nickname $EntraIdGroupName > $null
    Write-Host "Created AAD group $EntraIdGroupName"
}

# $rgSharedName = "rg-$($labName)"
# $rgExists = az group exists --name $rgSharedName
# if ($rgExists -eq "false") {
#     az group create --name $rgSharedName --location australiaeast > $null
#     Write-Host "Created shared resource group $rgSharedName"
# } else {
#     Write-Host "Shared resource group $rgSharedName already exists"
# }

for ($i = $startNumber; $i -le $endNumber; $i++) {
    Write-Host "---------User--------------"

    $userSeq = $i
    $userName = "$($labName)user$($userSeq)"
    $userEmail = "$($userName)@$($domain)"
    $rgName = "rg-$($userName)"
    
    $existingUser = az ad user show --id $userEmail 2>$null
    if ($existingUser) {
        Write-Host "User $userName already exists"
    } else {
        az ad user create --display-name $userName --password Password123456 --user-principal-name $userEmail --force-change-password-next-sign-in false > $null
        Write-Host "Created user $userName"
    }

    $userId = $(az ad user show --id $userEmail --query id -o tsv)
    az ad group member add --group $EntraIdGroupName --member-id $userId > $null
    Write-Host "Added user $userName to AAD group $EntraIdGroupName"

    az group create --name $rgName --location australiaeast > $null
    Write-Host "Created resource group $rgName"

    # Assign Contributor role to the user for the resource group
    $rgId = $(az group show --name $rgName --query id -o tsv)
    az role assignment create --assignee $userId --role 'Azure AI Developer' --scope $rgId > $null
    az role assignment create --assignee $userId --role 'Azure AI User' --scope $rgId > $null
    az role assignment create --assignee $userId --role 'Contributor' --scope $rgId > $null
    Write-Host "Assigned roles to user $userName for resource group $rgName"
}