# HumanEgo — 3D camera-pose viewers

Interactive 3D visualizations of egocentric Aria demos: the fused semidense room point cloud plus
each demo's registered camera frustums and head trajectory.

**Live:** https://nussairhroub.github.io/humanego-viewers/

**Presentation galleries:** [Dynamic Scene Gallery](presentation.html) ·
[Collected Demos](collected_demos.html) · [Hand Tracking](hand_tracking.html) ·
[Preprocessing](preprocessing.html) · [Object Orientations](object_orientations.html) · Robot Rollouts ([camera only](rollout_camera_gallery.html) · [all panels](rollout_gallery.html)) · [Orientation](orientation.html)
(demo clips in `media_cup_plate_02/`, rollout clips in `rollout_videos_after_143/` and `rollout_videos_camera/`)

| Task | Demos | Viewer | Method |
|---|---|---|---|
| cup_plate_02 | 64 | [cup_plate_02_viewer.html](cup_plate_02_viewer.html) | [method_pose_viewer.html](method_pose_viewer.html) |
| serve_bread | 61 | [serve_bread_viewer.html](serve_bread_viewer.html) | [method_pose_viewer.html](method_pose_viewer.html) |
| water_flowers | 61 | [water_flowers_viewer.html](water_flowers_viewer.html) | [method_pose_viewer.html](method_pose_viewer.html) |

### cup_plate_02 — room reconstructions

| Construction | Viewer | Method |
|---|---|---|
| Room reconstruction (dense true-color MoGe, 64 demos + test cam) | [cup_plate_02_recon_viewer.html](cup_plate_02_recon_viewer.html) | [method_room_recon.html](method_room_recon.html) |
| True-color semidense cloud | [cup_plate_02_color_viewer.html](cup_plate_02_color_viewer.html) | [method_color_cloud.html](method_color_cloud.html) |

### cup_plate_02 — policy observation clouds (demo 000)

| Construction | Viewer | Method |
|---|---|---|
| V1 sparse entity points | [pcd_obs_viewer_demo000.html](pcd_obs_viewer_demo000.html) | [method_pcd_obs.html](method_pcd_obs.html) |
| V2 dense scene clouds | [grey](pcd_dense_viewer_demo000.html) · [height-shaded](pcd_dense_shaded_viewer_demo000.html) | [method_pcd_dense.html](method_pcd_dense.html) |
| V3 fused scene reconstruction | [height-shaded](scene_recon_viewer_demo000.html) · [true color](scene_recon_color_viewer_demo000.html) | [method_scene_recon.html](method_scene_recon.html) |
| Canonical points from SAM 3D (prototype) | [static](canonical_points_viewer.html) · [frame slider](canonical_points_seq_viewer.html) · [tracked cup](canonical_points_tracked_viewer.html) | [method_canonical_points.html](method_canonical_points.html) |

Drag to rotate, scroll to zoom, shift-drag (or right-drag) to pan; use the slider to step through
demos, or "show all demos" to overlay every pose. Each page is a single self-contained HTML file
that renders with WebGL, falling back to a Canvas-2D software renderer where WebGL is unavailable —
no install or server required.

serve_bread and water_flowers use the [HumanEgo dataset](https://huggingface.co/datasets/Leo-TX/HumanEgo);
cup_plate_02 is from an internal capture. All geometry is derived from MPS SLAM closed-loop
trajectories and semidense point clouds, registered into a shared per-task frame (4-DoF: shared
gravity, so yaw + translation only).
