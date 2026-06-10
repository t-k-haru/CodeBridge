# -*- coding: utf-8 -*-
import os, re

_last_usage = {"input": 0, "output": 0}

# DEMOモード（ポートフォリオ用）。デフォルトON。
# ON のあいだ Azure OpenAI を一切呼ばず、サンプル応答を返すため課金は0円。
# 実際にAIを動かすには DEMO_MODE=0 を設定し、Azure の各キーを用意すること。
DEMO_MODE = os.getenv("DEMO_MODE", "1").strip().lower() in ("1", "true", "yes", "on")


def get_last_token_usage():
    return _last_usage["input"], _last_usage["output"]

def _get_client():
    from openai import AzureOpenAI
    ep = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    if "/api/projects/" in ep:
        ep = ep.split("/api/projects/")[0] + "/"
    return AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2025-01-01-preview",
        azure_endpoint=ep,
    )

DEPLOY = os.getenv("AZURE_OPENAI_DEPLOYMENT", "o4-mini")

def _call(messages, max_tokens=32000):
    if DEMO_MODE:
        # ポートフォリオ用の安全網。DEMOモードでは課金APIを絶対に叩かない。
        raise RuntimeError("DEMO_MODE is enabled — Azure OpenAI calls are disabled (課金0円)")
    client = _get_client()
    resp = client.chat.completions.create(
        model=DEPLOY, messages=messages, max_completion_tokens=max_tokens,
    )
    u = resp.usage
    if u:
        _last_usage["input"]  = u.prompt_tokens
        _last_usage["output"] = u.completion_tokens
    return resp.choices[0].message.content

SYS = (
    "You are an expert frontend engineer. "
    "Modify the given HTML demo page per the user instruction. "
    "Rules: 1) Only change what is asked. "
    "2) Keep ALL existing content/CSS/JS/data intact. "
    "3) Return the ENTIRE HTML file — do not omit any part. "
    "4) Wrap output in ```html ... ```. "
    "5) Preserve Japanese text and existing styles."
)

def generate_code(instruction, existing_code):
    if DEMO_MODE:
        # AIは呼ばず、既存HTMLにデモ用コメントを1行だけ差し込んで「変更例」として返す。
        _last_usage["input"] = _last_usage["output"] = 0
        marker = f"\n<!-- DEMO: AIによる変更プレビュー（指示: {instruction[:40]}）-->\n"
        if "</body>" in existing_code:
            new_code = existing_code.replace("</body>", marker + "</body>", 1)
        else:
            new_code = existing_code + marker
        return "```html\n" + new_code + "\n```"
    return _call([
        {"role": "system", "content": SYS},
        {"role": "user", "content": (
            "[Existing HTML — return ALL of this with ONLY the requested change]\n"
            "```html\n" + existing_code + "\n```\n\n"
            "[Change instruction]\n" + instruction + "\n\n"
            "IMPORTANT: Return the COMPLETE HTML. Do not compress or omit any section."
        )},
    ])

def fix_code(code, error, instruction):
    if DEMO_MODE:
        _last_usage["input"] = _last_usage["output"] = 0
        return "```html\n" + code + "\n```"
    return _call([{"role": "user", "content": (
        "Fix this HTML validation error while keeping the original instruction.\n"
        "[Instruction]: " + instruction + "\n"
        "[Error]: " + error + "\n"
        "[HTML excerpt]: " + code[:4000] + "...\n\n"
        "Return fixed complete HTML in ```html ... ```"
    )}])

def generate_report(instruction, original, new_code, test_output, test_error, iterations):
    status = "成功" if not test_error else "要確認"
    if DEMO_MODE:
        _last_usage["input"] = _last_usage["output"] = 0
        return (
            f"【DEMOモード】これはサンプルレポートです（AIは呼び出していません・課金0円）。\n\n"
            f"・指示: {instruction}\n"
            f"・検証結果: {status}（{iterations}回）\n"
            f"・変更概要: 既存HTMLに変更プレビュー用コメントを追加しました。\n"
            f"・リスク: 実運用時はここにAIが生成したレビュー所見が入ります。"
        )
    return _call([{"role": "user", "content": (
        "Create a concise HTML report in Japanese for an engineer reviewing this HTML change.\n"
        "Instruction: " + instruction + "\n"
        "Validation: " + status + " (" + str(iterations) + " attempts)\n"
        "Output: " + (test_output or 'none') + "\n"
        "Error: " + (test_error or 'none') + "\n\n"
        "Include: summary (1-2 sentences), bullet list of changes, any risks. No code blocks."
    )}, ], max_tokens=2000)

def extract_code_block(text):
    m = re.search(r"```html\s*(.*?)```", text, re.DOTALL)
    if m: return m.group(1).strip()
    m = re.search(r"```\s*(<!DOCTYPE|<html)(.*?)```", text, re.DOTALL)
    if m: return (m.group(1)+m.group(2)).strip()
    if "<!DOCTYPE" in text or "<html" in text: return text.strip()
    return text.strip()
