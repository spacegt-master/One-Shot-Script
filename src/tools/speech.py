import os
import json
import re
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()


def slugify_filename(name: str) -> str:
    """清理文件名，移除文件系统不支持的非法字符"""
    return re.sub(r'[\\/*?:"<>|]', "", name).replace(" ", "_")


@tool
def azure_speech_synthesis_tool(
    manifest_json: str, output_dir: str = "output_audio"
) -> str:
    """
    批量语音合成工具：接收完整的 azure_speech.json 内容，
    调用 Azure 语音服务进行批量合成。
    参数:
    - manifest_json: 任务清单 JSON 字符串
    - output_dir: 音频保存的目录路径（支持绝对路径或相对路径），由主 Agent 传递
    """

    # 1. 环境预检
    speech_key = os.environ.get("SPEECH_KEY")
    service_region = os.environ.get("SPEECH_REGION")

    if not speech_key or not service_region:
        return "错误：未检测到 SPEECH_KEY 或 SPEECH_REGION。请检查环境变量配置。"

    # 2. 目录初始化
    # 判断是否为绝对路径，如果不是则基于当前文件所在目录构建
    if os.path.isabs(output_dir):
        output_folder = output_dir
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        output_folder = os.path.join(base_dir, output_dir)

    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)
    except Exception as e:
        return f"无法创建或访问输出目录 '{output_folder}': {str(e)}"

    # 3. 解析 JSON 数据
    try:
        clean_json = manifest_json.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif clean_json.startswith("```"):
            clean_json = clean_json.split("```")[1].split("```")[0].strip()

        tasks = json.loads(clean_json)
        if not isinstance(tasks, list):
            return "错误：数据格式应为任务对象列表。"
    except Exception as e:
        return f"JSON 解析失败: {str(e)}"

    # 4. 配置基础语音服务
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key, region=service_region
    )
    results_report = []
    total_tasks = len(tasks)

    print(
        f"--- 启动批量加固合成任务 (Total: {total_tasks}, Target Path: {output_folder}) ---"
    )

    # 5. 迭代处理任务（带异常保护）
    for task in tasks:
        task_id = task.get("id", "000")
        character = task.get("character", "Unknown")
        voice_name = task.get("voice", "zh-CN-XiaoxiaoNeural")
        text_content = task.get("text", "").strip()

        # 处理文件名及路径
        safe_name = slugify_filename(str(character))
        file_name = f"{task_id:0>3}_{safe_name}.mp3"
        # 确保生成最终文件的绝对路径
        absolute_file_path = os.path.abspath(os.path.join(output_folder, file_name))

        try:
            # 更新语音配置
            speech_config.speech_synthesis_voice_name = voice_name
            audio_config = speechsdk.audio.AudioOutputConfig(
                filename=absolute_file_path
            )

            # 初始化合成器
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config, audio_config=audio_config
            )

            # 执行合成
            speech_result = synthesizer.speak_text_async(text_content).get()

            # 状态判定
            if (
                speech_result.reason
                == speechsdk.ResultReason.SynthesizingAudioCompleted
            ):
                results_report.append(
                    {
                        "id": task_id,
                        "character": character,
                        "status": "Success",
                        "path": absolute_file_path,
                    }
                )
                print(f"已完成: {file_name}")
            else:
                reason = "Unknown Error"
                if speech_result.reason == speechsdk.ResultReason.Canceled:
                    cancellation_details = speech_result.cancellation_details
                    reason = (
                        cancellation_details.error_details
                        if cancellation_details.reason
                        == speechsdk.CancellationReason.Error
                        else str(cancellation_details.reason)
                    )

                results_report.append(
                    {
                        "id": task_id,
                        "character": character,
                        "status": "Failed",
                        "reason": reason,
                    }
                )
                print(f"失败: {file_name} - {reason}")

            # 显式清理资源
            del synthesizer
            del audio_config

        except Exception as item_error:
            # 捕获单条任务异常
            results_report.append(
                {
                    "id": task_id,
                    "character": character,
                    "status": "Exception",
                    "reason": str(item_error),
                }
            )
            print(f"异常跳过: {task_id} - {str(item_error)}")

    # 6. 生成最终执行报告
    report_lines = [f"### 批量合成执行报告 (目标路径: {output_folder})"]
    success_count = sum(1 for r in results_report if r["status"] == "Success")
    report_lines.append(f"统计: 成功 {success_count} / 总计 {total_tasks}")
    report_lines.append("---")

    for res in results_report:
        if res["status"] == "Success":
            report_lines.append(
                f"✅ ID {res['id']} | {res['character']}: `{res['path']}`"
            )
        else:
            report_lines.append(
                f"❌ ID {res['id']} | {res['character']}: 失败 ({res['reason']})"
            )

    return "\n".join(report_lines)
