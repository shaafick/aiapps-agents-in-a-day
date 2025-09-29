---
title: "Computer Vision Analysis"
---

:::info TUTORIAL OVERVIEW
In this tutorial, you'll learn how to leverage GPT-4o's vision capabilities to analyze and extract information from images.

**What you'll build:** An image analysis system that can understand and describe visual content.

**What you'll learn:**
- GPT-4o vision API integration
- Image processing and base64 encoding
- Multi-modal AI interactions
- Vision-based business applications
:::

## Learning Objectives

By the end of this tutorial, you will be able to:

1. Integrate GPT-4o vision capabilities for image analysis
2. Handle image uploads and base64 encoding
3. Create multi-modal prompts combining text and images
4. Build practical vision-based business solutions

## Scenario

Your customer service team needs to process product images efficiently. The goal is to deliver a seamless and efficient customer service experience that enhances operational accuracy and accelerates processing times through automated image analysis.

## Goal

Leverage GPT-4o's vision capabilities for accurate analysis and verification of product photos. This reduces processing time while ensuring consistency and reliability in decision-making, ultimately enhancing the customer experience.

![Vision Challenge](images/challenge-3.png)

## Step-by-Step Implementation

### Step 1: Understanding GPT-4o Vision

GPT-4o with vision can:
- Analyze and describe images in detail
- Answer questions about visual content
- Identify objects, people, text in images
- Perform comparative analysis between images
- Extract structured data from visual information

### Step 2: Examine the Vision Component

Navigate to `/apps-chat/chatbot-frontend/src/pages/vision/Vision.tsx`. You'll find:
- An image upload input for local files
- A text input for questions about the image
- A describe button to trigger analysis
- Display areas for the uploaded image and AI response

### Step 3: Implement Image Processing

Before sending to the vision API, you need to:
- Handle file uploads
- Convert images to base64 format
- Validate image types and sizes
- Prepare multi-modal messages

#### Key Functions to Implement:

```typescript
function getBase64(event) {
    // TODO: Convert uploaded file to base64
    // 1. Get the selected file from the event
    // 2. Create a FileReader instance
    // 3. Read the file as data URL (base64)
    // 4. Handle success and error cases
}
```

### Step 4: Implement the Vision API

Your task is to complete the `visionApi` function to:
- Construct multi-modal messages with text and image
- Send requests to GPT-4o vision endpoint
- Handle the API response
- Extract and return the analysis results

#### Message Structure:
```typescript
const messages = [
    { "role": "system", "content": "You are a helpful assistant." },
    {
        "role": "user", 
        "content": [
            {
                "type": "text",
                "text": userQuestion
            },
            {
                "type": "image_url",
                "imageUrl": {
                    "url": base64ImageData
                }
            }
        ]
    }
];
```


### Step 5: Solution Reference

<details>
<summary>View Complete Solution</summary>
<details>
<summary>Try implementing it yourself first!</summary>
<details>
<summary>Click to reveal the solution code</summary>

```typescript
import React, { useState } from "react";
import { trackPromise } from "react-promise-tracker";
import { usePromiseTracker } from "react-promise-tracker";
import { OpenAIClient, AzureKeyCredential, Completions } from '@azure/openai';

const Page = () => {
    const { promiseInProgress } = usePromiseTracker();
    const [selectedImage, setSelectedImage] = useState<File | null>(null);
    const [imageBase64, setImageBase64] = useState<string>("");
    const [imageText, setImageText] = useState<string>();
    const [imageDesc, setImageDesc] = useState<string>("");

    async function process() {
        if (imageText != null) {
            trackPromise(
                visionApi(imageText, imageBase64)
            ).then((res) => {
                setImageDesc(res);
            })
        }
    }

    async function visionApi(text: string, image: string): Promise<string> {
        const messages = [
            { "role": "system", "content": "You are a helpful assistant." },
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text",
                        "text": text
                    },
                    {
                        "type": "image_url",
                        "imageUrl": {
                            "url": `${image}`
                        }
                    }
                ]
            }
        ];

        const options = {
            api_version: "2024-08-01-preview"
        };

        const openai_url = "https://aiaaa-s2-openai.openai.azure.com/";
        const openai_key = "<AZURE_OPENAI_API_KEY>";
        const client = new OpenAIClient(
            openai_url,
            new AzureKeyCredential(openai_key),
            options
        );

        const deploymentName = 'gpt-4o';
        const result = await client.getChatCompletions(deploymentName, messages, {
            maxTokens: 200,
            temperature: 0.25
        });
        
        return result.choices[0]?.message?.content ?? '';
    }

    function getBase64(event: Event) {
        const file = (event.target as HTMLInputElement).files?.[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = function () {
            setImageBase64(reader.result as string);
        };
        reader.onerror = function (error) {
            console.log('Error: ', error);
        };
    }

    const updateText = (e: React.ChangeEvent<HTMLInputElement>) => {
        setImageText(e.target.value);
    };

    return (
        <div className="pageContainer">
            <h2>Vision</h2>

            <div>
                <input
                    type="file"
                    name="myImage"
                    accept="image/*"
                    onChange={(event) => {
                        setSelectedImage(event.target.files?.[0] || null);
                        getBase64(event);
                    }}
                />
                <br />

                {selectedImage && (
                    <div>
                        <h4>Your Photo</h4>
                        <p>
                            <img
                                width={"400px"}
                                src={URL.createObjectURL(selectedImage)}
                                alt="Uploaded image"
                            />
                        </p>

                        <h4>Question</h4>
                        <input 
                            type="text" 
                            placeholder="(your question about the image)" 
                            onChange={updateText} 
                        />
                        <p>
                            <button onClick={() => process()}>Describe</button><br />
                            {promiseInProgress && <span>Loading...</span>}
                        </p>
                        <p>{imageDesc}</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Page;
```

</details>
</details>
</details>

### Step 5: Testing it out

- Replace `<AZURE_OPENAI_API_KEY>` placeholder value by looking up  https://aiaaa-s2-setting.azurewebsites.net
- Go to `apps-chat\chatbot-frontend` folder in terminal windows and run `npm run dev`
- Navigate to `Vision` page in the top navigation bar
- Click `Choose file` to select any image or photo
- Enter a question into the text box
- Click `Describe` button to see the answer


### Real-World Applications

### Quality Control
- Automated defect detection in manufacturing
- Product compliance verification
- Damage assessment for insurance claims

### Retail and E-commerce
- Product categorization and tagging
- Visual search implementations
- Inventory management automation

### Healthcare
- Medical image preliminary analysis
- Equipment monitoring and maintenance
- Document processing and digitization

### Security and Surveillance
- Incident detection and reporting
- Access control verification
- Safety compliance monitoring


### Integration Opportunities

Consider combining vision analysis with:

1. **Workflow Automation**: Trigger actions based on image content
2. **Database Integration**: Store analysis results for reporting
3. **Notification Systems**: Alert users to specific visual conditions
4. **ML Model Training**: Use results to improve custom models

## Additional Resources

- [GPT-4o Vision Documentation](https://docs.microsoft.com/azure/cognitive-services/openai/gpt-4-vision)
- [Computer Vision Best Practices](https://docs.microsoft.com/azure/cognitive-services/computer-vision/overview)
- [Image Processing Guidelines](https://docs.microsoft.com/azure/cognitive-services/openai/concepts/gpt-with-vision)
