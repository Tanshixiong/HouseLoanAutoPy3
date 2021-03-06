# coding:utf-8
"""
	description: 回退，取消，拒绝场景
	Author: tsx
	date: 2018-1-15
"""
import datetime
import time
import unittest

from cases import SET, v_l
from com import custom, base
from com.login import Login


class FallBack(unittest.TestCase, base.Base, SET):
	"""风控回退/拒绝/取消场景"""
	
	def setUp(self):
		self.env_file = "env.json"
		self.data_file = "data_xhd.json"
		base.Base.__init__(self, self.env_file, self.data_file)
		SET.__init__(self)
		self.se = SET()
		self.se.start_run()
	
	def tearDown(self):
		self.end_time = time.clock()
		self.case_using_time(self.begin_time, self.end_time)
		print(self.using_time)
		v_l.append({
			"name": self.case_name,
			"apply_code": self.apply_code,
			"result": self.run_result,
			"u_time": self.using_time,
			"s_time": self.s_time,
			"e_time": str(datetime.datetime.now()).split('.')[0]
			})
		self.se.end_run(v_l)
		self.page.driver.quit()
	
	def get_next_user(self, page, applycode):
		next_id = self.PM.process_monitor(page, applycode)
		if next_id is None:
			self.log.error("没有找到下一步处理人！")
			raise AssertionError("没有找到下一步处理人！")
		else:
			self.next_user_id = next_id
			self.log.info("下一步处理人:" + next_id)
			# 当前用户退出系统
			page.driver.quit()
	
	def test_01_branch_director_fallback(self):
		"""主管回退到申请录入"""
		
		"""
			1. 申请基本信息录入
		"""
		self.case_name = custom.get_current_function_name()
		try:
			
			custom.print_product_info(self.product_info)
			custom.print_person_info(self.person_info)
			self.before_application_entry()
			
			"""
				2. 风控回退
			"""
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			# 分公司主管回退
			res = self.PT.approval_to_review(page, self.apply_code, u'回退到申请录入', 1)
			if not res:
				self.run_result = False
				self.log.error("回退失败")
				raise ValueError("回退失败")
			else:
				self.log.info(u'分公司主管回退成功！')
				self.get_next_user(page, self.apply_code)
		except Exception as e:
			self.run_result = False
			raise e
	
	def test_02_branch_manager_fallback(self):
		"""分公司经理回退到申请录入"""
		self.case_name = custom.get_current_function_name()
		try:
			# 1. 进件
			custom.print_product_info(self.product_info)
			custom.print_person_info(self.person_info)
			self.before_application_entry()
			
			# 审批
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			# 分公司主管审批
			res = self.PT.approval_to_review(page, self.apply_code, u'分公司主管审批通过', 0)
			if not res:
				self.run_result = False
				self.log.error("审批失败")
				raise AssertionError('审批失败')
			else:
				self.log.info(u'分公司主管审批通过!')
				self.get_next_user(page, self.apply_code)
			
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			# 分公司经理回退
			res = self.PT.approval_to_review(page, self.apply_code, u'分公司经理回退到申请录入', 1)
			if not res:
				self.run_result = False
				self.log.error("回退失败")
				raise ValueError("回退失败")
			else:
				self.log.info(u'分公司经理回退到申请录入!')
				self.get_next_user(page, self.apply_code)
		except Exception as e:
			self.run_result = False
			raise e
	
	def test_03_regional_fallback(self):
		"""区域复核回退到申请录入"""
		self.case_name = custom.get_current_function_name()
		try:
			custom.print_product_info(self.product_info)
			custom.print_person_info(self.person_info)
			self.before_application_entry()
			# ----------- 审批--------------
			user_list = ['分公司主管', '分公司经理']
			for i in user_list:
				# 下一个处理人重新登录
				page = Login(self.next_user_id)
				res = self.PT.approval_to_review(page, self.apply_code, i, 0)
				self.risk_approval_result(res, i, page, self.apply_code)
			
			# ----------回退-----------
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			# 区域预复核回退
			res = self.PT.approval_to_review(page, self.apply_code, u'区域回退到申请录入', 1)
			if not res:
				self.run_result = False
				self.log.error("回退失败")
				raise ValueError("回退失败")
			else:
				self.log.info(u'区域回退到申请录入成功!')
				self.get_next_user(page, self.apply_code)
		except Exception as e:
			self.run_result = False
			raise e
	
	def test_04_manage_fallback(self):
		"""高级审批经理回退到申请录入"""
		self.case_name = custom.get_current_function_name()
		try:
			custom.print_product_info(self.product_info)
			custom.print_person_info(self.person_info)
			# 1. 申请录入
			self.before_application_entry()
			# 2. 审批
			user_list = ['分公司主管', '分公司经理', '区域经理']
			for i in user_list:
				# 下一个处理人重新登录
				page = Login(self.next_user_id)
				res = self.PT.approval_to_review(page, self.apply_code, i, 0)
				self.risk_approval_result(res, i, page, self.apply_code)
			
			if self.next_user_id != self.senior_manager:
				return
			
			# 3. 回退
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			# 审批经理回退
			res = self.PT.approval_to_review(page, self.apply_code, u'审批经理回退到申请录入成功', 1)
			if not res:
				self.run_result = False
				self.log.error("审批经理回退失败！")
				raise AssertionError('审批经理回退失败！')
			else:
				self.log.info(u'审批经理回退到申请录入成功!')
				self.get_next_user(page, self.apply_code)
		except Exception as e:
			self.run_result = False
			raise e
	
	def test_05_risk_fallback(self):
		"""风控逐级回退"""
		self.case_name = custom.get_current_function_name()
		option = [u'区域预复核', u'分公司经理', u'分公司风控主管', u'风控专员录入']
		try:
			custom.print_product_info(self.product_info)
			custom.print_person_info(self.person_info)
			self.before_application_entry()
			# 2. 风控审批
			user_list = ['分公司主管', '分公司经理', '区域经理']
			for i in user_list:
				# 下一个处理人重新登录
				page = Login(self.next_user_id)
				res = self.PT.approval_to_review(page, self.apply_code, i, 0)
				self.risk_approval_result(res, i, page, self.apply_code)
			
			if self.next_user_id != self.senior_manager:
				return
			
			# 3. 逐级回退
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			# 审批经理回退到区域预复核
			res = self.PT.risk_approval_fallback(page, self.apply_code, option[0], u'回退到区域预复核')
			if not res:
				self.run_result = False
				self.log.error("审批经理回退到区域预复核失败 ！")
				raise AssertionError('审批经理回退到区域预复核失败 ！')
			else:
				self.log.info(u'审批经理回退到区域预复核成功！')
				self.get_next_user(page, self.apply_code)
			
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			# 区域预复核回退到分公司经理
			res = self.PT.risk_approval_fallback(page, self.apply_code, option[1], u'回退到分公司经理')
			if not res:
				self.run_result = False
				self.log.error("区域预复核回退到分公司经理失败 ！")
				raise AssertionError('区域预复核回退到分公司经理失败 ！')
			else:
				self.log.info(u'区域预复核回退到分公司经理成功！')
				self.get_next_user(page, self.apply_code)
			
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			# 分公司经理回退到分公司主管
			res = self.PT.risk_approval_fallback(page, self.apply_code, option[2], u'回退到分公司主管')
			if not res:
				self.run_result = False
				self.log.error("分公司经理回退到分公司主管失败 ！")
				raise AssertionError('分公司经理回退到分公司主管失败 ！')
			else:
				self.log.info(u'区分公司经理回退到分公司主管成功！')
				self.get_next_user(page, self.apply_code)
			
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			# 分公司主管回退到申请录入
			res = self.PT.risk_approval_fallback(page, self.apply_code, option[3], u'回退到申请录入')
			if not res:
				self.run_result = False
				self.log.error("分公司主管回退到申请录入失败 ！")
				raise AssertionError('分公司主管回退到申请录入失败 ！')
			else:
				self.log.info(u'分公司主管回退到申请录入成功！')
				self.get_next_user(page, self.apply_code)
		except Exception as e:
			self.run_result = False
			raise e
	
	def test_01_branch_director_cancel(self):
		"""主管取消"""
		self.case_name = custom.get_current_function_name()
		try:
			"""
				1. 申请基本信息录入
			"""
			custom.print_product_info(self.product_info)
			custom.print_person_info(self.person_info)
			self.before_application_entry()
			"""
				2. 风控取消
			"""
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			# 分公司主管取消
			res = self.PT.approval_to_review(page, self.apply_code, u'主管取消', 2)
			if not res:
				self.run_result = False
				self.log.error("分公司主管取消失败")
				raise AssertionError('分公司主管取消失败')
			else:
				self.log.info(u'主管取消！')
				self.get_next_user(page, self.apply_code)
		except Exception as e:
			self.run_result = False
			raise e
	
	def test_02_branch_manager_cancel(self):
		"""分公司经理取消"""
		self.case_name = custom.get_current_function_name()
		try:
			# 1. 进件
			custom.print_product_info(self.product_info)
			custom.print_person_info(self.person_info)
			self.before_application_entry()
			# 2. 审批
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			# 分公司主管审批
			res = self.PT.approval_to_review(page, self.apply_code, u'分公司主管审批通过', 0)
			if not res:
				self.run_result = False
				self.log.error("审批失败")
				raise AssertionError('审批失败')
			else:
				self.log.info(u'分公司主管审批通过!')
				self.get_next_user(page, self.apply_code)
			
			# 3. 取消
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			# 分公司经理取消
			res = self.PT.approval_to_review(page, self.apply_code, u'分公司经理取消', 2)
			if not res:
				self.run_result = False
				self.log.error("分公司经理取消失败！")
				raise ValueError("分公司经理取消失败！")
			else:
				self.log.info(u'分公司经理取消!')
				self.get_next_user(page, self.apply_code)
		except Exception as e:
			self.run_result = False
			raise e
	
	def test_03_regional_cancel(self):
		"""区域复核取消"""
		self.case_name = custom.get_current_function_name()
		try:
			# 1. 进件
			custom.print_product_info(self.product_info)
			custom.print_person_info(self.person_info)
			self.before_application_entry()
			# 2. 审批
			user_list = ['分公司主管', '分公司经理']
			for i in user_list:
				# 下一个处理人重新登录
				page = Login(self.next_user_id)
				res = self.PT.approval_to_review(page, self.apply_code, i, 0)
				self.risk_approval_result(res, i, page, self.apply_code)
			
			# 3. 取消
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			# 区域预复核取消
			res = self.PT.approval_to_review(page, self.apply_code, u'区域取消', 2)
			if not res:
				self.run_result = False
				self.log.error("取消失败")
				raise AssertionError('取消失败')
			else:
				self.log.info(u'区域取消成功！')
				self.get_next_user(page, self.apply_code)
		except Exception as e:
			self.run_result = False
			raise e
	
	def test_04_manage_cancel(self):
		"""审批经理取消"""
		self.case_name = custom.get_current_function_name()
		try:
			# 1. 进件
			custom.print_product_info(self.product_info)
			custom.print_person_info(self.person_info)
			self.before_application_entry()
			# 2. 审批
			user_list = ['分公司主管', '分公司经理', '区域经理']
			for i in user_list:
				# 下一个处理人重新登录
				page = Login(self.next_user_id)
				res = self.PT.approval_to_review(page, self.apply_code, i, 0)
				self.risk_approval_result(res, i, page, self.apply_code)
			
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			# 审批经理取消
			res = self.PT.approval_to_review(page, self.apply_code, u'审审批经理取消成功', 2)
			if not res:
				self.run_result = False
				self.log.error("高级审批经理取消失败！")
				raise AssertionError('高级审批经理取消失败')
			else:
				self.log.info(u'高级审批经理取消成功！')
				self.get_next_user(page, self.apply_code)
		except Exception as e:
			self.run_result = False
			raise e
	
	def test_01_branch_director_reject(self):
		"""主管拒绝"""
		self.case_name = custom.get_current_function_name()
		try:
			"""
				1. 申请基本信息录入
			"""
			custom.print_product_info(self.product_info)
			custom.print_person_info(self.person_info)
			self.before_application_entry()
			"""
				2. 风控拒绝
			"""
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			# 分公司主管拒绝
			res = self.PT.approval_to_review(page, self.apply_code, u'主管拒绝', 3)
			if not res:
				self.run_result = False
				self.log.error("主管拒绝失败")
				raise AssertionError('主管拒绝失败')
			else:
				self.log.info('主管拒绝结束！')
				page.driver.quit()
			
			# 高级审批经理登录
			page = Login(self.senior_manager)
			
			# 拒绝
			value = self.HRL.reconsideration(page, self.apply_code)
			if value:
				self.log.info(u'主管拒绝成功，拒绝单已处于拒绝队列！')
				page.driver.quit()
			else:
				self.run_result = False
				self.log.error(u'主管拒绝失败，拒绝队列未找到该笔单！')
				raise AssertionError('主管拒绝失败，拒绝队列未找到该笔单！')
		except Exception as e:
			self.run_result = False
			raise e
	
	def test_01_branch_director_reject_pass(self):
		"""主管拒绝,并复议通过"""
		self.case_name = custom.get_current_function_name()
		try:
			"""
				1. 申请基本信息录入
			"""
			custom.print_product_info(self.product_info)
			self.before_application_entry()
			# 2. 进件
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			# 分公司主管回退
			res = self.PT.approval_to_review(page, self.apply_code, u'主管拒绝', 3)
			if not res:
				self.run_result = False
				self.log.error("主管拒绝失败")
				raise AssertionError('主管拒绝失败')
			else:
				self.log.info(u'主管拒绝！')
				page.driver.quit()
			
			# 高级审批经理登录
			page = Login(self.senior_manager)
			
			# 复议通过
			r1 = self.HRL.reconsideration(page, self.apply_code, 1)
			if r1:
				self.log.info(u'主管拒绝成功，复议通过！')
				page.driver.quit()
			else:
				self.run_result = False
				self.log.error(u'主管拒绝失败，复议出错！')
				raise AssertionError('主管拒绝失败，复议出错！')
		except Exception as e:
			self.run_result = False
			raise e
	
	def test_01_branch_director_reject_fail(self):
		"""主管拒绝,并复议不通过"""
		self.case_name = custom.get_current_function_name()
		try:
			"""
				1. 申请基本信息录入
			"""
			custom.print_product_info(self.product_info)
			custom.print_person_info(self.person_info)
			
			self.before_application_entry()
			"""
				2. 风控拒绝
			"""
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			# 分公司主管回退
			res = self.PT.approval_to_review(page, self.apply_code, u'主管拒绝', 3)
			if not res:
				self.run_result = False
				self.log.error("主管拒绝失败")
				raise AssertionError('主管拒绝失败，复议出错！')
			else:
				self.log.info(u'主管拒绝！')
				page.driver.quit()
			
			# 高级审批经理登录
			page = Login(self.senior_manager)
			
			# 复议通过
			r1 = self.HRL.reconsideration(page, self.apply_code, 2)
			if r1:
				self.log.info(u'主管拒绝成功，复议不通过成功！')
				page.driver.quit()
			else:
				self.run_result = False
				self.log.error(u'主管拒绝失败，复议不通过出错！')
				raise AssertionError('主管拒绝失败，复议不通过出错！')
		except Exception as e:
			self.run_result = False
			raise e
	
	def test_02_branch_manager_reject(self):
		"""分公司经理拒绝"""
		
		self.case_name = custom.get_current_function_name()
		try:
			custom.print_product_info(self.product_info)
			custom.print_person_info(self.person_info)
			self.before_application_entry()
			"""
				------------------------------------------------------------
									2. 风控审批拒绝
				------------------------------------------------------------
			"""
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			# 分公司主管审批
			res = self.PT.approval_to_review(page, self.apply_code, u'分公司主管审批', 0)
			if not res:
				self.run_result = False
				self.log.error("审批失败")
				raise AssertionError('审批失败')
			else:
				self.log.info(u'分公司主管审批通过!')
				self.get_next_user(page, self.apply_code)
			
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			# 分公司经理拒绝
			res = self.PT.approval_to_review(page, self.apply_code, u'分公司经理拒绝', 3)
			if not res:
				self.run_result = False
				self.log.error("分公司经理拒绝失败！")
				raise AssertionError('分公司经理拒绝失败！')
			else:
				self.log.info(u'分公司经理拒绝！')
				self.get_next_user(page, self.apply_code)
			
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			# 区域经理拒绝
			res = self.PT.approval_to_review(page, self.apply_code, u'区域经理拒绝', 3)
			if not res:
				self.run_result = False
				self.log.error("区域经理拒绝失败！")
				raise AssertionError('区域经理拒绝失败！')
			else:
				self.log.info(u'区域经理拒绝成功！')
				self.get_next_user(page, self.apply_code)
			
			# 下一步处理人登录
			page = Login(self.next_user_id)
			
			# 高级经理拒绝
			res = self.PT.approval_to_review(page, self.apply_code, u'高级经理拒绝', 3)
			if not res:
				self.run_result = False
				self.log.error("高级经理拒绝失败！")
				raise AssertionError('高级经理拒绝失败！')
			else:
				self.log.info(u'高级经理拒绝成功！')
				page.driver.quit()
			
			# 高级审批经理登录
			page = Login(self.senior_manager)
			
			# 拒绝
			value = self.HRL.reconsideration(page, self.apply_code)
			if value:
				self.log.info(u'分公司经理拒成功，拒绝单已处于拒绝队列！')
				page.driver.quit()
			else:
				self.run_result = False
				self.log.error(u'分公司经理拒绝失败，拒绝队列未找到该笔单！')
				raise AssertionError('分公司经理拒绝失败，拒绝队列未找到该笔单！')
		except Exception as e:
			self.run_result = False
			raise e
	
	def test_02_branch_manager_reject_pass(self):
		"""分公司经理拒绝,并复议通过"""
		
		self.case_name = custom.get_current_function_name()
		try:
			# 1. 进件
			custom.print_product_info(self.product_info)
			custom.print_person_info(self.person_info)
			self.before_application_entry()
			# 2. 审批
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			# 分公司主管审批
			res = self.PT.approval_to_review(page, self.apply_code, u'分公司主管审批通过', 0)
			if not res:
				self.run_result = False
				self.log.error("审批失败")
				raise AssertionError('审批失败')
			else:
				self.log.info(u'分公司主管审批通过!')
				self.get_next_user(page, self.apply_code)
			
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			# 分公司经理回退
			res = self.PT.approval_to_review(page, self.apply_code, u'分公司经理拒绝', 3)
			if not res:
				self.run_result = False
				self.log.error("分公司经理拒绝失败！")
				raise AssertionError('分公司经理拒绝失败！')
			else:
				self.log.info(u'分公司经理拒绝！')
				self.get_next_user(page, self.apply_code)
			
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			# 区域经理拒绝
			res = self.PT.approval_to_review(page, self.apply_code, u'区域经理拒绝', 3)
			if not res:
				self.run_result = False
				self.log.error("区域经理拒绝拒绝失败！")
				raise AssertionError('区域经理拒绝拒绝失败')
			else:
				self.log.info(u'区域经理拒绝！')
				self.get_next_user(page, self.apply_code)
			
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			# 高级经理拒绝
			res = self.PT.approval_to_review(page, self.apply_code, u'高级经理拒绝', 3)
			if not res:
				self.run_result = False
				self.log.error("高级经理拒绝失败！")
				raise AssertionError('高级经理拒绝失败！')
			else:
				self.log.info(u'高级经理拒绝成功！')
			
			# 高级审批经理登录
			page = Login(self.senior_manager)
			
			# 复议通过
			r1 = self.HRL.reconsideration(page, self.apply_code, 1)
			if r1:
				self.log.info(u'分公司经理拒绝成功，复议通过！')
				page.driver.quit()
			else:
				self.run_result = False
				self.log.error(u'分公司经理拒绝失败，复议出错！')
				raise AssertionError('分公司经理拒绝失败，复议出错！')
		except Exception as e:
			self.run_result = False
			raise e
	
	def test_02_branch_manager_reject_fail(self):
		"""分公司经理拒绝,并复议不通过"""
		self.case_name = custom.get_current_function_name()
		try:
			"""
				1. 申请基本信息录入
			"""
			custom.print_product_info(self.product_info)
			custom.print_person_info(self.person_info)
			self.before_application_entry()
			"""
				2. 风控拒绝
			"""
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			# 分公司主管审批
			res = self.PT.approval_to_review(page, self.apply_code, u'分公司主管审批通过', 0)
			if not res:
				self.run_result = False
				self.log.error("审批失败")
				raise AssertionError('审批失败')
			else:
				self.log.info(u'分公司主管审批通过!')
				self.get_next_user(page, self.apply_code)
			
			page = Login(self.next_user_id)
			# 分公司经理拒绝
			res = self.PT.approval_to_review(page, self.apply_code, u'分公司经理拒绝', 3)
			if not res:
				self.run_result = False
				self.log.error("分公司经理拒绝失败")
				raise AssertionError('分公司经理拒绝失败')
			else:
				self.log.info(u'分公司经理拒绝！')
			
			self.get_next_user(page, self.apply_code)
			
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			# 区域经理拒绝
			res = self.PT.approval_to_review(page, self.apply_code, u'区域经理拒绝', 3)
			if not res:
				self.run_result = False
				self.log.error("区域经理拒绝拒绝失败！")
				raise ValueError("区域经理拒绝拒绝失败！")
			else:
				self.log.info(u'区域经理拒绝！')
				self.get_next_user(page, self.apply_code)
			
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			# 高级经理拒绝
			res = self.PT.approval_to_review(page, self.apply_code, u'高级经理拒绝', 3)
			if not res:
				self.run_result = False
				self.log.error("高级经理拒绝失败！")
				raise AssertionError('高级经理拒绝失败！')
			else:
				self.log.info(u'高级经理拒绝成功！')
				page.driver.quit()
			
			# 高级审批经理登录
			page = Login(self.senior_manager)
			
			# 复议通过
			r1 = self.HRL.reconsideration(page, self.apply_code, 2)
			if r1:
				self.log.info(u'分公司经理拒绝成功，并复议不通过成功！')
				page.driver.quit()
			else:
				self.run_result = False
				self.log.error(u'分公司经理拒绝成功，但复议不通过出错！')
				raise AssertionError('分公司经理拒绝成功，但复议不通过出错！')
		except Exception as e:
			self.run_result = False
			raise e
	
	def test_03_regional_reject(self):
		"""区域复核拒绝"""
		self.case_name = custom.get_current_function_name()
		try:
			custom.print_product_info(self.product_info)
			custom.print_person_info(self.person_info)
			self.before_application_entry()
			
			# 2. 审批
			user_list = ['分公司主管', '分公司经理']
			for i in user_list:
				# 下一个处理人重新登录
				page = Login(self.next_user_id)
				res = self.PT.approval_to_review(page, self.apply_code, i, 0)
				self.risk_approval_result(res, i, page, self.apply_code)
			
			# 3. 拒绝
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			# 区域预复核拒绝
			res = self.PT.approval_to_review(page, self.apply_code, u'区域拒绝', 3)
			if not res:
				self.run_result = False
				self.log.error("区域拒绝失败")
				raise AssertionError('区域拒绝失败')
			else:
				self.log.info("区域拒绝！")
				self.get_next_user(page, self.apply_code)
			
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			res = self.PT.approval_to_review(page, self.apply_code, u'高级经理拒绝', 3)
			if not res:
				self.run_result = False
				self.log.error("高级经理拒绝失败")
				raise AssertionError('高级经理拒绝失败')
			else:
				self.log.info("高级经理拒绝拒绝成功！")
				page.driver.quit()
			
			# 高级审批经理登录
			page = Login(self.senior_manager)
			
			# 拒绝
			value = self.HRL.reconsideration(page, self.apply_code)
			if value:
				self.log.info(u'区域拒绝成功，拒绝单已处于拒绝队列！')
				page.driver.quit()
			else:
				self.run_result = False
				self.log.error(u'区域失败，拒绝队列未找到该笔单！')
				raise AssertionError('区域失败，拒绝队列未找到该笔单！')
		except Exception as e:
			self.run_result = False
			raise e
	
	def test_03_regional_reject_pass(self):
		"""区域复核拒绝，并复议通过"""
		
		self.case_name = custom.get_current_function_name()
		try:
			"""
				---------------------------------------------------------------------
										1. 申请基本信息录入
				---------------------------------------------------------------------
			"""
			custom.print_product_info(self.product_info)
			custom.print_person_info(self.person_info)
			
			self.before_application_entry()
			
			"""
				------------------------------------------------------------
									2. 风控审批取消
				------------------------------------------------------------
			"""
			# 2. 审批
			user_list = ['分公司主管', '分公司经理']
			for i in user_list:
				# 下一个处理人重新登录
				page = Login(self.next_user_id)
				res = self.PT.approval_to_review(page, self.apply_code, i, 0)
				self.risk_approval_result(res, i, page, self.apply_code)
			
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			# 区域预复核取消
			res = self.PT.approval_to_review(page, self.apply_code, u'区域拒绝', 3)
			if not res:
				self.run_result = False
				self.log.error("区域拒绝失败")
				raise AssertionError('区域拒绝失败')
			else:
				self.log.info("区域拒绝！")
				self.get_next_user(page, self.apply_code)
			
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			# 高级经理拒绝
			res = self.PT.approval_to_review(page, self.apply_code, u'高级经理拒绝', 3)
			if not res:
				self.run_result = False
				self.log.error("高级经理拒绝失败！")
				raise AssertionError('高级经理拒绝失败！')
			else:
				self.log.info(u'高级经理拒绝成功！')
				page.driver.quit()
			
			# 高级审批经理登录
			page = Login(self.senior_manager)
			
			# 复议通过
			r1 = self.HRL.reconsideration(page, self.apply_code, 1)
			if r1:
				self.log.info(u'区域拒绝成功！复议通过！')
				page.driver.quit()
			else:
				self.run_result = False
				self.log.error(u'区域拒绝失败，复议出错！')
				raise AssertionError('区域拒绝失败，复议出错！')
		except Exception as e:
			self.run_result = False
			raise e
	
	def test_03_regional_reject_fail(self):
		"""区域复核拒绝，并复议不通过"""
		self.case_name = custom.get_current_function_name()
		try:
			"""
				---------------------------------------------------------------------
										1. 申请基本信息录入
				---------------------------------------------------------------------
			"""
			custom.print_product_info(self.product_info)
			custom.print_person_info(self.person_info)
			self.before_application_entry()
			"""
				------------------------------------------------------------
									2. 风控审批拒绝
				------------------------------------------------------------
			"""
			# 2. 审批
			user_list = ['分公司主管', '分公司经理']
			for i in user_list:
				# 下一个处理人重新登录
				page = Login(self.next_user_id)
				res = self.PT.approval_to_review(page, self.apply_code, i, 0)
				self.risk_approval_result(res, i, page, self.apply_code)
			
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			# 区域预复核取消
			res = self.PT.approval_to_review(page, self.apply_code, u'区域拒绝', 3)
			if not res:
				self.run_result = False
				self.log.error("区域拒绝失败")
				raise AssertionError('区域拒绝失败')
			else:
				self.log.info("区域拒绝！")
				self.get_next_user(page, self.apply_code)
			
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			res = self.PT.approval_to_review(page, self.apply_code, u'高级经理拒绝', 3)
			if not res:
				self.run_result = False
				self.log.error("高级经理失败")
				raise AssertionError('高级经理失败')
			else:
				self.log.info("高级经理拒绝成功！")
				page.driver.quit()
			
			# 高级审批经理登录
			page = Login(self.senior_manager)
			
			# 复议通过
			r1 = self.HRL.reconsideration(page, self.apply_code, 2)
			if r1:
				self.log.info(u'区域拒绝成功，复议不通过成功！')
				page.driver.quit()
			else:
				self.run_result = False
				self.log.error(u'区域拒绝成功，复议不通过出错！')
				raise AssertionError('区域拒绝成功，复议不通过出错！')
		except Exception as e:
			self.run_result = False
			raise e
	
	def test_04_manage_reject(self):
		"""高级审批经理拒绝"""
		
		self.case_name = custom.get_current_function_name()
		try:
			custom.print_product_info(self.product_info)
			custom.print_person_info(self.person_info)
			self.before_application_entry()
			# ------------------------------------------------------------
			# 2. 风控审批拒绝
			# ------------------------------------------------------------
			
			# 2. 审批
			user_list = ['分公司主管', '分公司经理', '区域经理']
			for i in user_list:
				# 下一个处理人重新登录
				page = Login(self.next_user_id)
				res = self.PT.approval_to_review(page, self.apply_code, i, 0)
				self.risk_approval_result(res, i, page, self.apply_code)
			if self.next_user_id != self.senior_manager:
				return
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			# 高级经理拒绝
			res = self.PT.approval_to_review(page, self.apply_code, u'高级经理拒绝', 3)
			if not res:
				self.run_result = False
				self.log.error("高级经理拒绝失败！")
				raise AssertionError('高级经理拒绝失败！')
			else:
				self.log.info(u'高级经理拒绝成功！')
				page.driver.quit()
			
			# 高级审批经理登录
			page = Login(self.senior_manager)
			
			# 拒绝
			value = self.HRL.reconsideration(page, self.apply_code)
			if value:
				self.log.info(u'审批经理拒绝成功，拒绝单已处于拒绝队列！')
				page.driver.quit()
			else:
				self.run_result = False
				self.log.error(u'审批经理拒绝失败，拒绝队列未找到该笔单！')
				raise AssertionError(u'审批经理拒绝失败，拒绝队列未找到该笔单！')
		except Exception as e:
			self.run_result = False
			raise e
	
	def test_04_manage_reject_pass(self):
		"""高级审批经理拒绝,并复议通过"""
		
		self.case_name = custom.get_current_function_name()
		try:
			custom.print_product_info(self.product_info)
			custom.print_person_info(self.person_info)
			self.before_application_entry()
			"""
				------------------------------------------------------------
									2. 风控审批回退
				------------------------------------------------------------
			"""
			
			# 2. 审批
			user_list = ['分公司主管', '分公司经理', '区域经理']
			for i in user_list:
				# 下一个处理人重新登录
				page = Login(self.next_user_id)
				res = self.PT.approval_to_review(page, self.apply_code, i, 0)
				self.risk_approval_result(res, i, page, self.apply_code)
			
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			# 高级经理拒绝
			res = self.PT.approval_to_review(page, self.apply_code, u'高级经理拒绝', 3)
			if not res:
				self.run_result = False
				self.log.error("高级经理拒绝失败！")
				raise AssertionError('高级经理拒绝失败！')
			else:
				self.log.info(u'高级经理拒绝成功！')
				page.driver.quit()
			
			# 高级审批经理登录
			page = Login(self.senior_manager)
			
			# 复议通过
			r1 = self.HRL.reconsideration(page, self.apply_code, 1)
			if r1:
				self.log.info(u'复议通过！')
				page.driver.quit()
			else:
				self.run_result = False
				self.log.error(u'复议出错！')
				raise AssertionError('复议出错！')
		except Exception as e:
			self.run_result = False
			raise e
	
	def test_04_manage_reject_fail(self):
		"""高级审批经理拒绝,并复议不通过"""
		
		self.case_name = custom.get_current_function_name()
		try:
			custom.print_product_info(self.product_info)
			custom.print_person_info(self.person_info)
			self.before_application_entry()
			
			# 2. 审批
			user_list = ['分公司主管', '分公司经理', '区域经理']
			for i in user_list:
				# 下一个处理人重新登录
				page = Login(self.next_user_id)
				res = self.PT.approval_to_review(page, self.apply_code, i, 0)
				self.risk_approval_result(res, i, page, self.apply_code)
			
			# 下一个处理人重新登录
			page = Login(self.next_user_id)
			
			# 高级经理拒绝
			res = self.PT.approval_to_review(page, self.apply_code, u'高级经理拒绝', 3)
			if not res:
				self.run_result = False
				self.log.error("高级经理拒绝失败！")
				raise AssertionError('高级经理拒绝失败！')
			else:
				self.log.info(u'高级经理拒绝成功！')
				page.driver.quit()
			
			# 高级审批经理登录
			page = Login(self.senior_manager)
			
			# 复议通过
			r1 = self.HRL.reconsideration(page, self.apply_code, 2)
			if r1:
				self.log.info(u'复议不通过成功！')
				self.page.driver.quit()
			else:
				self.run_result = False
				self.log.error(u'复议不通过出错！')
				raise AssertionError(u'复议不通过出错！')
		except Exception as e:
			self.run_result = False
			raise e
