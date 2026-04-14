"""
Daily AI Research Report Generator
Generates a bilingual (Traditional Chinese + English) report covering
AI Agents, ML, and LLMs, then sends it to the configured email address.
"""

import os
import anthropic


def generate_report(date_str: str) -> str:
    """Call Claude with web_search to produce the full bilingual report."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    prompt = (
        f"Today is {date_str}. "
        "Please generate today's AI research report — search YouTube and the web for the "
        "latest on AI Agents, ML, and LLMs, then compile the full bilingual report in "
        "Traditional Chinese and English. "
        "Cover: top model releases and benchmarks, MCP/A2A protocol updates, agent "
        "frameworks, enterprise governance, scientific AI breakthroughs, and a forward "
        "look for the week. Format each story with English and Traditional Chinese "
        "paragraphs side-by-side, include a Trending Topics Radar table, Key Takeaways, "
        "and a Source Index."
    )

    # Collect all text blocks from a streaming response
    report_parts: list[str] = []

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=[
            {
                "type": "web_search_20250305",
                "name": "web_search",
            }
        ],
        messages=[{"role": "user", "content": prompt}],
        betas=["web-search-2025-03-05"],
    ) as stream:
        for event in stream:
            # Collect text deltas
            pass
        # Get the final message after streaming completes
        final_message = stream.get_final_message()

    for block in final_message.content:
        if hasattr(block, "text"):
            report_parts.append(block.text)

    return "\n".join(report_parts)


if __name__ == "__main__":
    from datetime import date

    today = date.today().strftime("%Y-%m-%d")
    print(f"Generating report for {today}…")
    report = generate_report(today)
    # Write to file so the email step can read it
    with open("report_output.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("Report written to report_output.md")
