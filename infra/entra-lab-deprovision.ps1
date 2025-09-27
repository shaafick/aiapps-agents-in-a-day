param (
    [string]$subscriptionId, # "xxxxx-xxxx-xxx-xxx",
    [string]$domain, # "xxx.com",
    [string]$labName,  # "lab3"
    [int]$startNumber = 200,
    [int]$endNumber = 0
)

# az login --tenant f1146386-451a-4cc6-846b-a67f747921e9

# sub-aiaaa-lab1
# .\entra-lab-deprovision.ps1 ba15181f-9a45-4eff-9043-4ddf263b6dc2 aiapps.top lab1 310 319

# sub-aiaaa-lab2
# .\entra-lab-deprovision.ps1 22f484c3-b754-45aa-8cec-e40bb48bcb34 aiapps.top lab2 320 329

# sub-aiaaa-lab3
# .\entra-lab-deprovision.ps1 bb2b6250-daa2-4e16-8387-2fa677dc4d7f aiapps.top lab3 330 339

# sub-aiaaa-lab4
# .\entra-lab-deprovision.ps1 ac5c4d49-95c6-4b65-a273-5e3e562e7544 aiapps.top lab4 340 349

# sub-aiaaa-lab5
# .\entra-lab-deprovision.ps1 bfa1eb08-61a0-41d1-99ef-f02f3286f537 aiapps.top lab5 350 359


az account set --subscription $subscriptionId

for ($i = $startNumber; $i -le $endNumber; $i++) {
    Write-Host "---------User--------------"

    $userSeq = $i
    $userName = "$($labName)user$($userSeq)"
    $rgName = "rg-$($userName)"

    az group delete --name $rgName --yes --no-wait
    Write-Host "Deleted resource group $rgName"

}