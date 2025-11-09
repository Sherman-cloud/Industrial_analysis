from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import json
import logging
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.outputs import ChatResult, ChatGeneration
import requests

# 配置日志
logger = logging.getLogger(__name__)

class SiliconFlowChat(BaseChatModel):
    """硅基流动API的Chat模型封装"""
    
    api_key: str
    model_name: str = "deepseek-ai/DeepSeek-R1"
    base_url: str = "https://api.siliconflow.cn/v1"
    temperature: float = 0.1
    max_tokens: int = 4000
    
    def __init__(self, api_key: str, model_name: str = "deepseek-ai/DeepSeek-R1", 
                 base_url: str = "https://api.siliconflow.cn/v1", **kwargs):
        super().__init__(
            api_key=api_key,
            model_name=model_name,
            base_url=base_url,
            **kwargs
        )
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs,
    ) -> ChatResult:
        """生成聊天响应"""
        # 转换消息格式
        api_messages = []
        for message in messages:
            if isinstance(message, SystemMessage):
                api_messages.append({"role": "system", "content": message.content})
            elif isinstance(message, HumanMessage):
                api_messages.append({"role": "user", "content": message.content})
            else:
                # 默认作为用户消息处理
                api_messages.append({"role": "user", "content": message.content})
        
        # 调用API
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model_name,
            "messages": api_messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False
        }
        
        if stop:
            data["stop"] = stop
        
        try:
            # 记录请求详情
            logger.debug(f"API请求URL: {self.base_url}/chat/completions")
            logger.debug(f"请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )
            
            # 记录响应详情
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")
            
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            generation = ChatGeneration(message=HumanMessage(content=content))
            return ChatResult(generations=[generation])
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP错误: {str(e)}")
            logger.error(f"响应内容: {e.response.text if e.response else '无响应'}")
            raise
        except Exception as e:
            logger.error(f"调用硅基流动API失败: {str(e)}")
            raise
    
    @property
    def _llm_type(self) -> str:
        return "siliconflow-chat"


class BaseAgent(ABC):
    """智能体基类"""
    
    def __init__(self, name: str, description: str, llm: BaseChatModel, 
                 tools: List[str], system_prompt: str = ""):
        self.name = name
        self.description = description
        self.llm = llm
        self.tools = tools
        self.system_prompt = system_prompt
        self.results = {}
    
    @abstractmethod
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """执行智能体任务"""
        pass
    
    def _create_messages(self, user_prompt: str) -> List[BaseMessage]:
        """创建消息列表"""
        messages = []
        if self.system_prompt:
            messages.append(SystemMessage(content=self.system_prompt))
        messages.append(HumanMessage(content=user_prompt))
        return messages
    
    def _call_llm(self, user_prompt: str) -> str:
        """调用LLM生成响应"""
        messages = self._create_messages(user_prompt)
        # 检查LLM类型并调用相应的方法
        if hasattr(self.llm, 'invoke'):
            response = self.llm.invoke(messages)
        elif hasattr(self.llm, '_generate'):
            response = self.llm._generate([messages])
            response = response.generations[0][0].text
        elif hasattr(self.llm, '__call__'):
            response = self.llm(messages)
        else:
            raise ValueError(f"LLM对象 {type(self.llm)} 不支持调用")
        
        # 处理不同类型的响应
        if hasattr(response, 'content'):
            return response.content
        elif isinstance(response, str):
            return response
        elif hasattr(response, 'text'):
            return response.text
        else:
            return str(response)
    
    def save_results(self, results: Dict[str, Any], output_path: str) -> None:
        """保存结果到文件"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logger.info(f"结果已保存到: {output_path}")
        except Exception as e:
            logger.error(f"保存结果失败: {str(e)}")


class MacroAgent(BaseAgent):
    """宏观经济分析智能体"""
    
    def __init__(self, model_name: str, api_key: str, data_query, data_analyzer, system_prompt: str = ""):
        # 初始化LLM
        llm = SiliconFlowChat(api_key=api_key, model_name=model_name)
        
        super().__init__(
            name="MacroAgent",
            description="分析宏观经济数据（GDP, CPI）与行业趋势的关系。",
            llm=llm,
            tools=["data_query", "data_analyzer"],
            system_prompt=system_prompt
        )
        
        # 保存工具引用
        self.data_query = data_query
        self.data_analyzer = data_analyzer
    
    def run(self, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行宏观经济分析"""
        # 获取数据
        try:
            gdp_data = self.data_query.get_data_summary("gdp.csv")
            cpi_data = self.data_query.get_data_summary("cpi.csv")
        except Exception as e:
            logger.error(f"获取宏观经济数据失败: {str(e)}")
            return {
                "status": "error",
                "error": f"获取宏观经济数据失败: {str(e)}"
            }
            
        # 构建提示词
        user_prompt = f"""
        作为宏观经济分析专家，请分析以下GDP和CPI数据与新能源汽车行业的关系。
        
        GDP数据概览:
        {gdp_data.get('summary', '')}
        
        CPI数据概览:
        {cpi_data.get('summary', '')}
        
        请关注：
        1. GDP增长与新能源汽车行业发展的相关性
        2. CPI变化对消费者购买新能源汽车意愿的影响
        3. 宏观经济环境对行业整体发展的潜在影响
        
        请以JSON格式返回分析结果，包含以下字段：
        - macro_summary: 宏观经济环境分析总结
        - macro_corr_matrix: 宏观经济指标与行业发展的相关性分析
        - key_insights: 关键洞察列表
        - recommendations: 基于宏观环境的建议
        """
        
        # 调用LLM
        response = self._call_llm(user_prompt)
        
        # 尝试解析JSON
        try:
            results = json.loads(response)
        except json.JSONDecodeError:
            # 如果解析失败，返回原始文本
            results = {
                "macro_summary": response,
                "macro_corr_matrix": {},
                "key_insights": [],
                "recommendations": []
            }
        
        self.results = results
        return results


class FinanceAgent(BaseAgent):
    """财务分析智能体"""
    
    def __init__(self, model_name: str, api_key: str, data_query, data_analyzer, system_prompt: str = ""):
        # 初始化LLM
        llm = SiliconFlowChat(api_key=api_key, model_name=model_name)
        
        super().__init__(
            name="FinanceAgent",
            description="负责新能源汽车行业的财务指标分析。",
            llm=llm,
            tools=["data_query", "data_analyzer"],
            system_prompt=system_prompt
        )
        
        # 保存工具引用
        self.data_query = data_query
        self.data_analyzer = data_analyzer
    
    def run(self, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行财务分析"""
        # 获取数据
        try:
            industry_data = self.data_query.get_data_summary("industry_data.csv")
            company_data = self.data_query.get_data_summary("company_data.csv")
        except Exception as e:
            logger.error(f"获取财务数据失败: {str(e)}")
            return {
                "status": "error",
                "error": f"获取财务数据失败: {str(e)}"
            }
            
        # 构建提示词
        user_prompt = f"""
        作为财务分析专家，请分析新能源汽车行业上市公司的财务表现。
        
        行业财务数据概览:
        {industry_data.get('summary', '')}
        
        公司财务数据概览:
        {company_data.get('summary', '')}
        
        请关注：
        1. 行业整体盈利能力趋势
        2. 资产负债结构与偿债能力
        3. 成长性指标与投资价值
        4. 行业内主要公司的财务表现对比
        
        请以JSON格式返回分析结果，包含以下字段：
        - finance_summary: 行业财务表现分析总结
        - key_metrics: 关键财务指标分析
        - company_comparison: 主要公司财务表现对比
        - investment_insights: 投资价值分析
        - risk_factors: 风险因素分析
        """
        
        # 调用LLM
        response = self._call_llm(user_prompt)
        
        # 尝试解析JSON
        try:
            results = json.loads(response)
        except json.JSONDecodeError:
            # 如果解析失败，返回原始文本
            results = {
                "finance_summary": response,
                "key_metrics": {},
                "company_comparison": {},
                "investment_insights": "",
                "risk_factors": ""
            }
        
        self.results = results
        return results


class MarketAgent(BaseAgent):
    """市场分析智能体"""
    
    def __init__(self, model_name: str, api_key: str, data_query, data_analyzer, system_prompt: str = ""):
        # 初始化LLM
        llm = SiliconFlowChat(api_key=api_key, model_name=model_name)
        
        super().__init__(
            name="MarketAgent",
            description="分析行业产销趋势、市场结构与渗透率。",
            llm=llm,
            tools=["data_query", "data_analyzer"],
            system_prompt=system_prompt
        )
        
        # 保存工具引用
        self.data_query = data_query
        self.data_analyzer = data_analyzer
    
    def run(self, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行市场分析"""
        # 获取数据
        try:
            production_data = self.data_query.get_data_summary("production_data.csv")
            charging_data = self.data_query.get_data_summary("charging_data.csv")
        except Exception as e:
            logger.error(f"获取市场数据失败: {str(e)}")
            return {
                "status": "error",
                "error": f"获取市场数据失败: {str(e)}"
            }
            
        # 构建提示词
        user_prompt = f"""
        作为市场分析专家，请分析新能源汽车市场的产销趋势和结构变化。
        
        产销数据概览:
        {production_data.get('summary', '')}
        
        充电设施数据概览:
        {charging_data.get('summary', '')}
        
        请关注：
        1. 产销量的季节性变化和长期趋势
        2. 主要厂商的市场份额变化
        3. 充电基础设施与市场发展的关系
        4. 市场渗透率变化及未来空间
        
        请以JSON格式返回分析结果，包含以下字段：
        - market_trend_summary: 市场产销趋势分析总结
        - penetration_rate: 市场渗透率分析
        - manufacturer_analysis: 主要厂商分析
        - infrastructure_insights: 基础设施建设洞察
        - market_forecast: 市场发展趋势预测
        """
        
        # 调用LLM
        response = self._call_llm(user_prompt)
        
        # 尝试解析JSON
        try:
            results = json.loads(response)
        except json.JSONDecodeError:
            # 如果解析失败，返回原始文本
            results = {
                "market_trend_summary": response,
                "penetration_rate": {},
                "manufacturer_analysis": {},
                "infrastructure_insights": "",
                "market_forecast": ""
            }
        
        self.results = results
        return results


class PolicyAgent(BaseAgent):
    """政策分析智能体"""
    
    def __init__(self, model_name: str, api_key: str, data_query, data_analyzer, system_prompt: str = ""):
        # 初始化LLM
        llm = SiliconFlowChat(api_key=api_key, model_name=model_name)
        
        super().__init__(
            name="PolicyAgent",
            description="结合宏观与行业数据，评估政策与市场信号的影响。",
            llm=llm,
            tools=["data_query", "data_analyzer"],
            system_prompt=system_prompt
        )
        
        # 保存工具引用
        self.data_query = data_query
        self.data_analyzer = data_analyzer
    
    def run(self, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行政策分析"""
        # 获取数据
        try:
            gdp_data = self.data_query.get_data_summary("gdp.csv")
            industry_data = self.data_query.get_data_summary("industry_data.csv")
        except Exception as e:
            logger.error(f"获取政策分析数据失败: {str(e)}")
            return {
                "status": "error",
                "error": f"获取政策分析数据失败: {str(e)}"
            }
            
        # 构建提示词
        user_prompt = f"""
        作为政策分析专家，请评估政策环境对新能源汽车行业的影响。
        
        宏观经济数据概览:
        {gdp_data.get('summary', '')}
        
        行业财务数据概览:
        {industry_data.get('summary', '')}
        
        请关注：
        1. 宏观经济政策与行业政策的协同效应
        2. 产业政策对市场发展的推动作用
        3. 基础设施政策与市场需求的匹配度
        4. 未来政策变化可能带来的影响
        
        请以JSON格式返回分析结果，包含以下字段：
        - policy_insight: 政策环境分析洞察
        - impact_analysis: 政策影响分析
        - policy_recommendations: 政策建议
        - regulatory_risks: 监管风险分析
        - future_outlook: 未来政策展望
        """
        
        # 调用LLM
        response = self._call_llm(user_prompt)
        
        # 尝试解析JSON
        try:
            results = json.loads(response)
        except json.JSONDecodeError:
            # 如果解析失败，返回原始文本
            results = {
                "policy_insight": response,
                "impact_analysis": {},
                "policy_recommendations": "",
                "regulatory_risks": "",
                "future_outlook": ""
            }
        
        self.results = results
        return results


class ForecastAgent(BaseAgent):
    """预测分析智能体"""
    
    def __init__(self, llm: BaseChatModel, tools: List[str], system_prompt: str = ""):
        super().__init__(
            name="ForecastAgent",
            description="根据历史趋势预测下一期市场走势。",
            llm=llm,
            tools=tools,
            system_prompt=system_prompt
        )
    
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """执行预测分析"""
        # 获取数据
        industry_data = inputs.get("industry_data")
        production_data = inputs.get("production_data")
        
        # 构建提示词
        user_prompt = f"""
        作为预测分析专家，请基于历史数据预测新能源汽车行业未来发展趋势。
        
        行业财务数据概览:
        {industry_data.get('summary', '')}
        
        产销数据概览:
        {production_data.get('summary', '')}
        
        请关注：
        1. 行业增长率的短期和中期预测
        2. 市场结构可能的变化
        3. 技术发展对市场的影响
        4. 风险因素与不确定性分析
        
        请以JSON格式返回分析结果，包含以下字段：
        - forecast_summary: 预测分析总结
        - growth_forecast: 增长率预测
        - market_structure_changes: 市场结构变化预测
        - technology_impact: 技术发展影响分析
        - risk_factors: 风险因素分析
        """
        
        # 调用LLM
        response = self._call_llm(user_prompt)
        
        # 尝试解析JSON
        try:
            results = json.loads(response)
        except json.JSONDecodeError:
            # 如果解析失败，返回原始文本
            results = {
                "forecast_summary": response,
                "growth_forecast": {},
                "market_structure_changes": {},
                "technology_impact": "",
                "risk_factors": ""
            }
        
        self.results = results
        return results


class ReportAgent(BaseAgent):
    """报告生成智能体"""
    
    def __init__(self, llm: BaseChatModel, tools: List[str], system_prompt: str = ""):
        super().__init__(
            name="ReportAgent",
            description="整合所有子智能体的输出，生成最终Markdown报告。",
            llm=llm,
            tools=tools,
            system_prompt=system_prompt
        )
    
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """生成综合报告"""
        # 获取各智能体的结果
        macro_results = inputs.get("MacroAgent", {})
        finance_results = inputs.get("FinanceAgent", {})
        market_results = inputs.get("MarketAgent", {})
        policy_results = inputs.get("PolicyAgent", {})
        forecast_results = inputs.get("ForecastAgent", {})
        
        # 构建提示词
        user_prompt = f"""
        请根据以下子智能体分析结果撰写一份完整的新能源汽车行业分析报告。
        
        宏观经济环境分析:
        {macro_results.get('macro_summary', '')}
        
        行业财务表现分析:
        {finance_results.get('finance_summary', '')}
        
        市场产销趋势分析:
        {market_results.get('market_trend_summary', '')}
        
        政策与环境影响分析:
        {policy_results.get('policy_insight', '')}
        
        预测与展望分析:
        {forecast_results.get('forecast_summary', '')}
        
        请按照以下结构撰写报告：
        # 新能源汽车行业分析报告
        
        ## 一、宏观经济环境
        [基于宏观经济分析结果]
        
        ## 二、行业财务表现
        [基于财务分析结果]
        
        ## 三、市场产销趋势
        [基于市场分析结果]
        
        ## 四、政策与环境影响
        [基于政策分析结果]
        
        ## 五、预测与展望
        [基于预测分析结果]
        
        ## 六、结论与建议
        [综合各模块结果，总结行业趋势与投资启示]
        """
        
        # 调用LLM
        response = self._call_llm(user_prompt)
        
        # 返回报告内容
        results = {
            "report_content": response,
            "report_type": "markdown"
        }
        
        self.results = results
        return results