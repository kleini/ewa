# unit: meter
# empty drum diameter 0.25m, perimeter 0.785m
# full drum diameter 0.305m, perimeter 0.96m
PERIMETER = 0.96
# Gear reduction from motor shaft to drum shaft
GEAR_REDUCTION = 1/3.7


class RopeSpeed(object):
    @staticmethod
    def calculate_speed(rpm):
        # unit: rounds per minute
        rpm_drum = rpm * GEAR_REDUCTION
        # unit: meter per minute
        speed_per_minute = rpm_drum * PERIMETER
        # unit: kilometer per hour
        speed_per_hour = speed_per_minute * 60 / 1000
        return speed_per_hour
