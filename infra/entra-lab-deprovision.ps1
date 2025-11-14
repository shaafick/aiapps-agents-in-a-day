param (
    [string]$subscriptionId, # "xxxxx-xxxx-xxx-xxx",
    [string]$domain, # "xxx.com",
    [string]$labName,  # "lab3"
    [int]$startNumber = 200,
    [int]$endNumber = 0
)

az account set --subscription $subscriptionId

for ($i = $startNumber; $i -le $endNumber; $i++) {
    Write-Host "---------User--------------"

    $userSeq = $i
    $userName = "$($labName)user$($userSeq)"
    $rgName = "rg-$($userName)"

    az group delete --name $rgName --yes --no-wait
    Write-Host "Deleted resource group $rgName"

}