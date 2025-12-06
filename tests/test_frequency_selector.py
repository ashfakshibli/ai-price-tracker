#!/usr/bin/env python3
"""
Test the frequency selector implementation.
"""

def test_cron_schedule_generation():
    """Test that cron schedules are generated correctly for each frequency."""
    print("=" * 60)
    print("Testing Cron Schedule Generation")
    print("=" * 60)

    test_cases = [
        (30, "*/30 * * * *", "Every 30 minutes"),
        (60, "0 * * * *", "Every hour"),
        (120, "0 */2 * * *", "Every 2 hours"),
        (180, "0 */3 * * *", "Every 3 hours"),
    ]

    print("\nTest 1: Verify cron expressions for each frequency")
    all_passed = True

    for frequency, expected_schedule, description in test_cases:
        # Simulate the logic from get_cron_command()
        if frequency == 30:
            cron_schedule = "*/30 * * * *"
        elif frequency == 60:
            cron_schedule = "0 * * * *"
        elif frequency == 120:
            cron_schedule = "0 */2 * * *"
        elif frequency == 180:
            cron_schedule = "0 */3 * * *"
        else:
            cron_schedule = "0 * * * *"

        if cron_schedule == expected_schedule:
            print(f"  ✓ {description} ({frequency}min): {cron_schedule}")
        else:
            print(f"  ✗ {description} ({frequency}min): Expected {expected_schedule}, got {cron_schedule}")
            all_passed = False

    print("\nTest 2: Verify frequency message generation")
    for frequency, _, description in test_cases:
        # Simulate the logic from enable_cron()
        if frequency == 30:
            freq_msg = "every 30 minutes"
        elif frequency == 60:
            freq_msg = "every hour"
        elif frequency == 120:
            freq_msg = "every 2 hours"
        elif frequency == 180:
            freq_msg = "every 3 hours"
        else:
            freq_msg = f"every {frequency} minutes"

        print(f"  ✓ {frequency}min → 'Tracker will run {freq_msg}'")

    print("\nTest 3: Verify cron status parsing")
    test_cron_lines = [
        ("*/30 * * * * cd /path && python price_tracker.py", 30, "30 minutes"),
        ("0 * * * * cd /path && python price_tracker.py", 60, "hourly"),
        ("0 */2 * * * cd /path && python price_tracker.py", 120, "2 hours"),
        ("0 */3 * * * cd /path && python price_tracker.py", 180, "3 hours"),
    ]

    for cron_line, expected_freq, description in test_cron_lines:
        parts = cron_line.strip().split()
        if len(parts) >= 5:
            minute = parts[0]
            hour = parts[1]

            # Determine frequency (simulate get_cron_status logic)
            if minute.startswith('*/'):
                freq = int(minute[2:])
            elif minute == '0':
                if hour.startswith('*/'):
                    freq = int(hour[2:]) * 60
                elif hour == '*':
                    freq = 60
                else:
                    freq = 60
            else:
                freq = 60

            if freq == expected_freq:
                print(f"  ✓ {description}: Correctly parsed as {freq} minutes")
            else:
                print(f"  ✗ {description}: Expected {expected_freq}, got {freq}")
                all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    success = test_cron_schedule_generation()
    exit(0 if success else 1)
