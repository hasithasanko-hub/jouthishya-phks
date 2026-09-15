import os
import sys
import threading
import webbrowser
import urllib.parse
from pathlib import Path
from http.server import ThreadingHTTPServer

APP_TITLE = "හෙළ ජ්‍යෝතිෂ්‍ය — PHKS Creation"


def resource_path(relative):
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / relative


def prepare_import_path():
    app_dir = resource_path("app")
    if str(app_dir) not in sys.path:
        sys.path.insert(0, str(app_dir))
    return app_dir


def start_server():
    app_dir = prepare_import_path()
    os.chdir(app_dir)
    try:
        import license_client
        cfg = license_client.load_config()
        ok, _msg, state = license_client.startup_check(cfg)
        mode = "trial" if ok and str((state or {}).get("status")) == "trial" else "paid"
        os.environ["HELA_ACCESS_MODE"] = mode
        os.environ["HELA_TRIAL_LIMIT"] = str(int(cfg.get("trial_calculation_limit", 10)))
        os.environ["HELA_PUBLISHER"] = str(cfg.get("publisher", "PHKS Creation"))
        os.environ["HELA_WHATSAPP"] = str(cfg.get("support_whatsapp", "+94715954563"))
    except Exception:
        # Fail closed: never unlock paid features if a licence check fails unexpectedly.
        os.environ.setdefault("HELA_ACCESS_MODE", "trial")
    import server
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd, port


def _open_url(url):
    if url:
        webbrowser.open(url)


def license_window(manager_only=False):
    import tkinter as tk
    from tkinter import messagebox
    import license_client

    cfg = license_client.load_config()
    result = {"launch": False}

    root = tk.Tk()
    root.title("හෙළ ජ්‍යෝතිෂ්‍ය - බලපත්‍ර කළමනාකරණය")
    root.geometry("720x680")
    root.minsize(680, 620)
    root.configure(bg="#081625")
    try:
        root.iconbitmap(str(resource_path("installer/HelaJyotishya.ico")))
    except Exception:
        pass

    gold = "#d6ae57"
    cream = "#f7ead2"
    panel = "#0d2135"
    maroon = "#6d2035"

    outer = tk.Frame(root, bg="#081625", padx=30, pady=25)
    outer.pack(fill="both", expand=True)
    tk.Label(outer, text="හෙළ ජ්‍යෝතිෂ්‍ය", font=("Nirmala UI", 26, "bold"), fg=gold, bg="#081625").pack(anchor="w")
    tk.Label(outer, text="වාණිජ බලපත්‍ර කළමනාකරණය", font=("Nirmala UI", 12), fg=cream, bg="#081625").pack(anchor="w")
    tk.Label(outer, text="PHKS Creation  •  WhatsApp +94 71 595 4563", font=("Segoe UI", 10, "bold"), fg="#9fb1c1", bg="#081625").pack(anchor="w", pady=(4, 18))

    card = tk.Frame(outer, bg=panel, padx=22, pady=20, highlightbackground="#38526a", highlightthickness=1)
    card.pack(fill="x")

    status_var = tk.StringVar(value="පරීක්ෂා කරමින්...")
    detail_var = tk.StringVar(value="")
    tk.Label(card, textvariable=status_var, font=("Nirmala UI", 16, "bold"), fg=cream, bg=panel).pack(anchor="w")
    tk.Label(card, textvariable=detail_var, font=("Nirmala UI", 10), fg="#b9c7d4", bg=panel, justify="left", wraplength=590).pack(anchor="w", pady=(7, 15))

    key_frame = tk.Frame(card, bg=panel)
    key_frame.pack(fill="x", pady=(4, 12))
    tk.Label(key_frame, text="බලපත්‍ර යතුර", font=("Nirmala UI", 10, "bold"), fg=gold, bg=panel).pack(anchor="w")
    key_entry = tk.Entry(key_frame, font=("Segoe UI", 11), relief="flat")
    key_entry.pack(fill="x", ipady=9, pady=(6, 0))

    buttons = tk.Frame(card, bg=panel)
    buttons.pack(fill="x", pady=(4, 0))

    def refresh(online=False):
        cache = license_client.load_cache()
        if online and cache:
            ok, msg, cache = license_client.validate_online(cache)
        else:
            ok, msg, cache = license_client.startup_check(cfg)
        st = license_client.display_status(cache if cache.get("license_key") else None)
        mode = str((cache or {}).get("status") or "")
        if ok and mode == "trial":
            status_var.set("නොමිලේ අත්හදා බැලීම සක්‍රීයයි")
        elif ok:
            status_var.set("ගෙවූ බලපත්‍රය සක්‍රීයයි")
        elif mode == "trial-expired":
            status_var.set("නොමිලේ අත්හදා බැලීම අවසන්")
        else:
            status_var.set("භාවිතය සක්‍රීය කර නැත")
        bits = [msg]
        if mode == "trial":
            bits.append(f"ඉතිරි දින: {cache.get('trial_days_left','—')}")
        if st.get("key_short"):
            bits.append("යතුර: ••••-" + st["key_short"])
        if st.get("expires_at"):
            bits.append("වලංගු කාලය අවසන්: " + st["expires_at"])
        if st.get("instance_name"):
            bits.append("පරිගණකය: " + st["instance_name"])
        detail_var.set("\n".join(bits))
        return ok

    def start_trial_now():
        ok, msg, _ = license_client.start_trial(cfg)
        if ok:
            messagebox.showinfo("හෙළ ජ්‍යෝතිෂ්‍ය", msg)
        else:
            messagebox.showwarning("හෙළ ජ්‍යෝතිෂ්‍ය", msg)
        refresh(False)

    def activate_now():
        ok, msg, _ = license_client.activate(key_entry.get())
        messagebox.showinfo("හෙළ ජ්‍යෝතිෂ්‍ය", msg) if ok else messagebox.showerror("හෙළ ජ්‍යෝතිෂ්‍ය", msg)
        refresh(False)

    def deactivate_now():
        if not messagebox.askyesno("තහවුරු කිරීම", "මෙම පරිගණකයෙන් බලපත්‍රය ඉවත් කරන්නද?"):
            return
        ok, msg = license_client.deactivate()
        messagebox.showinfo("හෙළ ජ්‍යෝතිෂ්‍ය", msg) if ok else messagebox.showerror("හෙළ ජ්‍යෝතිෂ්‍ය", msg)
        refresh(False)

    def launch_now():
        ok, msg, _ = license_client.startup_check(cfg)
        if not ok:
            messagebox.showerror("හෙළ ජ්‍යෝතිෂ්‍ය", msg)
            return
        result["launch"] = True
        root.destroy()

    trial_actions = tk.Frame(card, bg=panel)
    trial_actions.pack(fill="x", pady=(14, 4), before=buttons)
    existing_trial = license_client.trial_status(cfg)
    trial_caption = (
        "නොමිලේ අත්හදා බැලීම දිගටම භාවිතා කරන්න"
        if existing_trial[0]
        else f"දින {int(cfg.get('trial_days',14))} නොමිලේ අත්හදා බලන්න"
    )
    tk.Button(trial_actions, text=trial_caption, command=start_trial_now, font=("Nirmala UI", 11, "bold"), bg=gold, fg="#15100a", activebackground="#eccb7d", relief="flat", padx=16, pady=11).pack(fill="x")

    tk.Button(buttons, text="සක්‍රීය කරන්න", command=activate_now, font=("Nirmala UI", 10, "bold"), bg=maroon, fg="white", activebackground="#8c2a46", activeforeground="white", relief="flat", padx=18, pady=10).pack(side="left", padx=(0, 8))
    tk.Button(buttons, text="නැවත පරීක්ෂා කරන්න", command=lambda: refresh(True), font=("Nirmala UI", 10), bg="#15334c", fg=cream, relief="flat", padx=15, pady=10).pack(side="left", padx=4)
    tk.Button(buttons, text="මෙම පරිගණකයෙන් ඉවත් කරන්න", command=deactivate_now, font=("Nirmala UI", 10), bg="#15334c", fg=cream, relief="flat", padx=15, pady=10).pack(side="left", padx=4)

    plans = tk.Frame(outer, bg="#081625", pady=20)
    plans.pack(fill="x")
    tk.Label(plans, text="මිලදී ගැනීම / අලුත් කිරීම", font=("Nirmala UI", 13, "bold"), fg=gold, bg="#081625").pack(anchor="w", pady=(0, 8))
    links = cfg.get("checkout_links") or {}
    row = tk.Frame(plans, bg="#081625")
    row.pack(fill="x")
    for label, key in [("මාසික සැලැස්ම", "monthly"), ("වාර්ෂික සැලැස්ම", "yearly"), ("ජීවිතකාලීන", "lifetime")]:
        url = str(links.get(key, "") or "").strip()
        if not url:
            plan_name = {"monthly":"Monthly", "yearly":"Yearly", "lifetime":"Lifetime"}[key]
            msg = urllib.parse.quote(f"Hello PHKS Creation, I want to purchase the Hela Jyotishya {plan_name} plan.")
            url = f"https://wa.me/94715954563?text={msg}"
        cmd = (lambda u=url: _open_url(u))
        tk.Button(row, text=label, command=cmd, font=("Nirmala UI", 10, "bold"), bg="#102a42", fg=cream, activebackground="#1b456b", activeforeground="white", relief="flat", padx=14, pady=10).pack(side="left", padx=(0, 8))

    support = cfg.get("support_url") or cfg.get("support_email") or ""
    if support:
        tk.Label(plans, text="සහාය / මිලදී ගැනීම්: PHKS Creation • WhatsApp +94 71 595 4563", font=("Nirmala UI", 9), fg="#9fb1c1", bg="#081625").pack(anchor="w", pady=(12, 0))

    foot = tk.Frame(outer, bg="#081625")
    foot.pack(fill="x", side="bottom")
    if not manager_only:
        tk.Button(foot, text="මෘදුකාංගය විවෘත කරන්න", command=launch_now, font=("Nirmala UI", 11, "bold"), bg=gold, fg="#15100a", activebackground="#eccb7d", relief="flat", padx=22, pady=12).pack(side="right")
    tk.Button(foot, text="වසන්න", command=root.destroy, font=("Nirmala UI", 10), bg="#21384b", fg=cream, relief="flat", padx=18, pady=10).pack(side="right", padx=8)

    refresh(False)
    root.mainloop()
    return result["launch"]


def main():
    # Build-time smoke test used after PyInstaller creates the EXE.
    # This verifies dynamically imported app/server dependencies (especially SQLite)
    # are actually bundled before an installer is produced.
    if "--package-self-test" in sys.argv:
        prepare_import_path()
        import sqlite3
        import _sqlite3
        import server
        assert server.self_test()
        return

    manager_only = "--license-manager" in sys.argv
    import license_client
    cfg = license_client.load_config()

    if manager_only:
        license_window(manager_only=True)
        return

    if cfg.get("license_required", True):
        # Commercial access gateway is shown on every normal launch.
        # The customer explicitly chooses Continue Trial / Activate / Buy / Open Software.
        # This also makes the payment options visible even when a trial is already active.
        if not license_window(manager_only=False):
            return

    try:
        import webview
    except Exception as e:
        raise RuntimeError("Desktop window component could not start") from e

    httpd, port = start_server()
    url = f"http://127.0.0.1:{port}/"
    webview.create_window(APP_TITLE, url, width=1500, height=940, min_size=(1100, 720), resizable=True, text_select=True)
    try:
        webview.start(debug=False, private_mode=False)
    finally:
        httpd.shutdown()
        httpd.server_close()


if __name__ == "__main__":
    main()
