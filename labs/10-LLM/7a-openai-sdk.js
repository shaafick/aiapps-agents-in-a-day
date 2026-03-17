const { OpenAIClient, AzureKeyCredential } = require("@azure/openai");

const client = new OpenAIClient(
  "https://aiaaa-s2-openai.openai.azure.com/",
  new AzureKeyCredential("8d91f222533647a488602ebc75e7a180")
);

// Block Reference 1
// const chatResponse = client.getChatCompletions("gpt-4.1", [
//   { role: "user", content: "What are the different types of road bikes?" },
// ]);

// // Block Reference 2
// chatResponse
//   .then((result) => {
//     for (const choice of result.choices) {
//       console.log(choice.message.content);
//     }
//   })
//   .catch((err) => console.log(`Error: ${JSON.stringify(err)}`));

  // Block Reference 1
const chatResponse = client.getChatCompletions("gpt-4.1", [
  {
    role: "system",
    content:
      "You are a helpful, fun and friendly sales assistant for Contoso Bike Store, a bicycle and bicycle accessories store.",
  },
  { role: "user", content: "Do you sell bicycles?" },
]);