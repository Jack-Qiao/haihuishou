import random
import math
from constants import Colors, GameConfig

class SkillSystem:
    def __init__(self):
        self.passive_skills = []
        self.active_skills = []
        self.skill_cooldowns = {}
        self.level = 1
        self.exp = 0
        self.exp_to_next_level = 100
    
    def add_exp(self, amount):
        """添加经验值"""
        self.exp += amount
        if self.exp >= self.exp_to_next_level:
            self.level_up()
    
    def level_up(self):
        """升级"""
        self.level += 1
        self.exp -= self.exp_to_next_level
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        
        # 定义技能池
        passive_skills = [
            'speed_boost', 'double_points', 'magnet', 'thick_skin', 
            'regeneration', 'lucky_charm', 'ghost_mode', 'iron_stomach'
        ]
        active_skills = [
            'shield', 'teleport', 'time_slow', 'food_rain', 
            'obstacle_clear', 'super_speed', 'invincibility'
        ]
        
        # 随机选择技能类型
        skill_type = random.choice(['passive', 'active'])
        
        if skill_type == 'passive':
            available = [s for s in passive_skills if s not in self.passive_skills]
            if available and len(self.passive_skills) < 5:
                new_skill = random.choice(available)
                self.passive_skills.append(new_skill)
        else:
            available = [s for s in active_skills if s not in self.active_skills]
            if available and len(self.active_skills) < 3:
                new_skill = random.choice(available)
                self.active_skills.append(new_skill)
                # 初始化冷却时间
                self.skill_cooldowns[new_skill] = 0
    
    def use_active_skill(self, skill_index, game):
        """使用主动技能"""
        if skill_index >= len(self.active_skills):
            return
        
        skill = self.active_skills[skill_index]
        
        # 检查冷却时间
        if self.skill_cooldowns.get(skill, 0) > 0:
            return
        
        # 使用技能
        if skill == 'shield':
            self.skill_cooldowns[skill] = 600  # 10秒冷却
            game.invincible_timer = 180  # 3秒无敌
            game.create_shield_particles()
        
        elif skill == 'teleport':
            self.skill_cooldowns[skill] = 300  # 5秒冷却
            game.teleport_to_safe_position()
        
        elif skill == 'time_slow':
            self.skill_cooldowns[skill] = 900  # 15秒冷却
            game.time_slow_timer = 300  # 5秒效果
        
        elif skill == 'food_rain':
            self.skill_cooldowns[skill] = 1200  # 20秒冷却
            game.create_food_rain()
        
        elif skill == 'obstacle_clear':
            self.skill_cooldowns[skill] = 1800  # 30秒冷却
            game.obstacles.clear()
            game.create_clear_particles()
        
        elif skill == 'super_speed':
            self.skill_cooldowns[skill] = 480  # 8秒冷却
            game.super_speed_timer = 240  # 4秒效果
        
        elif skill == 'invincibility':
            self.skill_cooldowns[skill] = 1500  # 25秒冷却
            game.invincible_timer = 600  # 10秒无敌
            game.create_shield_particles()
    
    def update_cooldowns(self):
        """更新技能冷却时间"""
        for skill in self.skill_cooldowns:
            if self.skill_cooldowns[skill] > 0:
                self.skill_cooldowns[skill] -= 1
    
    def apply_passive_effects(self, game):
        """应用被动技能效果"""
        # 再生技能 - 每100帧恢复1格长度
        if 'regeneration' in self.passive_skills and game.animation_timer % 100 == 0:
            if len(game.snake) > 1:
                game.snake.append(game.snake[-1])
        
        # 铁胃技能 - 有概率不消化食物
        if 'iron_stomach' in self.passive_skills and hasattr(game, 'last_ate') and game.last_ate:
            if random.random() < 0.1:  # 10%概率
                game.snake.append(game.snake[-1])  # 额外增长
            game.last_ate = False
    
    def get_skill_names(self):
        """获取技能名称映射"""
        return {
            'speed_boost': 'Speed Boost',
            'double_points': 'Double Points',
            'magnet': 'Magnet',
            'thick_skin': 'Thick Skin',
            'regeneration': 'Regeneration',
            'lucky_charm': 'Lucky Charm',
            'ghost_mode': 'Ghost Mode',
            'iron_stomach': 'Iron Stomach',
            'shield': 'Shield',
            'teleport': 'Teleport',
            'time_slow': 'Time Slow',
            'food_rain': 'Food Rain',
            'obstacle_clear': 'Clear Obstacles',
            'super_speed': 'Super Speed',
            'invincibility': 'Invincibility'
        }
    
    def get_skill_descriptions(self):
        """获取技能描述映射"""
        return {
            'speed_boost': 'Move 50% faster',
            'double_points': 'Score x2',
            'magnet': 'Auto-attract food',
            'thick_skin': '30% dmg immunity',
            'regeneration': 'Grow every 5s',
            'lucky_charm': '20% chance x3 score',
            'ghost_mode': '20% chance pass walls',
            'iron_stomach': '10% chance extra growth',
            'shield': '3s invincibility (10s CD)',
            'teleport': 'Random safe position (5s CD)',
            'time_slow': 'Slow game speed (15s CD)',
            'food_rain': 'Spawn 3-5 temp foods (20s CD)',
            'obstacle_clear': 'Remove all obstacles (30s CD)',
            'super_speed': 'Ultra fast movement (8s CD)',
            'invincibility': 'Complete immunity (25s CD)'
        }
    
    def reset(self):
        """重置技能系统"""
        self.passive_skills = []
        self.active_skills = []
        self.skill_cooldowns = {}
        self.level = 1
        self.exp = 0
        self.exp_to_next_level = 100
