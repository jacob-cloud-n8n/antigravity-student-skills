---
name: youtube-thumbnail-beautifier
description: Use this skill when the user wants to beautify, redesign, polish, or improve a YouTube thumbnail so it looks more clickable, premium, dramatic, and high-CTR. The workflow must first ask the user for a base thumbnail image if none is provided, then use image editing / image2 capability to optimize the thumbnail while preserving the core topic, subject, and text intent.
---

# YouTube Thumbnail Beautifier

Create high-CTR YouTube thumbnails from a user's rough or existing thumbnail.

The goal is not mild cleanup. The goal is a thumbnail that feels visually stronger at first glance: clearer focus, stronger contrast, bigger emotion, readable text, cleaner hierarchy, and a more clickable composition.

## Required Workflow

### 1. Ask for the Base Thumbnail First

If the user has not attached or linked a thumbnail image, stop and ask them to upload the base thumbnail.

Use a short Chinese prompt:

```text
先把你目前的縮圖傳上來，我會用它當基礎，幫你美化成更有點擊感的 YouTube 縮略圖。
```

Do not generate from scratch before receiving the base thumbnail unless the user explicitly asks for a brand-new thumbnail concept.

### 2. Identify the Click Promise

Before editing, infer the thumbnail's click promise from visible text and subject matter.

Check:

- Main topic: What is the video about?
- Main emotion: shock, curiosity, urgency, authority, conflict, relief, or simplicity
- Primary subject: person, product, logo, interface, result, or before/after
- Main text: keep the meaning, but make it more readable and punchy if needed

If the meaning is unclear, ask one concise question for the video topic or title.

### 3. Use Image Editing / Image2

Use the available image editing capability to transform the provided base thumbnail.

Keep:

- Same overall topic
- Same main person or recognizable subject
- Same brand/product references unless the user asks to change them
- Same core text meaning
- YouTube thumbnail aspect ratio: 16:9

Improve:

- Bigger focal subject with cleaner cutout
- Stronger face lighting and skin clarity, if a person is present
- Higher contrast between foreground and background
- Text that is huge, readable, and not crowded
- Clear 2-3 layer hierarchy: subject, headline, supporting visual
- More premium color grading
- Less clutter in background
- Stronger depth: shadow, rim light, glow, separation
- More click tension: arrows, comparison marks, dramatic framing, or spotlight effects only when useful

Avoid:

- Tiny text
- Too many fonts
- Overloaded icons
- Muddy gradients
- Dark unreadable backgrounds
- Cropping important face or text
- Replacing the actual topic with generic AI art
- Making claims that are not already implied by the user

## Image Editing Prompt Template

When calling image editing / image2, adapt this prompt:

```text
Beautify this YouTube thumbnail into a premium high-click CTR style while preserving the original topic, main subject, and core text meaning.

Make the composition more dramatic and readable at mobile size.
Enhance the main subject with cleaner cutout, brighter face lighting, subtle rim light, and stronger separation from the background.
Simplify the background into a clean, high-contrast YouTube thumbnail backdrop.
Make the headline text very large, bold, sharp, and readable, with strong outline/shadow.
Use a clear 16:9 YouTube thumbnail layout with 2-3 strong focal elements only.
Add depth, contrast, punchy color grading, and professional creator-thumbnail polish.
Keep the result visually beautiful, modern, and immediately clickable.

Do not add unrelated objects.
Do not change the identity of the person.
Do not make the text small or crowded.
Do not create a generic poster; keep it recognizably a YouTube thumbnail.
```

If the thumbnail is for AI tools, Claude, ChatGPT, automation, coding, or productivity, prefer:

- Bright tech background
- Clean UI glow or blurred interface panels
- Strong blue, cyan, yellow, orange, black, or white contrast
- Big readable Chinese text
- Product logos kept recognizable when present

## Text Rules

Thumbnail text must pass the "one-second test":

- 3-8 Chinese characters is ideal
- 10-14 Chinese characters is acceptable if split into two lines
- Use one main headline, not paragraphs
- Strong outline and shadow are allowed
- Yellow/white text with black stroke is often effective
- Keep text away from edges and faces

If the source text is too long, compress it while preserving meaning. Examples:

- `每個人都必學的AI` -> `必學AI`
- `Claude Co-Work` -> `CLAUDE\nCO-WORK`
- `新手也能用的自動化流程` -> `新手自動化`

## Quality Checklist

After generating the improved thumbnail, verify:

- It still looks like the same video topic
- The first focal point is obvious
- Text is readable at small size
- Face or product is not distorted
- Background is cleaner than the original
- Contrast is stronger than the original
- There are no extra fingers, broken logos, weird symbols, or misspelled text
- The composition works at 16:9

If the result fails any major item, run another image edit with a more specific correction prompt.

## Response Style

When returning the result to the user:

- Show the generated image directly if possible
- Keep the response short
- Mention 2-4 concrete improvements made
- Do not over-explain design theory

Use Traditional Chinese by default.
