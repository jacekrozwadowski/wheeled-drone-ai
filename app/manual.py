import RPi.GPIO as GPIO
import time
import sys
import asyncio
from sshkeyboard import listen_keyboard, stop_listening


def driving_forward_pins():
    # fr, fl, br, bl
    return 24, 12, 22, 17


def driving_backwards_pins():
    # fr, fl, br, bl
    return 23, 25, 13, 27


if __name__ == "__main__":

    # Set the mode to BCM
    GPIO.setmode(GPIO.BCM)

    # Set the PWM frequency in Hz (adjust as needed)
    frequency = 100  # Hz

    # Set the initial duty cycle (0-100, for 70% duty cycle, set it to 70)
    duty_l = 52
    duty_r = 45
    duty_turn_h = 65
    duty_turn_l = 25

    # Initialize the PWM channels for forward
    pwm_frf_pin, pwm_flf_pin, pwm_brf_pin, pwm_blf_pin = driving_forward_pins()

    GPIO.setup(pwm_frf_pin, GPIO.OUT)
    pwm_frf = GPIO.PWM(pwm_frf_pin, frequency)

    GPIO.setup(pwm_flf_pin, GPIO.OUT)
    pwm_flf = GPIO.PWM(pwm_flf_pin, frequency)

    GPIO.setup(pwm_brf_pin, GPIO.OUT)
    pwm_brf = GPIO.PWM(pwm_brf_pin, frequency)

    GPIO.setup(pwm_blf_pin, GPIO.OUT)
    pwm_blf = GPIO.PWM(pwm_blf_pin, frequency)

    # Initialize the PWM channels for backwards
    pwm_frb_pin, pwm_flb_pin, pwm_brb_pin, pwm_blb_pin = driving_backwards_pins()

    GPIO.setup(pwm_frb_pin, GPIO.OUT)
    pwm_frb = GPIO.PWM(pwm_frb_pin, frequency)

    GPIO.setup(pwm_flb_pin, GPIO.OUT)
    pwm_flb = GPIO.PWM(pwm_flb_pin, frequency)

    GPIO.setup(pwm_brb_pin, GPIO.OUT)
    pwm_brb = GPIO.PWM(pwm_brb_pin, frequency)

    GPIO.setup(pwm_blb_pin, GPIO.OUT)
    pwm_blb = GPIO.PWM(pwm_blb_pin, frequency)

    # init forward
    pwm_fr = pwm_frf
    pwm_fl = pwm_flf
    pwm_br = pwm_brf
    pwm_bl = pwm_blf

    async def press(key):
        print(f"'{key}' pressed")
        global pwm_fr, pwm_fl, pwm_br, pwm_bl

        # direction change to forward
        if key == "f":
            pwm_fr.stop()
            pwm_fl.stop()
            pwm_br.stop()
            pwm_bl.stop()

            pwm_fr = pwm_frf
            pwm_fl = pwm_flf
            pwm_br = pwm_brf
            pwm_bl = pwm_blf

        # direction change to backwards
        if key == "b":
            pwm_fr.stop()
            pwm_fl.stop()
            pwm_br.stop()
            pwm_bl.stop()

            pwm_fr = pwm_frb
            pwm_fl = pwm_flb
            pwm_br = pwm_brb
            pwm_bl = pwm_blb

        # forward driving
        if key == "up":
            pwm_fr.start(duty_r)
            pwm_fl.start(duty_l)
            pwm_br.start(duty_r)
            pwm_bl.start(duty_l)

        # backwards driving
        if key == "down":
            pwm_fr.stop()
            pwm_fl.stop()
            pwm_br.stop()
            pwm_bl.stop()

        # left driving
        if key == "left":
            pwm_fr.ChangeDutyCycle(duty_turn_h)
            pwm_br.ChangeDutyCycle(duty_turn_h)
            pwm_fl.ChangeDutyCycle(duty_turn_l)
            pwm_bl.ChangeDutyCycle(duty_turn_l)

        # right driving
        if key == "right":
            pwm_fr.ChangeDutyCycle(duty_turn_l)
            pwm_br.ChangeDutyCycle(duty_turn_l)
            pwm_fl.ChangeDutyCycle(duty_turn_h)
            pwm_bl.ChangeDutyCycle(duty_turn_h)

        # end
        if key == "e":
            GPIO.cleanup()
            stop_listening()

    listen_keyboard(
        on_press=press,
    )
