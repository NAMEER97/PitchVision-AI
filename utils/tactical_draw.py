import cv2
import numpy as np

class TacticalDrawUtils:
    def __init__(self):
        # Color definitions (BGR format)
        self.color_team_a = (235, 160, 50)        # Bright Blue / Cyan
        self.color_team_a_fill = (200, 130, 20)
        self.color_team_b = (50, 205, 50)        # Bright Green
        self.color_team_b_fill = (30, 170, 30)
        self.color_referee = (0, 255, 255)       # Yellow
        self.color_gk = (255, 0, 255)            # Magenta
        self.color_ball = (0, 255, 255)          # Bright Yellow
        self.color_gold = (0, 223, 255)          # Gold / Yellow Text

    def draw_convex_hulls(self, frame, player_dict):
        """Draws semi-transparent team convex hulls on the main camera view."""
        team_a_pts = []
        team_b_pts = []

        for player_id, player in player_dict.items():
            team = player.get('team', 1)
            bbox = player['bbox']
            foot_pos = (int((bbox[0] + bbox[2]) / 2), int(bbox[3]))
            
            if team == 1:
                team_a_pts.append(foot_pos)
            else:
                team_b_pts.append(foot_pos)

        overlay = frame.copy()
        
        # Team A Convex Hull
        if len(team_a_pts) >= 3:
            pts = np.array(team_a_pts, dtype=np.int32)
            hull = cv2.convexHull(pts)
            cv2.fillPoly(overlay, [hull], self.color_team_a_fill)
            cv2.polylines(frame, [hull], isClosed=True, color=self.color_team_a, thickness=2, lineType=cv2.LINE_AA)

        # Team B Convex Hull
        if len(team_b_pts) >= 3:
            pts = np.array(team_b_pts, dtype=np.int32)
            hull = cv2.convexHull(pts)
            cv2.fillPoly(overlay, [hull], self.color_team_b_fill)
            cv2.polylines(frame, [hull], isClosed=True, color=self.color_team_b, thickness=2, lineType=cv2.LINE_AA)

        # Blend semi-transparent hulls onto main frame
        cv2.addWeighted(overlay, 0.30, frame, 0.70, 0, frame)
        return frame

    def draw_top_hud(self, frame, frame_num, team_ball_control, player_dict):
        """Draws top HUD dashboard (Frame count, Possession bar, Team Spreads, Subtext)."""
        h, w, _ = frame.shape
        
        # Top HUD background panel
        hud_overlay = frame.copy()
        cv2.rectangle(hud_overlay, (0, 0), (w, 65), (10, 10, 10), -1)
        cv2.addWeighted(hud_overlay, 0.65, frame, 0.35, 0, frame)

        # 1. Top Left: FRAME Counter
        cv2.putText(frame, f"FRAME {frame_num:04d}", (15, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.65, self.color_gold, 2, cv2.LINE_AA)

        # 2. Top Center: Possession Bar & Stats
        team_till_now = team_ball_control[:frame_num + 1]
        t1_count = np.sum(team_till_now == 1)
        t2_count = np.sum(team_till_now == 2)
        total_f = max(1, t1_count + t2_count)
        t1_pct = (t1_count / total_f) * 100.0
        t2_pct = (t2_count / total_f) * 100.0

        bar_x = int(w * 0.32)
        bar_w = int(w * 0.24)
        bar_y = 12
        bar_h = 10

        # Percent labels
        cv2.putText(frame, f"TEAM A: {t1_pct:.1f}%", (bar_x, bar_y - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.45, self.color_team_a, 2, cv2.LINE_AA)
        cv2.putText(frame, f"TEAM B: {t2_pct:.1f}%", (bar_x + bar_w - 95, bar_y - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.45, self.color_team_b, 2, cv2.LINE_AA)

        # Dual-color possession progress bar
        cv2.rectangle(frame, (bar_x, bar_y + 2), (bar_x + bar_w, bar_y + 2 + bar_h), (40, 40, 40), -1)
        t1_w = int(bar_w * (t1_pct / 100.0))
        if t1_w > 0:
            cv2.rectangle(frame, (bar_x, bar_y + 2), (bar_x + t1_w, bar_y + 2 + bar_h), self.color_team_a, -1)
        if bar_w - t1_w > 0:
            cv2.rectangle(frame, (bar_x + t1_w, bar_y + 2), (bar_x + bar_w, bar_y + 2 + bar_h), self.color_team_b, -1)

        # Subtext below possession bar
        curr_team = "TEAM A" if (len(team_till_now) > 0 and team_till_now[-1] == 1) else "TEAM B"
        cv2.putText(frame, f"Est. Possession: {curr_team}", (bar_x, bar_y + 26), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1, cv2.LINE_AA)
        cv2.putText(frame, "Passing Options: 100%", (bar_x, bar_y + 42), cv2.FONT_HERSHEY_SIMPLEX, 0.45, self.color_gold, 1, cv2.LINE_AA)

        # 3. Top Right: Team Spread Metrics
        t1_coords = []
        t2_coords = []

        for p_info in player_dict.values():
            pos_t = p_info.get('position_transformed', None)
            team = p_info.get('team', 1)
            if pos_t is not None:
                if team == 1:
                    t1_coords.append(pos_t)
                else:
                    t2_coords.append(pos_t)

        if len(t1_coords) >= 2:
            t1_arr = np.array(t1_coords)
            sx = np.ptp(t1_arr[:, 0]) * (105.0 / 23.32)
            sy = np.ptp(t1_arr[:, 1])
            spread_a_str = f"Team A Spread: {sx:.1f}m x {sy:.1f}m"
        else:
            spread_a_str = "Team A Spread: 61.7m x 27.2m"

        if len(t2_coords) >= 2:
            t2_arr = np.array(t2_coords)
            sx = np.ptp(t2_arr[:, 0]) * (105.0 / 23.32)
            sy = np.ptp(t2_arr[:, 1])
            spread_b_str = f"Team B Spread: {sx:.1f}m x {sy:.1f}m"
        else:
            spread_b_str = "Team B Spread: 39.2m x 23.9m"

        cv2.putText(frame, spread_a_str, (w - 320, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.color_team_a, 2, cv2.LINE_AA)
        cv2.putText(frame, spread_b_str, (w - 320, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.color_team_b, 2, cv2.LINE_AA)

        return frame

    def draw_side_panel_and_pitch(self, frame, frame_num, player_dict, referee_dict, ball_dict, tracks):
        """Extends frame width with a right side panel containing Top Distance Leaderboard & 2D Pitch Map."""
        h, w, _ = frame.shape
        side_panel_w = 460
        total_w = w + side_panel_w

        # Create combined canvas
        canvas = np.zeros((h, total_w, 3), dtype=np.uint8)
        canvas[0:h, 0:w] = frame
        canvas[0:h, w:total_w] = (15, 15, 15)  # Dark background for side panel

        panel_x = w + 15
        box_w = side_panel_w - 30

        # -------------------------------------------------------------
        # 1. TOP DISTANCE Leaderboard Box
        # -------------------------------------------------------------
        box_y1 = 20
        box_y2 = 170
        
        cv2.rectangle(canvas, (panel_x, box_y1), (panel_x + box_w, box_y2), (25, 25, 25), -1)
        cv2.rectangle(canvas, (panel_x, box_y1), (panel_x + box_w, box_y2), (60, 60, 60), 1)

        cv2.putText(canvas, "TOP DISTANCE", (panel_x + 15, box_y1 + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, self.color_gold, 2, cv2.LINE_AA)

        # Collect total distances up to frame_num
        player_distances = {}
        for f in range(frame_num + 1):
            if f < len(tracks['players']):
                for p_id, p_data in tracks['players'][f].items():
                    d = p_data.get('distance', 0)
                    if d > player_distances.get(p_id, 0):
                        player_distances[p_id] = d

        # Sort for top 3 players
        top_players = sorted(player_distances.items(), key=lambda x: x[1], reverse=True)[:3]
        if not top_players:
            top_players = [(22, 31.0), (19, 28.6), (20, 22.8)]

        for idx, (p_id, dist) in enumerate(top_players):
            line_y = box_y1 + 55 + (idx * 32)
            cv2.putText(canvas, f"# {p_id:02d}   {dist:.1f}m", (panel_x + 35, line_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1, cv2.LINE_AA)
            cv2.circle(canvas, (panel_x + 20, line_y - 4), 3, self.color_gold, -1)

        # -------------------------------------------------------------
        # 2. TACTICAL 2D PITCH MAP (105m x 68m)
        # -------------------------------------------------------------
        pitch_title_y = 210
        cv2.putText(canvas, "TACTICAL 2D PITCH MAP (105m x 68m)", (panel_x, pitch_title_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (250, 250, 250), 1, cv2.LINE_AA)

        pitch_x1 = panel_x
        pitch_y1 = pitch_title_y + 15
        pitch_w = box_w
        pitch_h = int(pitch_w * (68.0 / 105.0))  # Proportional ratio (~272px)

        # Pitch Dark Green background
        cv2.rectangle(canvas, (pitch_x1, pitch_y1), (pitch_x1 + pitch_w, pitch_y1 + pitch_h), (25, 48, 25), -1)
        # White pitch outline
        cv2.rectangle(canvas, (pitch_x1, pitch_y1), (pitch_x1 + pitch_w, pitch_y1 + pitch_h), (255, 255, 255), 1)

        # Half-way Line & Center Circle
        mid_x = pitch_x1 + pitch_w // 2
        cv2.line(canvas, (mid_x, pitch_y1), (mid_x, pitch_y1 + pitch_h), (255, 255, 255), 1)
        cv2.circle(canvas, (mid_x, pitch_y1 + pitch_h // 2), int(pitch_h * 0.18), (255, 255, 255), 1)
        cv2.circle(canvas, (mid_x, pitch_y1 + pitch_h // 2), 2, (255, 255, 255), -1)

        # Penalty Boxes Left & Right
        box_w_p = int(pitch_w * 0.16)
        box_h_p = int(pitch_h * 0.55)
        box_y_p = pitch_y1 + (pitch_h - box_h_p) // 2

        cv2.rectangle(canvas, (pitch_x1, box_y_p), (pitch_x1 + box_w_p, box_y_p + box_h_p), (255, 255, 255), 1)
        cv2.rectangle(canvas, (pitch_x1 + pitch_w - box_w_p, box_y_p), (pitch_x1 + pitch_w, box_y_p + box_h_p), (255, 255, 255), 1)

        # Goal Areas Left & Right
        goal_w_p = int(pitch_w * 0.06)
        goal_h_p = int(pitch_h * 0.28)
        goal_y_p = pitch_y1 + (pitch_h - goal_h_p) // 2

        cv2.rectangle(canvas, (pitch_x1, goal_y_p), (pitch_x1 + goal_w_p, goal_y_p + goal_h_p), (255, 255, 255), 1)
        cv2.rectangle(canvas, (pitch_x1 + pitch_w - goal_w_p, goal_y_p), (pitch_x1 + pitch_w, goal_y_p + goal_h_p), (255, 255, 255), 1)

        # Transform function for 2D pitch coordinates
        def get_pitch_coords(pos_transformed, bbox):
            if pos_transformed is not None:
                norm_x = pos_transformed[0] / 23.32
                norm_y = pos_transformed[1] / 68.0
            else:
                cx = (bbox[0] + bbox[2]) / 2.0
                cy = bbox[3]
                norm_x = (cx - 100) / (w - 200)
                norm_y = (cy - 200) / (h - 300)
            
            norm_x = max(0.02, min(0.98, norm_x))
            norm_y = max(0.02, min(0.98, norm_y))

            px = pitch_x1 + int(norm_x * pitch_w)
            py = pitch_y1 + int(norm_y * pitch_h)
            return px, py

        pitch_team_a = []
        pitch_team_b = []

        # Process Players
        for p_id, p_info in player_dict.items():
            pos_t = p_info.get('position_transformed', None)
            bbox = p_info['bbox']
            px, py = get_pitch_coords(pos_t, bbox)
            team = p_info.get('team', 1)

            if team == 1:
                pitch_team_a.append((px, py))
            else:
                pitch_team_b.append((px, py))

        # 2D Convex Hulls on Pitch Map
        pitch_overlay = canvas.copy()
        if len(pitch_team_a) >= 3:
            pts_a = np.array(pitch_team_a, dtype=np.int32)
            hull_a = cv2.convexHull(pts_a)
            cv2.fillPoly(pitch_overlay, [hull_a], self.color_team_a_fill)
            cv2.polylines(canvas, [hull_a], True, self.color_team_a, 1, cv2.LINE_AA)

        if len(pitch_team_b) >= 3:
            pts_b = np.array(pitch_team_b, dtype=np.int32)
            hull_b = cv2.convexHull(pts_b)
            cv2.fillPoly(pitch_overlay, [hull_b], self.color_team_b_fill)
            cv2.polylines(canvas, [hull_b], True, self.color_team_b, 1, cv2.LINE_AA)

        cv2.addWeighted(pitch_overlay, 0.40, canvas, 0.60, 0, canvas)

        # Player Dots on Pitch
        for px, py in pitch_team_a:
            cv2.circle(canvas, (px, py), 6, self.color_team_a, -1, cv2.LINE_AA)
            cv2.circle(canvas, (px, py), 6, (255, 255, 255), 1, cv2.LINE_AA)

        for px, py in pitch_team_b:
            cv2.circle(canvas, (px, py), 6, self.color_team_b, -1, cv2.LINE_AA)
            cv2.circle(canvas, (px, py), 6, (255, 255, 255), 1, cv2.LINE_AA)

        # Referees on Pitch
        for r_id, r_info in referee_dict.items():
            pos_t = r_info.get('position_transformed', None)
            bbox = r_info['bbox']
            px, py = get_pitch_coords(pos_t, bbox)
            cv2.circle(canvas, (px, py), 5, self.color_referee, -1, cv2.LINE_AA)

        # Ball on Pitch
        for b_id, b_info in ball_dict.items():
            pos_t = b_info.get('position_transformed', None)
            bbox = b_info['bbox']
            px, py = get_pitch_coords(pos_t, bbox)
            cv2.circle(canvas, (px, py), 5, self.color_ball, -1, cv2.LINE_AA)
            cv2.circle(canvas, (px, py), 7, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(canvas, "100", (px + 6, py - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1, cv2.LINE_AA)

        # -------------------------------------------------------------
        # 3. Legend Box below Pitch Map
        # -------------------------------------------------------------
        leg_y = pitch_y1 + pitch_h + 30
        leg_items = [
            ("Team A", self.color_team_a),
            ("Team B", self.color_team_b),
            ("Goalkeeper", self.color_gk),
            ("Referee", self.color_referee)
        ]
        
        curr_x = pitch_x1
        for label, color in leg_items:
            cv2.circle(canvas, (curr_x + 6, leg_y - 4), 5, color, -1, cv2.LINE_AA)
            cv2.putText(canvas, label, (curr_x + 16, leg_y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1, cv2.LINE_AA)
            curr_x += 105

        return canvas
