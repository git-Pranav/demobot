execute_process(COMMAND "/home/rsldemo/demobot/build/joystick/joystick_drivers/wiimote/catkin_generated/python_distutils_install.sh" RESULT_VARIABLE res)

if(NOT res EQUAL 0)
  message(FATAL_ERROR "execute_process(/home/rsldemo/demobot/build/joystick/joystick_drivers/wiimote/catkin_generated/python_distutils_install.sh) returned error code ")
endif()