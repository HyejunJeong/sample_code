import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient

from .isp_logger import set_isp_logfile
from .logging_openai_client import LoggingOpenAIClient
from .logging_websurfer import LoggingWebSurfer

import os

# Optional: load .env for local runs
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


async def main():
    set_isp_logfile("example_agent_traffic.log")

    assistant = AssistantAgent(
        name="assistant",
        system_message=(
            "You are part of a web browsing team.\n"
            "Your role is to collaborate with the MultimodalWebSurfer.\n"
            "You must not simulate browsing or guess what might be on websites.\n"
            "Instead, wait for the MultimodalWebSurfer to visit web pages and return content before you respond.\n"
            "Only use information the surfer provides. Do not use prior knowledge or make assumptions.\n"
            "Summarize findings only after the surfer has visited at least 5 pages.\n"
            "Conclude with 'Done with task.' once your summary is complete."
        ),
        model_client=LoggingOpenAIClient(model="gpt-4o"),
    )

    surfer = LoggingWebSurfer(
        name="web_surfer",
        model_client=OpenAIChatCompletionClient(model="gpt-4o"),
    )

    termination = MaxMessageTermination(100) | TextMentionTermination("Done with task.", sources="MultimodalWebSurfer") \
                                        | TextMentionTermination("ou're welcome") \
                                        | TextMentionTermination("here's anything else") \
                                        | TextMentionTermination("need more assistance") 

    agent_team = RoundRobinGroupChat(
        [assistant, surfer],
        termination_condition=termination
    )
    
    task = "Research Sony AI Ethics initiatives and summarize key themes."

    full_prompt = f"""{task}

Before concluding or summarizing, please collaborate with the MultimodalWebSurfer to explore relevant websites and gather concrete information.

To complete the task, you must:
1. Begin with a Bing search.
2. Click links or manually visit at least 5 different pages—not just summarize search results or rely on prior knowledge.
3. Visit and extract information from at least 5 different websites by clicking links.
4. Only use information found on pages you actually opened.
5. Once you have gathered concrete details from at least 5 different pages, write a brief summary and say: "Done with task."

Do not infer or assume anything unless it is directly stated on a visited webpage.
"""

    await team.run_stream(
        task=full_prompt
    )

    await surfer.close()


if __name__ == "__main__":
    asyncio.run(main())
