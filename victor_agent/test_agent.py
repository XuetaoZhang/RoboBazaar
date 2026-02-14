"""
RoboBazaar FinanceAgent - 测试脚本
"""
import json
import sys
from finance_agent import FinanceAgent, decide_payment

def test_rule_engine():
    """测试规则引擎模式"""
    print("\n" + "=" * 60)
    print("TEST 1: Rule Engine Mode")
    print("=" * 60)
    
    agent = FinanceAgent(use_llm=False)
    
    test_cases = [
        # (robot_id, risk_score, wallet_balance, expected_action)
        ("robot_01", 0.85, 10.0, "PAY_HUMAN"),      # 高风险，余额充足
        ("robot_02", 0.45, 10.0, "CONTINUE_AUTONOMOUS"),  # 低风险
        ("robot_03", 0.90, 0.1, "CONTINUE_AUTONOMOUS"),   # 高风险，余额不足
        ("robot_04", 0.70, 0.5, "CONTINUE_AUTONOMOUS"),   # 边界条件（等于阈值）
        ("robot_05", 0.71, 0.5, "PAY_HUMAN"),      # 刚过阈值
    ]
    
    passed = 0
    failed = 0
    
    for robot_id, risk, balance, expected in test_cases:
        result = agent.decide(robot_id, risk, balance)
        status = "✅" if result["action"] == expected else "❌"
        
        if result["action"] == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} {robot_id}: risk={risk}, balance={balance}")
        print(f"   Expected: {expected}, Got: {result['action']}")
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_convenience_function():
    """测试便捷函数"""
    print("\n" + "=" * 60)
    print("TEST 2: Convenience Function")
    print("=" * 60)
    
    result = decide_payment(
        robot_id="test_robot",
        risk_score=0.85,
        wallet_balance=5.0,
        use_llm=False
    )
    
    print(f"Result: {json.dumps(result, indent=2)}")
    
    assert result["action"] == "PAY_HUMAN"
    assert result["amount"] == 0.5
    assert result["currency"] == "USDC"
    
    print("✅ Convenience function test passed")
    return True


def test_json_output():
    """测试 JSON 输出格式"""
    print("\n" + "=" * 60)
    print("TEST 3: JSON Output Format")
    print("=" * 60)
    
    agent = FinanceAgent(use_llm=False)
    result = agent.decide("robot_json", 0.85, 10.0)
    
    required_keys = ["action", "amount", "currency", "robot_id", "reason"]
    
    for key in required_keys:
        if key not in result:
            print(f"❌ Missing key: {key}")
            return False
    
    # 验证可以序列化为 JSON
    try:
        json_str = json.dumps(result)
        parsed = json.loads(json_str)
        print(f"✅ Valid JSON: {json_str}")
        return True
    except Exception as e:
        print(f"❌ JSON error: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("RoboBazaar FinanceAgent Test Suite")
    print("=" * 60)
    
    results = []
    
    results.append(("Rule Engine", test_rule_engine()))
    results.append(("Convenience Function", test_convenience_function()))
    results.append(("JSON Output", test_json_output()))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
