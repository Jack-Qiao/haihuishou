import pygame
import sys
import random
import math
from constants import Colors, GameConfig, Direction
from particle import Particle
from skill_system import SkillSystem
from renderer import Renderer

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((GameConfig.WINDOW_WIDTH, GameConfig.WINDOW_HEIGHT))
        pygame.display.set_caption('Snake Game')
        self.clock = pygame.time.Clock()
        
        # 使用系统字体以支持中文显示
        try:
            # 尝试多个中文字体
            chinese_fonts = ['simhei', 'microsoftyahei', 'simsun', 'arial', 'helvetica']
            font_loaded = False
            for font_name in chinese_fonts:
                try:
                    self.font = pygame.font.SysFont(font_name, 36)
                    self.small_font = pygame.font.SysFont(font_name, 24)
                    # 测试中文字符渲染
                    test_surface = self.font.render('测试', True, (255, 255, 255))
                    font_loaded = True
                    break
                except:
                    continue
            
            if not font_loaded:
                # 如果所有中文字体都不可用，回退到默认字体
                self.font = pygame.font.Font(None, 36)
                self.small_font = pygame.font.Font(None, 24)
        except:
            # 如果系统字体不可用，回退到默认字体
            self.font = pygame.font.Font(None, 36)
            self.small_font = pygame.font.Font(None, 24)
        
        # 初始化系统
        self.renderer = Renderer(self.screen)
        self.skill_system = SkillSystem()
        
        # 动画相关变量
        self.animation_timer = 0
        self.food_animation_timer = 0
        self.particle_effects = []
        
        # 障碍物系统
        self.obstacles = []
        self.obstacle_timer = 0
        
        # 临时食物系统
        self.temp_foods = []
        
        self.reset_game()
    
    def reset_game(self):
        """重置游戏状态"""
        # 蛇的初始位置和方向
        self.snake = [(GameConfig.GRID_WIDTH // 2, GameConfig.GRID_HEIGHT // 2)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        
        # 生成食物
        self.food = self.generate_food()
        self.food_count = 0  # 食物计数器
        
        # 游戏状态
        self.score = 0
        self.game_over = False
        self.paused = False
        
        # 重置系统
        self.skill_system.reset()
        
        # 重置障碍物系统
        self.obstacles = []
        self.obstacle_timer = 0
        
        # 重置临时食物
        self.temp_foods = []
    
    def generate_food(self):
        """生成食物的随机位置"""
        while True:
            food_pos = (
                random.randint(0, GameConfig.GRID_WIDTH - 1),
                random.randint(0, GameConfig.GRID_HEIGHT - 1)
            )
            if (food_pos not in self.snake and 
                food_pos not in self.obstacles and
                food_pos not in self.temp_foods):
                return food_pos
    
    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                
                # 方向控制
                if not self.paused and not self.game_over:
                    if event.key == pygame.K_UP and self.direction != Direction.DOWN:
                        self.next_direction = Direction.UP
                    elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                        self.next_direction = Direction.DOWN
                    elif event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                        self.next_direction = Direction.LEFT
                    elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                        self.next_direction = Direction.RIGHT
                    
                    # 主动技能快捷键
                    elif event.key == pygame.K_1:
                        self.skill_system.use_active_skill(0, self)
                    elif event.key == pygame.K_2:
                        self.skill_system.use_active_skill(1, self)
                    elif event.key == pygame.K_3:
                        self.skill_system.use_active_skill(2, self)
        
        return True
    
    def update_game(self):
        """更新游戏状态"""
        if self.paused or self.game_over:
            return
        
        # 更新动画计时器
        self.animation_timer += 1
        self.food_animation_timer += 1
        
        # 更新粒子效果
        self.particle_effects = [p for p in self.particle_effects if p.update()]
        
        # 更新技能冷却时间
        self.skill_system.update_cooldowns()
        
        # 更新蛇的方向
        self.direction = self.next_direction
        
        # 获取蛇头位置
        head_x, head_y = self.snake[0]
        
        # 根据方向移动蛇头
        if self.direction == Direction.UP:
            new_head = (head_x, head_y - 1)
        elif self.direction == Direction.DOWN:
            new_head = (head_x, head_y + 1)
        elif self.direction == Direction.LEFT:
            new_head = (head_x - 1, head_y)
        elif self.direction == Direction.RIGHT:
            new_head = (head_x + 1, head_y)
        
        # 检查碰撞
        if self.check_collision(new_head):
            # 检查无敌状态
            if hasattr(self, 'invincible_timer') and self.invincible_timer > 0:
                self.invincible_timer -= 1
                self.create_shield_particles()
                return
            
            # 检查被动技能
            if 'thick_skin' in self.skill_system.passive_skills and random.random() < 0.3:
                # 厚皮技能：30%概率免疫伤害
                self.create_shield_particles()
                return
            elif 'ghost_mode' in self.skill_system.passive_skills and random.random() < 0.2:
                # 幽灵模式：20%概率穿透障碍物
                self.create_shield_particles()
                # 继续移动，不处理碰撞
            else:
                self.game_over = True
                # 添加死亡粒子效果
                self.create_death_particles()
                return
        
        # 处理穿越边界后的新位置
        x, y = new_head
        x = x % GameConfig.GRID_WIDTH
        y = y % GameConfig.GRID_HEIGHT
        new_head = (x, y)
        
        # 移动蛇
        self.snake.insert(0, new_head)
        
        # 检查是否吃到食物
        if new_head == self.food:
            # 判断是否是大食物
            is_big_food = self.food_count % 3 == 2  # 每3个食物中的第3个是大食物
            
            # 计算得分（考虑技能效果）
            base_score = 50 if is_big_food else 10  # 大食物50分，普通食物10分
            if 'double_points' in self.skill_system.passive_skills:
                base_score *= 2
            if 'lucky_charm' in self.skill_system.passive_skills and random.random() < 0.2:
                base_score *= 3  # 幸运符：20%概率三倍得分
                self.create_lucky_particles()
            self.score += base_score
            
            # 添加经验值
            exp_gain = 100 if is_big_food else 20  # 大食物100经验，普通食物20经验
            self.skill_system.add_exp(exp_gain)
            
            # 大食物增加5格长度，普通食物增加1格
            if is_big_food:
                # 大食物不减少蛇尾，相当于增加5格
                for _ in range(4):  # 额外增加4格（加上原本的1格，总共5格）
                    self.snake.append(self.snake[-1])  # 复制最后一格
                self.create_big_food_particles()
            else:
                # 普通食物正常处理（不删除蛇尾，相当于增加1格）
                pass
            
            self.food_count += 1
            self.food = self.generate_food()
            # 添加粒子效果
            self.create_food_particles()
        
        # 检查是否吃到临时食物
        elif new_head in self.temp_foods:
            # 临时食物给予5分和10经验
            temp_score = 5
            if 'double_points' in self.skill_system.passive_skills:
                temp_score *= 2
            self.score += temp_score
            self.skill_system.add_exp(10)
            
            # 移除被吃掉的临时食物
            self.temp_foods.remove(new_head)
            # 添加粒子效果
            self.create_food_particles()
        else:
            self.snake.pop()
        
        # 应用被动技能效果
        self.skill_system.apply_passive_effects(self)
        
        # 生成障碍物
        self.obstacle_timer += 1
        if self.obstacle_timer > 300:  # 每5秒生成一个障碍物
            self.generate_obstacle()
            self.obstacle_timer = 0
    
    def check_collision(self, new_head):
        """检查碰撞"""
        x, y = new_head
        
        # 检查是否撞到自己
        if new_head in self.snake:
            return True
        
        # 检查是否撞到障碍物
        if new_head in self.obstacles:
            return True
        
        return False
    
    def generate_obstacle(self):
        """生成障碍物"""
        for _ in range(10):  # 最多尝试10次
            x = random.randint(0, GameConfig.GRID_WIDTH - 1)
            y = random.randint(0, GameConfig.GRID_HEIGHT - 1)
            obstacle_pos = (x, y)
            
            if (obstacle_pos not in self.snake and 
                obstacle_pos != self.food and
                obstacle_pos not in self.obstacles and
                obstacle_pos not in self.temp_foods):
                self.obstacles.append(obstacle_pos)
                break
    
    def create_food_particles(self):
        """创建食物粒子效果"""
        head_x, head_y = self.snake[0]
        center_x = head_x * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
        center_y = head_y * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
        
        for _ in range(8):
            velocity_x = random.uniform(-2, 2)
            velocity_y = random.uniform(-3, -1)
            color = random.choice([Colors.GOLD, Colors.ORANGE, Colors.YELLOW])
            self.particle_effects.append(Particle(center_x, center_y, color, velocity_x, velocity_y))
    
    def create_death_particles(self):
        """创建死亡粒子效果"""
        head_x, head_y = self.snake[0]
        center_x = head_x * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
        center_y = head_y * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
        
        for _ in range(15):
            velocity_x = random.uniform(-3, 3)
            velocity_y = random.uniform(-3, 3)
            color = random.choice([Colors.RED, Colors.MAROON])
            self.particle_effects.append(Particle(center_x, center_y, color, velocity_x, velocity_y))
    
    def create_shield_particles(self):
        """创建护盾粒子效果"""
        head_x, head_y = self.snake[0]
        center_x = head_x * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
        center_y = head_y * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
        
        for _ in range(10):
            velocity_x = random.uniform(-2, 2)
            velocity_y = random.uniform(-2, 2)
            color = random.choice([Colors.BLUE, Colors.LIGHT_BLUE, Colors.WHITE])
            self.particle_effects.append(Particle(center_x, center_y, color, velocity_x, velocity_y))
    
    def create_big_food_particles(self):
        """创建大食物粒子效果"""
        head_x, head_y = self.snake[0]
        center_x = head_x * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
        center_y = head_y * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
        
        for _ in range(15):
            velocity_x = random.uniform(-3, 3)
            velocity_y = random.uniform(-3, 3)
            color = random.choice([Colors.PURPLE, Colors.PINK, Colors.GOLD])
            self.particle_effects.append(Particle(center_x, center_y, color, velocity_x, velocity_y))
    
    def create_lucky_particles(self):
        """创建幸运粒子效果"""
        head_x, head_y = self.snake[0]
        center_x = head_x * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
        center_y = head_y * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
        
        for _ in range(10):
            velocity_x = random.uniform(-2, 2)
            velocity_y = random.uniform(-4, -1)
            color = random.choice([Colors.GOLD, Colors.YELLOW])
            self.particle_effects.append(Particle(center_x, center_y, color, velocity_x, velocity_y))
    
    def create_clear_particles(self):
        """创建清除障碍物粒子效果"""
        for obstacle in self.obstacles:
            x, y = obstacle
            center_x = x * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
            center_y = y * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
            
            for _ in range(5):
                velocity_x = random.uniform(-3, 3)
                velocity_y = random.uniform(-3, 3)
                color = Colors.WHITE
                self.particle_effects.append(Particle(center_x, center_y, color, velocity_x, velocity_y))
    
    def teleport_to_safe_position(self):
        """传送到安全位置"""
        for _ in range(100):  # 最多尝试100次
            new_x = random.randint(2, GameConfig.GRID_WIDTH - 3)
            new_y = random.randint(2, GameConfig.GRID_HEIGHT - 3)
            new_pos = (new_x, new_y)
            
            # 检查位置是否安全
            if (new_pos not in self.obstacles and 
                new_pos != self.food and
                new_pos not in self.snake):
                # 传送蛇头
                self.snake[0] = new_pos
                self.create_teleport_particles()
                break
    
    def create_teleport_particles(self):
        """创建传送粒子效果"""
        head_x, head_y = self.snake[0]
        center_x = head_x * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
        center_y = head_y * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
        
        for _ in range(15):
            velocity_x = random.uniform(-4, 4)
            velocity_y = random.uniform(-4, 4)
            color = random.choice([Colors.PURPLE, Colors.PINK])
            self.particle_effects.append(Particle(center_x, center_y, color, velocity_x, velocity_y))
    
    def create_food_rain(self):
        """创建食物雨效果"""
        # 生成3-5个临时食物
        num_foods = random.randint(3, 5)
        for _ in range(num_foods):
            while True:
                x = random.randint(0, GameConfig.GRID_WIDTH - 1)
                y = random.randint(0, GameConfig.GRID_HEIGHT - 1)
                pos = (x, y)
                
                if (pos not in self.snake and 
                    pos != self.food and 
                    pos not in self.obstacles):
                    # 创建临时食物（黄色）
                    self.temp_foods.append(pos)
                    break
        
        # 创建食物雨粒子效果
        for _ in range(20):
            x = random.randint(0, GameConfig.GRID_WIDTH - 1)
            y = random.randint(0, GameConfig.GRID_HEIGHT - 1)
            center_x = x * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
            center_y = y * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
            
            velocity_x = random.uniform(-2, 2)
            velocity_y = random.uniform(-3, -1)
            color = Colors.YELLOW
            self.particle_effects.append(Particle(center_x, center_y, color, velocity_x, velocity_y))
    
    def draw(self):
        """绘制游戏画面"""
        # 绘制渐变背景
        self.renderer.draw_gradient_background(self.animation_timer)
        
        # 绘制粒子效果
        self.renderer.draw_particles(self.particle_effects)
        
        # 绘制障碍物
        self.renderer.draw_obstacles(self.obstacles, self.animation_timer)
        
        # 绘制蛇
        self.renderer.draw_snake(self.snake, self.direction, self.animation_timer)
        
        # 绘制食物
        self.renderer.draw_food(self.food, self.food_count, self.food_animation_timer, self.animation_timer)
        
        # 绘制临时食物
        self.renderer.draw_temp_foods(self.temp_foods, self.animation_timer)
        
        # 绘制技能面板
        self.renderer.draw_skill_panel(self.skill_system, self.animation_timer)
        
        # 绘制UI
        self.renderer.draw_ui(self.score, self.skill_system.level, self.skill_system.exp, 
                            self.skill_system.exp_to_next_level, self.food_count)
        
        # 游戏结束显示
        if self.game_over:
            self.renderer.draw_game_over(self.score)
        elif self.paused:
            self.renderer.draw_pause()
        
        pygame.display.flip()
    
    def run(self):
        """运行游戏主循环"""
        running = True
        
        while running:
            running = self.handle_events()
            self.update_game()
            self.draw()
            
            # 根据技能调整游戏速度
            current_speed = GameConfig.GAME_SPEED
            if 'speed_boost' in self.skill_system.passive_skills:
                current_speed = int(current_speed * 1.5)  # 速度提升50%
            
            # 超高速技能效果
            if hasattr(self, 'super_speed_timer') and self.super_speed_timer > 0:
                current_speed = int(current_speed * 3)  # 速度提升300%
                self.super_speed_timer -= 1
            
            self.clock.tick(current_speed)
        
        pygame.quit()
        sys.exit()

def main():
    """主函数"""
    game = SnakeGame()
    game.run()

if __name__ == '__main__':
    main()
