# generated from ament/cmake/core/templates/nameConfig.cmake.in

# prevent multiple inclusion
if(_pubsub_CONFIG_INCLUDED)
  # ensure to keep the found flag the same
  if(NOT DEFINED pubsub_FOUND)
    # explicitly set it to FALSE, otherwise CMake will set it to TRUE
    set(pubsub_FOUND FALSE)
  elseif(NOT pubsub_FOUND)
    # use separate condition to avoid uninitialized variable warning
    set(pubsub_FOUND FALSE)
  endif()
  return()
endif()
set(_pubsub_CONFIG_INCLUDED TRUE)

# output package information
if(NOT pubsub_FIND_QUIETLY)
  message(STATUS "Found pubsub: 0.0.0 (${pubsub_DIR})")
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "Package 'pubsub' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  message(WARNING "${_msg}")
endif()

# flag package as ament-based to distinguish it after being find_package()-ed
set(pubsub_FOUND_AMENT_PACKAGE TRUE)

# include all config extra files
set(_extras "")
foreach(_extra ${_extras})
  include("${pubsub_DIR}/${_extra}")
endforeach()
