# HumanEgo — 3D camera-pose viewers

Interactive 3D visualizations of egocentric Aria demos: the fused semidense room point cloud plus
each demo's registered camera frustums and head trajectory.

**Live:** https://nussairhroub.github.io/humanego-viewers/

| Task | Demos | Viewer |
|---|---|---|
| cup_plate_02 | 64 | [cup_plate_02_viewer.html](cup_plate_02_viewer.html) |
| serve_bread | 61 | [serve_bread_viewer.html](serve_bread_viewer.html) |
| water_flowers | 61 | [water_flowers_viewer.html](water_flowers_viewer.html) |

Drag to rotate, scroll to zoom, shift-drag (or right-drag) to pan; use the slider to step through
demos, or "show all demos" to overlay every pose. Each page is a single self-contained HTML file
that renders with WebGL, falling back to a Canvas-2D software renderer where WebGL is unavailable —
no install or server required.

serve_bread and water_flowers use the [HumanEgo dataset](https://huggingface.co/datasets/Leo-TX/HumanEgo);
cup_plate_02 is from an internal capture. All geometry is derived from MPS SLAM closed-loop
trajectories and semidense point clouds, registered into a shared per-task frame (4-DoF: shared
gravity, so yaw + translation only).
