const { OpenAIClient, AzureKeyCredential } = require("@azure/openai");

const client = new OpenAIClient(
  "https://aiaaa-s2-openai.openai.azure.com/",
  new AzureKeyCredential("8d91f222533647a488602ebc75e7a180")
);