# CMake generated Testfile for 
# Source directory: /workspace/src/sample
# Build directory: /workspace/build/sample
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(copyright "/usr/bin/python3" "-u" "/opt/ros/dashing/share/ament_cmake_test/cmake/run_test.py" "/workspace/build/sample/test_results/sample/copyright.xunit.xml" "--package-name" "sample" "--output-file" "/workspace/build/sample/ament_copyright/copyright.txt" "--command" "/opt/ros/dashing/bin/ament_copyright" "--xunit-file" "/workspace/build/sample/test_results/sample/copyright.xunit.xml")
set_tests_properties(copyright PROPERTIES  LABELS "copyright;linter" TIMEOUT "60" WORKING_DIRECTORY "/workspace/src/sample")
add_test(cppcheck "/usr/bin/python3" "-u" "/opt/ros/dashing/share/ament_cmake_test/cmake/run_test.py" "/workspace/build/sample/test_results/sample/cppcheck.xunit.xml" "--package-name" "sample" "--output-file" "/workspace/build/sample/ament_cppcheck/cppcheck.txt" "--command" "/opt/ros/dashing/bin/ament_cppcheck" "--xunit-file" "/workspace/build/sample/test_results/sample/cppcheck.xunit.xml")
set_tests_properties(cppcheck PROPERTIES  LABELS "cppcheck;linter" TIMEOUT "120" WORKING_DIRECTORY "/workspace/src/sample")
add_test(cpplint "/usr/bin/python3" "-u" "/opt/ros/dashing/share/ament_cmake_test/cmake/run_test.py" "/workspace/build/sample/test_results/sample/cpplint.xunit.xml" "--package-name" "sample" "--output-file" "/workspace/build/sample/ament_cpplint/cpplint.txt" "--command" "/opt/ros/dashing/bin/ament_cpplint" "--xunit-file" "/workspace/build/sample/test_results/sample/cpplint.xunit.xml")
set_tests_properties(cpplint PROPERTIES  LABELS "cpplint;linter" TIMEOUT "120" WORKING_DIRECTORY "/workspace/src/sample")
add_test(lint_cmake "/usr/bin/python3" "-u" "/opt/ros/dashing/share/ament_cmake_test/cmake/run_test.py" "/workspace/build/sample/test_results/sample/lint_cmake.xunit.xml" "--package-name" "sample" "--output-file" "/workspace/build/sample/ament_lint_cmake/lint_cmake.txt" "--command" "/opt/ros/dashing/bin/ament_lint_cmake" "--xunit-file" "/workspace/build/sample/test_results/sample/lint_cmake.xunit.xml")
set_tests_properties(lint_cmake PROPERTIES  LABELS "lint_cmake;linter" TIMEOUT "60" WORKING_DIRECTORY "/workspace/src/sample")
add_test(uncrustify "/usr/bin/python3" "-u" "/opt/ros/dashing/share/ament_cmake_test/cmake/run_test.py" "/workspace/build/sample/test_results/sample/uncrustify.xunit.xml" "--package-name" "sample" "--output-file" "/workspace/build/sample/ament_uncrustify/uncrustify.txt" "--command" "/opt/ros/dashing/bin/ament_uncrustify" "--xunit-file" "/workspace/build/sample/test_results/sample/uncrustify.xunit.xml")
set_tests_properties(uncrustify PROPERTIES  LABELS "uncrustify;linter" TIMEOUT "60" WORKING_DIRECTORY "/workspace/src/sample")
add_test(xmllint "/usr/bin/python3" "-u" "/opt/ros/dashing/share/ament_cmake_test/cmake/run_test.py" "/workspace/build/sample/test_results/sample/xmllint.xunit.xml" "--package-name" "sample" "--output-file" "/workspace/build/sample/ament_xmllint/xmllint.txt" "--command" "/opt/ros/dashing/bin/ament_xmllint" "--xunit-file" "/workspace/build/sample/test_results/sample/xmllint.xunit.xml")
set_tests_properties(xmllint PROPERTIES  LABELS "xmllint;linter" TIMEOUT "60" WORKING_DIRECTORY "/workspace/src/sample")
