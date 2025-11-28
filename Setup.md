# AI Apps and Agents in a day (Setup)

## Provisioning Resources

- Go to `infra` folder, check `entra-lab-provision-exec.ps1` script and run it. make sure to uncomment lines as required.

- open `apps\setting-api` in VS Code, update the password value in `login.json` and deploy manually from VS Code. the app is hosted in insight demo tenant called `aiaaa-s2-setting`

## Deprovisioning Resources

- Go to Azure Portal and Entra -> Users. Search for login name starting with `lab`, select all items in the list and delete them. 

- Login to Azure CLI using `az login`. `az login --tenant f1146386-451a-4cc6-846b-a67f747921e9 --use-device-code`, sign in as `admin@aiapps.top`

- Go to `infra` folder, check `entra-lab-deprovision-exec.ps1` script and run it. make sure to uncomment lines as required.

- Go to Azure Portal and Foundry. Purge all deleted resources for each subscription. 

- Go to Azure Portal and KeyVaule. Purge all deleted resources for each subscription. 

- Go to `labs\00-Setup` folder, use db-cleanup.js to remove participants database. keep the demo db `aiaaa_labdemo_66` for sample application.


