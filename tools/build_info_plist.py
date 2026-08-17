#!/usr/bin/env python3
"""Build deepseek-workflow/Workflow/info.plist from the reference
alfredapp/openai-workflow info.plist.

The DeepSeek workflow keeps the ChatGPT chat flow untouched (DeepSeek's API is
OpenAI-compatible) but:
  * points all requests at the DeepSeek API (deepseek_api_* variables),
  * drops the DALL·E image flow (DeepSeek has no image generation API),
  * renames user-facing strings from ChatGPT to DeepSeek.

Usage:
    python3 tools/build_info_plist.py PATH_TO_REFERENCE_INFO_PLIST
"""

import plistlib
import re
import sys

REFERENCE = sys.argv[1] if len(sys.argv) > 1 else \
    "/tmp/openai-workflow-ref/Workflow/info.plist"
OUTPUT = "Workflow/info.plist"

# ---------------------------------------------------------------------------
# Objects belonging to the DALL·E flow — removed entirely.
# ---------------------------------------------------------------------------
DALLE_OBJECT_UIDS = {
    "698A6D21-8A81-4110-9BF3-BF2FA07C5DC3",  # keyword "dalle"
    "C05A6557-586B-4B86-AFFB-459590991D55",  # text view (DALL·E)
    "01A59F71-DA66-43E4-A948-1F2B653710DF",  # argument (archive_dir)
    "61B83861-C1E7-4430-9D5B-399018364F26",  # reveal file
    "6EE7D872-0140-4B1B-B21A-D233250E9CC4",  # automation: sort children
    "6AAF51CA-1EE9-4CB8-B632-1B83BBD40B45",  # junction
    "C7C34D1A-42E0-4C94-B94D-C344D3EE63CE",  # external trigger "continue_images"
    "C81D4557-D55C-4B23-8FB3-B28519D292A0",  # automation: directory.new (archive)
    "0052DD7D-01DA-4E09-8B83-3F4994975B5F",  # call external trigger
    "BD3EE72E-D542-4AEB-AED1-EA3C1F7BF6EC",  # automation: file.uti.matching
    "2DFDEB25-8ABB-4A11-A363-0879F9878137",  # automation: directory.children.sort
    "98D8AB67-AA1E-452D-9E1D-3BE47B471BA7",  # automation: finder.move
}


def main():
    with open(REFERENCE, "rb") as handle:
        plist = plistlib.load(handle)

    # --- Top-level metadata -------------------------------------------------
    plist["name"] = "DeepSeek"
    plist["description"] = "DeepSeek integrations"
    plist["bundleid"] = "com.deepseek.workflow"
    plist["createdby"] = "DeepSeek Workflow"
    plist["version"] = "1.0"
    plist.pop("webaddress", None)
    plist["readme"] = (
        "# DeepSeek\n\n"
        "Ask DeepSeek anything straight from Alfred. Powered by the DeepSeek API.\n\n"
        "## Setup\n\n"
        "1. Get a DeepSeek API key at https://platform.deepseek.com/api_keys\n"
        "2. Add it to the workflow's Configuration.\n\n"
        "## Usage\n\n"
        "Type `deepseek` followed by your question. "
        "↩ Ask a new question · ⌘↩ Clear and start new chat · ⌥↩ Chat history · "
        "⌃↩ Copy full chat · ⇧↩ Stop generating answer.\n\n"
        "Forked from the [Alfred OpenAI Workflow](https://github.com/alfredapp/openai-workflow)."
    )

    # --- Workflow-level variables ------------------------------------------
    plist["variables"] = {
        "deepseek_api_endpoint": "https://api.deepseek.com/v1/chat/completions",
        "deepseek_model_override": "",
    }

    # --- Remove DALL·E objects, their connections and their uidata ----------
    objects = [o for o in plist["objects"] if o["uid"] not in DALLE_OBJECT_UIDS]
    plist["objects"] = objects

    connections = {}
    for source, destinations in plist["connections"].items():
        if source in DALLE_OBJECT_UIDS:
            continue
        kept = [d for d in destinations if d["destinationuid"] not in DALLE_OBJECT_UIDS]
        if kept:
            connections[source] = kept
    plist["connections"] = connections

    plist["uidata"] = {uid: data for uid, data in plist["uidata"].items()
                       if uid not in DALLE_OBJECT_UIDS}

    # --- Rename chat-flow strings / variables -------------------------------
    def find(uid):
        return next(o for o in plist["objects"] if o["uid"] == uid)

    find("CBBF8BED-C42D-4793-8FEA-EA80FC94C493")["config"]["name"] = "Ask DeepSeek"
    find("DA9FB2AC-0A0A-463D-B07A-B25CD699C24C")["config"]["text"] = "Ask DeepSeek '{query}'"
    find("BF340515-39CD-47C9-965D-B1631A3BF45F")["config"]["keyword"] = "{var:deepseek_keyword}"
    find("BF340515-39CD-47C9-965D-B1631A3BF45F")["config"]["text"] = "Ask DeepSeek"
    find("4DB440D5-3814-4C79-9724-D19FDDDA4BEC")["config"]["inputfile"] = "deepseek"
    find("4DB440D5-3814-4C79-9724-D19FDDDA4BEC")["config"]["loadingtext"] = "Querying DeepSeek API…"
    find("B2F04B2C-63AD-4A6D-9A81-7F333D0A075A")["config"]["title"] = "DeepSeek Chat History"

    history_arg = find("879C841D-04CC-40AA-800D-689027CF0FB4")["config"]["variables"]
    history_arg["deepseek_history_save"] = history_arg.pop("chatgpt_history_save")
    find("74890339-2177-4514-B0CD-9D06DF626D21")["config"]["conditions"][0]["inputstring"] = \
        "{var:deepseek_history_save}"

    # --- User-facing configuration ------------------------------------------
    plist["userconfigurationconfig"] = [
        {
            "variable": "deepseek_api_key",
            "type": "textfield",
            "label": "DeepSeek API Key",
            "description": "Get it at https://platform.deepseek.com/api_keys",
            "config": {"default": "", "placeholder": "", "required": True, "trim": True},
        },
        {
            "variable": "deepseek_keyword",
            "type": "textfield",
            "label": "DeepSeek Keyword",
            "description": "",
            "config": {"default": "deepseek", "placeholder": "", "required": False, "trim": True},
        },
        {
            "variable": "deepseek_history_save",
            "type": "checkbox",
            "label": "Keep History",
            "description": "",
            "config": {
                "default": True,
                "required": False,
                "text": "Save current chat when starting a new one",
            },
        },
        {
            "variable": "deepseek_model",
            "type": "popupbutton",
            "label": "Model",
            "description": "",
            "config": {
                "default": "deepseek-chat",
                "pairs": [
                    ["DeepSeek Chat", "deepseek-chat"],
                    ["DeepSeek Reasoner", "deepseek-reasoner"],
                ],
            },
        },
        {
            "variable": "max_context",
            "type": "slider",
            "label": "Context",
            "description": "How many older questions and answers to send.",
            "config": {
                "defaultvalue": 24,
                "markercount": 25,
                "maxvalue": 50,
                "minvalue": 2,
                "onlystoponmarkers": True,
                "showmarkers": True,
            },
        },
        {
            "variable": "timeout_seconds",
            "type": "slider",
            "label": "Timeout",
            "description": "How many seconds to wait before giving up connection.",
            "config": {
                "defaultvalue": 10,
                "markercount": 6,
                "maxvalue": 30,
                "minvalue": 5,
                "onlystoponmarkers": True,
                "showmarkers": True,
            },
        },
        {
            "variable": "system_prompt",
            "type": "textarea",
            "label": "System Prompt",
            "description": "Initial message to guide DeepSeek on the answers you expect.",
            "config": {"default": "", "required": False, "trim": True, "verticalsize": 3},
        },
    ]

    with open(OUTPUT, "wb") as handle:
        plistlib.dump(plist, handle, sort_keys=False)

    print(f"Wrote {OUTPUT} ({len(plist['objects'])} objects, "
          f"{len(plist['connections'])} connections)")


if __name__ == "__main__":
    main()
