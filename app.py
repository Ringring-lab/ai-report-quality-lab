import re
from collections import Counter

import streamlit as st


st.set_page_config(
    page_title="AI Report Quality Lab",
    page_icon="🧪",
    layout="wide",
)


def clamp(value, minimum=0, maximum=100):
    return max(minimum, min(maximum, round(value)))


def analyze_report(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    paragraphs = [
        p.strip()
        for p in re.split(r"\n\s*\n", text)
        if p.strip()
    ]

    sentences = [
        s.strip()
        for s in re.split(r"[。！？!?]+|(?<=[a-zA-Z0-9])[.!]\s+", text)
        if s.strip()
    ]

    character_count = len(text)
    paragraph_count = len(paragraphs)
    sentence_count = len(sentences)

    avg_sentence_length = (
        sum(len(sentence) for sentence in sentences) / sentence_count
        if sentence_count
        else 0
    )

    heading_pattern = re.compile(
        r"^(#{1,6}\s+|第.+[章節]|【.+】|■|◆|●|\d+[.．、]\s*)"
    )
    heading_count = sum(bool(heading_pattern.match(line)) for line in lines)

    evidence_patterns = [
        r"\d",
        r"%",
        r"％",
        r"https?://",
        r"出典",
        r"参考",
        r"調査",
        r"データ",
        r"according to",
        r"source",
        r"survey",
        r"data",
    ]
    evidence_hits = sum(
        len(re.findall(pattern, text, flags=re.IGNORECASE))
        for pattern in evidence_patterns
    )

    action_words = [
        "提案",
        "改善",
        "実施",
        "対応",
        "推奨",
        "検討",
        "導入",
        "次に",
        "必要",
        "べき",
        "recommend",
        "should",
        "next step",
        "action",
        "implement",
        "improve",
    ]
    action_hits = sum(
        text.lower().count(word.lower())
        for word in action_words
    )

    normalized_sentences = [
        re.sub(r"\s+", "", sentence.lower())
        for sentence in sentences
        if len(re.sub(r"\s+", "", sentence)) >= 10
    ]

    sentence_counts = Counter(normalized_sentences)

    duplicate_count = sum(
        count - 1
        for count in sentence_counts.values()
        if count > 1
    )

    duplicate_ratio = (
        duplicate_count / len(normalized_sentences)
        if normalized_sentences
        else 0
    )

    # Structure
    structure_score = 45
    structure_score += min(25, heading_count * 5)
    structure_score += min(20, paragraph_count * 2)

    if sentence_count >= 5:
        structure_score += 10

    structure_score = clamp(structure_score)

    # Readability
    if avg_sentence_length == 0:
        readability_score = 0
    elif avg_sentence_length <= 45:
        readability_score = 95
    elif avg_sentence_length <= 65:
        readability_score = 85
    elif avg_sentence_length <= 85:
        readability_score = 70
    elif avg_sentence_length <= 110:
        readability_score = 55
    else:
        readability_score = 35

    # Evidence / specificity
    evidence_density = (
        evidence_hits / sentence_count
        if sentence_count
        else 0
    )
    specificity_score = clamp(30 + evidence_density * 100)

    # Redundancy
    redundancy_score = clamp(100 - duplicate_ratio * 250)

    # Actionability
    action_density = (
        action_hits / sentence_count
        if sentence_count
        else 0
    )
    actionability_score = clamp(35 + action_density * 180)

    scores = {
        "構造": structure_score,
        "可読性": readability_score,
        "具体性・根拠": specificity_score,
        "重複の少なさ": redundancy_score,
        "アクション性": actionability_score,
    }

    overall_score = round(sum(scores.values()) / len(scores))

    return {
        "character_count": character_count,
        "paragraph_count": paragraph_count,
        "sentence_count": sentence_count,
        "avg_sentence_length": avg_sentence_length,
        "heading_count": heading_count,
        "evidence_hits": evidence_hits,
        "action_hits": action_hits,
        "duplicate_ratio": duplicate_ratio,
        "scores": scores,
        "overall_score": overall_score,
    }


def score_message(score):
    if score >= 85:
        return "強み"
    if score >= 70:
        return "良好"
    if score >= 55:
        return "改善余地あり"
    return "要改善"


st.title("🧪 AI Report Quality Lab")

st.write(
    """
    長文レポートを、**構造・可読性・具体性／根拠・重複・アクション性**
    の5つの観点から分析するプロトタイプです。
    """
)

st.info(
    "v0.2｜単純な○×判定から、複数指標によるスコアリングと改善提案へアップデート。"
)

report = st.text_area(
    "分析したいレポートを貼り付けてください",
    height=350,
    placeholder="ここにAIなどで生成した長文レポートを貼り付けます...",
)

if st.button("🔍 レポートを分析", type="primary"):

    if not report.strip():
        st.warning("レポートを入力してください。")

    else:
        result = analyze_report(report)

        st.subheader("🏆 Overall Quality Score")

        overall = result["overall_score"]
        st.metric("総合スコア", f"{overall} / 100")
        st.progress(overall / 100)

        st.subheader("📊 Quality Dimensions")

        columns = st.columns(5)

        for column, (name, score) in zip(
            columns,
            result["scores"].items(),
        ):
            with column:
                st.metric(name, f"{score}")
                st.caption(score_message(score))

        st.subheader("📐 基本分析")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("文字数", result["character_count"])
        col2.metric("段落数", result["paragraph_count"])
        col3.metric("文の数", result["sentence_count"])
        col4.metric(
            "平均文長",
            f'{result["avg_sentence_length"]:.1f}',
        )

        st.subheader("💡 改善ポイント")

        improvements = []

        if result["scores"]["構造"] < 70:
            improvements.append(
                "見出しや段落を使って、情報の階層をより明確にすると構造が伝わりやすくなります。"
            )

        if result["scores"]["可読性"] < 70:
            improvements.append(
                "長い文を分割し、1文で伝える内容を絞ると読みやすさを改善できます。"
            )

        if result["scores"]["具体性・根拠"] < 70:
            improvements.append(
                "数値・データ・出典・具体例など、主張を支える根拠を追加できる箇所を確認してください。"
            )

        if result["scores"]["重複の少なさ"] < 70:
            improvements.append(
                "同じ内容を繰り返している文を統合・削除すると、レポートをより簡潔にできます。"
            )

        if result["scores"]["アクション性"] < 70:
            improvements.append(
                "分析結果だけで終わらず、『次に何をするか』が分かる提案・推奨・実施項目を追加すると実用性が上がります。"
            )

        if improvements:
            for improvement in improvements:
                st.warning(f"→ {improvement}")
        else:
            st.success(
                "5つの評価軸で大きな弱点は検出されませんでした。次の段階ではAIによる内容面の評価を行います。"
            )

        st.subheader("🔬 Analysis Details")

        detail1, detail2, detail3 = st.columns(3)

        detail1.metric("見出し候補", result["heading_count"])
        detail2.metric("根拠シグナル", result["evidence_hits"])
        detail3.metric("行動シグナル", result["action_hits"])

        st.caption(
            "※ v0.2はルールベースの評価モデルです。スコアは文章品質の絶対評価ではなく、改善箇所を発見するための指標として設計しています。" )