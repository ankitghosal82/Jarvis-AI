import { generateText } from "ai"
import { cohere } from "@ai-sdk/cohere"

export async function POST(req: Request) {
  try {
    const { prompt, language, userName, pdfContent } = await req.json()

    let systemPrompt = `You are JARVIS, a helpful, voice-activated AI assistant.
    Your responses should be in ${language}.
    You can:
    - Answer general questions, including weather.
    - Provide information about people or topics: If the user asks 'Who is [person]?' or 'What is [topic]?', provide a concise summary and then include a link to Wikipedia in Markdown format like '[Read more on Wikipedia](https://en.wikipedia.org/wiki/Special:Search?search=[topic or person])'. Ensure the URL is correctly encoded.
    - Play YouTube videos: If the user asks 'Play [song/video]?', respond with 'YOUTUBE_SEARCH:[song/video name]'.
    - Remember the user's name. If the user's name is provided as "${userName}", address them by your name.
    - Explain code: If the user provides code and asks for an explanation (e.g., "Explain this code: [code]"), provide a clear explanation.
    - Fix grammar or translate: If the user asks to "fix grammar" or "translate" a text, perform the requested action.
    
    Keep responses concise and helpful.`

    if (pdfContent) {
      systemPrompt += `\n\nUser has provided the following PDF content for context:
      ---PDF CONTENT START---
      ${pdfContent}
      ---PDF CONTENT END---
      If the user asks questions about this PDF content (e.g., "summarize this chapter", "what is the main idea of section 3?"), use the provided text to answer. Otherwise, ignore the PDF content.`
    }

    const { text } = await generateText({
      model: cohere("command-r-plus"),
      prompt: prompt,
      system: systemPrompt,
    })

    return new Response(JSON.stringify({ text }), {
      headers: { "Content-Type": "application/json" },
    })
  } catch (error) {
    console.error("Error in AI API:", error)
    return new Response(JSON.stringify({ error: "Failed to generate response" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    })
  }
}
