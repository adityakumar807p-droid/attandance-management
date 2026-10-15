from flask import Flask, render_template, request, redirect, url_for, flash
from app import load_data, plan_request, run_call

app = Flask(__name__)
app.secret_key = "koi-bhi-lamba-random-text"

@app.route("/")
def index():
    data = load_data()
    rows = []
    for s in data["students"]:
        recorded = [v for v in s["attendance"].values() if v is not None]
        present = recorded.count("P")
        pct = round(present / len(recorded) * 100, 1) if recorded else 0.0
        rows.append({
            "rollno": s["rollno"],
            "name": s["name"],
            "attendance": s["attendance"],
            "pct": pct,
        })
    return render_template("index.html", days=data["days"], rows=rows)

@app.route("/ask", methods=["POST"])
def ask():
    text = request.form.get("instruction", "").strip()
    if not text:
        flash("Pehle kuch likho.")
        return redirect(url_for("index"))

    try:
        call = plan_request(text)
    except Exception as e:
        flash(f"AI error: {e}")
        return redirect(url_for("index"))

    # Terminal wala input() web par nahi chalega, isliye checkbox se confirm lenge
    if call.get("tool") == "remove_attendance" and not request.form.get("confirm"):
        args = call.get("arguments", {})
        flash(f"Remove ke liye 'Confirm remove' tick karke dobara bhejo (roll {args.get('rollno')}, {args.get('date')}).")
        return redirect(url_for("index"))

    result = run_call(call)
    if result.get("ok"):
        flash(f"Ho gaya: {result.get('result')}")
    else:
        flash(f"Error: {result.get('error')}")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)