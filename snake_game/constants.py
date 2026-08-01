import pygame
from enum import Enum

# 颜色定义
class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    DARK_GREEN = (0, 200, 0)
    BLUE = (0, 0, 255)
    GRAY = (128, 128, 128)
    
    # 新增精美颜色
    DARK_BLUE = (25, 25, 112)
    LIGHT_BLUE = (135, 206, 235)
    GOLD = (255, 215, 0)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 165, 0)
    PURPLE = (128, 0, 128)
    PINK = (255, 192, 203)
    LIME = (50, 205, 50)
    TEAL = (0, 128, 128)
    MAROON = (128, 0, 0)
    NAVY = (0, 0, 128)
    
    # 渐变背景颜色
    BG_TOP = (25, 25, 112)      # 深蓝色顶部
    BG_BOTTOM = (70, 130, 180)  # 钢蓝色底部
    
    # 新增精美颜色
    NEON_GREEN = (57, 255, 20)
    NEON_BLUE = (0, 255, 255)
    NEON_PINK = (255, 20, 147)
    NEON_PURPLE = (138, 43, 226)
    NEON_ORANGE = (255, 69, 0)
    NEON_YELLOW = (255, 255, 0)
    DARK_PURPLE = (48, 25, 52)
    LIGHT_PURPLE = (147, 112, 219)
    DEEP_BLUE = (25, 25, 112)
    EMERALD = (0, 201, 87)
    RUBY = (155, 17, 30)
    SAPPHIRE = (15, 82, 186)

# 方向枚举
class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

# 游戏配置
class GameConfig:
    SKILL_PANEL_WIDTH = 250  # 左侧技能面板宽度
    GAME_WIDTH = 800
    GAME_HEIGHT = 600
    UI_WIDTH = 250  # 右侧UI面板宽度
    WINDOW_WIDTH = SKILL_PANEL_WIDTH + GAME_WIDTH + UI_WIDTH
    WINDOW_HEIGHT = GAME_HEIGHT
    GRID_SIZE = 20
    GRID_WIDTH = GAME_WIDTH // GRID_SIZE
    GRID_HEIGHT = GAME_HEIGHT // GRID_SIZE
    GAME_SPEED = 10  # FPS
