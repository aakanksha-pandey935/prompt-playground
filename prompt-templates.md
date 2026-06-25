# Reusable Prompt Templates

A collection of 8 prompt engineering patterns with descriptions, templates, and filled examples.

---

## 1. Role

**What it does:** Assigns the model a specific expert identity before the task, anchoring tone, vocabulary, and judgment to that role.

**Template:**
```
You are a {{role}} with {{years}} years of experience in {{domain}}.

{{task_description}}
```

**Example:**
```
You are a senior DevOps engineer with 10 years of experience in Kubernetes and cloud infrastructure.

Review the following Dockerfile and identify any security or performance issues:

FROM ubuntu:latest
RUN apt-get install -y curl
COPY . /app
CMD ["./app"]
```

---

## 2. Few-Shot

**What it does:** Provides 2–3 labeled input/output examples so the model learns the expected pattern before seeing the real input.

**Template:**
```
{{task_description}}

Example 1:
Input: {{example_1_input}}
Output: {{example_1_output}}

Example 2:
Input: {{example_2_input}}
Output: {{example_2_output}}

Example 3:
Input: {{example_3_input}}
Output: {{example_3_output}}

Now do the same for:
Input: {{real_input}}
Output:
```

**Example:**
```
Classify the sentiment of each customer review as Positive, Negative, or Neutral.

Example 1:
Input: "The product arrived fast and works perfectly!"
Output: Positive

Example 2:
Input: "It broke after two days. Very disappointed."
Output: Negative

Example 3:
Input: "It's okay. Nothing special but does the job."
Output: Neutral

Now do the same for:
Input: "I wasn't expecting much but it actually exceeded my expectations."
Output:
```

---

## 3. Chain-of-Thought (CoT)

**What it does:** Instructs the model to reason step-by-step before producing the final answer, improving accuracy on complex tasks.

**Template:**
```
{{task_description}}

Think through this step by step before giving your final answer.

Problem: {{problem}}
```

**Example:**
```
Solve the following word problem and explain your reasoning clearly.

Think through this step by step before giving your final answer.

Problem: A store sells apples for $0.75 each and oranges for $1.20 each.
Maria buys 4 apples and 3 oranges. She pays with a $10 bill.
How much change does she receive?
```

---

## 4. Structured Output

**What it does:** Constrains the model to return a specific format (JSON, table, fixed-key bullets) so the output can be parsed or displayed consistently.

**Template:**
```
{{task_description}}

Return your answer as a JSON object with exactly these fields:
{
  "{{field_1}}": "{{description_1}}",
  "{{field_2}}": "{{description_2}}",
  "{{field_3}}": "{{description_3}}"
}

Do not include any text outside the JSON block.

Input: {{input}}
```

**Example:**
```
Extract the key details from the job posting below.

Return your answer as a JSON object with exactly these fields:
{
  "job_title": "the role being hired for",
  "company": "company name",
  "location": "city or remote",
  "required_skills": ["list", "of", "skills"],
  "salary_range": "salary if mentioned, else null"
}

Do not include any text outside the JSON block.

Input: "We're hiring a Senior React Developer at Acme Corp in Austin, TX.
Must know TypeScript, Redux, and REST APIs. Salary: $120k–$150k."
```

---

## 5. Chaining

**What it does:** Breaks a complex task into sequential prompts where the output of one becomes the input of the next. Each prompt is focused and narrow.

**Template:**

**Prompt A (Step 1):**
```
{{step_1_instruction}}

Input: {{raw_input}}

Return only the result of this step, nothing else.
```

**Prompt B (Step 2 — feeds from Prompt A output):**
```
{{step_2_instruction}}

Input: {{output_from_step_1}}

Return only the result of this step, nothing else.
```

**Prompt C (Step 3 — feeds from Prompt B output):**
```
{{step_3_instruction}}

Input: {{output_from_step_2}}
```

**Example:**

**Prompt A:**
```
Extract all action items from the meeting notes below as a plain bulleted list.

Input: "We discussed the Q3 roadmap. John will update the design by Friday.
Sarah needs to schedule the stakeholder call. The team agreed to revisit
pricing next week. Dev to deploy the staging fix by EOD."

Return only the result of this step, nothing else.
```

**Prompt B:**
```
For each action item below, assign a priority: High, Medium, or Low.
Format: "- [Priority] action item"

Input: <output from Prompt A>

Return only the result of this step, nothing else.
```

**Prompt C:**
```
Format the prioritized action items below into a professional email update
addressed to the team manager.

Input: <output from Prompt B>
```

---

## 6. System Prompt

**What it does:** A persistent, reusable instruction block sent as the system message. Sets global behavior, tone, and constraints for the entire conversation.

**Template:**
```
You are {{assistant_name}}, a {{role}} assistant for {{company_or_context}}.

Your behavior rules:
- Always respond in {{language}}.
- Tone: {{tone}} (e.g., formal, friendly, concise).
- When you don't know something, say "I don't have enough information" — never guess.
- {{additional_rule_1}}
- {{additional_rule_2}}

Your primary goal: {{goal}}
```

**Example:**
```
You are Aria, a customer support assistant for NovaTech SaaS.

Your behavior rules:
- Always respond in English.
- Tone: friendly but professional.
- When you don't know something, say "I don't have enough information on that — let me connect you with a specialist."
- Never discuss competitor products.
- Keep responses under 150 words unless the user asks for detail.

Your primary goal: Help users resolve issues with NovaTech's project management platform quickly and clearly.
```

---

## 7. Negative Constraints

**What it does:** Explicitly tells the model what NOT to do, preventing common failure modes like verbosity, jargon, hallucination, or off-topic content.

**Template:**
```
{{task_description}}

Constraints — do NOT:
- {{constraint_1}}
- {{constraint_2}}
- {{constraint_3}}
- {{constraint_4}}

{{input_or_question}}
```

**Example:**
```
Summarize the research paper abstract below for a general audience.

Constraints — do NOT:
- Use technical jargon or acronyms without explaining them.
- Exceed 3 sentences.
- Add information not present in the abstract.
- Use phrases like "the paper argues" or "the authors claim" — write directly.

Abstract: "This study investigates the impact of circadian rhythm disruption
on cognitive performance in shift workers using polysomnography and
validated neuropsychological assessments across a 6-month longitudinal cohort."
```

---

## 8. Persona

**What it does:** Instructs the model to adopt a character with a consistent personality, backstory, and communication style throughout the interaction.

**Template:**
```
You are {{persona_name}}.

Background: {{backstory}}
Personality: {{personality_traits}}
Speech style: {{how_they_talk}}
Quirks: {{notable_habits_or_phrases}}

Stay in character for the entire conversation. Never break persona.

The user will now speak with you.
```

**Example:**
```
You are Morgan, a grizzled 20-year software veteran who has seen every trend come and go.

Background: Started coding in C on Unix machines, survived the dot-com crash,
built systems that are still running in production today.
Personality: Blunt, pragmatic, low tolerance for hype, secretly loves mentoring junior devs.
Speech style: Uses short sentences. Occasional dry humor. References war stories from past projects.
Quirks: Often says "I've seen this before" and "Keep it simple, always."

Stay in character for the entire conversation. Never break persona.

The user will now speak with you.
```
