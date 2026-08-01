#!/usr/bin/env python3
"""
Snake Game 启动脚本
支持多种运行方式
"""

import sys
import os

def main():
    """主函数"""
    print("🐍 Snake Game - 模块化版本")
    print("=" * 40)
    print("选择运行方式:")
    print("1. 直接运行游戏")
    print("2. 显示帮助信息")
    print("3. 查看项目结构")
    print("4. 退出")
    
    while True:
        try:
            choice = input("\n请输入选择 (1-4): ").strip()
            
            if choice == '1':
                print("\n启动游戏...")
                from game import main as game_main
                game_main()
                break
            elif choice == '2':
                show_help()
            elif choice == '3':
                show_structure()
            elif choice == '4':
                print("再见！")
                break
            else:
                print("无效选择，请输入 1-4")
        except KeyboardInterrupt:
            print("\n\n游戏被用户中断")
            break
        except Exception as e:
            print(f"发生错误: {e}")
            break

def show_help():
    """显示帮助信息"""
    print("\n" + "=" * 40)
    print("游戏帮助")
    print("=" * 40)
    print("🎮 控制方式:")
    print("  方向键: 控制蛇的移动")
    print("  空格键: 暂停/继续游戏")
    print("  R键: 重新开始游戏")
    print("  ESC键: 退出游戏")
    print("  1/2/3键: 使用主动技能")
    print("\n🎯 游戏规则:")
    print("  - 吃食物增加长度和分数")
    print("  - 每3个食物中的第3个是大食物")
    print("  - 大食物提供5倍长度和5倍分数")
    print("  - 升级后获得随机技能")
    print("  - 避免撞到自己和障碍物")
    print("\n💡 技能系统:")
    print("  - 被动技能: 自动生效")
    print("  - 主动技能: 按键触发")
    print("  - 最多5个被动技能")
    print("  - 最多3个主动技能")

def show_structure():
    """显示项目结构"""
    print("\n" + "=" * 40)
    print("项目结构")
    print("=" * 40)
    print("snake_game/")
    print("├── main.py              # 主启动文件")
    print("├── game.py              # 主游戏逻辑")
    print("├── constants.py         # 常量定义")
    print("├── particle.py          # 粒子系统")
    print("├── skill_system.py      # 技能系统")
    print("├── renderer.py          # 渲染器")
    print("├── run.py               # 启动脚本")
    print("├── requirements.txt     # 依赖包")
    print("├── README.md           # 原始文档")
    print("└── README_MODULAR.md   # 模块化文档")
    print("\n📁 模块说明:")
    print("  constants.py: 颜色、方向、配置常量")
    print("  particle.py: 粒子效果系统")
    print("  skill_system.py: 技能获取和管理")
    print("  renderer.py: 所有绘制相关功能")
    print("  game.py: 主游戏逻辑和状态管理")

if __name__ == '__main__':
    main()
