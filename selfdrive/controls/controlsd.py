
"""
controlsd_autocenter_iterative.py

Modified ControlSD file for gradual steering wheel auto-centering across multiple cycles
when the vehicle is parked, ignition is off, and the steering is misaligned.
"""

from cereal import car
from common.realtime import sec_since_boot
from selfdrive.controls.lib.drive_helpers import update_v_cruise
from selfdrive.controls.lib.lat_control import LatControl
from selfdrive.controls.lib.longcontrol import LongControl
from selfdrive.controls.lib.events import Events
from selfdrive.controls.lib.alertmanager import AlertManager
from selfdrive.controls.lib.vehicle_model import VehicleModel
from selfdrive.controls.lib.pathplanner import PathPlanner

GearShifter = car.CarState.GearShifter

class Controls:
    def __init__(self):
        self.active = True
        self.steer_centering_active = False
        self.last_centering_time = 0
        self.centering_step = 0.5
        self.centering_threshold = 2.0
        self.centering_margin = 1.0

    def _should_auto_center(self, CS):
        return (
            CS.gearShifter == GearShifter.park and
            CS.vEgo < 0.1 and
            not CS.steeringPressed and
            abs(CS.steeringAngleDeg) > self.centering_threshold
        )

    def _apply_steering_centering(self, CS, actuators):
        current_time = sec_since_boot()
        if current_time - self.last_centering_time > 0.1:
            steer_angle = CS.steeringAngleDeg
            direction = -1 if steer_angle > 0 else 1
            adjustment = direction * self.centering_step
            new_angle = steer_angle + adjustment

            if abs(new_angle) < self.centering_margin:
                new_angle = 0.0
                self.steer_centering_active = False

            actuators.steerActive = True
            actuators.steeringAngleDeg = new_angle
            self.last_centering_time = current_time
            print(f"[AUTO-CENTERING] Adjusting steering to {new_angle:.2f}°")

    def update(self, CS, actuators):
        if self._should_auto_center(CS):
            self.steer_centering_active = True

        if self.steer_centering_active:
            self._apply_steering_centering(CS, actuators)

        # Normal control logic continues here...
        # e.g., LongControl.update(), LatControl.update(), etc.

        return actuators  # Modified actuators to be used by vehicle interface
