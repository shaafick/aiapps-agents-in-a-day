# AI Apps and Agents in a day (Setup)

## Provisioning Resources



## Deprovisioning Resources

- Go to Azure Portal and Entra -> Users. Search for login name starting with `lab`, select all items in the list and delete them. 

- Go to `infra` folder, check `entra-lab-deprovision-exec.ps1` script and run it. make sure to uncomment lines as required.

- Go to Azure Portal and Foundry. Purge all deleted resources for each subscription. 

- Go to Azure Portal and KeyVaule. Purge all deleted resources for each subscription. 

- Go to `labs\00-Setup` folder, use db-cleanup.js to remove participants database. keep the demo db `aiaaa_labdemo_66` for sample application.


