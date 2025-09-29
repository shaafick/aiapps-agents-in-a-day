---
title: "Speech Processing"
---

:::info TUTORIAL OVERVIEW
In this tutorial, you'll learn how to implement text-to-speech capabilities using Azure Speech Services to enhance accessibility and user experience.

**What you'll build:** A speech synthesis system that converts text to natural-sounding speech.

**What you'll learn:**
- Azure Speech Services integration
- Browser audio playback
- Accessibility considerations
- Speech synthesis customization
:::

## Learning Objectives

By the end of this tutorial, you will be able to:

1. Integrate Azure Speech Services for text-to-speech
2. Configure voice settings and output formats
3. Handle audio playback in web browsers
4. Implement accessibility features for diverse users

## Scenario

Your retail store wants to enhance accessibility and provide a more natural, engaging experience for customers. The goal is to implement text-to-speech (TTS) to improve efficiency and self-service capabilities, allowing shoppers to receive audio information about products, navigation, and promotions.

## Goal

Implement text-to-speech functionality that reduces reliance on staff while maintaining a personalized touch through natural-sounding voice interactions.

![Speech Challenge](images/challenge-4.png)

## Step-by-Step Implementation

### Step 1: Understanding Azure Speech Services

Azure Speech Services provides:
- High-quality neural voices
- Multiple languages and accents
- SSML (Speech Synthesis Markup Language) support
- Real-time and batch processing
- Customizable voice models

### Step 2: Examine the Speech Component

Navigate to `apps-chat\chatbot-frontend\pages\speech\Speech.tsx`. You'll find:
- A text input for content to be spoken
- A read button to trigger speech synthesis
- Placeholder for audio playback controls

### Step 3: Set Up Speech Configuration

Before implementing the speech API, you need to:
- Configure the Speech SDK
- Set up authentication with your Speech service
- Choose appropriate voice and language settings

```typescript
useEffect(() => {
    const speechConfig = SpeechConfig.fromSubscription(
        'YOUR_SPEECH_KEY', 
        'YOUR_REGION'
    );
    
    // Configure voice settings
    speechConfig.speechSynthesisVoiceName = 'en-US-AriaNeural';
    speechConfig.speechSynthesisOutputFormat = SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3;
    
    // Initialize synthesizer
    const synthesizer = new SpeechSynthesizer(speechConfig);
}, []);
```

### Step 4: Implement Speech Synthesis

Your task is to complete the `speechApi` function to:
- Convert text to speech using Azure Speech Services
- Handle the audio output appropriately
- Manage playback in the browser
- Provide user feedback during processing

#### Key Implementation Steps:
```typescript
async function speechApi(text: string): Promise<void> {
    return new Promise((resolve, reject) => {
        synthesizer.speakTextAsync(
            text,
            result => {
                // Handle successful synthesis
                // Play audio in browser
                resolve();
            },
            error => {
                // Handle errors
                reject(error);
            }
        );
    });
}
```

### Step 6: Solution Reference

<details>
<summary>View Complete Solution</summary>
<details>
<summary>Try implementing it yourself first!</summary>
<details>
<summary>Click to reveal the solution code</summary>

```typescript
import React, { useState, useEffect, useRef } from "react";
import { trackPromise } from "react-promise-tracker";
import { usePromiseTracker } from "react-promise-tracker";
import * as sdk from 'microsoft-cognitiveservices-speech-sdk';

const Page = () => {
    const { promiseInProgress } = usePromiseTracker();
    const [speechText, setSpeechText] = useState<string>("");
    const synthesizerRef = useRef<sdk.SpeechSynthesizer | null>(null);
    const speechConfigRef = useRef<sdk.SpeechConfig | null>(null);

    useEffect(() => {
        const speech_key = '<Speech_Service_API_Key>';
        const speech_region = 'eastus';
        
        speechConfigRef.current = sdk.SpeechConfig.fromSubscription(
            speech_key,
            speech_region
        );
        
        speechConfigRef.current.speechSynthesisVoiceName = 'en-US-AriaNeural';
        speechConfigRef.current.speechSynthesisOutputFormat = 
            sdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3;
        
        synthesizerRef.current = new sdk.SpeechSynthesizer(
            speechConfigRef.current
        );

        return () => {
            if (synthesizerRef.current) {
                synthesizerRef.current.close();
            }
        };
    }, []);

    async function process() {
        if (speechText && synthesizerRef.current) {
            trackPromise(speechApi(speechText));
        }
    }

    async function speechApi(text: string): Promise<void> {
        return new Promise((resolve, reject) => {
            if (!synthesizerRef.current) {
                reject(new Error('Speech synthesizer not initialized'));
                return;
            }

            synthesizerRef.current.speakTextAsync(
                text,
                result => {
                    if (result.reason === sdk.ResultReason.SynthesizingAudioCompleted) {
                        console.log('Speech synthesis completed');
                        // Audio is automatically played by the SDK
                        resolve();
                    } else {
                        reject(new Error('Speech synthesis failed'));
                    }
                },
                error => {
                    console.error('Speech synthesis error:', error);
                    reject(error);
                }
            );
        });
    }

    const updateText = (e: React.ChangeEvent<HTMLInputElement>) => {
        setSpeechText(e.target.value);
    };

    return (
        <div className="pageContainer">
            <h2>Speech</h2>
            <p>Enter text below to hear it spoken aloud using Azure Speech Services.</p>
            <div>
                <input 
                    type="text" 
                    placeholder="(enter some text to be read aloud)" 
                    value={speechText}
                    onChange={updateText}
                    style={{ width: '300px', marginRight: '10px' }}
                />
                <button onClick={process} disabled={!speechText || promiseInProgress}>
                    Read
                </button>
                <br />
                {promiseInProgress && <span>Processing speech...</span>}
            </div>
        </div>
    );
};

export default Page;
```

</details>
</details>
</details>


### Step 7: Testing it out

- Replace `<Speech_Service_API_Key>` placeholder value by looking up  https://aiaaa-s2-setting.azurewebsites.net
- Go to `apps-chat\chatbot-frontend` folder in terminal windows and run `npm run dev`
- Navigate to `Speech` page in the top navigation bar
- Type some texts into the input box
- Click `Read` to play the speech

## Real-World Applications

### Retail Environments
- Product information announcements
- Store navigation assistance
- Promotional content delivery
- Accessibility for visually impaired customers

### Customer Service
- Automated phone responses
- Kiosk voice guidance
- Multi-language support
- Queue management announcements

### E-learning and Training
- Course content narration
- Interactive tutorials
- Assessment feedback
- Language learning pronunciation

### Integration Opportunities

1. **Chatbot Integration**: Add voice responses to chat interactions
2. **Notification Systems**: Speak important alerts and updates
3. **Workflow Automation**: Voice-guided step-by-step processes
4. **Multilingual Support**: Combine with translation for global accessibility

## Additional Resources

- [Azure Speech Services Documentation](https://docs.microsoft.com/azure/cognitive-services/speech-service/)
- [Speech SDK for JavaScript](https://docs.microsoft.com/azure/cognitive-services/speech-service/quickstarts/setup-platform?pivots=programming-language-javascript)
- [SSML Reference](https://docs.microsoft.com/azure/cognitive-services/speech-service/speech-synthesis-markup)
- [Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/Understanding/)
