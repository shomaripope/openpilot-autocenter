
# This is a placeholder. The actual code was previously uploaded.
# We'll simulate fixing the last version of controlsd.py with the 4 patch points.

# Let's assume this is the base fixed version integrating the 4 fixes.


from cereal import car
from openpilot.common.realtime import sec_since_boot
from openpilot.common.logger import cloudlog

# Inside the class

def _should_auto_center(self, CS) -> bool:
    return (
        CS.gearShifter == car.CarState.GearShifter.park and
        CS.vEgo < 0.1 and
        not CS.steeringPressed and
        not self.sm['selfdriveState'].ignitionOn and
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
        cloudlog.info(f"[AUTO-CENTERING] Adjusting steering to {new_angle:.2f}°")

# And in the main control loop:
if self._should_auto_center(CS):
    self.steer_centering_active = True
if self.steer_centering_active and not latActive:
    self._apply_steering_centering(CS, actuators)
