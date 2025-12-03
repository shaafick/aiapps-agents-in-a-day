# AI Apps and Agents in a day (Setup)

## Provisioning Resources

- Go to `infra` folder, check `entra-lab-provision-exec.ps1` script and run it. make sure to uncomment lines as required.

![](res\script-provision.png)

- open `apps\setting-api` in VS Code, update the password value in `login.json`, also fill in the api keys inside `setting.json` 

```
Azure OpenAI API Key
AZURE_OPENAI_API_KEY
MONGODB_CONNECTION_STRING
GPT-4o API Key
Dall-e 3 API Key
Computer Vision API Key
Translator Service API Key
Speech Service API Key
```

- deploy `apps\setting-api` manually from VS Code. the app is hosted in insight demo tenant called `aiaaa-s2-setting`. 

![](res\deploy-setting.png)

- Test the api keys are working for various labs, also test setting app is working. https://aiaaa-s2-setting.azurewebsites.net/Home/Settings

![](res\test-setting.png)

## Deprovisioning Resources

- Go to Azure Portal and Entra -> Users. Search for login name starting with `lab`, select all items in the list and delete them. 

![](res\delete-login.png)

- Login to Azure CLI using `az login`. `az login --tenant f1146386-451a-4cc6-846b-a67f747921e9 --use-device-code`, sign in as `admin@aiapps.top`

- Go to `infra` folder, check `entra-lab-deprovision-exec.ps1` script and run it. make sure to uncomment lines as required.

![](res\script-deprovision.png)

- Go to Azure Portal and Foundry. Purge all deleted resources for each subscription. 

![](res\purge-foundry.png)

- Go to Azure Portal and KeyVault. Purge all deleted resources for each subscription. 

![](res\purge-kv.png)

- Go to `labs\00-Setup` folder, use db-cleanup.js to remove participants database. keep the demo db `aiaaa_labdemo_66` for sample application.

- Copy the output statement and appended to .js file and run again to clean up databases. (exclude aiaaa_labdemo_66)

![](res\cosmos-db-delete.png)
