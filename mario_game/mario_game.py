import pygame
import random
import math
from enum import Enum

# 初始化pygame
pygame.init()

# 颜色定义
class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    BROWN = (139, 69, 19)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 165, 0)
    GRAY = (128, 128, 128)
    LIGHT_BLUE = (135, 206, 235)
    DARK_GREEN = (0, 100, 0)

# 游戏状态
class GameState(Enum):
    PLAYING = 1
    GAME_OVER = 2
    PAUSED = 3
    VICTORY = 4

# 游戏配置
class GameConfig:
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 600
    FPS = 60
    GRAVITY = 0.8
    JUMP_STRENGTH = -15
    PLAYER_SPEED = 5
    CAMERA_SPEED = 3

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.lives = 3
        self.score = 0
        self.invulnerable = False
        self.invulnerable_timer = 0
        
    def update(self, platforms):
        # 应用重力
        if not self.on_ground:
            self.vel_y += GameConfig.GRAVITY
        
        # 更新位置
        self.x += self.vel_x
        self.y += self.vel_y
        
        # 检查平台碰撞
        self.check_platform_collision(platforms)
        
        # 更新无敌状态
        if self.invulnerable:
            self.invulnerable_timer -= 1
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
        
        # 限制垂直位置（防止掉出屏幕底部）
        if self.y > GameConfig.WINDOW_HEIGHT:
            self.take_damage()
    
    def check_platform_collision(self, platforms):
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.on_ground = False
        
        for platform in platforms:
            platform_rect = pygame.Rect(platform['x'], platform['y'], platform['width'], platform['height'])
            
            if player_rect.colliderect(platform_rect):
                # 从上方落下
                if self.vel_y > 0 and self.y < platform['y']:
                    self.y = platform['y'] - self.height
                    self.vel_y = 0
                    self.on_ground = True
                # 从下方撞击
                elif self.vel_y < 0 and self.y > platform['y']:
                    self.y = platform['y'] + platform['height']
                    self.vel_y = 0
                # 从左侧撞击 - 简化逻辑
                elif self.vel_x > 0 and self.x < platform['x']:
                    self.x = platform['x'] - self.width
                    self.vel_x = 0  # 停止水平移动
                # 从右侧撞击 - 简化逻辑
                elif self.vel_x < 0 and self.x > platform['x']:
                    self.x = platform['x'] + platform['width']
                    self.vel_x = 0  # 停止水平移动
    
    def jump(self):
        if self.on_ground:
            self.vel_y = GameConfig.JUMP_STRENGTH
            self.on_ground = False
    
    def move_left(self):
        self.vel_x = -GameConfig.PLAYER_SPEED
        self.facing_right = False
    
    def move_right(self):
        self.vel_x = GameConfig.PLAYER_SPEED
        self.facing_right = True
    
    def stop_horizontal(self):
        self.vel_x = 0
    
    def take_damage(self):
        if not self.invulnerable:
            self.lives -= 1
            self.invulnerable = True
            self.invulnerable_timer = 120  # 2秒无敌时间
            self.x = 50  # 重置位置
            self.y = 400
            self.vel_x = 0
            self.vel_y = 0
    
    def add_score(self, points):
        self.score += points
    
    def draw(self, screen, camera_x):
        # 绘制玛丽（简单的矩形表示）
        color = Colors.RED if not self.invulnerable or (self.invulnerable_timer // 5) % 2 else Colors.ORANGE
        pygame.draw.rect(screen, color, (self.x - camera_x, self.y, self.width, self.height))
        
        # 绘制眼睛
        eye_color = Colors.WHITE
        pygame.draw.circle(screen, eye_color, (int(self.x - camera_x + 8), int(self.y + 8)), 3)
        pygame.draw.circle(screen, eye_color, (int(self.x - camera_x + 24), int(self.y + 8)), 3)
        
        # 绘制帽子
        pygame.draw.rect(screen, Colors.RED, (self.x - camera_x, self.y - 5, self.width, 8))

class Enemy:
    def __init__(self, x, y, enemy_type="goomba"):
        self.x = x
        self.y = y
        self.width = 24
        self.height = 24
        self.vel_x = -1
        self.alive = True
        self.enemy_type = enemy_type
        
    def update(self, platforms):
        if not self.alive:
            return
            
        # 移动敌人
        self.x += self.vel_x
        
        # 应用重力
        self.y += GameConfig.GRAVITY
        
        # 检查平台碰撞
        enemy_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        on_ground = False
        
        for platform in platforms:
            platform_rect = pygame.Rect(platform['x'], platform['y'], platform['width'], platform['height'])
            
            if enemy_rect.colliderect(platform_rect):
                # 如果敌人在平台上方
                if self.y < platform['y']:
                    self.y = platform['y'] - self.height
                    on_ground = True
                # 如果敌人撞到平台侧面，改变方向
                elif self.vel_x > 0 and self.x < platform['x']:
                    self.x = platform['x'] - self.width
                    self.vel_x *= -1
                elif self.vel_x < 0 and self.x > platform['x']:
                    self.x = platform['x'] + platform['width']
                    self.vel_x *= -1
        
        # 检查是否到达平台边缘，如果是则改变方向
        if on_ground:
            # 检查前方是否有地面
            next_x = self.x + self.vel_x * 10  # 预测下一个位置
            ground_ahead = False
            
            for platform in platforms:
                platform_rect = pygame.Rect(platform['x'], platform['y'], platform['width'], platform['height'])
                if (next_x + self.width > platform['x'] and 
                    next_x < platform['x'] + platform['width'] and
                    self.y + self.height >= platform['y'] and
                    self.y + self.height <= platform['y'] + 20):
                    ground_ahead = True
                    break
            
            # 如果前方没有地面，改变方向
            if not ground_ahead:
                self.vel_x *= -1
    
    def draw(self, screen, camera_x):
        if self.alive:
            color = Colors.BROWN if self.enemy_type == "goomba" else Colors.GREEN
            pygame.draw.rect(screen, color, (self.x - camera_x, self.y, self.width, self.height))
            # 绘制眼睛
            pygame.draw.circle(screen, Colors.WHITE, (int(self.x - camera_x + 6), int(self.y + 6)), 2)
            pygame.draw.circle(screen, Colors.WHITE, (int(self.x - camera_x + 18), int(self.y + 6)), 2)

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.collected = False
        self.animation_timer = 0
        
    def update(self):
        self.animation_timer += 1
        
    def draw(self, screen, camera_x):
        if not self.collected:
            # 简单的旋转动画
            scale = 1 + 0.2 * math.sin(self.animation_timer * 0.2)
            size = int(self.width * scale)
            pygame.draw.circle(screen, Colors.YELLOW, 
                             (int(self.x - camera_x + self.width//2), int(self.y + self.height//2)), 
                             size//2)
            pygame.draw.circle(screen, Colors.ORANGE, 
                             (int(self.x - camera_x + self.width//2), int(self.y + self.height//2)), 
                             size//4)

class MarioGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((GameConfig.WINDOW_WIDTH, GameConfig.WINDOW_HEIGHT))
        pygame.display.set_caption('Super Mario Game')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.game_state = GameState.PLAYING
        self.camera_x = 0
        
        # 初始化游戏对象
        self.player = Player(50, 400)
        self.enemies = []
        self.coins = []
        self.platforms = []
        
        self.create_level()
    
    def create_level(self):
        """创建游戏关卡"""
        # 地面平台
        for i in range(0, 2000, 100):
            self.platforms.append({
                'x': i, 'y': GameConfig.WINDOW_HEIGHT - 50, 
                'width': 100, 'height': 50, 'type': 'ground'
            })
        
        # 浮空平台
        platforms_data = [
            (200, 450, 100, 20),
            (400, 350, 100, 20),
            (600, 250, 100, 20),
            (800, 400, 150, 20),
            (1000, 300, 100, 20),
            (1200, 200, 100, 20),
            (1400, 350, 120, 20),
            (1600, 450, 100, 20),
        ]
        
        for x, y, width, height in platforms_data:
            self.platforms.append({
                'x': x, 'y': y, 'width': width, 'height': height, 'type': 'platform'
            })
        
        # 添加敌人
        enemy_positions = [300, 500, 700, 900, 1100, 1300, 1500]
        for x in enemy_positions:
            self.enemies.append(Enemy(x, GameConfig.WINDOW_HEIGHT - 100))
        
        # 添加金币
        coin_positions = [
            (250, 400), (450, 300), (650, 200), (850, 350),
            (1050, 250), (1250, 150), (1450, 300), (1650, 400)
        ]
        for x, y in coin_positions:
            self.coins.append(Coin(x, y))
    
    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_r and self.game_state == GameState.GAME_OVER:
                    self.restart_game()
        
        return True
    
    def handle_input(self):
        """处理持续输入"""
        if self.game_state != GameState.PLAYING:
            return
            
        keys = pygame.key.get_pressed()
        
        # 重置水平速度
        self.player.vel_x = 0
        
        # 处理水平移动
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.vel_x = -GameConfig.PLAYER_SPEED
            self.player.facing_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.vel_x = GameConfig.PLAYER_SPEED
            self.player.facing_right = True
        
        # 处理跳跃（可以与移动同时进行）
        if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player.jump()
    
    def update_game(self):
        """更新游戏状态"""
        if self.game_state != GameState.PLAYING:
            return
        
        # 处理输入（在更新玩家之前）
        self.handle_input()
        
        # 更新玩家
        self.player.update(self.platforms)
        
        # 更新敌人
        for enemy in self.enemies:
            enemy.update(self.platforms)
        
        # 更新金币
        for coin in self.coins:
            coin.update()
        
        # 检查碰撞
        self.check_collisions()
        
        # 更新摄像机
        self.update_camera()
        
        # 检查游戏结束条件
        if self.player.lives <= 0:
            self.game_state = GameState.GAME_OVER
        
        # 检查胜利条件（收集所有金币）
        if all(coin.collected for coin in self.coins):
            self.game_state = GameState.VICTORY
    
    def check_collisions(self):
        """检查碰撞"""
        player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
        
        # 检查与敌人的碰撞
        for enemy in self.enemies:
            if not enemy.alive:
                continue
                
            enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
            
            if player_rect.colliderect(enemy_rect):
                # 如果玩家从上方跳到敌人身上
                if self.player.vel_y > 0 and self.player.y < enemy.y:
                    enemy.alive = False
                    self.player.vel_y = GameConfig.JUMP_STRENGTH // 2  # 小跳
                    self.player.add_score(100)
                else:
                    self.player.take_damage()
        
        # 检查与金币的碰撞
        for coin in self.coins:
            if coin.collected:
                continue
                
            coin_rect = pygame.Rect(coin.x, coin.y, coin.width, coin.height)
            
            if player_rect.colliderect(coin_rect):
                coin.collected = True
                self.player.add_score(200)
    
    def update_camera(self):
        """更新摄像机位置"""
        target_x = self.player.x - GameConfig.WINDOW_WIDTH // 3
        self.camera_x += (target_x - self.camera_x) * 0.1
        
        # 限制摄像机范围
        self.camera_x = max(0, self.camera_x)
    
    def draw(self):
        """绘制游戏画面"""
        # 绘制天空背景
        self.screen.fill(Colors.LIGHT_BLUE)
        
        # 绘制平台
        self.draw_platforms()
        
        # 绘制金币
        for coin in self.coins:
            coin.draw(self.screen, self.camera_x)
        
        # 绘制敌人
        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera_x)
        
        # 绘制玩家
        self.player.draw(self.screen, self.camera_x)
        
        # 绘制UI
        self.draw_ui()
        
        # 绘制游戏状态
        if self.game_state == GameState.GAME_OVER:
            self.draw_game_over()
        elif self.game_state == GameState.VICTORY:
            self.draw_victory()
        
        pygame.display.flip()
    
    def draw_platforms(self):
        """绘制平台"""
        for platform in self.platforms:
            color = Colors.BROWN if platform['type'] == 'ground' else Colors.GREEN
            pygame.draw.rect(self.screen, color, 
                           (platform['x'] - self.camera_x, platform['y'], 
                            platform['width'], platform['height']))
            
            # 绘制平台边框
            pygame.draw.rect(self.screen, Colors.DARK_GREEN, 
                           (platform['x'] - self.camera_x, platform['y'], 
                            platform['width'], platform['height']), 2)
    
    def draw_ui(self):
        """绘制用户界面"""
        # 绘制分数
        score_text = self.font.render(f'Score: {self.player.score}', True, Colors.WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # 绘制生命
        lives_text = self.font.render(f'Lives: {self.player.lives}', True, Colors.WHITE)
        self.screen.blit(lives_text, (10, 50))
        
        # 绘制控制说明
        controls = [
            'Arrow Keys / WASD: Move',
            'Space/Up/W: Jump',
            'Can jump while moving!',
            'ESC: Exit',
            'R: Restart (when game over)'
        ]
        
        for i, control in enumerate(controls):
            control_text = self.small_font.render(control, True, Colors.WHITE)
            self.screen.blit(control_text, (10, GameConfig.WINDOW_HEIGHT - 100 + i * 20))
    
    def draw_game_over(self):
        """绘制游戏结束画面"""
        overlay = pygame.Surface((GameConfig.WINDOW_WIDTH, GameConfig.WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(Colors.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font.render('GAME OVER!', True, Colors.RED)
        score_text = self.font.render(f'Final Score: {self.player.score}', True, Colors.WHITE)
        restart_text = self.small_font.render('Press R to Restart', True, Colors.WHITE)
        
        game_over_rect = game_over_text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, GameConfig.WINDOW_HEIGHT // 2 - 50))
        score_rect = score_text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, GameConfig.WINDOW_HEIGHT // 2))
        restart_rect = restart_text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, GameConfig.WINDOW_HEIGHT // 2 + 50))
        
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(restart_text, restart_rect)
    
    def draw_victory(self):
        """绘制胜利画面"""
        overlay = pygame.Surface((GameConfig.WINDOW_WIDTH, GameConfig.WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(Colors.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        victory_text = self.font.render('VICTORY!', True, Colors.YELLOW)
        score_text = self.font.render(f'Final Score: {self.player.score}', True, Colors.WHITE)
        restart_text = self.small_font.render('Press R to Play Again', True, Colors.WHITE)
        
        victory_rect = victory_text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, GameConfig.WINDOW_HEIGHT // 2 - 50))
        score_rect = score_text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, GameConfig.WINDOW_HEIGHT // 2))
        restart_rect = restart_text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, GameConfig.WINDOW_HEIGHT // 2 + 50))
        
        self.screen.blit(victory_text, victory_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(restart_text, restart_rect)
    
    def restart_game(self):
        """重新开始游戏"""
        self.game_state = GameState.PLAYING
        self.camera_x = 0
        self.player = Player(50, 400)
        self.enemies = []
        self.coins = []
        self.platforms = []
        self.create_level()
    
    def run(self):
        """运行游戏主循环"""
        running = True
        
        while running:
            running = self.handle_events()
            self.update_game()
            self.draw()
            self.clock.tick(GameConfig.FPS)
        
        pygame.quit()

def main():
    """主函数"""
    game = MarioGame()
    game.run()

if __name__ == '__main__':
    main()
