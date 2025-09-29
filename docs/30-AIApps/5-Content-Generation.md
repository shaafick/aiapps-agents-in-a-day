---
title: "Content Generation"
---

:::info TUTORIAL OVERVIEW
In this tutorial, you'll learn how to build an automated SEO content generation system that analyzes web pages and creates optimized content.

**What you'll build:** A web scraping and content analysis tool that generates SEO-optimized metadata.

**What you'll learn:**
- Web scraping and HTML parsing
- AI-powered content analysis
- SEO optimization techniques
- Structured data generation
:::

## Learning Objectives

By the end of this tutorial, you will be able to:

1. Implement web scraping to extract page content
2. Process HTML and convert it to analyzable text
3. Use AI to generate Search engine optimized (SEO) content
4. Create structured metadata for search engines

## Scenario

Your marketing team needs to improve website traffic and search engine rankings. The goal is to automate the creation of SEO-optimized content by analyzing existing web pages and generating relevant keywords, compelling titles, and effective meta tags to enhance online visibility.

## Goal

Build a system that can automatically retrieve web page content, analyze it for SEO opportunities, and generate optimized metadata that drives organic growth through improved search engine rankings.

![SEO Challenge](images/challenge-5.png)

## Step-by-Step Implementation

### Step 1: Understanding SEO Fundamentals

Key SEO elements to generate:
- **Title Tags**: Compelling, keyword-rich page titles
- **Meta Descriptions**: Concise, engaging summaries
- **Keywords**: Relevant search terms and phrases
- **Header Structure**: Organized content hierarchy
- **Schema Markup**: Structured data for search engines

### Step 2: Examine the SEO Component

Navigate to `apps-chat\chatbot-frontend\pages\seo\Seo.tsx`. You'll find:
- A URL input field for target web pages
- A generate button to trigger analysis
- A display area for generated SEO content
- Test URL: `http://localhost:4000/product.html`

### Step 3: Implement Web Content Extraction

Your first task is to retrieve and process web page content:

```typescript
async function extractWebContent(url: string): Promise<string> {
    // TODO: Implement web content extraction
    // 1. Fetch the HTML content from the URL
    // 2. Parse and clean the HTML
    // 3. Extract meaningful text content
    // 4. Remove scripts, styles, and navigation elements
    // 5. Return clean text for analysis
}
```

### Step 4: HTML Processing and Cleaning

Process the raw HTML to extract meaningful content:

```typescript
function cleanHtmlContent(html: string): string {
    // Remove script and style elements
    // Extract text from important elements (h1, h2, p, etc.)
    // Clean up whitespace and formatting
    // Return structured text content
}
```

### Step 5: AI-Powered SEO Analysis

Implement the core SEO generation function:

```typescript
async function seoApi(url: string): Promise<string> {
    // TODO: Complete SEO analysis implementation
    // 1. Extract web page content
    // 2. Prepare analysis prompt for AI
    // 3. Call Azure OpenAI for content analysis
    // 4. Generate structured SEO metadata
    // 5. Return formatted JSON response
}
```


### Step 6: Code Solution

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
import { OpenAIClient, AzureKeyCredential } from '@azure/openai';

const Page = () => {
    const { promiseInProgress } = usePromiseTracker();
    const [seoUrl, setSeoUrl] = useState<string>("");
    const [seoText, setSeoText] = useState<string>("");

    async function process() {
        if (seoUrl) {
            trackPromise(
                seoApi(seoUrl)
            ).then((res) => {
                setSeoText(res);
            }).catch((error) => {
                console.error('SEO analysis failed:', error);
                setSeoText('Error analyzing the webpage. Please check the URL and try again.');
            });
        }
    }

    async function seoApi(url: string): Promise<string> {
        try {
            // Fetch webpage content
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const html = await response.text();
            
            // Clean and extract meaningful content
            const cleanContent = cleanHtmlContent(html);
            
            // Prepare AI prompt for SEO analysis
            const messages = [
                { 
                    "role": "system", 
                    "content": `You are an SEO expert. Analyze the provided HTML content and generate SEO-optimized metadata. 
                    Return a valid JSON object with the following structure:
                    {
                        "seoTitle": "compelling page title (50-60 characters)",
                        "seoDescription": "engaging meta description (150-160 characters)",
                        "seoKeywords": ["keyword1", "keyword2", "keyword3"],
                        "focusKeyword": "primary keyword",
                        "suggestions": ["improvement suggestion 1", "suggestion 2"]
                    }
                    
                    Ensure the output is valid JSON format only.`
                },
                {
                    "role": "user", 
                    "content": `Analyze this webpage content and generate SEO metadata:\n\n${cleanContent}`
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
                maxTokens: 500,
                temperature: 0.3
            });

            return result.choices[0]?.message?.content ?? 'No SEO analysis generated';
        } catch (error) {
            console.error('Error in seoApi:', error);
            throw error;
        }
    }

    function cleanHtmlContent(html: string): string {
        // Create a temporary DOM element to parse HTML
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        
        // Remove script and style elements
        const scripts = doc.querySelectorAll('script, style');
        scripts.forEach(el => el.remove());
        
        // Extract text from important elements
        const title = doc.querySelector('title')?.textContent || '';
        const headings = Array.from(doc.querySelectorAll('h1, h2, h3, h4, h5, h6'))
            .map(el => el.textContent).join(' ');
        const paragraphs = Array.from(doc.querySelectorAll('p'))
            .map(el => el.textContent).join(' ');
        const metaDescription = doc.querySelector('meta[name="description"]')?.getAttribute('content') || '';
        
        // Combine and clean content
        const content = `Title: ${title}\nHeadings: ${headings}\nContent: ${paragraphs}\nMeta Description: ${metaDescription}`;
        
        // Clean whitespace and return
        return content.replace(/\s+/g, ' ').trim();
    }

    const updateText = (e: React.ChangeEvent<HTMLInputElement>) => {
        setSeoUrl(e.target.value);
    };

    return (
        <div className="pageContainer">
            <h2>SEO Content Generator</h2>
            <p>
                Analyze web pages and generate SEO-optimized content automatically.
                <br />
                Sample product page: <code>http://localhost:4000/product.html</code>
            </p>
            <div>
                <input 
                    type="url" 
                    placeholder="Enter webpage URL" 
                    value={seoUrl}
                    onChange={updateText}
                    style={{ width: '400px', marginRight: '10px' }}
                />
                <button onClick={process} disabled={!seoUrl || promiseInProgress}>
                    Generate SEO Content
                </button>
                <br />
                {promiseInProgress && <span>Analyzing webpage...</span>}
            </div>
            <div style={{ marginTop: '20px' }}>
                {seoText && (
                    <div>
                        <h3>Generated SEO Content:</h3>
                        <pre style={{ 
                            background: '#f5f5f5', 
                            padding: '10px', 
                            borderRadius: '5px',
                            whiteSpace: 'pre-wrap',
                            fontSize: '14px'
                        }}>
                            {seoText}
                        </pre>
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


### Step 7: Testing it out

- Replace `<AZURE_OPENAI_API_KEY>` placeholder value by looking up  https://aiaaa-s2-setting.azurewebsites.net
- Go to `apps-chat\chatbot-frontend` folder in terminal windows and run `npm run dev`
- Navigate to `SEO` page in the top navigation bar
- Copy `https://****.app.github.dev/product.html` into the text box. **** should be your codespaces name
- Click `Generate` to see SEO content


## Integration Opportunities

### Content Management Systems
- WordPress plugin integration
- Shopify SEO automation
- Custom CMS implementations
- Bulk page optimization

### Analytics and Monitoring
- Google Search Console integration
- Rank tracking automation
- Performance monitoring dashboards
- A/B testing for titles and descriptions

### Workflow Automation
- Automated SEO audits
- Content optimization alerts
- Competitor monitoring
- Performance reporting

## Real-World Applications

### E-commerce SEO
- Product page optimization
- Category page enhancements
- Review and rating integration
- Local store optimization

### Content Marketing
- Blog post optimization
- Landing page creation
- Social media content
- Email marketing integration

### Enterprise SEO
- Large-scale site optimization
- International SEO strategies
- Technical SEO auditing
- Brand reputation management

