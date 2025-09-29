---
title: "Multilingual Translation Services"
---

:::info TUTORIAL OVERVIEW
In this tutorial, you'll learn how to build a multilingual translation feature using Azure Translator services.

**What you'll build:** A translation system that converts customer reviews from various languages to English.

**What you'll learn:**
- Azure Translator service integration
- RESTful API implementation
- Language detection capabilities
- Error handling for translation services
:::

## Learning Objectives

By the end of this tutorial, you will be able to:

1. Integrate Azure Translator service with REST APIs
2. Implement automatic language detection
3. Handle translation errors gracefully
4. Build responsive translation UI components

## Scenario

Your company receives customer reviews in multiple languages, and you need to extract meaningful insights from this multilingual feedback. The goal is to leverage translation services to interpret customer feedback across various languages, enabling efficient summarization and analysis for data-driven decision-making.

## Goal

Build a feature that takes non-English customer reviews and translates them to English, allowing your team to understand and respond to global customer feedback effectively.

![Translation Challenge](images/challenge-2.png)

## Step-by-Step Implementation

### Step 1: Understanding Azure Translator

Azure Translator is a cloud-based machine translation service that supports:
- Real-time text translation
- Automatic language detection
- Over 100 supported languages
- Custom translation models

### Step 2: Examine the Translation Component

Navigate to `apps-chat\chatbot-frontend\pages\translation\Translation.tsx`. You'll find:
- An input field for original text
- A translate button
- A display area for translated results

### Step 3: Implement the Translation API

Your task is to complete the `translationApi` function to:
- Send text to Azure Translator service
- Handle the REST API response
- Extract translated text from the response
- Manage errors and edge cases

:::note Language Configuration
**Important**: Make sure to adjust the `from` and `to` language parameters in the translation URL according to your needs:
- `from=en` (source language: English)
- `to=fr` (target language: French)
- You can change these to any supported language codes (es, de, it, etc.)
- Remove the `from` parameter to enable automatic language detection
:::

#### Key Requirements:
- Use Azure Translator REST API
- Configure proper endpoints and API keys
- Handle language detection automatically
- Parse JSON responses correctly

### Step 4: Code Implementation

Here's the structure you need to implement:

```typescript
async function translationApi(text: string): Promise<string> {
    // TODO: Implement translation API call
    // 1. Set up the translation endpoint URL
    // 2. Configure headers with API key and region
    // 3. Prepare the request body with text to translate
    // 4. Make the POST request to Azure Translator
    // 5. Parse response and extract translated text
    // 6. Handle errors appropriately
}
```


### Step 5: Code Solution

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

const Page = () => {
    const { promiseInProgress } = usePromiseTracker();
    const [originalText, setOriginalText] = useState<string>();
    const [translatedText, setTranslatedText] = useState<string>("");

    async function process() {
        if (originalText != null) {
            trackPromise(
                translationApi(originalText)
            ).then((res) => {
                setTranslatedText(res);
            })
        }
    }

    async function translationApi(text: string): Promise<string> {
        const translation_url = `https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to=en&from=fr`;
        const translation_key = "<Translator_Service_API_Key>";

        const body = [{
            "text": `${text}`
        }];

        const response = await fetch(translation_url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Ocp-Apim-Subscription-Region": "eastus",
                "Ocp-Apim-Subscription-Key": translation_key,
            },
            body: JSON.stringify(body),
        });
        
        const data = await response.json();
        return data[0].translations[0].text;
    }

    const updateText = (e: React.ChangeEvent<HTMLInputElement>) => {
        setOriginalText(e.target.value);
    };

    return (
        <div className="pageContainer">
            <h2>Translation</h2>
            <p></p>
            <p>
                <input type="text" placeholder="(enter text in English to translate to French)" onChange={updateText} />
                <button onClick={() => process()}>Translate</button><br />
                {
                    (promiseInProgress === true) ?
                        <span>Loading...</span>
                        :
                        null
                }
            </p>
            <p>
                {translatedText}
            </p>
        </div>
    );
};

export default Page;
```

</details>
</details>
</details>


### Step 6: Testing Your Implementation

- Replace `<Translator_Service_API_Key>` placeholder value by looking up  https://aiaaa-s2-setting.azurewebsites.net
- Go to `apps-chat\chatbot-frontend` folder in terminal windows and run `npm run dev`
- Navigate to `Translation` page in the top navigation bar
- Test with different languages (French, Spanish, German, etc.)
- Try complex sentences with technical terms
- Test with mixed-language content
- Verify error handling with invalid input

#### Integration Ideas

Consider integrating this translation feature with:

1. **Customer Support Systems**: Automatically translate support tickets
2. **Content Management**: Translate website content for global audiences
3. **Social Media Monitoring**: Analyze international brand mentions
4. **E-commerce Reviews**: Understand global customer feedback

## Additional Resources

- [Azure Translator Documentation](https://docs.microsoft.com/azure/cognitive-services/translator/)
- [Translator REST API Reference](https://docs.microsoft.com/azure/cognitive-services/translator/reference/v3-0-reference)
- [Language Support Matrix](https://docs.microsoft.com/azure/cognitive-services/translator/language-support)
