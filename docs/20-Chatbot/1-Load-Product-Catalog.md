# Load Product Catalog

:::tip Azure Cosmos DB

Azure Cosmos DB is a globally distributed, multi-model database service for any scale. The Azure Cosmos DB for MongoDB supports Vector Search, which allows you to search for documents based on their similarity to a query document.

:::

In this lab, you will load the product catalog data into Azure Cosmos DB. The product catalog will be used by the chatbot to answer questions related to the products in the catalog.

The product catalog data is provided in a CSV file. You will be writing a custom script to convert the CSV file to JSON format and then load the JSON data into the Cosmos DB.

![RAG](images/rag_design_data_ingestion.png)

## Setup the lab environment

1. Open repo in `VS Code` and then open `Terminal` -> `New Terminal`. Navigate to the lab folder `~/labs/20-Chatbot/` within the repository.

   ```bash
   cd labs/20-Chatbot
   ```

:::info
The `~/labs/20-Chatbot/completed` folder contains the completed solution for this lab. Please use `start` folder to carry out the exercise. You can compare your code with the files in `completed` folder if your code does not run correctly.
:::

2. Check `.env` file has correct configurations. Placeholder string should be all replaced in earlier `Lab Setup` step.

3. To install the required packages, execute the following command in the terminal window:

   ```bash
   npm install
   ```

## Prepare the data set

The quality of the dataset feeding into the LLM model makes a big difference. While it is typically the responsibility of the data team, there may be various conversions and integrations required to format the dataset. Let's take a look at the product dataset and see if any modifications are needed before loading it into Cosmos DB.

The `product` data set is located in the `data/product.csv` file. It has the following fields: `id`,`categoryId`,`categoryName`,`sku`,`name`,`description`,`price`,`tags`. The `tags` field is a JSON array of strings.

1. Here is a snapshot of the `product.csv` file:

   ![alt text](images/rag_load_data_image.png)

2. The `1a-convert.js` file already contains the complete code to convert the CSV file to JSON format and fix data type issues. The file includes proper handling for:
   - Parsing the CSV file format
   - Converting the tags field from JSON strings
   - Converting the price field to a proper float value

3. Run the conversion script to generate the `product.json` file:

   ```bash
   node 1a-convert.js
   ```

4. Open the generated `product.json` file to verify the data has been correctly formatted:
   ![alt text](images/rag_load_data_image-1.png)

   Notice that the `price` field is now a proper number (not a string) and the tags field has been correctly parsed as a JSON array.

## Bulk load product data

There are multiple options available for performing bulk operations in Cosmos DB. In this section, we will focus on using the `bulkWrite` method. The `bulkWrite` method allows you to execute multiple write operations in a single batch, including insert, update, and delete operations.

1. Open the `1b-import.js` file. You'll see it already has the basic MongoDB connection setup. Now add the following code block where indicated by the `TODO: Add product data loading code here` comment:

   ```javascript
   // Load product data
   console.log("Loading product data");
   // Initialize the product collection pointer (will automatically be created if it doesn't exist)
   const productCollection = db.collection("products");

   // Define the path to the local JSON file
   const jsonFilePath = path.join("data", "product.json");

   // Read the JSON file
   const productRawData = fs.readFileSync(
     path.join("data", "product.json"),
     "utf8"
   );
   const productData = JSON.parse(productRawData).map((prod) =>
     cleanData(prod)
   );

   // Delete any existing products
   console.log("Deleting existing products");
   await productCollection.deleteMany({});

   var result = await productCollection.bulkWrite(
     productData.map((product) => ({
       insertOne: {
         document: product,
       },
     }))
   );
   console.log(`${result.insertedCount} products inserted`);
   ```

2. Now add the following code for loading customer and sales data where indicated by the `TODO: Add customer and sales data loading code here` comment:

   ```javascript
   // Load customer and sales data
   console.log("Retrieving combined Customer/Sales data");
   const customerCollection = db.collection("customers");
   const salesCollection = db.collection("sales");

   const custSalesRawData = fs.readFileSync(
     path.join("data", "custSalesData.json"),
     "utf8"
   );
   const custSalesData = JSON.parse(custSalesRawData).map((custSales) =>
     cleanData(custSales)
   );

   console.log("Split customer and sales data");
   const customerData = custSalesData.filter(
     (cust) => cust["type"] === "customer"
   );
   const salesData = custSalesData.filter(
     (sales) => sales["type"] === "salesOrder"
   );
   
   console.log("Loading customer data");
   await customerCollection.deleteMany({});
   result = await customerCollection.insertMany(customerData);
   console.log(`${result.insertedCount} customers inserted`);
   
   console.log("Loading sales data");
   await salesCollection.deleteMany({});
   result = await salesCollection.insertMany(salesData);
   console.log(`${result.insertedCount} sales inserted`);
   ```

3. Save the `1b-import.js` file.

4. Run the application by executing the following command in the terminal window:

   ```bash
   node 1b-import.js
   ```
   ![A console window displays indicating customers and sales have been inserted into the customers and sales collections](images/rag_load_data_prod_cust_sales_loaded.png "Customers and sales loaded")

   :::tip
   We reduced the total products in the data set from 295 to only 49 in the end. Do you know why?
   :::   

## Browse the data in the Cosmos DB

1. If you are using VS Code locally, please install MongoDb extension, search  `MongoDB for VS code` in `Extensions` tab. If you are using GitHub Codespaces, extension is already installed.

   ![alt text](images/rag_load_data_image-6.png)

2. Locate `MongoDb` extension icon in the left navigation bar, it looks like a leaf icon. Once opened, let's add a connection to the database. Please find db connection string on https://aiaaa-s2-setting.azurewebsites.net (MONGODB_CONNECTION_STRING).  Click on `Connect` icon, copy CosmosDb connection string to the top textbox in VS Code. 

   ![alt text](images/rag_load_data_image-2.png)

3. Click on the first item in the `Connections` tab, and locate your own database. Then you can browse the json records in the `product` and `customer` table by expending it.

   ![alt text](images/rag_load_data_image-7.png)

In this section, we used bulk load operations to load `product`, `customer`, and `sales` data into Cosmos DB. We also had to cleanup the data before loading it into the database. In the next section, we will convert the data into embeddings and perform vector search on the data.
