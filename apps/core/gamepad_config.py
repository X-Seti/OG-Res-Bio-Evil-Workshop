#!/usr/bin/env python3
#this belongs in apps/core/gamepad_config.py - Version: 1
# X-Seti - November19 2025 - Multi-Emulator Launcher - Gamepad Configuration

"""
Global Gamepad Configuration Manager
Handles controller detection, mapping, and RetroArch configuration
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

##Methods list -
# __init__
# detect_controllers
# get_controller_info
# get_retroarch_autoconfig
# save_config
# test_controller_input
# _create_retroarch_config
# _detect_ps4_controller
# _get_default_mapping

##class GamepadConfig -

class GamepadConfig: #vers 1
    """Manages gamepad configuration and mapping"""
    
    # Default button mappings for standard controllers
    DEFAULT_MAPPING = {
        "a": 0,
        "b": 1,
        "x": 2,
        "y": 3,
        "select": 6,
        "start": 7,
        "l1": 4,
        "r1": 5,
        "l2": -1,  # Axis
        "r2": -1,  # Axis
        "l3": 9,
        "r3": 10,
        "dpad_up": -1,
        "dpad_down": -1,
        "dpad_left": -1,
        "dpad_right": -1,
        "left_stick_x": 0,  # Axis
        "left_stick_y": 1,  # Axis
        "right_stick_x": 2,  # Axis
        "right_stick_y": 3   # Axis
    }
    
    def __init__(self, base_dir: Path): #vers 1
        """Initialize gamepad configuration"""
        self.base_dir = Path(base_dir)
        self.config_dir = self.base_dir / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_file = self.config_dir / "gamepad_config.json"
        self.controllers = {}
        
        self._load_config()
        
    def detect_controllers(self) -> List[Dict]: #vers 1
        """Detect connected controllers
        
        Returns:
            List of controller info dicts
        """
        controllers = []
        
        try:
            import pygame
            pygame.init()
            pygame.joystick.init()
            
            num_joysticks = pygame.joystick.get_count()
            
            for i in range(num_joysticks):
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                
                controller_info = {
                    "id": i,
                    "name": joystick.get_name(),
                    "axes": joystick.get_numaxes(),
                    "buttons": joystick.get_numbuttons(),
                    "hats": joystick.get_numhats(),
                    "guid": joystick.get_guid() if hasattr(joystick, 'get_guid') else None
                }
                
                # Check if it's a PS4 controller
                if "DualShock 4" in controller_info["name"] or "PS4" in controller_info["name"]:
                    controller_info["type"] = "ps4"
                    controller_info["mapping"] = self._detect_ps4_controller()
                else:
                    controller_info["type"] = "generic"
                    controller_info["mapping"] = self._get_default_mapping()
                
                controllers.append(controller_info)
                
            pygame.quit()
            
        except ImportError:
            print("pygame not available for controller detection")
        except Exception as e:
            print(f"Error detecting controllers: {e}")
            
        return controllers
        
    def get_controller_info(self, controller_id: int) -> Optional[Dict]: #vers 1
        """Get info about a specific controller"""
        return self.controllers.get(str(controller_id))
        
    def save_config(self, controller_id: int, mapping: Dict): #vers 1
        """Save controller mapping configuration"""
        self.controllers[str(controller_id)] = mapping
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.controllers, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving gamepad config: {e}")
            return False
            
    def get_retroarch_autoconfig(self, controller_id: int) -> str: #vers 1
        """Generate RetroArch autoconfig file content"""
        controller = self.controllers.get(str(controller_id))
        if not controller:
            return ""
            
        return self._create_retroarch_config(controller)
        
    def test_controller_input(self, controller_id: int, timeout: int = 5) -> Dict: #vers 1
        """Test controller input for button mapping
        
        Args:
            controller_id: Controller to test
            timeout: Seconds to wait for input
            
        Returns:
            Dict of detected button presses
        """
        detected_inputs = {}
        
        try:
            import pygame
            import time
            
            pygame.init()
            pygame.joystick.init()
            
            if controller_id >= pygame.joystick.get_count():
                return detected_inputs
                
            joystick = pygame.joystick.Joystick(controller_id)
            joystick.init()
            
            start_time = time.time()
            print(f"Testing controller: {joystick.get_name()}")
            print("Press buttons to map them...")
            
            while time.time() - start_time < timeout:
                pygame.event.pump()
                
                # Check buttons
                for i in range(joystick.get_numbuttons()):
                    if joystick.get_button(i):
                        detected_inputs[f"button_{i}"] = True
                        print(f"  Button {i} pressed")
                        
                # Check axes
                for i in range(joystick.get_numaxes()):
                    value = joystick.get_axis(i)
                    if abs(value) > 0.5:
                        detected_inputs[f"axis_{i}"] = value
                        print(f"  Axis {i}: {value:.2f}")
                        
                # Check hats (D-pad)
                for i in range(joystick.get_numhats()):
                    hat = joystick.get_hat(i)
                    if hat != (0, 0):
                        detected_inputs[f"hat_{i}"] = hat
                        print(f"  Hat {i}: {hat}")
                        
                time.sleep(0.1)
                
            pygame.quit()
            
        except Exception as e:
            print(f"Error testing controller: {e}")
            
        return detected_inputs
        
    def _load_config(self): #vers 1
        """Load saved controller configurations"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.controllers = json.load(f)
            except Exception as e:
                print(f"Error loading gamepad config: {e}")
                
    def _get_default_mapping(self) -> Dict: #vers 1
        """Get default controller mapping"""
        return self.DEFAULT_MAPPING.copy()
        
    def _detect_ps4_controller(self) -> Dict: #vers 1
        """Get PS4 DualShock 4 specific mapping"""
        return {
            "a": 1,      # Cross
            "b": 2,      # Circle
            "x": 0,      # Square
            "y": 3,      # Triangle
            "select": 8,  # Share
            "start": 9,   # Options
            "l1": 4,
            "r1": 5,
            "l2": 6,
            "r2": 7,
            "l3": 10,
            "r3": 11,
            "dpad_up": -1,
            "dpad_down": -1,
            "dpad_left": -1,
            "dpad_right": -1,
            "left_stick_x": 0,
            "left_stick_y": 1,
            "right_stick_x": 2,
            "right_stick_y": 5,
            "touchpad": 13,
            "ps_button": 12
        }
        
    def _create_retroarch_config(self, controller: Dict) -> str: #vers 1
        """Create RetroArch autoconfig format"""
        name = controller.get("name", "Controller")
        mapping = controller.get("mapping", {})
        
        config_lines = [
            f'input_device = "{name}"',
            f'input_driver = "udev"',
            f'input_vendor_id = "0"',
            f'input_product_id = "0"',
            ""
        ]
        
        # Map buttons
        retroarch_map = {
            "a": "input_a_btn",
            "b": "input_b_btn",
            "x": "input_x_btn",
            "y": "input_y_btn",
            "start": "input_start_btn",
            "select": "input_select_btn",
            "l1": "input_l_btn",
            "r1": "input_r_btn",
            "l2": "input_l2_btn",
            "r2": "input_r2_btn",
            "l3": "input_l3_btn",
            "r3": "input_r3_btn"
        }
        
        for key, retroarch_key in retroarch_map.items():
            if key in mapping:
                config_lines.append(f'{retroarch_key} = "{mapping[key]}"')
                
        # Map analog sticks
        analog_map = {
            "left_stick_x": ("input_l_x_plus_axis", "input_l_x_minus_axis"),
            "left_stick_y": ("input_l_y_plus_axis", "input_l_y_minus_axis"),
            "right_stick_x": ("input_r_x_plus_axis", "input_r_x_minus_axis"),
            "right_stick_y": ("input_r_y_plus_axis", "input_r_y_minus_axis")
        }
        
        for key, (plus_key, minus_key) in analog_map.items():
            if key in mapping:
                axis = mapping[key]
                config_lines.append(f'{plus_key} = "+{axis}"')
                config_lines.append(f'{minus_key} = "-{axis}"')
                
        return "\n".join(config_lines)


def list_connected_controllers(): #vers 1
    """List all connected controllers"""
    try:
        import pygame
        pygame.init()
        pygame.joystick.init()
        
        num_joysticks = pygame.joystick.get_count()
        
        if num_joysticks == 0:
            print("No controllers detected")
            return
            
        print(f"\nDetected {num_joysticks} controller(s):")
        print("=" * 60)
        
        for i in range(num_joysticks):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            
            print(f"\nController {i}:")
            print(f"  Name: {joystick.get_name()}")
            print(f"  Buttons: {joystick.get_numbuttons()}")
            print(f"  Axes: {joystick.get_numaxes()}")
            print(f"  Hats: {joystick.get_numhats()}")
            
        pygame.quit()
        
    except ImportError:
        print("pygame not installed. Install with: pip install pygame")
    except Exception as e:
        print(f"Error: {e}")


# CLI usage
if __name__ == "__main__":
    import sys
    
    base_dir = Path.cwd()
    
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        # List connected controllers
        list_connected_controllers()
        
    elif len(sys.argv) > 1 and sys.argv[1] == "detect":
        # Detect and save controller config
        config = GamepadConfig(base_dir)
        controllers = config.detect_controllers()
        
        print(f"\nDetected {len(controllers)} controller(s):")
        print("=" * 60)
        
        for ctrl in controllers:
            print(f"\nController {ctrl['id']}:")
            print(f"  Name: {ctrl['name']}")
            print(f"  Type: {ctrl['type']}")
            print(f"  Buttons: {ctrl['buttons']}")
            print(f"  Axes: {ctrl['axes']}")
            
    elif len(sys.argv) > 2 and sys.argv[1] == "test":
        # Test controller input
        controller_id = int(sys.argv[2])
        timeout = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        
        config = GamepadConfig(base_dir)
        inputs = config.test_controller_input(controller_id, timeout)
        
        print(f"\nDetected inputs:")
        for key, value in inputs.items():
            print(f"  {key}: {value}")
            
    elif len(sys.argv) > 2 and sys.argv[1] == "export":
        # Export RetroArch config
        controller_id = int(sys.argv[2])
        
        config = GamepadConfig(base_dir)
        retroarch_config = config.get_retroarch_autoconfig(controller_id)
        
        output_file = base_dir / "config" / "controller.cfg"
        with open(output_file, 'w') as f:
            f.write(retroarch_config)
            
        print(f"RetroArch config saved to: {output_file}")
        
    else:
        print("Multi-Emulator Launcher - Gamepad Configuration")
        print("=" * 60)
        print("\nUsage:")
        print("  python gamepad_config.py list              - List connected controllers")
        print("  python gamepad_config.py detect            - Detect and identify controllers")
        print("  python gamepad_config.py test <id> [sec]   - Test controller input")
        print("  python gamepad_config.py export <id>       - Export RetroArch config")
        print("\nExamples:")
        print("  python gamepad_config.py list")
        print("  python gamepad_config.py test 0 10")
        print("  python gamepad_config.py export 0")
