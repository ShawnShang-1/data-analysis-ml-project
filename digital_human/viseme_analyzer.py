"""
视位（Viseme）分析模块 — 将中文文本映射为嘴型时间线

策略：
1. 将中文文本按字切分
2. 每个字映射到对应的 viseme（嘴型）类型
3. 根据音频时长均匀分配时间线
4. 在静音处插入 sil（闭嘴）状态

Viseme 类型（简化版，适配 CSS 动画）：
- sil: 闭嘴（静音/标点）
- aa: 大开口（a, ang）
- o: 圆唇（o, u, wu, yu）
- ee: 扁唇（i, e, ei）
- f: 唇齿（f）
- m: 闭唇（b, p, m）
- rest: 默认/中性（其他）
"""

import re
from typing import List, Tuple, Dict

# 顶部一次性导入 pypinyin
try:
    from pypinyin import pinyin, Style
    _PYPINYIN_AVAILABLE = True
except ImportError:
    _PYPINYIN_AVAILABLE = False

# ── 中文拼音韵母 → Viseme 映射 ──
# 注意：ue/ve 应为圆唇 "o"，不能重复定义为 "ee"

PINYIN_TO_VISEME = {
    # 大开口 (aa)
    "a": "aa", "ai": "aa", "ao": "aa", "an": "aa", "ang": "aa",
    "ia": "aa", "iao": "aa", "ian": "aa", "iang": "aa",
    "ua": "aa", "uai": "aa", "uan": "aa", "uang": "aa",
    # 圆唇 (o)
    "o": "o", "uo": "o", "ou": "o", "iou": "o", "iu": "o",
    "ong": "o", "iong": "o",
    "u": "o", "v": "o", "vn": "o",
    "ue": "o", "ve": "o",   # nüe, lüe 等为圆唇音
    "ui": "o",              # 对、退、嘴等
    # 扁唇 (ee)
    "e": "ee", "ei": "ee", "en": "ee", "eng": "ee",
    "er": "ee", "i": "ee", "in": "ee", "ing": "ee",
    "ie": "ee",
    # 唇齿 (f) — 拼音中 f 声母的字
    # 闭唇 (m) — b, p, m 声母的字
    # rest — 默认
}

# 声母 → 特殊 viseme 映射（闭唇、唇齿）
# 优先级高于韵母：b/p/m 发音时必须先闭唇
INITIAL_TO_VISEME = {
    "b": "m", "p": "m", "m": "m",  # 闭唇
    "f": "f",                        # 唇齿
}

# 标点 → sil
PUNCTUATION = set("，。！？；：、""''（）【】《》…—　 .,!?;:\"'()[]{}")


def _get_pinyin(char: str) -> Tuple[str, str]:
    """获取汉字的声母和韵母（一次调用 pypinyin，避免重复）"""
    if not _PYPINYIN_AVAILABLE:
        return "", ""
    try:
        initial = pinyin(char, style=Style.INITIALS, strict=False)[0][0]
        final = pinyin(char, style=Style.FINALS, strict=False)[0][0]
        return initial, final
    except Exception:
        return "", ""


def char_to_viseme(char: str) -> str:
    """
    将单个汉字映射到 viseme 类型

    Returns:
        viseme 类型: sil | aa | o | ee | f | m | rest
    """
    # 标点和空格 → 闭嘴
    if char in PUNCTUATION or char.strip() == "":
        return "sil"

    # 获取拼音
    initial, final = _get_pinyin(char)

    # 优先检查声母（b/p/m/f 的闭唇/唇齿动作必须先于韵母）
    if initial in INITIAL_TO_VISEME:
        return INITIAL_TO_VISEME[initial]

    # 再检查韵母 → viseme
    if final in PINYIN_TO_VISEME:
        return PINYIN_TO_VISEME[final]

    # 默认返回 rest
    return "rest"


def generate_viseme_timeline(
    text: str,
    audio_duration: float,
    silence_ratio: float = 0.15,
) -> List[Dict]:
    """
    根据文本和音频时长生成 viseme 时间线

    Args:
        text: 回答文本
        audio_duration: 音频时长（秒）
        silence_ratio: 静音占比（标点停顿占总时长的比例）

    Returns:
        [
            {"time": 0.0, "viseme": "sil", "char": "大"},
            {"time": 0.3, "viseme": "aa", "char": "家"},
            ...
        ]
    """
    if not text.strip():
        return [{"time": 0.0, "viseme": "sil", "char": ""}]

    # 1. 将文本按字符切分，每个字符分配 viseme
    chars = list(text.strip())
    char_visemes = []
    for char in chars:
        viseme = char_to_viseme(char)
        char_visemes.append({"char": char, "viseme": viseme})

    # 2. 计算每个字符的时间分配
    total_chars = len(chars)
    if total_chars == 0:
        return [{"time": 0.0, "viseme": "sil", "char": ""}]

    # 统计非静音字符数
    non_silence_chars = sum(1 for cv in char_visemes if cv["viseme"] != "sil")
    silence_chars = total_chars - non_silence_chars

    if non_silence_chars == 0:
        return [{"time": 0.0, "viseme": "sil", "char": text}]

    # 初始静音从总时长中扣除，避免时间线超出音频时长
    initial_silence = min(0.1, audio_duration * 0.05)
    remaining_duration = audio_duration - initial_silence

    # 非静音字符的总时长
    speaking_duration = remaining_duration * (1 - silence_ratio)
    # 每个非静音字符的时长
    char_duration = speaking_duration / non_silence_chars
    # 每个静音字符的时长
    silence_char_duration = (
        (remaining_duration * silence_ratio) / silence_chars if silence_chars > 0 else 0
    )

    # 3. 生成时间线
    timeline = []
    current_time = 0.0

    # 初始静音
    timeline.append({"time": 0.0, "viseme": "sil", "char": ""})
    current_time += initial_silence

    for cv in char_visemes:
        timeline.append({
            "time": round(current_time, 3),
            "viseme": cv["viseme"],
            "char": cv["char"],
        })

        if cv["viseme"] == "sil":
            current_time += silence_char_duration
        else:
            current_time += char_duration

    # 末尾静音（确保不超过音频时长）
    end_time = min(current_time, audio_duration)
    timeline.append({
        "time": round(end_time, 3),
        "viseme": "sil",
        "char": "",
    })

    return timeline


def get_viseme_expression_map() -> Dict[str, str]:
    """获取 viseme 类型到 CSS 类名的映射"""
    return {
        "sil": "mouth-closed",      # 闭嘴
        "aa": "mouth-open-wide",    # 大开口
        "o": "mouth-rounded",       # 圆唇
        "ee": "mouth-wide",         # 扁唇
        "f": "mouth-f",             # 唇齿
        "m": "mouth-pressed",       # 闭唇
        "rest": "mouth-neutral",    # 中性
    }


def get_expression_types() -> Dict[str, str]:
    """获取表情类型描述"""
    return {
        "smiling": "微笑 — 讲解时使用",
        "explaining": "讲解 — 认真讲解时使用",
        "thinking": "思考 — 思考问题时使用",
        "nodding": "点头 — 表示肯定",
        "surprised": "惊讶 — 强调重点",
        "focusing": "专注 — 倾听/等待输入",
    }