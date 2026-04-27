def ai_insight(row: pd.Series, cost_saved: float) -> str:
    # Try real AI first
    if GEMINI_OK:
        try:
            prompt = f"""
            Analyze shipment:
            Route: {row['from']} → {row['to']}
            Risk: {row['risk']}
            Delay: {row['delay']}
            Cost: ₹{row['cost']}

            Give exactly 2 short actionable insights.
            """
            res = gemini.generate_content(prompt)
            return res.text

        except Exception:
            # ⛔ NEVER show API error
            pass

    # ✅ Always fallback silently to smart local AI
    insights = []

    if row["risk"] >= 70:
        insights.append(
            f"• High disruption risk ({row['risk']}%). Immediate rerouting or contingency planning required."
        )
    elif row["risk"] >= 40:
        insights.append(
            f"• Moderate risk on {row['from']} → {row['to']}. Monitor closely for delays."
        )
    else:
        insights.append(
            f"• Stable route with low risk ({row['risk']}%). No intervention needed."
        )

    if row["delay"] >= 5:
        insights.append(
            f"• Delay of {row['delay']} days may impact delivery commitments."
        )
    else:
        insights.append(
            f"• ETA {row['eta']} days is within acceptable limits."
        )

    if cost_saved > 0:
        insights.append(
            f"• Optimization opportunity: Save approx ₹{int(cost_saved)}."
        )

    return "\n".join(insights[:2])
