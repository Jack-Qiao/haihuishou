import pygame
import math
import random
from constants import Colors, GameConfig, Direction

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.stars = []
    
    def draw_gradient_background(self, animation_timer):
        """绘制渐变背景"""
        # 绘制游戏区域的渐变背景
        game_start_x = GameConfig.SKILL_PANEL_WIDTH
        
        # 创建更精美的渐变效果
        for y in range(GameConfig.GAME_HEIGHT):
            # 计算渐变比例，添加波浪效果
            ratio = y / GameConfig.GAME_HEIGHT
            wave = math.sin(y * 0.02 + animation_timer * 0.01) * 0.1
            ratio = max(0, min(1, ratio + wave))
            
            # 混合颜色，使用更丰富的色彩
            r = int(Colors.BG_TOP[0] * (1 - ratio) + Colors.BG_BOTTOM[0] * ratio)
            g = int(Colors.BG_TOP[1] * (1 - ratio) + Colors.BG_BOTTOM[1] * ratio)
            b = int(Colors.BG_TOP[2] * (1 - ratio) + Colors.BG_BOTTOM[2] * ratio)
            
            # 添加微妙的色彩变化
            r = max(0, min(255, r + int(math.sin(y * 0.05) * 5)))
            g = max(0, min(255, g + int(math.cos(y * 0.03) * 3)))
            b = max(0, min(255, b + int(math.sin(y * 0.07) * 4)))
            
            color = (r, g, b)
            pygame.draw.line(self.screen, color, (game_start_x, y), (game_start_x + GameConfig.GAME_WIDTH, y))
        
        # 添加星空效果
        self.draw_stars(game_start_x, animation_timer)
        
        # 绘制UI区域背景 - 使用渐变
        ui_start_x = game_start_x + GameConfig.GAME_WIDTH
        for y in range(GameConfig.WINDOW_HEIGHT):
            ratio = y / GameConfig.WINDOW_HEIGHT
            r = int(30 * (1 - ratio) + 20 * ratio)
            g = int(30 * (1 - ratio) + 15 * ratio)
            b = int(30 * (1 - ratio) + 25 * ratio)
            color = (r, g, b)
            pygame.draw.line(self.screen, color, (ui_start_x, y), (ui_start_x + GameConfig.UI_WIDTH, y))
        
        # 绘制分隔线 - 添加发光效果
        for i in range(3):
            alpha = 255 - i * 80
            line_color = (255, 255, 255, alpha)
            pygame.draw.line(self.screen, line_color, 
                           (ui_start_x - i, 0), 
                           (ui_start_x - i, GameConfig.WINDOW_HEIGHT), 1)
    
    def draw_stars(self, game_start_x, animation_timer):
        """绘制星空效果"""
        # 生成固定的星星位置
        if not self.stars:
            for _ in range(50):
                x = random.randint(game_start_x, game_start_x + GameConfig.GAME_WIDTH)
                y = random.randint(0, GameConfig.GAME_HEIGHT)
                size = random.randint(1, 3)
                twinkle_speed = random.uniform(0.02, 0.08)
                self.stars.append({'x': x, 'y': y, 'size': size, 'twinkle_speed': twinkle_speed})
        
        # 绘制星星
        for star in self.stars:
            # 闪烁效果
            twinkle = abs(math.sin(animation_timer * star['twinkle_speed']))
            brightness = int(200 + 55 * twinkle)
            color = (brightness, brightness, brightness)
            
            # 绘制星星
            pygame.draw.circle(self.screen, color, (star['x'], star['y']), star['size'])
            
            # 添加星星光芒
            if twinkle > 0.8:
                for i in range(4):
                    angle = i * math.pi / 2
                    end_x = star['x'] + math.cos(angle) * (star['size'] + 2)
                    end_y = star['y'] + math.sin(angle) * (star['size'] + 2)
                    pygame.draw.line(self.screen, color, (star['x'], star['y']), (end_x, end_y), 1)
    
    def draw_snake(self, snake, direction, animation_timer):
        """绘制蛇"""
        game_start_x = GameConfig.SKILL_PANEL_WIDTH
        for i, segment in enumerate(snake):
            x, y = segment
            rect = pygame.Rect(
                game_start_x + x * GameConfig.GRID_SIZE + 2,
                y * GameConfig.GRID_SIZE + 2,
                GameConfig.GRID_SIZE - 4,
                GameConfig.GRID_SIZE - 4
            )
            
            # 蛇头用不同颜色和动画效果
            if i == 0:
                # 蛇头颜色渐变 - 使用霓虹绿色
                head_color = Colors.NEON_GREEN
                # 添加呼吸动画效果
                pulse = 1 + 0.15 * math.sin(animation_timer * 0.4)
                size_offset = int(3 * pulse)
                head_rect = pygame.Rect(
                    game_start_x + x * GameConfig.GRID_SIZE + 2 - size_offset,
                    y * GameConfig.GRID_SIZE + 2 - size_offset,
                    GameConfig.GRID_SIZE - 4 + size_offset * 2,
                    GameConfig.GRID_SIZE - 4 + size_offset * 2
                )
                
                # 绘制发光效果
                glow_color = (57, 255, 20, 100)
                glow_rect = pygame.Rect(
                    game_start_x + x * GameConfig.GRID_SIZE + 1 - size_offset - 2,
                    y * GameConfig.GRID_SIZE + 1 - size_offset - 2,
                    GameConfig.GRID_SIZE - 2 + size_offset * 2 + 4,
                    GameConfig.GRID_SIZE - 2 + size_offset * 2 + 4
                )
                pygame.draw.rect(self.screen, (57, 255, 20, 50), glow_rect)
                pygame.draw.rect(self.screen, head_color, head_rect)
                
                # 绘制蛇头细节
                self.draw_snake_head_details(game_start_x, x, y, direction, animation_timer, size_offset)
            else:
                # 蛇身颜色渐变 - 使用更丰富的颜色
                body_ratio = i / len(snake)
                if i % 2 == 0:
                    body_color = Colors.EMERALD
                else:
                    body_color = Colors.LIME
                
                # 添加呼吸效果
                body_pulse = 1 + 0.05 * math.sin(animation_timer * 0.2 + i * 0.5)
                body_size = int((GameConfig.GRID_SIZE - 4) * body_pulse)
                body_offset = (GameConfig.GRID_SIZE - body_size) // 2
                
                body_rect = pygame.Rect(
                    game_start_x + x * GameConfig.GRID_SIZE + body_offset,
                    y * GameConfig.GRID_SIZE + body_offset,
                    body_size, body_size
                )
                
                pygame.draw.rect(self.screen, body_color, body_rect)
                
                # 添加高光效果
                highlight_rect = pygame.Rect(
                    game_start_x + x * GameConfig.GRID_SIZE + 4,
                    y * GameConfig.GRID_SIZE + 4,
                    GameConfig.GRID_SIZE - 8,
                    GameConfig.GRID_SIZE - 8
                )
                pygame.draw.rect(self.screen, Colors.WHITE, highlight_rect, 1)
                
                # 添加内部装饰
                inner_rect = pygame.Rect(
                    game_start_x + x * GameConfig.GRID_SIZE + 6,
                    y * GameConfig.GRID_SIZE + 6,
                    GameConfig.GRID_SIZE - 12,
                    GameConfig.GRID_SIZE - 12
                )
                pygame.draw.rect(self.screen, (255, 255, 255, 30), inner_rect)
    
    def draw_snake_head_details(self, game_start_x, x, y, direction, animation_timer, size_offset):
        """绘制蛇头细节"""
        center_x = game_start_x + x * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
        center_y = y * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
        
        # 根据移动方向调整眼睛位置
        eye_offset_x = 0
        eye_offset_y = 0
        
        if direction == Direction.UP:
            eye_offset_y = -2
        elif direction == Direction.DOWN:
            eye_offset_y = 2
        elif direction == Direction.LEFT:
            eye_offset_x = -2
        elif direction == Direction.RIGHT:
            eye_offset_x = 2
        
        # 绘制眼睛发光效果
        eye_glow = Colors.NEON_BLUE
        eye_blink = abs(math.sin(animation_timer * 0.3)) > 0.8  # 眨眼效果
        
        if not eye_blink:
            # 左眼
            pygame.draw.circle(self.screen, eye_glow, 
                             (center_x - 4 + eye_offset_x, center_y - 2 + eye_offset_y), 5)
            # 右眼
            pygame.draw.circle(self.screen, eye_glow, 
                             (center_x + 4 + eye_offset_x, center_y - 2 + eye_offset_y), 5)
            
            # 眼睛瞳孔
            pygame.draw.circle(self.screen, Colors.WHITE, 
                             (center_x - 4 + eye_offset_x, center_y - 2 + eye_offset_y), 3)
            pygame.draw.circle(self.screen, Colors.WHITE, 
                             (center_x + 4 + eye_offset_x, center_y - 2 + eye_offset_y), 3)
            
            # 眼睛高光
            pygame.draw.circle(self.screen, Colors.NEON_BLUE, 
                             (center_x - 5 + eye_offset_x, center_y - 3 + eye_offset_y), 1)
            pygame.draw.circle(self.screen, Colors.NEON_BLUE, 
                             (center_x + 3 + eye_offset_x, center_y - 3 + eye_offset_y), 1)
        
        # 绘制鼻孔
        nostril_color = Colors.DARK_PURPLE
        pygame.draw.circle(self.screen, nostril_color, 
                         (center_x - 2, center_y + 3), 1)
        pygame.draw.circle(self.screen, nostril_color, 
                         (center_x + 2, center_y + 3), 1)
        
        # 绘制舌头（根据方向）
        tongue_color = Colors.NEON_PINK
        tongue_length = 6 + int(3 * math.sin(animation_timer * 0.5))  # 舌头伸缩动画
        
        if direction == Direction.UP:
            tongue_points = [
                (center_x, center_y + 8),
                (center_x - 2, center_y + 8 + tongue_length),
                (center_x, center_y + 8 + tongue_length + 2),
                (center_x + 2, center_y + 8 + tongue_length)
            ]
        elif direction == Direction.DOWN:
            tongue_points = [
                (center_x, center_y - 8),
                (center_x - 2, center_y - 8 - tongue_length),
                (center_x, center_y - 8 - tongue_length - 2),
                (center_x + 2, center_y - 8 - tongue_length)
            ]
        elif direction == Direction.LEFT:
            tongue_points = [
                (center_x + 8, center_y),
                (center_x + 8 + tongue_length, center_y - 2),
                (center_x + 8 + tongue_length + 2, center_y),
                (center_x + 8 + tongue_length, center_y + 2)
            ]
        else:  # RIGHT
            tongue_points = [
                (center_x - 8, center_y),
                (center_x - 8 - tongue_length, center_y - 2),
                (center_x - 8 - tongue_length - 2, center_y),
                (center_x - 8 - tongue_length, center_y + 2)
            ]
        
        pygame.draw.polygon(self.screen, tongue_color, tongue_points)
        
        # 绘制蛇头鳞片效果
        scale_color = (0, 200, 0, 100)
        for scale_y in range(3):
            for scale_x in range(3):
                scale_pos_x = center_x - 6 + scale_x * 4
                scale_pos_y = center_y - 6 + scale_y * 4
                pygame.draw.circle(self.screen, scale_color, (scale_pos_x, scale_pos_y), 1)
        
        # 绘制蛇头边缘高光
        highlight_color = (100, 255, 100, 150)
        pygame.draw.arc(self.screen, highlight_color, 
                       (center_x - 8, center_y - 8, 16, 16), 0, math.pi, 2)
    
    def draw_food(self, food, food_count, food_animation_timer, animation_timer):
        """绘制食物"""
        x, y = food
        game_start_x = GameConfig.SKILL_PANEL_WIDTH
        
        # 判断是否是大食物
        is_big_food = food_count % 3 == 2  # 每3个食物中的第3个是大食物
        
        # 添加旋转和缩放动画
        scale = 1 + 0.3 * math.sin(food_animation_timer * 0.3) if is_big_food else 1 + 0.2 * math.sin(food_animation_timer * 0.2)
        size = int((GameConfig.GRID_SIZE - 4) * scale)
        offset = (GameConfig.GRID_SIZE - size) // 2
        
        # 绘制主体
        food_rect = pygame.Rect(
            game_start_x + x * GameConfig.GRID_SIZE + offset,
            y * GameConfig.GRID_SIZE + offset,
            size, size
        )
        
        # 根据食物类型选择颜色
        if is_big_food:
            # 大食物 - 霓虹紫色渐变
            food_color = Colors.NEON_PURPLE
            border_color = Colors.NEON_PINK
            highlight_color = Colors.LIGHT_PURPLE
            glow_color = Colors.NEON_PURPLE
        else:
            # 普通食物 - 霓虹金色渐变
            food_color = Colors.NEON_ORANGE
            border_color = Colors.NEON_YELLOW
            highlight_color = Colors.GOLD
            glow_color = Colors.NEON_ORANGE
        
        # 绘制发光效果
        glow_size = size + 4
        glow_offset = (GameConfig.GRID_SIZE - glow_size) // 2
        glow_rect = pygame.Rect(
            game_start_x + x * GameConfig.GRID_SIZE + glow_offset,
            y * GameConfig.GRID_SIZE + glow_offset,
            glow_size, glow_size
        )
        pygame.draw.rect(self.screen, (glow_color[0], glow_color[1], glow_color[2], 100), glow_rect)
        
        pygame.draw.rect(self.screen, food_color, food_rect)
        
        # 添加高光效果
        highlight_size = size // 3
        highlight_rect = pygame.Rect(
            game_start_x + x * GameConfig.GRID_SIZE + offset + 2,
            y * GameConfig.GRID_SIZE + offset + 2,
            highlight_size, highlight_size
        )
        pygame.draw.rect(self.screen, highlight_color, highlight_rect)
        
        # 添加边框
        pygame.draw.rect(self.screen, border_color, food_rect, 2)
        
        # 绘制食物细节
        self.draw_food_details(game_start_x, x, y, is_big_food, scale, animation_timer)
    
    def draw_food_details(self, game_start_x, x, y, is_big_food, scale, animation_timer):
        """绘制食物细节"""
        center_x = game_start_x + x * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
        center_y = y * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
        
        if is_big_food:
            # 大食物特殊效果
            # 绘制旋转的星星
            star_rotation = animation_timer * 0.1
            star_size = 4 + int(2 * math.sin(animation_timer * 0.3))
            
            for i in range(5):
                angle = star_rotation + i * (2 * math.pi / 5)
                star_x = center_x + int(star_size * math.cos(angle))
                star_y = center_y + int(star_size * math.sin(angle))
                pygame.draw.circle(self.screen, Colors.GOLD, (star_x, star_y), 2)
            
            # 绘制光环效果
            ring_radius = 8 + int(3 * math.sin(animation_timer * 0.2))
            pygame.draw.circle(self.screen, Colors.NEON_PINK, (center_x, center_y), ring_radius, 2)
            
            # 绘制内部纹理
            for i in range(4):
                texture_angle = animation_timer * 0.05 + i * (math.pi / 2)
                texture_x = center_x + int(3 * math.cos(texture_angle))
                texture_y = center_y + int(3 * math.sin(texture_angle))
                pygame.draw.circle(self.screen, Colors.LIGHT_PURPLE, (texture_x, texture_y), 1)
        else:
            # 普通食物细节
            # 绘制苹果柄
            stem_color = Colors.MAROON
            pygame.draw.line(self.screen, stem_color, 
                           (center_x, center_y - 6), (center_x, center_y - 8), 2)
            
            # 绘制苹果叶子
            leaf_color = Colors.LIME
            leaf_points = [
                (center_x, center_y - 8),
                (center_x + 3, center_y - 10),
                (center_x + 2, center_y - 8)
            ]
            pygame.draw.polygon(self.screen, leaf_color, leaf_points)
            
            # 绘制苹果高光
            highlight_color = (255, 255, 255, 100)
            pygame.draw.circle(self.screen, highlight_color, 
                             (center_x - 2, center_y - 2), 2)
            
            # 绘制苹果纹理
            for i in range(3):
                texture_x = center_x - 3 + i * 3
                texture_y = center_y + 1
                pygame.draw.circle(self.screen, Colors.RUBY, (texture_x, texture_y), 1)
    
    def draw_temp_foods(self, temp_foods, animation_timer):
        """绘制临时食物"""
        game_start_x = GameConfig.SKILL_PANEL_WIDTH
        for temp_food in temp_foods:
            x, y = temp_food
            rect = pygame.Rect(
                game_start_x + x * GameConfig.GRID_SIZE + 3,
                y * GameConfig.GRID_SIZE + 3,
                GameConfig.GRID_SIZE - 6,
                GameConfig.GRID_SIZE - 6
            )
            
            # 临时食物用黄色，带闪烁效果
            flash = abs(math.sin(animation_timer * 0.2))
            temp_color = (
                int(255 * flash),
                int(255 * flash),
                0
            )
            
            pygame.draw.rect(self.screen, temp_color, rect)
            pygame.draw.rect(self.screen, Colors.YELLOW, rect, 2)
            
            # 添加小星星标记
            center_x = game_start_x + x * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
            center_y = y * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
            
            # 绘制闪烁星星
            star_blink = abs(math.sin(animation_timer * 0.4 + x * 0.5 + y * 0.3))
            star_color = (255, 255, int(255 * star_blink))
            pygame.draw.circle(self.screen, star_color, (center_x, center_y), 2)
            
            # 绘制星星光芒
            if star_blink > 0.7:
                for i in range(4):
                    angle = i * (math.pi / 2)
                    end_x = center_x + int(4 * math.cos(angle))
                    end_y = center_y + int(4 * math.sin(angle))
                    pygame.draw.line(self.screen, star_color, (center_x, center_y), (end_x, end_y), 1)
    
    def draw_obstacles(self, obstacles, animation_timer):
        """绘制障碍物"""
        game_start_x = GameConfig.SKILL_PANEL_WIDTH
        for obstacle in obstacles:
            x, y = obstacle
            rect = pygame.Rect(
                game_start_x + x * GameConfig.GRID_SIZE + 2,
                y * GameConfig.GRID_SIZE + 2,
                GameConfig.GRID_SIZE - 4,
                GameConfig.GRID_SIZE - 4
            )
            
            # 绘制障碍物主体
            pygame.draw.rect(self.screen, Colors.RED, rect)
            
            # 添加危险纹理
            center_x = game_start_x + x * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
            center_y = y * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
            
            # 绘制警告符号
            warning_color = Colors.YELLOW
            warning_size = 3 + int(2 * math.sin(animation_timer * 0.5))
            
            # 绘制X符号
            pygame.draw.line(self.screen, warning_color, 
                           (center_x - warning_size, center_y - warning_size),
                           (center_x + warning_size, center_y + warning_size), 2)
            pygame.draw.line(self.screen, warning_color, 
                           (center_x + warning_size, center_y - warning_size),
                           (center_x - warning_size, center_y + warning_size), 2)
            
            # 添加边框发光效果
            for i in range(3):
                glow_color = (255, 0, 0, 100 - i * 30)
                glow_rect = pygame.Rect(
                    game_start_x + x * GameConfig.GRID_SIZE + 1 - i,
                    y * GameConfig.GRID_SIZE + 1 - i,
                    GameConfig.GRID_SIZE - 2 + i * 2,
                    GameConfig.GRID_SIZE - 2 + i * 2
                )
                pygame.draw.rect(self.screen, glow_color, glow_rect, 1)
    
    def draw_particles(self, particles):
        """绘制粒子效果"""
        for particle in particles:
            particle.draw(self.screen)
    
    def draw_skill_panel(self, skill_system, animation_timer):
        """绘制左侧技能面板"""
        panel_width = 250  # 增加面板宽度
        panel_height = GameConfig.GAME_HEIGHT
        
        # 绘制面板背景 - 使用渐变
        for y in range(panel_height):
            ratio = y / panel_height
            r = int(25 * (1 - ratio) + 15 * ratio)
            g = int(20 * (1 - ratio) + 10 * ratio)
            b = int(35 * (1 - ratio) + 20 * ratio)
            color = (r, g, b)
            pygame.draw.line(self.screen, color, (0, y), (panel_width, y))
        
        # 绘制边框发光效果
        for i in range(3):
            alpha = 255 - i * 80
            line_color = (100, 150, 255, alpha)
            pygame.draw.line(self.screen, line_color, 
                           (panel_width - i, 0), 
                           (panel_width - i, panel_height), 1)
        
        # 面板内容起始位置
        panel_x = 10
        y_offset = 20
        
        # 技能系统标题 - 添加发光效果
        title = pygame.font.Font(None, 36).render('SKILL SYSTEM', True, Colors.NEON_BLUE)
        title_glow = pygame.font.Font(None, 36).render('SKILL SYSTEM', True, (0, 255, 255, 100))
        self.screen.blit(title_glow, (panel_x + 1, y_offset + 1))
        self.screen.blit(title, (panel_x, y_offset))
        y_offset += 40
        
        # 被动技能标题 - 添加动画效果
        pulse = 1 + 0.1 * math.sin(animation_timer * 0.2)
        passive_color = (
            min(255, int(Colors.NEON_GREEN[0] * pulse)),
            min(255, int(Colors.NEON_GREEN[1] * pulse)),
            min(255, int(Colors.NEON_GREEN[2] * pulse))
        )
        passive_title = pygame.font.Font(None, 24).render('PASSIVE SKILLS', True, passive_color)
        self.screen.blit(passive_title, (panel_x, y_offset))
        y_offset += 25
        
        # 绘制被动技能
        skill_names = skill_system.get_skill_names()
        skill_descriptions = skill_system.get_skill_descriptions()
        
        if skill_system.passive_skills:
            for i, skill in enumerate(skill_system.passive_skills):
                skill_name = skill_names.get(skill, skill)
                skill_desc = skill_descriptions.get(skill, '')
                skill_color = Colors.LIME
                
                # 绘制技能背景 - 添加渐变和发光效果
                skill_bg = pygame.Rect(panel_x, y_offset + i * 35, 230, 30)
                
                # 渐变背景
                for bg_y in range(skill_bg.y, skill_bg.y + skill_bg.height):
                    ratio = (bg_y - skill_bg.y) / skill_bg.height
                    r = int(50 * (1 - ratio) + 30 * ratio)
                    g = int(45 * (1 - ratio) + 25 * ratio)
                    b = int(55 * (1 - ratio) + 35 * ratio)
                    color = (r, g, b)
                    pygame.draw.line(self.screen, color, (skill_bg.x, bg_y), (skill_bg.x + skill_bg.width, bg_y))
                
                # 发光边框
                for glow in range(3):
                    glow_color = (skill_color[0]//3, skill_color[1]//3, skill_color[2]//3)
                    glow_rect = pygame.Rect(skill_bg.x - glow, skill_bg.y - glow, skill_bg.width + glow*2, skill_bg.height + glow*2)
                    pygame.draw.rect(self.screen, glow_color, glow_rect, 1)
                
                pygame.draw.rect(self.screen, skill_color, skill_bg, 2)
                
                # 技能名称
                skill_text = pygame.font.Font(None, 24).render(skill_name, True, skill_color)
                self.screen.blit(skill_text, (panel_x + 5, y_offset + i * 35 + 2))
                
                # 技能描述
                desc_text = pygame.font.Font(None, 24).render(skill_desc, True, Colors.WHITE)
                self.screen.blit(desc_text, (panel_x + 5, y_offset + i * 35 + 15))
        else:
            no_passive = pygame.font.Font(None, 24).render('None', True, Colors.GRAY)
            self.screen.blit(no_passive, (panel_x, y_offset))
        
        # 主动技能标题
        y_offset += len(skill_system.passive_skills) * 35 + 40
        active_title = pygame.font.Font(None, 24).render('ACTIVE SKILLS', True, Colors.ORANGE)
        self.screen.blit(active_title, (panel_x, y_offset))
        y_offset += 25
        
        # 绘制主动技能
        if skill_system.active_skills:
            for i, skill in enumerate(skill_system.active_skills):
                skill_name = skill_names.get(skill, skill)
                skill_desc = skill_descriptions.get(skill, '')
                cooldown = skill_system.skill_cooldowns.get(skill, 0)
                
                # 技能颜色（冷却中为灰色）
                skill_color = Colors.GRAY if cooldown > 0 else Colors.ORANGE
                
                # 绘制技能背景
                skill_bg = pygame.Rect(panel_x, y_offset + i * 40, 230, 35)
                pygame.draw.rect(self.screen, (40, 40, 40), skill_bg)
                pygame.draw.rect(self.screen, skill_color, skill_bg, 1)
                
                # 技能名称和快捷键
                skill_text = pygame.font.Font(None, 24).render(f'{i+1}. {skill_name}', True, skill_color)
                self.screen.blit(skill_text, (panel_x + 5, y_offset + i * 40 + 2))
                
                # 技能描述
                desc_text = pygame.font.Font(None, 24).render(skill_desc, True, Colors.WHITE)
                self.screen.blit(desc_text, (panel_x + 5, y_offset + i * 40 + 15))
                
                # 冷却时间
                if cooldown > 0:
                    cooldown_text = pygame.font.Font(None, 24).render(f'{cooldown//60}s', True, Colors.RED)
                    self.screen.blit(cooldown_text, (panel_x + 200, y_offset + i * 40 + 2))
        else:
            no_active = pygame.font.Font(None, 24).render('None', True, Colors.GRAY)
            self.screen.blit(no_active, (panel_x, y_offset))
        
        # 添加技能获取说明
        y_offset += len(skill_system.active_skills) * 40 + 50
        info_title = pygame.font.Font(None, 24).render('SKILL INFO', True, Colors.BLUE)
        self.screen.blit(info_title, (panel_x, y_offset))
        y_offset += 25
        
        info_lines = [
            '• Level up to get skills',
            '• Passive: Auto effects',
            '• Active: Press 1/2/3 to use',
            '• Max 5 passive skills',
            '• Max 3 active skills',
            '• Skills are permanent'
        ]
        
        for i, line in enumerate(info_lines):
            info_text = pygame.font.Font(None, 24).render(line, True, Colors.WHITE)
            self.screen.blit(info_text, (panel_x, y_offset + i * 18))
    
    def draw_ui(self, score, level, exp, exp_to_next_level, food_count):
        """绘制右侧UI信息"""
        # UI面板起始位置
        ui_x = GameConfig.SKILL_PANEL_WIDTH + GameConfig.GAME_WIDTH + 10
        
        # 绘制标题
        title_text = pygame.font.Font(None, 36).render('SNAKE GAME', True, Colors.GOLD)
        self.screen.blit(title_text, (ui_x, 20))
        
        # 绘制分数
        score_text = pygame.font.Font(None, 36).render(f'Score: {score}', True, Colors.GOLD)
        self.screen.blit(score_text, (ui_x, 60))
        
        # 绘制等级和经验值
        level_text = pygame.font.Font(None, 24).render(f'Level: {level}', True, Colors.LIME)
        self.screen.blit(level_text, (ui_x, 100))
        
        exp_text = pygame.font.Font(None, 24).render(f'EXP: {exp}/{exp_to_next_level}', True, Colors.LIME)
        self.screen.blit(exp_text, (ui_x, 125))
        
        # 绘制经验条
        exp_bar_width = 180
        exp_bar_height = 10
        exp_bar_x = ui_x
        exp_bar_y = 150
        
        # 经验条背景
        exp_bar_bg = pygame.Rect(exp_bar_x, exp_bar_y, exp_bar_width, exp_bar_height)
        pygame.draw.rect(self.screen, (50, 50, 50), exp_bar_bg)
        
        # 经验条进度
        if exp_to_next_level > 0:
            exp_progress = exp / exp_to_next_level
            exp_fill_width = int(exp_bar_width * exp_progress)
            exp_fill = pygame.Rect(exp_bar_x, exp_bar_y, exp_fill_width, exp_bar_height)
            pygame.draw.rect(self.screen, Colors.LIME, exp_fill)
        
        # 经验条边框
        pygame.draw.rect(self.screen, Colors.WHITE, exp_bar_bg, 1)
        
        # 显示下一个大食物
        next_big_food = 3 - (food_count % 3)
        if next_big_food == 3:
            next_big_food = 0
        next_text = pygame.font.Font(None, 24).render(f'Next big food: {next_big_food}', True, Colors.PURPLE)
        self.screen.blit(next_text, (ui_x, 170))
        
        # 绘制控制说明
        controls_y = GameConfig.WINDOW_HEIGHT - 150
        control_title = pygame.font.Font(None, 24).render('CONTROLS', True, Colors.WHITE)
        self.screen.blit(control_title, (ui_x, controls_y))
        
        controls = [
            'Arrow Keys: Move',
            'Space: Pause',
            'R: Restart',
            'ESC: Exit',
            '1/2/3: Use Active Skills'
        ]
        
        for i, control in enumerate(controls):
            control_text = pygame.font.Font(None, 24).render(control, True, Colors.WHITE)
            self.screen.blit(control_text, (ui_x, controls_y + 25 + i * 20))
    
    def draw_game_over(self, score):
        """绘制游戏结束画面"""
        # 半透明遮罩 - 只覆盖游戏区域
        overlay = pygame.Surface((GameConfig.GAME_WIDTH, GameConfig.GAME_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(Colors.BLACK)
        self.screen.blit(overlay, (GameConfig.SKILL_PANEL_WIDTH, 0))
        
        # 游戏结束文本
        game_over_text = pygame.font.Font(None, 36).render('GAME OVER!', True, Colors.RED)
        score_text = pygame.font.Font(None, 36).render(f'Final Score: {score}', True, Colors.WHITE)
        restart_text = pygame.font.Font(None, 24).render('Press R to Restart', True, Colors.WHITE)
        
        # 居中显示在游戏区域
        game_over_rect = game_over_text.get_rect(center=(GameConfig.SKILL_PANEL_WIDTH + GameConfig.GAME_WIDTH // 2, GameConfig.GAME_HEIGHT // 2 - 50))
        score_rect = score_text.get_rect(center=(GameConfig.SKILL_PANEL_WIDTH + GameConfig.GAME_WIDTH // 2, GameConfig.GAME_HEIGHT // 2))
        restart_rect = restart_text.get_rect(center=(GameConfig.SKILL_PANEL_WIDTH + GameConfig.GAME_WIDTH // 2, GameConfig.GAME_HEIGHT // 2 + 50))
        
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(restart_text, restart_rect)
    
    def draw_pause(self):
        """绘制暂停画面"""
        # 半透明遮罩 - 只覆盖游戏区域
        overlay = pygame.Surface((GameConfig.GAME_WIDTH, GameConfig.GAME_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(Colors.BLACK)
        self.screen.blit(overlay, (GameConfig.SKILL_PANEL_WIDTH, 0))
        
        pause_text = pygame.font.Font(None, 36).render('PAUSED', True, Colors.WHITE)
        pause_rect = pause_text.get_rect(center=(GameConfig.SKILL_PANEL_WIDTH + GameConfig.GAME_WIDTH // 2, GameConfig.GAME_HEIGHT // 2))
        self.screen.blit(pause_text, pause_rect)
