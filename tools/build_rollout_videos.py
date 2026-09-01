#!/usr/bin/env python3
"""Render rig rollouts into the two video formats this site uses.

Produces, per rollout, a 1280x1006 four-panel video (camera / detected objects /
policy input / gripper overlay) and a 640x514 camera-only video, both at 4 fps —
one frame per policy step — plus a summary.json for the page copy.

A panel with no frames on disk (e.g. no clean_*.png, because the checkpoint's RGB
branch is fed zeros and the loop skips inpainting) is drawn as a labelled placeholder.

    scp -r aloha@<rig>:/home/aloha/HumanEgo/results/rollout_187_* ./pulled/
    python3 tools/build_rollout_videos.py ./pulled rollout_videos_ict_only
"""
import json, os, glob, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
import matplotlib

FONTDIR = os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf")
F_HEAD = ImageFont.truetype(os.path.join(FONTDIR, "DejaVuSansMono-Bold.ttf"), 22)
F_HEAD_S = ImageFont.truetype(os.path.join(FONTDIR, "DejaVuSansMono-Bold.ttf"), 15)
F_LAB = ImageFont.truetype(os.path.join(FONTDIR, "DejaVuSansMono-Bold.ttf"), 13)

PW, PH = 640, 480
HDR, HDR_S = 46, 34
MISSING = "policy input (arm inpainted) — not produced by this policy"

POLICY = {  # run dir -> (display name, effective observation)
    "001_HumanEgo_baseline_NoRGB": ("HumanEgo NoRGB", "ict only"),
    "002_HumanEgo_Baseline_with_auxs": ("HumanEgo +aux", "rgb_ict"),
    "IctOnly": ("IctOnly", "ict_only"), "IctCanonOff": ("IctCanonOff", "ict_only"),
    "HumanEgo": ("HumanEgo", "rgb_ict"), "PcdV1": ("PcdV1", "pointcloud"),
}


def label(dr, x, y, text, font=F_LAB):
    w = dr.textlength(text, font=font)
    dr.rectangle([x, y, x + w + 9, y + 17], fill=(255, 255, 255))
    dr.text((x + 4, y + 2), text, font=font, fill=(0, 0, 0))


def panel(canvas, path, x, y, lab):
    dr = ImageDraw.Draw(canvas)
    if path and os.path.exists(path):
        canvas.paste(Image.open(path).convert("RGB").resize((PW, PH)), (x, y))
    else:
        dr.rectangle([x, y, x + PW - 1, y + PH - 1], fill=(26, 26, 26))
        lab = MISSING
    label(dr, x + 7, y + 7, lab)


def build(rdir, outdir, name):
    recs = [json.loads(l) for l in open(os.path.join(rdir, "rollout.jsonl"))]
    cfg = recs[0]
    steps = [r for r in recs if r.get("type") == "step"]
    n = len(steps)
    ck = cfg["ckpt"].rstrip("/").split("/")[-2]
    pol, obs = POLICY.get(ck, (ck, cfg["obs_mode"]))
    t0 = steps[0]["t"]
    fr = os.path.join(rdir, "frames")

    tmp4 = os.path.join(outdir, "_p"); tmpc = os.path.join(outdir, "_c")
    for d in (tmp4, tmpc):
        shutil.rmtree(d, ignore_errors=True); os.makedirs(d)

    for i, s in enumerate(steps):
        t = s["t"] - t0
        dp = s.get("done_prob", 0.0)
        raw = os.path.join(fr, f"raw_{i:04d}.png")
        obj = os.path.join(fr, f"objects_{i:04d}.png")
        gri = os.path.join(fr, f"gripper_{i:04d}.png")
        cle = os.path.join(fr, f"clean_{i:04d}.png")

        c = Image.new("RGB", (PW * 2, HDR + PH * 2), (0, 0, 0))
        d = ImageDraw.Draw(c)
        d.text((12, HDR // 2), f"{name}   ·   {pol} ({obs})   ·   step {i+1}/{n}"
                               f"   ·   t = {t:.1f} s   ·   done {dp:.2f}",
               font=F_HEAD, fill=(255, 255, 255), anchor="lm")
        panel(c, raw, 0, HDR, "camera")
        panel(c, obj, PW, HDR, "detected objects")
        panel(c, cle, 0, HDR + PH, "policy input (arm inpainted)")
        panel(c, gri, PW, HDR + PH, "gripper / target")
        c.save(os.path.join(tmp4, f"f_{i:04d}.png"))

        cc = Image.new("RGB", (PW, HDR_S + PH), (0, 0, 0))
        dd = ImageDraw.Draw(cc)
        dd.text((10, HDR_S // 2), f"{name.replace('_', ' ')} · {pol} · step {i+1}/{n}"
                                  f" · t = {t:.0f} s", font=F_HEAD_S, fill=(255, 255, 255), anchor="lm")
        if os.path.exists(raw):
            cc.paste(Image.open(raw).convert("RGB").resize((PW, PH)), (0, HDR_S))
        cc.save(os.path.join(tmpc, f"f_{i:04d}.png"))

    stem = os.path.basename(rdir)
    for src, out in ((tmp4, f"{stem}.mp4"), (tmpc, f"{stem}_cam.mp4")):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", "4",
                        "-i", os.path.join(src, "f_%04d.png"),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                        "-movflags", "+faststart", os.path.join(outdir, out)], check=True)
        shutil.rmtree(src, ignore_errors=True)

    mv = os.path.join(rdir, "moves.jsonl")
    moves = [json.loads(l) for l in open(mv)] if os.path.exists(mv) else []
    path_cm = sum(m.get("step_cm", 0.0) for m in moves)
    grasps = [m.get("grasp", 0.0) for m in moves]

    span = steps[-1]["t"] - t0
    return {"moves": len(moves), "path_cm": path_cm,
            "max_grasp": max(grasps) if grasps else None,
            "final_grasp": grasps[-1] if grasps else None,
            "ckpt": cfg["ckpt"], "logged_obs_mode": cfg["obs_mode"],
            "control_hz": cfg["control"]["control_hz"], "rec": stem, "policy": f"{pol} ({obs})", "steps": n, "span": span,
            "final_done": steps[-1].get("done_prob", 0.0),
            "max_done": max(s.get("done_prob", 0.0) for s in steps),
            "first_done": steps[0].get("done_prob", 0.0),
            "sec_per_step": (span / (n - 1)) if n > 1 else 0.0,
            "done_threshold": cfg["control"]["done_threshold"],
            "self_terminated": max(s.get("done_prob", 0.0) for s in steps) >= cfg["control"]["done_threshold"]}


if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    summ = []
    for rdir in sorted(glob.glob(os.path.join(src, "rollout_*"))):
        stem = os.path.basename(rdir)
        name = "rollout_" + stem.split("_")[1]
        print("building", stem)
        summ.append(build(rdir, out, name))
    json.dump(summ, open(os.path.join(out, "summary.json"), "w"), indent=2)
    print(json.dumps(summ, indent=2))
