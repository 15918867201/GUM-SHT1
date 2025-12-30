# -*- coding: utf-8 -*-
"""
API测试脚本 - 用于测试制造停机监控系统的API功能

功能包括：
- 功能测试：基本请求、不同时间范围、数据格式、实时数据
- 边界测试：空时间范围、开始时间大于结束时间、极端时间范围、未来时间
- 错误处理测试：缺失参数、无效参数、无效JSON、不支持的方法
- 代理测试：代理准确性、CORS头、OPTIONS请求
- 性能测试：响应时间基准、并发请求
- 安全测试：HTTPS强制、输入验证
"""

import requests
import json
import time
import concurrent.futures
import datetime
import statistics

class APITester:
    """API测试器类，用于执行各种API测试"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        "timeout": 10,  # 默认请求超时时间（秒）
        "headers": {
            "Content-Type": "application/json",
            "ngrok-skip-browser-warning": "1"
        },
        "concurrent_users": 10,  # 默认并发用户数
        "performance_iterations": 10  # 默认性能测试迭代次数
    }
    def __init__(self, api_url, internal_api_url=None, config=None):
        """初始化API测试器
        
        Args:
            api_url (str): API的URL地址
            internal_api_url (str, optional): 内部API的URL地址（用于代理测试）
            config (dict, optional): 自定义配置
        """
        self.api_url = api_url
        self.internal_api_url = internal_api_url
        self.test_results = []
        self.current_test = None
        
        # 合并默认配置和自定义配置
        self.config = self.DEFAULT_CONFIG.copy()
        if config:
            self.config.update(config)
        
    def log_test_result(self, test_name, status, expected, actual, message="", response_time=None):
        result = {
            "test_name": test_name,
            "status": status,
            "expected": expected,
            "actual": actual,
            "message": message,
            "response_time": response_time,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{test_name}: {status} - {message}")
        if response_time:
            print(f"  Response time: {response_time:.2f} ms")
            
    def make_api_request(self, payload, method="POST", headers=None, expected_status=200, timeout=None):
        """发送API请求并返回响应和响应时间
        
        Args:
            payload (dict): 请求有效负载
            method (str): 请求方法（POST, GET, OPTIONS）
            headers (dict, optional): 请求头
            expected_status (int): 期望的HTTP状态码
            timeout (int, optional): 请求超时时间
            
        Returns:
            tuple: (response对象, 响应时间毫秒)
        """
        # 使用配置的默认值或传入的值
        if headers is None:
            headers = self.config["headers"]
        if timeout is None:
            timeout = self.config["timeout"]
        
        start_time = time.time()
        response = None
        
        try:
            if method == "POST":
                response = requests.post(self.api_url, json=payload, headers=headers, timeout=timeout)
            elif method == "GET":
                response = requests.get(self.api_url, params=payload, headers=headers, timeout=timeout)
            elif method == "OPTIONS":
                response = requests.options(self.api_url, headers=headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
        except requests.RequestException:
            pass  # 捕获所有请求异常，在validate_response中处理
        finally:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            return response, response_time
            
    def validate_response(self, response, expected_status=200):
        """验证API响应是否有效
        
        Args:
            response (Response对象): API响应对象
            expected_status (int): 期望的HTTP状态码
            
        Returns:
            tuple: (是否有效, 结果或错误信息)
        """
        if response is None:
            return False, "Request failed or timed out"
            
        if response.status_code != expected_status:
            return False, f"Expected status {expected_status}, got {response.status_code}"
            
        try:
            json_data = response.json()
            return True, json_data
        except json.JSONDecodeError:
            return False, "Response is not valid JSON format"
            
    def generate_timestamp_range(self, hours=24):
        """生成时间戳范围
        
        Args:
            hours (int): 时间范围的小时数
            
        Returns:
            tuple: (开始时间戳, 结束时间戳)
        """
        end_time = int(time.time())
        start_time = end_time - (hours * 3600)
        return start_time, end_time

    def run_all_tests(self):
        print("Running all API tests...")
        start_time = time.time()
        
        # Run all test categories
        self.run_functional_tests()
        self.run_boundary_tests()
        self.run_error_handling_tests()
        self.run_proxy_tests()
        self.run_performance_tests()
        self.run_security_tests()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        self.generate_test_report()
        print(f"\nAll tests completed in {total_time:.2f} seconds")
        
    def run_functional_tests(self):
        print("\n=== Running Functional Tests ===")
        self.test_basic_request()
        self.test_different_time_ranges()
        self.test_data_format()
        self.test_real_time_data()
        
    def run_boundary_tests(self):
        print("\n=== Running Boundary Tests ===")
        self.test_empty_time_range()
        self.test_start_time_greater_than_end_time()
        self.test_extreme_time_ranges()
        self.test_future_time()
        self.test_missing_data_range()
        
    def run_error_handling_tests(self):
        print("\n=== Running Error Handling Tests ===")
        self.test_missing_parameters()
        self.test_invalid_parameters()
        self.test_invalid_json()
        self.test_unsupported_methods()
        
    def run_proxy_tests(self):
        print("\n=== Running Proxy Tests ===")
        if self.internal_api_url:
            self.test_proxy_accuracy()
        self.test_cors_headers()
        self.test_options_request()
        
    def run_performance_tests(self):
        print("\n=== Running Performance Tests ===")
        self.test_response_time_benchmark()
        self.test_concurrent_requests(self.config["concurrent_users"])
        
    def run_security_tests(self):
        print("\n=== Running Security Tests ===")
        self.test_https_enforcement()
        self.test_input_validation()
        
    def generate_test_report(self):
        report_path = "test_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        # Generate summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed_tests = total_tests - passed_tests
        
        print(f"\n=== Test Summary ===")
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success rate: {passed_tests/total_tests*100:.1f}%")
        
        # Performance summary if available
        performance_results = [r for r in self.test_results if r["response_time"] is not None]
        if performance_results:
            response_times = [r["response_time"] for r in performance_results]
            print(f"\n=== Performance Metrics ===")
            print(f"Average response time: {statistics.mean(response_times):.2f} ms")
            print(f"Median response time: {statistics.median(response_times):.2f} ms")
            print(f"95th percentile: {sorted(response_times)[int(len(response_times)*0.95)]:.2f} ms")
            print(f"Min response time: {min(response_times):.2f} ms")
            print(f"Max response time: {max(response_times):.2f} ms")
        
        print(f"\nDetailed report saved to: {report_path}")

    # Functional Tests
    def test_basic_request(self):
        test_name = "Basic Request Test"
        try:
            start_ts, end_ts = self.generate_timestamp_range(24)
            payload = {"start_datetime": start_ts, "end_datetime": end_ts}
            response, response_time = self.make_api_request(payload)
            
            is_valid, result = self.validate_response(response)
            if is_valid:
                self.log_test_result(test_name, "PASS", 200, response.status_code, "Basic request succeeded", response_time)
            else:
                self.log_test_result(test_name, "FAIL", 200, response.status_code if response else "None", result, response_time)
        except Exception as e:
            self.log_test_result(test_name, "ERROR", 200, "None", f"Exception: {str(e)}")
    
    def test_different_time_ranges(self):
        test_name = "Different Time Ranges Test"
        try:
            # Test different time ranges
            time_ranges = [1, 6, 24, 72, 168]  # 1小时, 6小时, 1天, 3天, 1周
            
            for hours in time_ranges:
                range_test_name = f"{test_name} ({hours}h)"
                start_ts, end_ts = self.generate_timestamp_range(hours)
                payload = {"start_datetime": start_ts, "end_datetime": end_ts}
                response, response_time = self.make_api_request(payload)
                
                is_valid, result = self.validate_response(response)
                if is_valid:
                    self.log_test_result(range_test_name, "PASS", 200, response.status_code, f"Time range {hours}h succeeded", response_time)
                else:
                    self.log_test_result(range_test_name, "FAIL", 200, response.status_code if response else "None", result, response_time)
        except Exception as e:
            self.log_test_result(test_name, "ERROR", 200, "None", f"Exception: {str(e)}")
    
    def test_data_format(self):
        test_name = "Data Format Test"
        try:
            start_ts, end_ts = self.generate_timestamp_range(24)
            payload = {"start_datetime": start_ts, "end_datetime": end_ts}
            response, response_time = self.make_api_request(payload)
            
            is_valid, result = self.validate_response(response)
            if is_valid:
                # Check if response contains expected data structure
                if isinstance(result, dict):
                    # Check for common data fields
                    expected_fields = ["rows", "total", "data"]
                    for field in expected_fields:
                        if field in result:
                            self.log_test_result(f"{test_name} - {field}", "PASS", "Exists", "Exists", f"Field {field} exists", response_time)
                        else:
                            self.log_test_result(f"{test_name} - {field}", "FAIL", "Exists", "Missing", f"Field {field} is missing", response_time)
                else:
                    self.log_test_result(test_name, "FAIL", "dict", type(result).__name__, "Response is not a dictionary", response_time)
            else:
                self.log_test_result(test_name, "FAIL", 200, response.status_code if response else "None", result, response_time)
        except Exception as e:
            self.log_test_result(test_name, "ERROR", 200, "None", f"Exception: {str(e)}")
    
    def test_real_time_data(self):
        test_name = "Real-time Data Test"
        try:
            # Test with very recent time range
            end_ts = int(time.time())
            start_ts = end_ts - 3600  # 1 hour ago
            payload = {"start_datetime": start_ts, "end_datetime": end_ts}
            response, response_time = self.make_api_request(payload)
            
            is_valid, result = self.validate_response(response)
            if is_valid:
                self.log_test_result(test_name, "PASS", 200, response.status_code, "Real-time data request succeeded", response_time)
            else:
                self.log_test_result(test_name, "FAIL", 200, response.status_code if response else "None", result, response_time)
        except Exception as e:
            self.log_test_result(test_name, "ERROR", 200, "None", f"Exception: {str(e)}")
    
    # Boundary Tests
    def test_empty_time_range(self):
        test_name = "Empty Time Range Test"
        try:
            # Test with same start and end time
            ts = int(time.time())
            payload = {"start_datetime": ts, "end_datetime": ts}
            response, response_time = self.make_api_request(payload)
            
            is_valid, result = self.validate_response(response)
            if is_valid:
                self.log_test_result(test_name, "PASS", 200, response.status_code, "Empty time range handled correctly", response_time)
            else:
                self.log_test_result(test_name, "FAIL", 200, response.status_code if response else "None", result, response_time)
        except Exception as e:
            self.log_test_result(test_name, "ERROR", 200, "None", f"Exception: {str(e)}")
    
    def test_start_time_greater_than_end_time(self):
        test_name = "Start Time > End Time Test"
        try:
            start_ts = int(time.time())
            end_ts = start_ts - 3600  # end time before start time
            payload = {"start_datetime": start_ts, "end_datetime": end_ts}
            response, response_time = self.make_api_request(payload)
            
            is_valid, result = self.validate_response(response)
            if is_valid:
                self.log_test_result(test_name, "FAIL", "Error", "Success", "Should return error for invalid time range", response_time)
            else:
                self.log_test_result(test_name, "PASS", "Error", "Error", "Correctly rejected invalid time range", response_time)
        except Exception as e:
            self.log_test_result(test_name, "ERROR", 200, "None", f"Exception: {str(e)}")
    
    def test_extreme_time_ranges(self):
        test_name = "Extreme Time Ranges Test"
        try:
            # Test very large time range (10 years)
            end_ts = int(time.time())
            start_ts = end_ts - (10 * 365 * 24 * 3600)
            payload = {"start_datetime": start_ts, "end_datetime": end_ts}
            response, response_time = self.make_api_request(payload)
            
            is_valid, result = self.validate_response(response)
            if is_valid:
                self.log_test_result(test_name, "PASS", 200, response.status_code, "Extreme time range handled correctly", response_time)
            else:
                self.log_test_result(test_name, "FAIL", 200, response.status_code if response else "None", result, response_time)
        except Exception as e:
            self.log_test_result(test_name, "ERROR", 200, "None", f"Exception: {str(e)}")
    
    def test_future_time(self):
        test_name = "Future Time Test"
        try:
            # Test with future time range
            start_ts = int(time.time()) + 3600
            end_ts = start_ts + 7200
            payload = {"start_datetime": start_ts, "end_datetime": end_ts}
            response, response_time = self.make_api_request(payload)
            
            is_valid, result = self.validate_response(response)
            if is_valid:
                self.log_test_result(test_name, "PASS", 200, response.status_code, "Future time range handled correctly", response_time)
            else:
                self.log_test_result(test_name, "FAIL", 200, response.status_code if response else "None", result, response_time)
        except Exception as e:
            self.log_test_result(test_name, "ERROR", 200, "None", f"Exception: {str(e)}")
    
    def test_missing_data_range(self):
        test_name = "Missing Data Range Test"
        try:
            # Test with very old time range (should return empty data)
            end_ts = 0  # Unix epoch
            start_ts = end_ts - 3600
            payload = {"start_datetime": start_ts, "end_datetime": end_ts}
            response, response_time = self.make_api_request(payload)
            
            is_valid, result = self.validate_response(response)
            if is_valid:
                self.log_test_result(test_name, "PASS", 200, response.status_code, "Missing data range handled correctly", response_time)
            else:
                self.log_test_result(test_name, "FAIL", 200, response.status_code if response else "None", result, response_time)
        except Exception as e:
            self.log_test_result(test_name, "ERROR", 200, "None", f"Exception: {str(e)}")
    
    # Error Handling Tests
    def test_missing_parameters(self):
        test_name = "Missing Parameters Test"
        try:
            # Test missing both parameters
            payload = {}
            response, response_time = self.make_api_request(payload)
            
            is_valid, result = self.validate_response(response)
            if is_valid:
                self.log_test_result(f"{test_name} (No Params)", "FAIL", "Error", "Success", "Should return error for missing parameters", response_time)
            else:
                self.log_test_result(f"{test_name} (No Params)", "PASS", "Error", "Error", "Correctly rejected missing parameters", response_time)
            
            # Test missing start_datetime
            start_ts, end_ts = self.generate_timestamp_range(24)
            payload = {"end_datetime": end_ts}
            response, response_time = self.make_api_request(payload)
            
            is_valid, result = self.validate_response(response)
            if is_valid:
                self.log_test_result(f"{test_name} (Missing Start)", "FAIL", "Error", "Success", "Should return error for missing start_datetime", response_time)
            else:
                self.log_test_result(f"{test_name} (Missing Start)", "PASS", "Error", "Error", "Correctly rejected missing start_datetime", response_time)
            
            # Test missing end_datetime
            payload = {"start_datetime": start_ts}
            response, response_time = self.make_api_request(payload)
            
            is_valid, result = self.validate_response(response)
            if is_valid:
                self.log_test_result(f"{test_name} (Missing End)", "FAIL", "Error", "Success", "Should return error for missing end_datetime", response_time)
            else:
                self.log_test_result(f"{test_name} (Missing End)", "PASS", "Error", "Error", "Correctly rejected missing end_datetime", response_time)
                
        except Exception as e:
            self.log_test_result(test_name, "ERROR", 200, "None", f"Exception: {str(e)}")
    
    def test_invalid_parameters(self):
        test_name = "Invalid Parameters Test"
        try:
            # Test with invalid parameter types
            invalid_payloads = [
                {"start_datetime": "not_a_number", "end_datetime": "also_not_a_number"},
                {"start_datetime": "123abc", "end_datetime": 1234567890},
                {"start_datetime": 1234567890, "end_datetime": "1234567890xyz"},
                {"start_datetime": None, "end_datetime": 1234567890},
                {"start_datetime": 1234567890, "end_datetime": None}
            ]
            
            for i, payload in enumerate(invalid_payloads):
                subtest_name = f"{test_name} ({i+1})"
                response, response_time = self.make_api_request(payload)
                
                is_valid, result = self.validate_response(response)
                if is_valid:
                    self.log_test_result(subtest_name, "FAIL", "Error", "Success", "Should return error for invalid parameters", response_time)
                else:
                    self.log_test_result(subtest_name, "PASS", "Error", "Error", "Correctly rejected invalid parameters", response_time)
        except Exception as e:
            self.log_test_result(test_name, "ERROR", 200, "None", f"Exception: {str(e)}")
    
    def test_invalid_json(self):
        test_name = "Invalid JSON Test"
        try:
            # Test with invalid JSON data
            headers = {
                "Content-Type": "application/json",
                "ngrok-skip-browser-warning": "1"
            }
            
            # Make a raw request with invalid JSON
            response = requests.post(self.api_url, data="not_valid_json", headers=headers, timeout=10)
            
            if response.status_code != 200:
                self.log_test_result(test_name, "PASS", "Error", response.status_code, "Correctly rejected invalid JSON")
            else:
                self.log_test_result(test_name, "FAIL", "Error", response.status_code, "Should return error for invalid JSON")
        except Exception as e:
            self.log_test_result(test_name, "ERROR", 200, "None", f"Exception: {str(e)}")
    
    def test_unsupported_methods(self):
        test_name = "Unsupported Methods Test"
        try:
            start_ts, end_ts = self.generate_timestamp_range(24)
            payload = {"start_datetime": start_ts, "end_datetime": end_ts}
            
            # Test GET method (should fail)
            response, response_time = self.make_api_request(payload, method="GET")
            if response.status_code != 200:
                self.log_test_result(f"{test_name} (GET)", "PASS", "Error", response.status_code, "Correctly rejected GET method", response_time)
            else:
                self.log_test_result(f"{test_name} (GET)", "FAIL", "Error", response.status_code, "Should reject GET method", response_time)
            
            # Test PUT method (should fail)
            try:
                response = requests.put(self.api_url, json=payload, timeout=10)
                if response.status_code != 200:
                    self.log_test_result(f"{test_name} (PUT)", "PASS", "Error", response.status_code, "Correctly rejected PUT method")
                else:
                    self.log_test_result(f"{test_name} (PUT)", "FAIL", "Error", response.status_code, "Should reject PUT method")
            except Exception as e:
                self.log_test_result(f"{test_name} (PUT)", "PASS", "Error", "Error", "Correctly rejected PUT method")
                
        except Exception as e:
            self.log_test_result(test_name, "ERROR", 200, "None", f"Exception: {str(e)}")
    
    # Proxy Tests
    def test_proxy_accuracy(self):
        test_name = "Proxy Accuracy Test"
        try:
            if not self.internal_api_url:
                self.log_test_result(test_name, "SKIP", 200, "None", "Internal API URL not provided")
                return
            
            start_ts, end_ts = self.generate_timestamp_range(24)
            payload = {"start_datetime": start_ts, "end_datetime": end_ts}
            
            # Get response from proxy
            proxy_response, proxy_time = self.make_api_request(payload)
            if not proxy_response:
                self.log_test_result(test_name, "FAIL", 200, "None", "Proxy request failed")
                return
            
            # Get response from internal API
            internal_response = requests.post(self.internal_api_url, json=payload, timeout=10)
            if not internal_response:
                self.log_test_result(test_name, "FAIL", 200, "None", "Internal API request failed")
                return
            
            # Compare responses
            if proxy_response.status_code == internal_response.status_code:
                if proxy_response.json() == internal_response.json():
                    self.log_test_result(test_name, "PASS", "Match", "Match", "Proxy and internal API responses match", proxy_time)
                else:
                    self.log_test_result(test_name, "FAIL", "Match", "Mismatch", "Proxy and internal API responses differ in data")
            else:
                self.log_test_result(test_name, "FAIL", internal_response.status_code, proxy_response.status_code, "Proxy and internal API status codes differ")
                
        except Exception as e:
            self.log_test_result(test_name, "ERROR", 200, "None", f"Exception: {str(e)}")
    
    def test_cors_headers(self):
        test_name = "CORS Headers Test"
        try:
            # Test OPTIONS request to check CORS headers
            response, response_time = self.make_api_request({}, method="OPTIONS")
            
            if response:
                # Check CORS headers
                cors_headers = {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type"
                }
                
                for header, expected_value in cors_headers.items():
                    actual_value = response.headers.get(header)
                    if actual_value:
                        if actual_value == expected_value:
                            self.log_test_result(f"{test_name} - {header}", "PASS", expected_value, actual_value, f"CORS header {header} is correct", response_time)
                        else:
                            self.log_test_result(f"{test_name} - {header}", "FAIL", expected_value, actual_value, f"CORS header {header} is incorrect", response_time)
                    else:
                        self.log_test_result(f"{test_name} - {header}", "FAIL", expected_value, "None", f"CORS header {header} is missing", response_time)
            else:
                self.log_test_result(test_name, "FAIL", "200", "None", "OPTIONS request failed")
                
        except Exception as e:
            self.log_test_result(test_name, "ERROR", 200, "None", f"Exception: {str(e)}")
    
    def test_options_request(self):
        test_name = "OPTIONS Request Test"
        try:
            response, response_time = self.make_api_request({}, method="OPTIONS")
            
            if response and response.status_code == 200:
                self.log_test_result(test_name, "PASS", 200, response.status_code, "OPTIONS request succeeded", response_time)
            else:
                self.log_test_result(test_name, "FAIL", 200, response.status_code if response else "None", "OPTIONS request failed", response_time)
                
        except Exception as e:
            self.log_test_result(test_name, "ERROR", 200, "None", f"Exception: {str(e)}")
    
    # Performance Tests
    def test_response_time_benchmark(self):
        test_name = "Response Time Benchmark Test"
        try:
            start_ts, end_ts = self.generate_timestamp_range(24)
            payload = {"start_datetime": start_ts, "end_datetime": end_ts}
            
            # Run multiple iterations to get reliable metrics
            iterations = self.config["performance_iterations"]
            response_times = []
            
            for i in range(iterations):
                response, response_time = self.make_api_request(payload)
                if response and response.status_code == 200:
                    response_times.append(response_time)
                    
            if response_times:
                avg_time = statistics.mean(response_times)
                median_time = statistics.median(response_times)
                p95_time = sorted(response_times)[int(len(response_times)*0.95)]
                
                self.log_test_result(test_name, "PASS", "<1000ms", f"Avg: {avg_time:.2f}ms", "Response time benchmark completed")
                print(f"  Average: {avg_time:.2f} ms")
                print(f"  Median: {median_time:.2f} ms")
                print(f"  95th percentile: {p95_time:.2f} ms")
                print(f"  Fastest: {min(response_times):.2f} ms")
                print(f"  Slowest: {max(response_times):.2f} ms")
            else:
                self.log_test_result(test_name, "FAIL", "<1000ms", "N/A", "No successful responses")
                
        except Exception as e:
            self.log_test_result(test_name, "ERROR", 200, "None", f"Exception: {str(e)}")
    
    def test_concurrent_requests(self, concurrent_users=10):
        test_name = f"Concurrent Requests Test ({concurrent_users} users)"
        try:
            start_ts, end_ts = self.generate_timestamp_range(24)
            payload = {"start_datetime": start_ts, "end_datetime": end_ts}
            
            # Run concurrent requests
            response_times = []
            success_count = 0
            
            def send_request():
                try:
                    response, response_time = self.make_api_request(payload)
                    if response and response.status_code == 200:
                        response_times.append(response_time)
                        return True
                    return False
                except:
                    return False
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
                results = list(executor.map(lambda x: send_request(), range(concurrent_users)))
                success_count = sum(results)
            
            if response_times:
                avg_time = statistics.mean(response_times)
                median_time = statistics.median(response_times)
                p95_time = sorted(response_times)[int(len(response_times)*0.95)] if len(response_times) >= 20 else "N/A"
                
                self.log_test_result(test_name, "PASS", concurrent_users, success_count, f"Concurrent requests completed", avg_time)
                print(f"  Success rate: {success_count/concurrent_users*100:.1f}%")
                print(f"  Average response time: {avg_time:.2f} ms")
                print(f"  Median response time: {median_time:.2f} ms")
                if p95_time != "N/A":
                    print(f"  95th percentile: {p95_time:.2f} ms")
            else:
                self.log_test_result(test_name, "FAIL", concurrent_users, 0, "No successful concurrent responses")
                
        except Exception as e:
            self.log_test_result(test_name, "ERROR", 200, "None", f"Exception: {str(e)}")
    
    # Security Tests
    def test_https_enforcement(self):
        test_name = "HTTPS Enforcement Test"
        try:
            # Check if the API is accessible via HTTP
            if "https://" in self.api_url:
                http_url = self.api_url.replace("https://", "http://")
                
                start_ts, end_ts = self.generate_timestamp_range(24)
                payload = {"start_datetime": start_ts, "end_datetime": end_ts}
                
                try:
                    response = requests.post(http_url, json=payload, timeout=5)
                    if response.status_code == 301 or response.status_code == 302:
                        self.log_test_result(test_name, "PASS", "Redirect", response.status_code, "API redirects HTTP to HTTPS")
                    else:
                        self.log_test_result(test_name, "FAIL", "Redirect", response.status_code, "API should enforce HTTPS")
                except requests.RequestException:
                    self.log_test_result(test_name, "PASS", "Redirect", "N/A", "HTTP endpoint not accessible")
            else:
                self.log_test_result(test_name, "SKIP", "HTTPS", "HTTP", "API URL is not HTTPS")
                
        except Exception as e:
            self.log_test_result(test_name, "ERROR", 200, "None", f"Exception: {str(e)}")
    
    def test_input_validation(self):
        test_name = "Input Validation Test"
        try:
            # Test with potentially malicious inputs
            malicious_payloads = [
                {"start_datetime": 1234567890, "end_datetime": 1234567890, "sql": "' OR '1'='1"},
                {"start_datetime": 1234567890, "end_datetime": "<script>alert('xss')</script>"},
                {"start_datetime": 1234567890, "end_datetime": 1234567890, "../../etc/passwd": "file"},
                {"start_datetime": 1234567890, "end_datetime": 1234567890, "__proto__": {"admin": True}}
            ]
            
            for i, payload in enumerate(malicious_payloads):
                subtest_name = f"{test_name} ({i+1})"
                response, response_time = self.make_api_request(payload)
                
                if response and response.status_code == 200:
                    # Check if the response is a valid JSON and doesn't contain error messages
                    try:
                        json_data = response.json()
                        if isinstance(json_data, dict) and "error" not in json_data:
                            self.log_test_result(subtest_name, "PASS", 200, response.status_code, "Malicious input handled safely", response_time)
                        else:
                            self.log_test_result(subtest_name, "FAIL", 200, response.status_code, "API returned error for malicious input", response_time)
                    except:
                        self.log_test_result(subtest_name, "FAIL", 200, response.status_code, "API returned invalid response for malicious input", response_time)
                else:
                    self.log_test_result(subtest_name, "PASS", 200, response.status_code if response else "None", "Malicious input rejected", response_time)
                
        except Exception as e:
            self.log_test_result(test_name, "ERROR", 200, "None", f"Exception: {str(e)}")


def main():
    """主函数，用于执行API测试"""
    # API配置 - 使用本地代理服务器进行测试
    API_URL = "http://localhost:5000/api/huacore.forms/documentapi/getvalue"
    INTERNAL_API_URL = "http://10.157.85.11/api/huacore.forms/documentapi/getvalue"
    
    # 自定义配置（可选）
    custom_config = {
        "timeout": 15,  # 增加超时时间
        "concurrent_users": 15,  # 增加并发用户数
        "performance_iterations": 10  # 性能测试迭代次数
    }
    
    # 创建测试器实例
    tester = APITester(API_URL, INTERNAL_API_URL, custom_config)
    
    # 运行所有测试
    tester.run_all_tests()

if __name__ == "__main__":
    main()