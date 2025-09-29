# Build Chatbot Backend

The backend API is a Node.js web application, using Express and Swagger, that will expose endpoints for the frontend application to interact with. The backend API could be deployed as a web app on Azure App Service.

## Run the backend API locally

When developing a backend API, it is often useful to run the application locally to test and debug. This section outlines how to run the backend API locally while watching the file system for code changes. Any detected changes will automatically restart the backend API.

1. Open the backend API folder location in VS Code: `apps-chat/chatbot-backend`

2. Open a **Terminal** window in VS Code (<kbd>CTRL</kbd>+<kbd>`</kbd>).

3. Check that the `.env` file has correct configurations.  All placeholder strings should have been replaced in the earlier `Lab Setup` step.

## Add LangChain Agent to Backend API

1. In the previous task, we created a LangChain agent that is capable of generating responses using RAG. Now, let's integrate this code into our Backend API service.

2. Compare `labs\20-Chatbot\4b-agent.js` and `labs\20-Chatbot\4a-langchain-agent.js`. You will notice that additional code has been added to the function to manage chat history.

   ![alt text](images/chatbot-frontend-image-1.png)

3. The `agent.js` is used in `apps-chat/chatbot-backend/bikestore/agent.js` to enable the backend to connect to both CosmosDb and OpenAI service.

4. Take your time and have a look at these files:
   - `apps-chat\chatbot-backend\app.js` configures node.js app
   - `apps-chat\chatbot-backend\swagger.js` configures swagger
   - `apps-chat\chatbot-backend\bikestore\agent.js` contains Langchain agent logics


## Test out Backend API Swagger

1. Run the following command to install any dependencies:

   ```bash
   npm install
   ```

2. Run the following command to start the backend api.

   ```bash
   npm run dev
   ```

3. Open a browser and navigate to http://localhost:5000/docs to view the Swagger UI. If you are using `codespaces`, refer to the note below. In the newly opened browser, add `/docs` to the url in the address bar to open swagger interface.

   ![The Swagger UI displays for the locally running backend api](images/local_backend_swagger_ui.png "Local backend api Swagger UI")

   :::info
   If you are running the `codespaces` in web browser, please use the codespaces generated url. You shall see `Open in browser` button asking if you want to open the site in browser. If you missed the button, go to `PORTS` tab to find it. In the newly opened browser, add `/docs` to the url in the address bar to open swagger interface.

   The URL would look similar to: https://ominous-space-goldfish-v6vv749557wjfxj99-5000.app.github.dev/docs/

   Additionally, please also make the `Visibility` of the site to `Public` as shown in below screenshot. This is to allow frontend to access the API backend later.

   ![Codespaces Visibility](images/backend-codespaces-port.png)
   :::


4. Expand the **GET / Root** endpoint and select **Try it out**. Select **Execute** to send the request. The response should display a status of `ready`.

   ![The Swagger UI displays the GET / Root endpoint response that has a status of ready.](images/local_backend_swagger_ui_root_response.png "Local backend api Swagger UI Root response")

5. Expand the **POST /ai** endpoint and select **Try it out**. In the **Request body** field, enter the following JSON.

   ```json
   {
     "session_id": "abc123",
     "prompt": "hello, how are you"
   }
   ```

6. Select **Execute** to send the request. 

   ![The Swagger UI displays the POST /ai endpoint response that has a status of ready.](images/local_backend_swagger_ui_ai_response.png "Local backend api Swagger UI AI response")

7. Please keep the backend running.
