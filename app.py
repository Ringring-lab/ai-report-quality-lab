import re
import streamlit as st

st.set_page_config(
    page_title="AI Report Quality Lab",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 AI Report Quality Lab")

st.write(
    """
    長文レポートの品質を、**構造・読みやすさ・具体性・重複・アクション性**
    の観点からチェックするプロトタイプです。
    """
)

st.info("v0.1｜まずはローカル分析でレポートの特徴を可視化します。")

report = st.text_area(
    "分析したいレポートを貼り付けてください",
    height=350,
    placeholder="ここにAIなどで生成した長文レポートを貼り付けます..."
)

if st.button("🔍 レポートを分析", type="primary"):

    if not report.strip():
        st.warning("レポートを入力してください。")

    else:
        paragraphs = [
            p.strip()
            for p in report.split("\n")
            if p.strip()
        ]

        sentences = [
            s.strip()
            for s in re.split(r"[。！？.!?]+", report)
            if s.strip()
        ]

        character_count = len(report)
        paragraph_count = len(paragraphs)
        sentence_count = len(sentences)

        avg_sentence_length = (
            character_count / sentence_count
            if sentence_count
            else 0
        )

        st.subheader("📊 基本分析")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("文字数", character_count)
        col2.metric("段落数", paragraph_count)
        col3.metric("文の数", sentence_count)
        col4.metric("平均文長", f"{avg_sentence_length:.1f}")

        st.subheader("🔎 Quality Check")

        if paragraph_count >= 5:
            st.success("✅ 構造：複数の段落に整理されています。")
        else:
            st.warning("⚠️ 構造：段落を増やすと読みやすくなる可能性があります。")

        if avg_sentence_length <= 80:
            st.success("✅ 可読性：1文の長さは比較的読みやすい範囲です。")
        else:
            st.warning("⚠️ 可読性：長い文章が多い可能性があります。")

        if re.search(r"\d", report):
            st.success("✅ 具体性：数字を含む記述があります。")
        else:
            st.warning("⚠️ 具体性：数字や具体的な根拠を追加できるか確認してください。")

        action_words = [
            "提案",
            "改善",
            "実施",
            "対応",
            "次に",
            "推奨",
            "recommend",
            "next",
            "action"
        ]

        if any(word.lower() in report.lower() for word in action_words):
            st.success("✅ アクション性：改善・提案につながる表現があります。")
        else:
            st.warning("⚠️ アクション性：次の行動につながる記述を追加できるか確認してください。")

        st.caption(
            "※ v0.1では簡易ルールによる分析です。今後AI評価・改善提案機能を追加します。" )